"""
Workflow node definitions for a two-step multi-scale homogenization
using pyiron_workflow and Abaqus.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import requests
from pyiron_workflow import Workflow


# =============================================================================
# API helpers
# =============================================================================

def load_materials(url: str = "http://127.0.0.1:5001/ontomat/materials") -> dict:
    """
    Load all available materials from the OntOMat knowledge graph.

    Parameters
    ----------
    url : str
        Endpoint URL.

    Returns
    -------
    materials : dict
        Mapping of material label to IRI.
    """
    response = requests.get(url, timeout=30)
    rows = response.json()["results"]["bindings"]

    materials = {}
    for row in rows:
        mat_id = row.get("material", {}).get("value", "")
        mat_label = row.get("label", {}).get("value", "")
        if mat_label and mat_label not in materials:
            materials[mat_label] = mat_id

    return materials


def extract_material_properties(
    material_iri: str,
    properties: list[str],
    post_url: str = "http://127.0.0.1:5001/ontomat/values-by-material-and-property-class",
) -> dict:
    """
    Extract property values and standard deviations for a material from the KG.

    Parameters
    ----------
    material_iri : str
        IRI of the requested material.
    properties : list of str
        IRIs of requested property classes.
    post_url : str
        URL for the POST request.

    Returns
    -------
    result : dict
        Nested dictionary with value, std_dev, and unit per property.
    """
    result = {}

    for prop in properties:
        payload = json.dumps({
            "materia_id": material_iri,
            "property_class": prop,
        })

        response = requests.post(post_url, data=payload, timeout=30).json()
        entries = response["results"]["bindings"]

        values, std_devs, units = [], [], []
        for entry in entries:
            values.append(entry["value"]["value"] if "value" in entry else np.nan)
            std_devs.append(entry["std_dev"]["value"] if "std_dev" in entry else np.nan)
            units.append(entry["unit"]["value"] if "unit" in entry else np.nan)

        result[prop] = {"value": values, "std_dev": std_devs, "unit": units}

    return result


# =============================================================================
# Workflow nodes
# =============================================================================

@Workflow.wrap.as_function_node
def generate_sim_folder(sim_path: str = "") -> str:
    """Generate (or ensure existence of) the simulation folder."""
    if sim_path == "":
        sim_path = os.path.join(os.getcwd(), "sim_tmp") + "/"
    Path(sim_path).mkdir(parents=True, exist_ok=True)
    return sim_path


@Workflow.wrap.as_function_node
def remove_sim_folder(remove: bool = True, sim_path: str = ""):
    """Optionally remove the simulation folder after completion."""
    if remove:
        shutil.rmtree(sim_path)


@Workflow.wrap.as_function_node
def ontomat_query(
    fiber_material_IRI: str,
    matrix_material_IRI: str,
    sim_path: str,
    stochastic_factor: list,
) -> tuple[dict, str]:
    """
    Query the OntOMat KG for material properties and apply stochastic factors.

    Returns
    -------
    materials : dict
        Material parameters for fiber and matrix.
    sim_path : str
        Forwarded simulation path.
    """
    E1_IRI = "https://www.materialdigital.de/ontomat/ElasticModulusE1"
    nu12_IRI = "https://www.materialdigital.de/ontomat/PoissonsRatioV12"

    # Fiber
    fiber_name = fiber_material_IRI.split("/")[-1]
    fiber_props = extract_material_properties(fiber_material_IRI, [E1_IRI, nu12_IRI])
    E_fiber = float(fiber_props[E1_IRI]["value"][0])
    E_fiber_std = float(fiber_props[E1_IRI]["std_dev"][0])
    if np.isnan(E_fiber_std):
        E_fiber_std = 0.0
    nu_fiber = float(fiber_props[nu12_IRI]["value"][0])
    nu_fiber_std = float(fiber_props[nu12_IRI]["std_dev"][0])
    if np.isnan(nu_fiber_std):
        nu_fiber_std = 0.0

    # Matrix
    matrix_name = matrix_material_IRI.split("/")[-1]
    matrix_props = extract_material_properties(matrix_material_IRI, [E1_IRI, nu12_IRI])
    E_matrix = float(matrix_props[E1_IRI]["value"][0])
    E_matrix_std = float(matrix_props[E1_IRI]["std_dev"][0])
    if np.isnan(E_matrix_std):
        E_matrix_std = 0.0
    nu_matrix = float(matrix_props[nu12_IRI]["value"][0])
    nu_matrix_std = float(matrix_props[nu12_IRI]["std_dev"][0])
    if np.isnan(nu_matrix_std):
        nu_matrix_std = 0.0

    materials = {
        "fiber": {
            "name": fiber_name,
            "symmetry_class": "isotropic",
            "E": (E_fiber + E_fiber_std * stochastic_factor[0]),
            "nu": (nu_fiber + nu_fiber_std * stochastic_factor[2]),
        },
        "matrix": {
            "name": matrix_name,
            "symmetry_class": "isotropic",
            "E": (E_matrix + E_matrix_std * stochastic_factor[1]),
            "nu": (nu_matrix + nu_matrix_std * stochastic_factor[3]),
        },
    }

    return materials, sim_path


@Workflow.wrap.as_function_node
def ontomat_upload(material_ID: str, material_coefficients: dict):
    """Upload homogenized material parameters to the OntOMat KG."""
    # TODO: implement actual upload logic
    print("Uploading to OntOMat knowledge graph...")


@Workflow.wrap.as_function_node
def pre_process_micro(
    materials: dict,
    sim_path: str,
    plugin_path: str,
    abq: str,
    cae_name: str = "micro_structure.cae",
    job_name: str = "UD_hex_homogen",
    vol_frac: float = 0.1,
    fiber_rad: float = 0.3,
    interface_ratio: float = 0.0,
    depth: float = 0.3,
    num_rad: int = 10,
    num_depth: int = 5,
) -> tuple[str, str]:
    """Generate Abaqus CAE input for the micro-scale RVE."""
    abaqus_micro_input = {
        "micro": {
            "fiber": {
                "volume_content": vol_frac,
                "radius": fiber_rad,
                "interface_ratio": interface_ratio,
                "name": materials["fiber"]["name"],
                "symmetry_class": materials["fiber"]["symmetry_class"],
                "E": materials["fiber"]["E"],
                "nu": materials["fiber"]["nu"],
            },
            "matrix": {
                "name": materials["matrix"]["name"],
                "symmetry_class": materials["matrix"]["symmetry_class"],
                "E": materials["matrix"]["E"],
                "nu": materials["matrix"]["nu"],
            },
            "geometry": {
                "depth": depth,
                "mesh": {"num_rad": num_rad, "num_depth": num_depth},
            },
        },
        "simulation": {
            "sim_path": sim_path,
            "plugin_path": plugin_path,
            "cae_name": cae_name,
            "job_name": job_name,
        },
    }

    abaqus_json_path = os.path.join(sim_path, "abaqus_micro.json")
    with open(abaqus_json_path, "w") as f:
        json.dump(abaqus_micro_input, f, indent=2, sort_keys=True)

    cmd = f"{abq} cae noGUI=generate_cae_micro.py -- {abaqus_json_path}"
    subprocess.call(cmd, shell=True)

    return sim_path, job_name


@Workflow.wrap.as_function_node
def pre_process_meso(
    material: dict,
    orientations: list,
    sim_path: str,
    plugin_path: str,
    abq: str,
    cae_name: str = "meso_structure.cae",
    job_name: str = "UD_laminate_homogen",
) -> tuple[str, str]:
    """Generate Abaqus CAE input for the meso-scale laminate."""
    abaqus_meso_input = {
        "meso": {
            "orientations": orientations,
            "material_parameters": material,
        },
        "simulation": {
            "sim_path": sim_path,
            "plugin_path": plugin_path,
            "cae_name": cae_name,
            "job_name": job_name,
        },
    }

    abaqus_json_path = os.path.join(sim_path, "abaqus_meso.json")
    with open(abaqus_json_path, "w") as f:
        json.dump(abaqus_meso_input, f, indent=2, sort_keys=True)

    cmd = f"{abq} cae noGUI=generate_cae_meso.py -- {abaqus_json_path}"
    subprocess.call(cmd, shell=True)

    return sim_path, job_name


@Workflow.wrap.as_function_node
def abaqus_runner(
    sim_path: str,
    job_name: str,
    abaqus_cores: int = 1,
    abaqus_version: str = "2023",
    lic_server: str = "lic4",
) -> tuple[str, str]:
    """Submit the Abaqus job to the solver."""
    cmd = (
        f"cd {sim_path}; abawrapper -v {abaqus_version} "
        f"-j {job_name} -cpus {abaqus_cores} -l {lic_server} -inter"
    )
    subprocess.call(cmd, shell=True)
    return sim_path, job_name


@Workflow.wrap.as_function_node
def abaqus_evaluator(
    sim_path: str,
    job_name: str,
    abq: str,
    eval_script_path: str,
    RVE_volume: float = 1.0,
) -> tuple[str, dict, dict]:
    """Evaluate the Abaqus ODB and extract homogenized stiffness."""
    cmd = f"{abq} cae noGUI={eval_script_path} -- {sim_path} {job_name} {RVE_volume}"
    subprocess.call(cmd, shell=True)

    voigt_path = os.path.join(sim_path, f"{job_name}_homogenized_stiffness_voigt.json")
    with open(voigt_path, "r") as f:
        homogen_Voigt_json = json.load(f)

    mandel_path = os.path.join(sim_path, f"{job_name}_homogenized_stiffness_mandel.json")
    with open(mandel_path, "r") as f:
        homogen_Mandel_json = json.load(f)

    return sim_path, homogen_Voigt_json, homogen_Mandel_json


# =============================================================================
# Workflow assembly
# =============================================================================

def build_workflow() -> Workflow:
    """
    Construct the two-step micro→meso homogenization workflow.

    Returns
    -------
    wf : pyiron_workflow.Workflow
    """
    wf = Workflow("micro_simulation")

    # --- Micro scale ---
    wf.generate_sim_folder = generate_sim_folder()
    wf.ontomat_query = ontomat_query(
        sim_path=wf.generate_sim_folder.outputs.sim_path,
    )
    wf.pre_process_micro = pre_process_micro(
        materials=wf.ontomat_query.outputs.materials,
        sim_path=wf.ontomat_query.outputs.sim_path,
    )
    wf.abaqus_runner_micro = abaqus_runner(
        sim_path=wf.pre_process_micro.outputs.sim_path,
        job_name=wf.pre_process_micro.outputs.job_name,
    )
    wf.abaqus_evaluator_micro = abaqus_evaluator(
        sim_path=wf.abaqus_runner_micro.outputs.sim_path,
        job_name=wf.abaqus_runner_micro.outputs.job_name,
    )
    wf.ontomat_upload_micro = ontomat_upload(
        material_coefficients=wf.abaqus_evaluator_micro.outputs.homogen_Mandel_json,
    )

    # --- Meso scale ---
    wf.pre_process_meso = pre_process_meso(
        material=wf.abaqus_evaluator_micro.outputs.homogen_Voigt_json,
        sim_path=wf.abaqus_evaluator_micro.outputs.sim_path,
    )
    wf.abaqus_runner_meso = abaqus_runner(
        sim_path=wf.pre_process_meso.outputs.sim_path,
        job_name=wf.pre_process_meso.outputs.job_name,
    )
    wf.abaqus_evaluator_meso = abaqus_evaluator(
        sim_path=wf.abaqus_runner_meso.outputs.sim_path,
        job_name=wf.abaqus_runner_meso.outputs.job_name,
    )
    wf.ontomat_upload_meso = ontomat_upload(
        material_coefficients=wf.abaqus_evaluator_meso.outputs.homogen_Mandel_json,
    )

    # --- Cleanup ---
    wf.remove_sim_folder = remove_sim_folder(
        sim_path=wf.abaqus_evaluator_meso.outputs.sim_path,
    )

    return wf