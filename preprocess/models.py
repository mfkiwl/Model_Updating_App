#%% Beam elements statment
from sqlalchemy import select
from sqlalchemy.orm import aliased
from pydantic import BaseModel
from typing import List, Dict

from create_database import Nodes,Lines,Members,CrossSections,create_session

session = create_session()


node_i = aliased(Nodes, name='node_i')
node_j = aliased(Nodes, name='node_j')


stmt = (
    select(
        Lines.line_id,
        Lines.node_i,
        node_i.x.label('node_i_x'),
        node_i.y.label('node_i_y'),
        node_i.z.label('nodes_i_z'),
        Lines.node_j,
        node_j.x.label('node_j_x'),
        node_j.y.label('node_j_y'),
        node_j.z.label('nodes_j_z'),
        Members.cross_section_id,
        CrossSections.J,
        CrossSections.Iz,
        CrossSections.Iy,
        CrossSections.A
    )
    .join(node_i, Lines.node_i == node_i.id)
    .join(node_j, Lines.node_j == node_j.id)
    .join(Members,Lines.line_id == Members.line_id)
    .join(CrossSections, Members.cross_section_id == CrossSections.cross_section_id)
)

result = session.execute(stmt).fetchall()


class Node(BaseModel):
    node_id: int 
    x: float
    y: float
    z: float
    
class LineElement(BaseModel):
    line_id: int
    node_i: Node
    node_j: Node

class AllNodes(BaseModel):
    nodes: Dict[int,Node]

    def add_node(self, new_node: Node):
        if  new_node.node_id not in self.nodes:
            self.nodes[new_node.node_id] = new_node
        
class AllLines(BaseModel):
    lines: List[LineElement]

    def append_lines(self,new_line: LineElement):
        self.lines.append(new_line)

class MemberElement(BaseModel):
    ref_line: LineElement
    cross_section_id: int
    J: float 
    Iy: float 
    Iz: float
    A: float

class Members(BaseModel):
    
    members: List[MemberElement]

    def append_member(self, new_member: MemberElement):
        self.members.append(new_member)


all_members = Members(members = [])
all_nodes = AllNodes(nodes = {})
line_elements = AllLines(lines = [])

for row in result:
    node_i = Node(node_id=row.node_i, x=row.node_i_x, y=row.node_i_y, z=row.nodes_i_z)
    all_nodes.add_node(new_node = node_i)

    node_j = Node(node_id=row.node_j, x=row.node_j_x, y=row.node_j_y, z=row.nodes_j_z)
    all_nodes.add_node(new_node = node_j)

    line_element = LineElement(line_id=row.line_id, node_i=node_i, node_j=node_j)
    line_elements.append_lines(line_element)

    member_element = MemberElement(ref_line = line_element, cross_section_id= row.cross_section_id,
                                   J= row.J, Iy=row.Iy, Iz= row.Iz, A=row.A)
    all_members.append_member(new_member=member_element)

print(line_elements)
print(all_nodes)
print(all_members)