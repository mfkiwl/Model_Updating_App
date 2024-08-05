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
from _helpers_model_upd import mas_dist,metropolis_hastings,run_chains_parallel,run_model_single,plot_pair_grid

from Opensees_Engine import Model


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

    chain_results = run_chains_parallel(models,num_chains=4, n_iterations=100)
    
    for i, chain_result in enumerate(chain_results):
        print(f"Chain {i}")
        plot_pair_grid(chain_result)



    
    
