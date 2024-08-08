import pandas as pd

from sqlalchemy import create_engine
from pathlib import Path

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

_dir = Path('../Footbridge')


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


#%% Nodes
# Read the csv file, using semicolon as separator and skipping the first row
nodes_df = pd.read_csv(_dir /'FE Mesh Nodes.csv', delimiter=';', skiprows=1)
# Select the necessary columns
nodes_df = nodes_df[['No.', 'X [mm]', 'Y [mm]', 'Z [mm]']]
nodes_df.columns = ['id', 'x', 'y', 'z']

#%% Cross Sections
cross_sections_df = pd.read_csv(_dir/'1.13 Cross-Sections .csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
# Select the necessary columns
cross_sections_df = cross_sections_df[['No.','Torsion J', 'Bending Iy', 'Bending Iz', 'Axial A']]
cross_sections_df.columns = ['id', 'J', 'Iy', 'Iz', 'A']

#%% Names
cross_sections_df = pd.read_csv(_dir /'1.13 Cross-Sections .csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
# Select the 'Description [mm]' column, which corresponds to 'Cross-Section'
names_df = cross_sections_df[['No.','Description [mm]']]
names_df.columns = ['id', 'name']

#%% Shells
mesh_cells_df = pd.read_csv(_dir /'FE Mesh Cells .csv', delimiter=';', skiprows=1)

# Select the necessary columns
mesh_cells_df = mesh_cells_df[['No.', 'No..1', '1', '2', '3', '4']]
mesh_cells_df.columns = ['id', 'surface_section_id', 'node_i', 'node_j', 'node_k', 'node_l']

# Shell section 
    # Read the csv file, using semicolon as separator and skipping the first row
surfaces_df = pd.read_csv(_dir /'1.4 Surfaces.csv', delimiter=';', skiprows=1)

# Select the necessary columns
surfaces_df = surfaces_df[['No.', 'No..1', 'd [mm]','A [mm2]']]
surfaces_df.columns = ['id', 'surface_section_id', 'd', 'A']

#%% Element ids
members_df = pd.read_csv(_dir /'1.17 Members.csv', delimiter=';', skiprows=1, encoding='ISO-8859-1')
# Select the necessary columns
members_df = members_df[[members_df.columns[1], 'Start','beta [°]']]
members_df.columns = ['line_id', 'sec_id', 'beta']

#%% Lines
lines_df = pd.read_csv(_dir /'1.2 Lines.csv', delimiter=';', skiprows=1, dtype=str)

# We know that 'Nodes No.' is not a numerical field but a string identifier.
# Replace whitespace characters around the comma if any, to ensure that the split happens correctly
lines_df['Nodes No.'] = lines_df['Nodes No.'].str.replace(' , ', ',', regex=False)

# Split 'Nodes No.' column on comma and expand into separate columns
lines_df[['Start Node', 'End Node']] = lines_df['Nodes No.'].str.split(',', expand=True)

# Select the necessary columns and rename them
lines_df = lines_df[['No.', 'Start Node', 'End Node']]
lines_df.columns = ['line_id', 'node_i', 'node_j']

#%% Materials
pd_materials = pd.read_csv(_dir /'1.3 Materials.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
pd_materials  = pd_materials [['No.', 'E [kN/cm2]','G [kN/cm2]','ny [-]','gamma [kN/m3]']]
pd_materials.columns = ['material_id', 'E', 'G', 'ny', 'gamma']
#%% point loads 
pd_point_loads = pd.read_csv(_dir /'LC1 - 3.1 Nodal Loads.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
pd_point_loads  =pd_point_loads [['No.', 'On Nodes No.','PX', 'PY', 'PZ', 'MX','MY','MZ']]
pd_point_loads.columns = ['id', 'node_id', 'PX', 'PY', 'PZ', 'MX', 'MY', 'MZ']

#%% surface loads
pd_surface_load = pd.read_csv(_dir /'LC1 - 3.4 Surface Loads.csv',delimiter = ';',skiprows = 1,encoding='ISO-8859-1')
pd_surface_load   =pd_surface_load [['No.','On Surfaces No.',pd_surface_load.columns[6]]]
# pd_surface_load   =pd_surface_load [['No.','On Surfaces No.','p [kN/m2]']]
pd_surface_load['On Surfaces No.'] = pd_surface_load['On Surfaces No.'].apply(expand_ranges)
pd_surface_load.columns = ['id', 'surface_section_id', 'p']
#%% ORM Model

Base = declarative_base()

class Nodes(Base):
    __tablename__ = 'nodes'
    id =Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

class CrossSections(Base):
    __tablename__ = 'cross_sections'
    cross_section_id = Column(Integer, primary_key=True)
    J = Column(Float)
    Iy = Column(Float)
    Iz = Column(Float)
    A = Column(Float)

class CrossSectionsNames(Base):
    __tablename__ = 'cross_sections_names'
    cross_section_id = Column(Integer, primary_key=True)
    name = Column(String)

class ShellSections(Base):
    __tablename__ = 'shell_section_table'
    id = Column(Integer, primary_key=True)
    surface_section_id = Column(Integer)
    node_i= Column(Integer)
    node_j= Column(Integer)
    node_k= Column(Integer)
    node_l= Column(Integer)

class SurfaceSections(Base):
    ''' d: thickness, A: area '''
    __tablename__ = 'surface_section_table'
    surface_section_id = Column(Integer, primary_key=True)
    material_id = Column(Integer)
    d = Column(Float)
    A = Column(Float)

class Members(Base):
    ''' sec_id: section id, beta: angle '''
    __tablename__ = 'members'
    line_id = Column(Integer, primary_key=True)
    cross_section_id = Column(Integer)
    beta = Column(Float)

class Lines(Base):
    ''' node_i, node_j: start and end nodes '''
    __tablename__ = 'lines'
    line_id = Column(Integer, primary_key=True)
    node_i = Column(Integer)
    node_j = Column(Integer)

class Materials(Base):
    ''' E: Young's modulus, G: shear modulus, ny: Poisson's ratio, gamma: weight '''
    __tablename__ = 'materials'
    material_id = Column(Integer, primary_key=True)
    E = Column(Float)
    G = Column(Float)
    ny = Column(Float)
    gamma = Column(Float)

class PointLoads(Base):
    ''' PX, PY, PZ: forces, MX, MY, MZ: moments, Units: kN,kNm '''
    __tablename__ = 'point_loads'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer)
    PX = Column(Float)
    PY = Column(Float)
    PZ = Column(Float)
    MX = Column(Float)
    MY = Column(Float)
    MZ = Column(Float)

class SurfaceLoads(Base):
    ''' p: pressure kn/m2'''
    __tablename__ = 'surface_loads'
    id = Column(Integer, primary_key=True)
    surface_section_id = Column(Integer)
    p = Column(Float)



# Create local db
engine = create_engine("sqlite:///model.db", echo=True)
# Create table
Base.metadata.create_all(engine)
# Create session
Session = sessionmaker(bind=engine)
session = Session()

#%% Insert data into the database
nodes_df.to_sql('nodes', con=engine, if_exists='replace', index=False)
cross_sections_df.to_sql('cross_sections', con=engine, if_exists='replace', index=False)
names_df.to_sql('cross_sections_names', con=engine, if_exists='replace', index=False)
mesh_cells_df.to_sql('shell_section_table', con=engine, if_exists='replace', index=False)
surfaces_df.to_sql('surface_section_table', con=engine, if_exists='replace', index=False)
members_df.to_sql('members', con=engine, if_exists='replace', index=False)
lines_df.to_sql('lines', con=engine, if_exists='replace', index=False)
pd_materials.to_sql('materials', con=engine, if_exists='replace', index=False)
pd_point_loads.to_sql('point_loads', con=engine, if_exists='replace', index=False)
pd_surface_load.to_sql('surface_loads', con=engine, if_exists='replace', index=False)
# Close the session
session.close()

