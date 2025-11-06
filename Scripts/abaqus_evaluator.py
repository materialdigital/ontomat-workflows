# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 11:18:45 2025

@author: chri
"""

import subprocess


def abaqus_evaluator(abq, sim_path, job_name, eval_script_path, RVE_volume):

    call_command = abq + \
        ' cae noGUI={} -- {} {} {}'.format(eval_script_path,
                                           sim_path, job_name, RVE_volume)

    subprocess.call(call_command, shell=True)
