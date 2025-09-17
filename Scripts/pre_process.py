import json
from ontomat_query import ontomat_query
import subprocess
from pathlib import Path


def pre_process(input_json, input_json_path):
    """
    Genearte FE structure (cae and inp files) of a regular, hexagonally alligned
    uni-directional fiber reinforced composite. The backend is the Abaqus
    'micro mechanics' plugin, which also takes care of the meshing, periodicity
    and boundary conditions.

    Parameters
    ----------
    input_json : DICT
        JSON file, which stores all necessary parameters. The JSON should
        have the following structure:
            {
                "fiber" : {
                    "material_id" : ...         <- Unique ID in KG of OntOMat
                    "radius" : ...,             <- Fiber radius
                    "interface_ratio" : ...,    <- Interface ratio to fiber radius
                    "volume_content" : ...,     <- Fiber volume content
                    },
                "matrix" : {
                    "material_id" : ...         <- Unique ID in KG of OntOMat
                    },
                "geometry" : {
                    "depth" : ...,              <- Depth of RVE
                    "mesh" : {
                        "num_rad" : ...,        <- Element count in radial direction
                        "num_depth" : ...       <- Element count in depth direction
                        }
                    },
                "simulation" : {
                    "sim_path" : ...,           <- Path to where generated files will be stored
                    "cae_name" : ...,           <- Name of *.cae file
                    "job_name" : ...,           <- Name of *.inp file
                    "eval_script_path" : ...,   <- Path to evaluation script after job is finished
                    "abaqus_path" : ...         <- Path to Abaqus executable
                    }
            }
    input_json_path : STRING
        Path to JSON file.

    Returns
    -------
    None.

    """

    # query OntOMat for material parameters -> QueryNode
    fiber_material_ID = input_json["fiber"]["material_id"]
    fiber_mat = ontomat_query(fiber_material_ID)

    matrix_material_ID = input_json["matrix"]["material_id"]
    matrix_mat = ontomat_query(matrix_material_ID)

    # generate full dict
    materials = {}
    materials['fiber'] = fiber_mat
    materials['matrix'] = matrix_mat

    # prepare simulation files ...
    sim_path = input_json["simulation"]["sim_path"]
    Path(sim_path).mkdir(parents=True, exist_ok=True)

    material_json_path = sim_path + 'materials.json'
    with open(material_json_path, 'w') as materials_file:
        json.dump(materials, materials_file)

    # ... cae and inp
    abq = input_json["simulation"]["abaqus_path"]

    call_command = abq + \
        ' cae noGUI=generate_cae.py -- {} {}'.format(
            input_json_path, material_json_path)

    # most likely requires some error handeling
    subprocess.call(call_command, shell=True)
