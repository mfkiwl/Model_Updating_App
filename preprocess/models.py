from typing import List, Dict
from pydantic import BaseModel

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

class AllMembers(BaseModel):
    
    members: List[MemberElement]

    def append_member(self, new_member: MemberElement):
        self.members.append(new_member)

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

class AllQuadsMembers(BaseModel):
    quads_members: List[QuadMember]

    def append_quadd_member(self, new_quad: QuadMember):
        self.quads_members.append(new_quad)

