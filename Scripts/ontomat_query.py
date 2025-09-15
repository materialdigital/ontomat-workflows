# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 14:21:14 2025

@author: chri
"""


def OntOMat_Query(material_id):

    # for now only dummy stuff

    if material_id == 'carbon':
        material = {'name': 'carbon',
                    'symmetry_class': 'isotropic', 'E': 230e3, 'nu': 0.1}

    else:
        material = {'name': 'PA6',
                    'symmetry_class': 'isotropic', 'E': 2e3, 'nu': 0.33}

    return material
