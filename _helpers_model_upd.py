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

            acceptance_ratio = np.exp(-np.abs(freq_diff) / self.std_dev)

            if acceptance_ratio > np.random.rand():
                current_values = proposed_values
                self.recorder_list.append_multiple(current_values)
                self.target_parameter.append_posterior(propsed_freq)
        return self.recorder_list, self.target_parameter
    
def run_chains_parallel(function:callable,
                        args:List[Tuple],
                        num_chains)-> List:
    if len(args) != num_chains:
        raise ValueError("Number of model instances must match the number of chains.")
    with Pool(num_chains) as pool:
        results = pool.map(function, args)    
    return results

def run_model_single(model,mass = '-4'):
    proposed_mass = mas_dist()
    model.surface_materials[0,4] = 2e-20
    model.nodal_loads[0][4] = proposed_mass
    model.nodal_loads[1][4] = proposed_mass
    _, _ = model.create_model(verbose=False)
    freq = model.Modal_analysis(20)
    proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
    print(proposed_freq_4,proposed_mass)
    
    
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