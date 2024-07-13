
import numpy as np 


def nodes2dict(Model)->dict:
    model_nodes: np.ndarray = Model.nodes
    nodes_dict = {}

    for id, x, y, z in model_nodes:
        nodes_dict[id] = {
            "x": float(x),
            "y": float(y),
            "z": float(z)
        }
    return nodes_dict


def conect2dict(Model)->dict:
    model_conectivity: np.ndarray = Model.conect
    conectivity_dict = {}

    for eleid, nodei,nodej in model_conectivity:
        conectivity_dict[eleid] = {
            "nodei" : int(nodei),
            "nodej" : int(nodej)
        }
    return conectivity_dict

def mesh_quad2dict(Model)->dict:
    '''
    this function assumes that is 4 nodes quad 
    element
    '''
    model_quads: np.ndarray= Model.mesh_cells()
    quads_dict = {}

    for shll_id , mat_id , nodei,nodej,nodek, nodel in model_quads:
        quads_dict[shll_id] = {
            "mat_id":mat_id,
            "nodei":nodei,
            "nodej":nodej,
            "nodek":nodek,
            "nodel":nodel
        }
    return quads_dict

