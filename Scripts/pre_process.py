import json
from ontomat_query import OntOMat_Query
import subprocess
from pathlib import Path


if __name__ == "__main__":

    input_json_path = "C:\IWM_IRTG\Code\Python\Pyiron_Workflow\workflow_input.json"

    with open(input_json_path, 'r') as json_file:
        input_json = json.load(json_file)

    # query OntOMat for material parameters -> QueryNode
    fiber_material_ID = input_json["fiber"]["material_id"]
    fiber_mat = OntOMat_Query(fiber_material_ID)

    matrix_material_ID = input_json["matrix"]["material_id"]
    matrix_mat = OntOMat_Query(matrix_material_ID)

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
    subprocess.call(call_command, shell=True)


    # run simulation and evaluate Node
    
    # ...
    
    
    # OntOMat upload Node
    
    # ...