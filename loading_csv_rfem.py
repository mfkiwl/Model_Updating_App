import pandas as pd
import sys

def expand_ranges(range_str):
    ranges = range_str.split(',')
    expanded = []
    for r in ranges:
        if '-' in r:
            start, end = map(int, r.split('-'))
            expanded.extend(list(range(start, end+1)))
        else:
            expanded.append(int(r))
    return expanded  # return the list directly

def run_parsers(_dir):
    
    # sys.path.append(_dir)

    # Read the csv file, using semicolon as separator and skipping the first row
    nodes_df = pd.read_csv(_dir /'FE Mesh Nodes.csv', delimiter=';', skiprows=1)
    # Select the necessary columns
    nodes_df = nodes_df[['No.', 'X [mm]', 'Y [mm]', 'Z [mm]']]
    # Write the modified dataframe to a new txt file
    nodes_df.to_csv(_dir / 'Nodes.txt', sep='\t', index=False, header=False)
    
    # %% 
    # Read the csv file, using semicolon as separator, skipping the first row, and specifying 'ISO-8859-1' encoding
    cross_sections_df = pd.read_csv(_dir/'1.13 Cross-Sections .csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
    
    # Select the necessary columns
    cross_sections_df = cross_sections_df[['No.','Torsion J', 'Bending Iy', 'Bending Iz', 'Axial A']]
    
    # Write the modified dataframe to a new txt file
    cross_sections_df.to_csv(_dir /'Member.txt', sep='\t', index=False, header=False)
    
    # %% Nmaes 
    # Read the csv file, using semicolon as separator, skipping the first row, and specifying 'ISO-8859-1' encoding
    cross_sections_df = pd.read_csv(_dir /'1.13 Cross-Sections .csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
    
    # Select the 'Description [mm]' column, which corresponds to 'Cross-Section'
    names_df = cross_sections_df[['Description [mm]']]
    
    # Write the 'Names' dataframe to a new txt file
    names_df.to_csv(_dir /'Names.txt', sep='\t', index=False, header=False)
    
    #%%         Fe mesh cells 
    
    # Read the csv file, using semicolon as separator and skipping the first row
    mesh_cells_df = pd.read_csv(_dir /'FE Mesh Cells .csv', delimiter=';', skiprows=1)
    
    # Select the necessary columns
    mesh_cells_df = mesh_cells_df[['No.', 'No..1', '1', '2', '3', '4']]
    
    # Write the modified dataframe to a new txt file
    mesh_cells_df.to_csv(_dir /'Mesh_Cells.txt', sep='\t', index=False, header=False)
    #%%             Surfaces 
    
    # Read the csv file, using semicolon as separator and skipping the first row
    surfaces_df = pd.read_csv(_dir /'1.4 Surfaces.csv', delimiter=';', skiprows=1)
    
    # Select the necessary columns
    surfaces_df = surfaces_df[['No.', 'No..1', 'd [mm]','A [mm2]']]
    
    # Write the modified dataframe to a new txt file
    surfaces_df.to_csv(_dir /'Surface.txt', sep='\t', index=False, header=False)
    
    #%%            element id 
    # Read the csv file, using semicolon as separator, skipping the first row, and specifying the encoding
    # Read the csv file, using semicolon as separator, skipping the first row, and specifying the encoding
    members_df = pd.read_csv(_dir /'1.17 Members.csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
    
    # Select the necessary columns
    members_df = members_df[[members_df.columns[1], 'Start','beta [°]']]
    
    # Write the modified dataframe to a new txt file
    members_df.to_csv(_dir /'Elementid.txt', sep=',', index=False, header=False)

    # %% 
    
    # Read the csv file, using semicolon as separator, skipping the first row
    lines_df = pd.read_csv(_dir /'1.2 Lines.csv', delimiter=';', skiprows=1, dtype=str)
    
    # We know that 'Nodes No.' is not a numerical field but a string identifier.
    # Replace whitespace characters around the comma if any, to ensure that the split happens correctly
    lines_df['Nodes No.'] = lines_df['Nodes No.'].str.replace(' , ', ',', regex=False)
    
    # Split 'Nodes No.' column on comma and expand into separate columns
    lines_df[['Start Node', 'End Node']] = lines_df['Nodes No.'].str.split(',', expand=True)
    
    # Select the necessary columns and rename them
    lines_df = lines_df[['No.', 'Start Node', 'End Node']]
    
    # Write the dataframe to a new txt file
    lines_df.to_csv(_dir /'Lines.txt', sep=',', index=False, header=False)
    
    
    
#%% load materials 
    # Read the csv file, using semicolon as separator, skipping the first row

    pd_materials = pd.read_csv(_dir /'1.3 Materials.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
    pd_materials  = pd_materials [['No.', 'E [kN/cm2]','G [kN/cm2]','ny [-]','gamma [kN/m3]']]
    pd_materials.to_csv(_dir /'plate_materials.txt', sep='\t', index=False, header=False)


#%% Load Nodes 
    # Read the csv file, using semicolon as separator, skipping the first row

    pd_point_loads = pd.read_csv(_dir /'LC1 - 3.1 Nodal Loads.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
    pd_point_loads  =pd_point_loads [['No.', 'On Nodes No.','PX', 'PY', 'PZ', 'MX','MY','MZ']]
    pd_point_loads.to_csv(_dir /'nodal_nodes.txt', sep='\t', index=False, header=False)


#%% Load surface loads  
    # Read the csv file, using semicolon as separator, skipping the first row
    pd_surface_load = pd.read_csv(_dir /'LC1 - 3.4 Surface Loads.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
    pd_surface_load   =pd_surface_load [['No.','On Surfaces No.',pd_surface_load.columns[6]]]
    # pd_surface_load   =pd_surface_load [['No.','On Surfaces No.','p [kN/m2]']]
    pd_surface_load['On Surfaces No.'] = pd_surface_load['On Surfaces No.'].apply(expand_ranges)
    pd_surface_load.to_csv(_dir /'surface_loads.txt', sep='\t', index=False, header=False)

# %%  Support 

    # pf_support = pd.read_csv(_dir /'1.7 Nodal Supports.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
    # pd_support = pf_support[pd_surface_load.columns[1]]
    # pd_support.to_csv(_dir /'supports.txt', sep=',', index=False, header=False)
    f_support = pd.read_csv(_dir / '1.7 Nodal Supports.csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
    
    # Select the 'On Nodes No.' column and split it into a list of integers
    support_nodes = f_support['On Nodes No.'].str.split(',', expand=True)
    
    # Save this DataFrame to a new text file
    support_nodes.to_csv(_dir / 'supports.txt', sep='\t', index=False, header=False)
