# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 11:18:45 2025

@author: chri
"""

import subprocess


def abaqus_evaluator(input_json, RVE_volume):

    abq = input_json["simulation"]["abaqus_path"]
    sim_path = input_json["simulation"]["sim_path"]
    job_name = input_json["simulation"]["job_name"]
    eval_script_path = input_json["simulation"]["eval_script_path"]

    call_command = abq + \
        ' cae noGUI={} -- {} {} {}'.format(eval_script_path,
                                           sim_path, job_name, RVE_volume)

    subprocess.call(call_command, shell=True)
