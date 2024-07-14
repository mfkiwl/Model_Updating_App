
import numpy as np 
import json

def nodes2dict(Model)->dict:
    model_nodes: np.ndarray = Model.nodes
    nodes_dict = {}

    for id, x, y, z in model_nodes:
        nodes_dict[int(id)] = {
            "x": float(x),
            "y": float(y),
            "z": float(z)
        }
    return nodes_dict


def conect2dict(Model)->dict:
    model_conectivity: np.ndarray = Model.conect
    conectivity_dict = {}

    for eleid, nodei,nodej in model_conectivity:
        conectivity_dict[int(eleid)] = {
            "nodei" : int(nodei),
            "nodej" : int(nodej)
        }
    return conectivity_dict

def mesh_quad2dict(Model)->dict:
    '''
    this function assumes that is 4 nodes quad 
    element
    '''
    model_quads: np.ndarray= Model.mesh_cells
    quads_dict = {}

    for shll_id , mat_id , nodei,nodej,nodek, nodel in model_quads:
        quads_dict[int(shll_id)] = {
            "mat_id":int(mat_id),
            "nodei":int(nodei),
            "nodej":int(nodej),
            "nodek":int(nodek),
            "nodel":int(nodel)
        }
    return quads_dict

def save_json(data:dict, path:str)->None:
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)