
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


def sections_assignations(Model):
    '''
    dict : key is element id , values are section id and rotation
    
    '''
    sections_assignation = Model.idele
    sect_asig_dict = {}
    for eleid,sectionid,rotation in sections_assignation:
        sect_asig_dict[int(eleid)] = {
            "secid": int(sectionid),
            "rotation": float(rotation)
        }
    return sect_asig_dict


def get_model_modeshapes(Model, mode_shape_num:int , scale_factor:int)->dict:
    ops, _ = Model.create_model(verbose=False)

    nodes:dict  = nodes2dict(Model)
    modeshape:dict = {}
    magnitude:dict = {} 
    mode_shape_dict = {}


    _ = Model.Modal_analysis(Nm = mode_shape_num)

    for modid  in range(1,mode_shape_num+1):
        for node_key, coordinates in nodes.items():
            x,y,z = coordinates.values()

            ux = ops.nodeEigenvector(node_key, modid)[0]
            uy = ops.nodeEigenvector(node_key, modid)[1]
            uz = ops.nodeEigenvector(node_key, modid)[2]

            magnitud_value = np.linalg.norm([ux,uy,uz])

            modeshape[node_key] = {'x': coordinates['x']+scale_factor*ux,
                            'y': coordinates['y']+scale_factor*uy,
                            'z': coordinates['z']+scale_factor*uz
                            }
            magnitude[node_key] = {'magnitud':magnitud_value}


        mode_shape_dict[f'modeshape_{modid}'] = modeshape
        mode_shape_dict[f'magnitud_{modid}'] = magnitude
    mode_shape_dict['nodes'] = nodes

    return mode_shape_dict



def save_json(data:dict, path:str)->None:
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)