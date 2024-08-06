import numpy as np 
import sys
import time
import matplotlib.pyplot as plt 
import time
import opsvis as opsv
import warnings
import copy

from pathlib import Path
from loading_csv_rfem import run_parsers
from _helpers_model_upd import ModelUpdater,mas_dist,metropolis_hastings,run_chains_parallel,run_model_single,plot_pair_grid,update_model

from Opensees_Engine import Model

from classes import Parameter, ProposalParameters, ParameterRecorder, TargedParameter, RecorderList

plt.close('all')
warnings.filterwarnings('ignore')

#%% Create txt from the rfem csv 
current_directory = Path.cwd()
_dir = current_directory / "Footbridge"
run_parsers(_dir)

node_path = _dir / 'Nodes.txt' 
conectivity_path = _dir /'Lines.txt'
element_id_path = _dir /'Elementid.txt'
members_prop_path =_dir / 'Member.txt'
members_name_path =_dir / 'Names.txt'
mesh_cells_path = _dir /'Mesh_Cells.txt'
surfaces_path =_dir / 'Surface.txt'
surface_materials =_dir / 'plate_materials.txt'
nodal_loads_path = _dir /'nodal_nodes.txt'
surface_loads_path = _dir /'surface_loads.txt'
support =  np.loadtxt(_dir/"supports.txt")



#%% main 
if __name__ == '__main__':
    model = Model(node_path, conectivity_path, element_id_path, members_prop_path,
                  members_name_path, mesh_cells_path, surfaces_path,surface_materials,nodal_loads_path,surface_loads_path)
    
    model.modify_units_surface_material()
    model.set_supports(support.tolist())

    model1 = model
    model2 = copy.deepcopy(model1)
    model3 = copy.deepcopy(model1)
    model4 = copy.deepcopy(model1)

    models = [model1, model2,model3,model4]



    def update_model(model,proposed_mass, proposed_Et):
        model.surfaces[2][2] = 53.0
        model.surface_materials[0, 4] = 2e-20
        model.nodal_loads[0][4] = proposed_mass
        model.nodal_loads[1][4] = proposed_mass
        
        _, _ = model.create_model(verbose=False, Et=proposed_Et)
        freq = model.Modal_analysis(20)
        proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
        return proposed_freq_4


    mas_param = Parameter(name = "masa",initval=-4.5, mean=-4.6, std=0.5, distribution=np.random.normal)
    et_param = Parameter(name = "Modifier",initval= 1, mean=1.5, std=0.2, distribution=np.random.lognormal)

    proposals = ProposalParameters(parameters=[mas_param, et_param])

    mass_recorder = ParameterRecorder(parameter= mas_param, values=[])
    et_recorder = ParameterRecorder(parameter=et_param ,values=[])

    recorder_list = RecorderList(recorders=[mass_recorder, et_recorder])

    target_freq = TargedParameter(name="target_freq", target_value=8.74, function_to_update=update_model)

    model_updater = ModelUpdater(model=model1,
                                proposal_parameters= proposals, 
                                recorder_list= recorder_list,
                                target_parameter= target_freq,
                                n_iterations=100,
                                std_dev=0.2)
    
    recorder_list, target_freq = model_updater.meetropolis_hastings()
    
    # mas_value: float = mas_param.get_value()
    # et_value: float = et_param.get_value()

    # print(update_model(model1,float(round(mas_value, 2))
    #                    ,float(round(et_value, 2))))
    




    # chain_results = run_chains_parallel(models,num_chains=4, n_iterations=100)
    
    # for i, chain_result in enumerate(chain_results):
    #     print(f"Chain {i}")
    #     plot_pair_grid(chain_result)



    
    
