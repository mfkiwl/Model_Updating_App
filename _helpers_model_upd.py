import numpy as np 
import concurrent
import pandas  as pd 
import seaborn as sns
from classes import Parameter, ProposalParameters, RecorderList, TargedParameter
from Opensees_Engine import Model
from typing import List, Tuple

import matplotlib.pyplot as plt
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor


def mas_dist(mu = -4.6, std =  0.5, n_samples = 1):
    samples = np.random.normal(mu, std, n_samples)
    return float(round(samples[0], 2))

def mas_dist2(mu=-4.6, std=0.5, n_samples=1):
    samples = np.random.normal(mu, std, n_samples)
    return float(round(samples[0], 10))

def Et_dist(mu=1.5, std=0.2, n_samples=1):
    log_mu = np.log(mu)  
    samples = np.random.lognormal(mean=log_mu, sigma=std, size=n_samples)
    return np.round(samples, 2)[0]


class ModelUpdater:
    def __init__(self,
                 model: Model, 
                 proposal_parameters: ProposalParameters,
                 target_parameter: TargedParameter,
                 recorder_list: RecorderList,
                 n_iterations: int,
                 std_dev: float):
        
        self.model = model
        self.proposal_parameters = proposal_parameters
        self.target_parameter = target_parameter
        self.n_iterations = n_iterations
        self.std_dev = std_dev
        self.recorder_list = recorder_list

    def meetropolis_hastings(self
                             )-> Tuple[RecorderList, TargedParameter]:

        current_values: List[float] = self.proposal_parameters.get_init_values()
        self.proposal_parameters.set_means(current_values)
        for i in range(self.n_iterations):
            proposed_values = self.proposal_parameters.get_values()
            # Update the model with the proposed values
            propsed_freq = self.target_parameter.function_to_update(
                self.model, *proposed_values)
            
            # Calculate the freq diff
            freq_diff = propsed_freq - self.target_parameter.target_value
            print(freq_diff)

            acceptance_ratio = np.exp(-np.abs(freq_diff) / self.std_dev)

            if acceptance_ratio > np.random.rand():
                current_values = proposed_values
                self.recorder_list.append_multiple(current_values)
                self.target_parameter.append_posterior(propsed_freq)
        return self.recorder_list, self.target_parameter

def metropolis_hastings(model, target_freq=8.74, init_mass=0, n_iterations=100, std_dev=0.1, chain_id=0):
    np.random.seed(chain_id)
    current_Et = 1.2
    current_mass = init_mass
    current_freq_4 = 0  # Initialize
    
    accepted_mass = []
    accepted_Et = []
    freq_dist = []
    freq_diff = []  # To store the difference between proposed_freq_4 and target_freq
    
    for i in range(n_iterations):
        proposed_mass = mas_dist(mu=current_mass, std=std_dev, n_samples=1)
        proposed_Et = Et_dist(mu=current_Et, std=0.2 ,n_samples=1)

        proposed_freq_4 = update_model(model, proposed_mass, proposed_Et)
        freq_difference = proposed_freq_4 - target_freq
        print(freq_difference)
        freq_diff.append(freq_difference)
        acceptance_ratio = np.exp(-np.abs(freq_difference) / 0.1)
        
        if acceptance_ratio > np.random.rand():
            current_mass = proposed_mass
            current_Et = proposed_Et
            current_freq_4 = proposed_freq_4
            accepted_mass.append(current_mass)
            accepted_Et.append(current_Et)
            freq_dist.append(proposed_freq_4)
            
    return accepted_mass, freq_dist, accepted_Et, freq_diff


def metropolis_hastings(model, target_freq=8.74, init_mass=0, n_iterations=100, std_dev=0.1, chain_id=0):
    np.random.seed(chain_id)
    current_Et = 1.2
    current_mass = init_mass
    current_freq_4 = 0  # Initialize
    
    accepted_mass = []
    accepted_Et = []
    freq_dist = []
    freq_diff = []  # To store the difference between proposed_freq_4 and target_freq
    
    for i in range(n_iterations):
        proposed_mass = mas_dist(mu=current_mass, std=std_dev, n_samples=1)
        proposed_Et = Et_dist(mu=current_Et, std=0.2 ,n_samples=1)

        proposed_freq_4 = update_model(model, proposed_mass, proposed_Et)
        freq_difference = proposed_freq_4 - target_freq
        freq_diff.append(freq_difference)
        acceptance_ratio = np.exp(-np.abs(freq_difference) / 0.1)
        
        if acceptance_ratio > np.random.rand():
            current_mass = proposed_mass
            current_Et = proposed_Et
            current_freq_4 = proposed_freq_4
            accepted_mass.append(current_mass)
            accepted_Et.append(current_Et)
            freq_dist.append(proposed_freq_4)
            
    return accepted_mass, freq_dist, accepted_Et, freq_diff



def metropolis_hastings_iomac(model, target_freq=5.445, init_mass_variation=0.0, n_iterations=100, std_dev=0.05, chain_id=0):
    np.random.seed(chain_id)
    current_mass_variation = init_mass_variation
    
    accepted_mass_variations = []
    freq_dist = []
    freq_diff = []  # To store differences between proposed frequencies and target frequency
    
    for i in range(n_iterations):
        proposed_mass_variation = mas_dist2(mu=current_mass_variation, std=std_dev, n_samples=1)
        
        # Apply the proposed mass variation to each of the first 5 nodal loads
        for load_index in range(5):  # Assuming the nodal loads to be adjusted are the first 5
            model.nodal_loads[load_index][4] = str(float(model.nodal_loads[load_index][4]) + proposed_mass_variation)
        
        _, _ = model.create_model(verbose=False)
        freq = model.Modal_analysis(20)
        proposed_freq_0 = freq[0]**0.5 / (2 * np.pi)
        
        # Calculate the frequency difference from the target
        freq_difference = proposed_freq_0 - target_freq
        freq_diff.append(freq_difference)
        
        # Calculate acceptance probability
        acceptance_ratio = np.exp(-np.abs(freq_difference) / 0.01)
        
        if acceptance_ratio > np.random.rand():
            current_mass_variation = proposed_mass_variation
            accepted_mass_variations.append(current_mass_variation)
            freq_dist.append(proposed_freq_0)
    
    return accepted_mass_variations, freq_dist, freq_diff
    

def update_model(model,proposed_mass, proposed_Et):
    model.surfaces[2][2] = 53.0
    model.surface_materials[0, 4] = 2e-20
    model.nodal_loads[0][4] = proposed_mass
    model.nodal_loads[1][4] = proposed_mass
    
    _, _ = model.create_model(verbose=False, Et=proposed_Et)
    freq = model.Modal_analysis(20)
    proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
    return proposed_freq_4
    

def run_model_single(model,mass = '-4'):
    proposed_mass = mas_dist()
    model.surface_materials[0,4] = 2e-20
    model.nodal_loads[0][4] = proposed_mass
    model.nodal_loads[1][4] = proposed_mass
    _, _ = model.create_model(verbose=False)
    freq = model.Modal_analysis(20)
    proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
    print(proposed_freq_4,proposed_mass)
    

def _run_chain_wrapper(args):
    i, model, init_mass, iterations = args
    return metropolis_hastings(model, target_freq=8.74, init_mass=init_mass, n_iterations=iterations, std_dev=0.2, chain_id=0)

def run_chains_parallel(models, num_chains=2, n_iterations=5):
    if len(models) != num_chains:
        raise ValueError("Number of model instances must match the number of chains.")
        
    init_masses = [mas_dist() for _ in range(num_chains)]
    chain_args = [(i, models[i], init_masses[i], n_iterations) for i in range(num_chains)]
    with Pool(num_chains) as pool:
        results = pool.map(_run_chain_wrapper, chain_args)    
    return results
    
def plot_pair_grid(chain_result):
    # Extract the results from a single chain
    accepted_mass, freq_dist, accepted_Et = chain_result[:3]
    
    # Create a DataFrame
    df = pd.DataFrame({
        'accepted_mass': accepted_mass,
        'freq_dist': freq_dist,
        'accepted_Et': accepted_Et
    })
    
    # Create a pair grid
    g = sns.PairGrid(df)
    g.map_diag(sns.histplot)
    g.map_upper(sns.scatterplot)
    g.map_lower(sns.kdeplot)
    plt.show()