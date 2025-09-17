# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 08:05:57 2025

@author: chri
"""

import subprocess


def abaqus_runner(job_path, job_name, abaqus_cores):

    call_command = "cd {job_path}; abawrapper -v 2023 -j {job_name} -cpus {abaqus_cores} -l lic5 -inter".format(
        job_path=job_path, job_name=job_name, abaqus_cores=abaqus_cores)

    subprocess.call(call_command, shell=True)

    print(call_command)
