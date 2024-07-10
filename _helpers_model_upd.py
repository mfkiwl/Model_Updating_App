import numpy as np 
import concurrent
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
import pandas  as pd 
import seaborn as sns
import matplotlib.pyplot as plt


def mas_dist(mu = -4.6, std =  0.5, n_samples = 1):
    samples = np.random.normal(mu, std, n_samples)
    return float(round(samples[0], 2))

def mas_dist2(mu=-4.6, std=0.5, n_samples=1):
    samples = np.random.normal(mu, std, n_samples)
    return float(round(samples[0], 10))

def Et_dist(mu=1.5, std=0.2, n_samples=1):
    log_mu = np.log(mu)  # Calcular el logaritmo natural de la media
    samples = np.random.lognormal(mean=log_mu, sigma=std, size=n_samples)
    return np.round(samples, 2)[0]


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
        model.surfaces[2][2] = 53.0
        model.surface_materials[0, 4] = 2e-20
        model.nodal_loads[0][4] = proposed_mass
        model.nodal_loads[1][4] = proposed_mass
        
        _, _ = model.create_model(verbose=False, Et=proposed_Et)
        freq = model.Modal_analysis(20)
        proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
        
        # Calculate the difference between proposed frequency and target frequency
        freq_difference = proposed_freq_4 - target_freq
        freq_diff.append(freq_difference)
        
        # Adjust the acceptance criterion to optimize the difference
        acceptance_ratio = np.exp(-np.abs(freq_difference) / 0.1)  # Here, 0.1 is the desired std_dev
        
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




def run_model_single(model,mass = '-4'):
        proposed_mass = mas_dist()
        model.surface_materials[0,4] = 2e-20
        model.nodal_loads[0][4] = proposed_mass
        model.nodal_loads[1][4] = proposed_mass
        _, _ = model.create_model(verbose=False)
        freq = model.Modal_analysis(20)
        proposed_freq_4 = freq[4]**0.5 / (2 * np.pi)
        print(proposed_freq_4,proposed_mass)
        

# def _run_chain_wrapper(args):
#     i, model, init_mass, iterations = args
#     return metropolis_hastings_iomac(model, init_mass=init_mass, n_iterations=iterations, chain_id=i)
def _run_chain_wrapper(args):
    i, model, init_mass, iterations = args
    return metropolis_hastings(model, target_freq=8.74, init_mass=init_mass, n_iterations=iterations, std_dev=0.1, chain_id=0)

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