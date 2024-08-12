#%% Beam elements statment
from sqlalchemy import select
from sqlalchemy.orm import aliased
from pydantic import BaseModel
from typing import List, Dict, Tuple

from create_database import Nodes,Lines,Members,CrossSections,create_session, ShellSections, SurfaceSections
from models import AllLines, AllMembers , Node, AllNodes , LineElement, MemberElement, Quad, QuadMember, AllQuadsMembers

def get_beams_topology(session:any):
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

    return session.execute(stmt).fetchall()


def get_quads_topology(session:any):
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

    return session.execute(stmt).fetchall()


def beams_facotory(all_nodes: AllNodes, all_lines: AllLines, all_members: AllMembers)->Tuple[AllNodes,AllLines,AllMembers]:
   
    for row in beam_result:
        node_i = Node(node_id=row.node_i, x=row.node_i_x, y=row.node_i_y, z=row.nodes_i_z)
        all_nodes.add_node(new_node = node_i)

        node_j = Node(node_id=row.node_j, x=row.node_j_x, y=row.node_j_y, z=row.nodes_j_z)
        all_nodes.add_node(new_node = node_j)

        line_element = LineElement(line_id=row.line_id, node_i=node_i, node_j=node_j)
        all_lines.append_lines(line_element)

        member_element = MemberElement(ref_line = line_element, cross_section_id= row.cross_section_id,
                                    J= row.J, Iy=row.Iy, Iz= row.Iz, A=row.A)
        all_members.append_member(new_member=member_element)
    
    return all_nodes, all_lines, all_members

def quads_factory(all_nodes: AllNodes, quad_result : any) -> Tuple[AllNodes,AllQuadsMembers]:
   
    all_quads = AllQuadsMembers(quads_members = [])

    for row in quad_result:
        node_i = Node(node_id= row.node_i_id,x = row.node_i_x,y = row.node_i_y, z =row.node_i_z)
        all_nodes.add_node(new_node = node_i)

        node_j = Node(node_id=row.node_j_id,x=row.node_j_x,y = row.node_j_y,z = row.node_j_z)
        all_nodes.add_node(new_node = node_j)

        node_k = Node(node_id=row.node_k_id,x=row.node_k_x,y = row.node_k_y,z = row.node_k_z)
        all_nodes.add_node(new_node = node_k)

        node_l = Node(node_id=row.node_l_id,x=row.node_l_x,y = row.node_l_y,z = row.node_l_z)
        all_nodes.add_node(new_node = node_l)

        quad = Quad(quad_id= row.id, surface_section_id= row.surface_section_id,
                    node_i= node_i, node_j= node_j, node_k = node_k, node_l = node_l)
        
        quad_member = QuadMember(ref_quad=quad, surface_section_id= row.surface_section_id,
                                material_id= row.material_id, thickness= row.d,
                                area= row.A)

        all_quads.append_quadd_member(quad_member)

    return all_nodes, all_quads


if __name__ == "__main__":
    session = create_session()
    beam_result = get_beams_topology(session=session)
    quad_result = get_quads_topology(session=session)

    all_members = AllMembers(members = [])
    all_nodes = AllNodes(nodes = {})
    line_elements = AllLines(lines = [])

    all_nodes, line_elements, all_members = beams_facotory(all_nodes= all_nodes, 
                                                           all_lines= line_elements,
                                                           all_members= all_members)
    
    all_nodes, all_quads = quads_factory(all_nodes= all_nodes, quad_result=quad_result)



    print(line_elements)
    print(all_nodes)
    print(all_members)
    print(all_quads)