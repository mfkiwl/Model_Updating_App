#%% Beam elements statment
from sqlalchemy import select
from sqlalchemy.orm import aliased
from pydantic import BaseModel
from typing import List, Dict

from create_database import create_session, Nodes, ShellSections, SurfaceSections, Materials


session = create_session()




query = '''SELECT
            shell_section_table.id,
            shell_section_table.surface_section_id,
            node_i.x AS node_i_x,
            node_i.y AS node_i_y,
            node_i.z AS node_i_z,

            node_j.x AS node_j_x,
            node_j.y AS node_j_y,
            node_j.z AS node_j_z,

            node_k.x AS node_k_x,
            node_k.y AS node_k_y,
            node_k.z AS node_k_z,

            node_l.x AS node_l_x,
            node_l.y AS node_l_y,
            node_l.z AS node_l_z,

            surface_section_table.material_id AS  material_id,
            surface_section_table.d AS thickness,
            surface_section_table.A AS area
        
        FROM
            shell_section_table

        JOIN
            nodes AS node_i ON shell_section_table.node_i = node_i.id
        JOIN
            nodes AS node_j ON shell_section_table.node_j = node_j.id
        JOIN
            nodes AS node_k ON shell_section_table.node_k = node_k.id
        JOIN
            nodes AS node_l ON shell_section_table.node_l = node_l.id
        JOIN
            surface_section_table 
            ON shell_section_table.surface_section_id = surface_section_table.surface_section_id
'''

node_i = aliased(Nodes, name='node_i')
node_j = aliased(Nodes, name='node_j')
node_k = aliased(Nodes, name='node_k')
node_l = aliased(Nodes, name='node_l')

stmt = (select(
    ShellSections.id,
    ShellSections.surface_section_id,

    node_i.id.label('node_i_id'),
    node_i.x.label('node_i_x'),
    node_i.y.label('node_i_y'),
    node_i.z.label('node_i_z'),

    node_j.id.label('node_j_id'),
    node_j.x.label('node_j_x'),
    node_j.y.label('node_j_y'),
    node_j.z.label('node_j_z'),

    node_k.id.label('node_k_id'),
    node_k.x.label('node_k_x'),
    node_k.y.label('node_k_y'),
    node_k.z.label('node_k_z'),

    node_k.id.label('node_l_id'),
    node_l.x.label('node_l_x'),
    node_l.y.label('node_l_y'),
    node_l.z.label('node_l_z'),

    SurfaceSections.material_id,
    SurfaceSections.d,
    SurfaceSections.A
)
.join(node_i, node_i.id == ShellSections.node_i)
.join(node_j, node_j.id == ShellSections.node_j)
.join(node_k, node_k.id == ShellSections.node_k)
.join(node_l, node_l.id == ShellSections.node_l)
.join(SurfaceSections, ShellSections.surface_section_id == SurfaceSections.surface_section_id)
)

result = session.execute(stmt).fetchall()


class Node(BaseModel):
    node_id: int 
    x: float
    y: float
    z: float


class Quad(BaseModel):
    quad_id:int
    surface_section_id:int
    node_i:Node
    node_j:Node
    node_k:Node
    node_l:Node

class QuadMember(BaseModel):
    ref_quad: Quad
    surface_section_id:int
    material_id:int
    thickness: float
    area: float


list_of_nodes = []
list_of_q_members = []
for row in result:
    node_i = Node(node_id= row.node_i_id,x = row.node_i_x,y = row.node_i_y, z =row.node_i_z)
    node_j = Node(node_id=row.node_j_id,x=row.node_j_x,y = row.node_j_y,z = row.node_j_z)
    node_k = Node(node_id=row.node_k_id,x=row.node_k_x,y = row.node_k_y,z = row.node_k_z)
    node_l = Node(node_id=row.node_l_id,x=row.node_l_x,y = row.node_l_y,z = row.node_l_z)

    quad = Quad(quad_id= row.id, surface_section_id= row.surface_section_id,
                node_i= node_i, node_j= node_j, node_k = node_k, node_l = node_l)
    
    quad_member = QuadMember(ref_quad=quad, surface_section_id= row.surface_section_id,
                            material_id= row.material_id, thickness= row.d,
                            area= row.A)
    list_of_q_members.append(quad_member)

print(list_of_q_members)
