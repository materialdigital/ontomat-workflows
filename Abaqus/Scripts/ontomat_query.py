# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 14:21:14 2025

@author: chri
"""


def ontomat_query(material_id):
    """
    Return material parameters based on a SPARQL query to KG of OntOMat.

    Parameters
    ----------
    material_id : STRING
        Unique ID of material.

    Returns
    -------
    material : DICT
        Relevant material parameters.

    """

    # For now dummy data

    if material_id == 'carbon':
        material = {'name': 'carbon',
                    'symmetry_class': 'isotropic', 'E': 230e3, 'nu': 0.1}

    else:
        material = {'name': 'PA6',
                    'symmetry_class': 'isotropic', 'E': 2e3, 'nu': 0.33}

    return material
