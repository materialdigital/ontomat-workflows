import subprocess
from pathlib import Path


def pre_process_meso(input_json, input_json_path):
    """
    Genearte FE structure (cae and inp files) of a UD laminate.
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


    # prepare simulation files ...
    sim_path = input_json["simulation"]["sim_path"]
    Path(sim_path).mkdir(parents=True, exist_ok=True)

    job_name = input_json["simulation"]["micro"]["job_name"]
    material_json_path = sim_path + job_name + "_" + "homogenized_stiffness_voigt.json"

    # ... cae and inp
    abq = input_json["simulation"]["abaqus_path"]

    call_command = abq + \
        ' cae noGUI=generate_cae_meso.py -- {} {}'.format(
            input_json_path, material_json_path)

    # most likely requires some error handeling
    subprocess.call(call_command, shell=True)
