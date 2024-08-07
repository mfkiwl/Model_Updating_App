import numpy as np 
import matplotlib.pyplot as plt 
import opsvis as opsv
import warnings
import copy

from typing import List, Tuple
from pathlib import Path
from loading_csv_rfem import run_parsers
from _helpers_model_upd import ModelUpdater,run_chains_parallel

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

def update_model(model,proposed_mass, proposed_Et):
    model.surfaces[2][2] = 53.0
    model.surface_materials[0, 4] = 2e-20
    model.nodal_loads[0][4] = proposed_mass
    model.nodal_loads[1][4] = proposed_mass
    
    _, _ = model.create_model(verbose=False, Et=proposed_Et)
    freq = model.Modal_analysis(20)
    proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
    return proposed_freq_4

def model_updater_factory(args: Tuple[Parameter, Parameter, Model, float, int]) -> Tuple[RecorderList, TargedParameter]:
    mas_param, et_param, model, std_dev, n_iterations = args

    proposals = ProposalParameters(parameters=[mas_param, et_param])

    mass_recorder = ParameterRecorder(parameter= mas_param, values=[])

    et_recorder = ParameterRecorder(parameter=et_param ,values=[])

    recorder_list = RecorderList(recorders=[mass_recorder, et_recorder])

    target_freq = TargedParameter(name="target_freq", target_value=8.74, function_to_update=update_model)

    model_updater = ModelUpdater(model=model,
                                proposal_parameters= proposals, 
                                recorder_list= recorder_list,
                                target_parameter= target_freq,
                                n_iterations=n_iterations,
                                std_dev= std_dev)
    
    return model_updater.meetropolis_hastings()

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

    stds = [0.01, 0.1, 0.2, 0.5]
    masses = [-4.5, -4.6, -4.7, -4.1]
    Ets = [0.5, 1, 1.5, 2]

    args = []
    for model, mass, std, Et in zip(models, masses, stds, Ets):
        args.append((
            Parameter(name="masa", initval=mass, mean=-4.6, std=std, distribution=np.random.normal),
            Parameter(name="Modifier", initval=Et, mean=1.5, std=std, distribution=np.random.lognormal),
            model,
            std,
            100
        ))

    # Run the model updater factories in parallel
    results = run_chains_parallel(model_updater_factory, args, num_chains=len(args))


        
    

    
