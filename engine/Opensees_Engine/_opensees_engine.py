import ast
import numpy as np
import opsvis as opsv
import openseespy.opensees as ops

from scipy import optimize
from scipy.stats import norm
from pathlib import Path


class Model():
    def __init__(self, node_path, conectivity_path, element_id_path,
                 members_prop_path, members_name_path, mesh_cells_path,
                 surfaces_path,surface_materials,nodal_loads_path
                 ,surface_load_path) -> None:
        
        self.nodes = np.genfromtxt(node_path, invalid_raise=False)
        self.conect = np.loadtxt(conectivity_path, delimiter=',')
        self.idele = np.genfromtxt(element_id_path, delimiter=',')
        self.members_prop = np.genfromtxt(members_prop_path, invalid_raise=False)
        self.names = np.genfromtxt(members_name_path, dtype='str', delimiter = '\t')
        self.mesh_cells = np.genfromtxt(mesh_cells_path, invalid_raise=False)
        self.surfaces = np.genfromtxt(surfaces_path, invalid_raise=False)
        self.nodes_w_support = None
        self.default_restrains = None
        self.global_surface_tag = 100000.0
        self.g = 10000 #9800
        self.surface_materials = np.genfromtxt(surface_materials, invalid_raise=False)
        self.nodal_loads = np.genfromtxt(nodal_loads_path, dtype='str', delimiter = '\t')
        self.nodes_with_mass = None
        self.surface_loads = np.genfromtxt(surface_load_path, dtype='str', delimiter = '\t')
        self.hinges_tag = 100000
        self.tag_material = 100000
    
    @property
    def steel_properties(self):
        G = 0.25*10**3
        gama = 7.85*10**-5
        E = 200*10**3 
        return G,gama,E
    
    def concrete_properties(self):
        G_c = 11125 # N/mm2
        gama_conc = 2.5*10**-5
        E_conc = 26700  # N/mm2
        
        return G_c, gama_conc, E_conc
      
    def hinge_nodes_by_member(self,_member_id,loc):
    
        # get index of the member id in idele
        idele_location = np.where(_member_id == self.conect[:,0])[0][0]
        # get note tags
        _,node_i_tag,node_j_tag = self.conect[idele_location,:]
        # get node id index in nodes
        node_i_index =  np.where(node_i_tag == self.nodes[:,0])[0][0]
        node_j_index =  np.where(node_j_tag == self.nodes[:,0])[0][0]
        # create node tag 
        hinge_tag_i = self.hinges_tag+node_i_tag
        hinge_tag_j = self.hinges_tag+node_j_tag
        if loc == 'start':

            self.nodes= np.vstack((self.nodes,self.nodes[node_i_index]))
            self.nodes[-1,0] = hinge_tag_i
            self.conect[idele_location,1] =  hinge_tag_i  
            self.hinges_tag = self.hinges_tag +50 
            return [node_i_tag,hinge_tag_i]  
        else:
            self.nodes= np.vstack((self.nodes,self.nodes[node_j_index]))
            self.nodes[-1,0] = hinge_tag_j
            self.conect[idele_location,2] =  hinge_tag_j 
            self.hinges_tag = self.hinges_tag +50 
            return [node_j_tag,hinge_tag_j]  
        
    def semirigid_support(self,support_hinges,E_sup_rot = 550000000):
        for master,slave in support_hinges:
            ops.equalDOF(master,slave,*[1,2,3,5,6])
            mattag = self.tag_material +10
            ops.uniaxialMaterial('Elastic',int(mattag),E_sup_rot)
            link_tag = self.hinges_tag + 35
            ops.element('zeroLength', link_tag, master,slave,'-mat', int(mattag), '-dir',4) 
            
            self.hinges_tag = self.hinges_tag +50 
            self.tag_material  = self.tag_material +100
            
    def set_hinges(self,hinges_lists):
        for master,slave in hinges_lists:
            ops.equalDOF(master,slave,*[1,2,3,6])

    def get_index_cross_section_prop(self, _member_id):
        # idele tells me what cross section number the membe id has assinged
        idele_location = np.where(_member_id == self.idele[:,0])[0][0]
        _idele = self.idele[idele_location,1]
        if np.isnan(_idele):
            return _idele,0
        else: 
            rotation = self.idele[idele_location,2]
            # we het the cross section number now we look into cross section props
            # to get the index of the cross section number 
            cross_index = np.where(_idele == self.members_prop[:,0])[0][0]
            return cross_index , rotation
            
    def modify_units_surface_material(self):
        self.surface_materials[:,1] =  self.surface_materials[:,1]*10
        self.surface_materials[:,2] =  self.surface_materials[:,2]*10
        self.surface_materials[:,4] =  self.surface_materials[:,4]*0.000001

    def set_supports(self,nodes_w_support,default_restrains = [1,1,1,0,0,0]):
        self.nodes_w_support = nodes_w_support
        self.default_restrains = default_restrains
        
    def set_multiple_support(self,support_zipped_list):
        for support in support_zipped_list:
            list_of_nodes2fix = support[0]
            restrains = support[1]
            for node in list_of_nodes2fix:
                ops.fix(int(node),*restrains)
             
    def create_nodes_mass(self):  
        # Create a numpy array to alocate mass 
        masa = np.zeros((len(self.nodes),2))
        # Create opensees nodes 
        for i in range(len(self.nodes)):
            ops.node(int(self.nodes[i,0]),self.nodes[i,1],self.nodes[i,2],self.nodes[i,3])
            masa[i, 0] = self.nodes[i,0]
        return masa

    def mass_shell(self, i, j, k, l, gama_conc, t):
        # assuming ops.nodeCoord returns a list of coordinates [x, y, z]
        cords_i = np.array(ops.nodeCoord(int(i)))
        cords_j = np.array(ops.nodeCoord(int(j)))
        cords_k = np.array(ops.nodeCoord(int(k)))
        cords_l = np.array(ops.nodeCoord(int(l)))
        
        # define vectors of the triangles
        vector_ij = cords_j - cords_i
        vector_ik = cords_k - cords_i
        vector_il = cords_l - cords_i
        
        # calculate areas of the two triangles (1/2 * magnitude of the cross product of two sides)
        area1 = np.linalg.norm(np.cross(vector_ij, vector_ik)) / 2.0
        area2 = np.linalg.norm(np.cross(vector_ij, vector_il)) / 2.0
        
        # total area of the quadrilateral
        area = area1 + area2
        
        # calculate mass
        mass = t * area * gama_conc/self.g/4
        return mass
      
    def mass_shell_triangle(self, i, j, k, gama_conc, t):
        # assuming ops.nodeCoord returns a list of coordinates [x, y, z]
        cords_i = np.array(ops.nodeCoord(int(i)))
        cords_j = np.array(ops.nodeCoord(int(j)))
        cords_k = np.array(ops.nodeCoord(int(k)))

        # define vectors of the triangle
        vector_ij = cords_j - cords_i
        vector_ik = cords_k - cords_i

        # calculate area of the triangle (1/2 * magnitude of the cross product of two sides)
        area = np.linalg.norm(np.cross(vector_ij, vector_ik)) / 2.0

        # calculate mass
        mass = t * area * gama_conc / self.g / 4
        return mass
     
    def shells_factory(self,masa,verbose = False,Et = None):

        gtag = self.global_surface_tag
        for surface_id , material_id , t_id,_ in self.surfaces:
            indx_surf_mat = np.where(self.surface_materials[:,0] == material_id)[0][0]
            _,_E,_G,_U,_gamma_surf = self.surface_materials[indx_surf_mat,:].tolist()
            mesh_index =  np.where(self.mesh_cells[:,1] == surface_id)
            if Et == None:
                ops.section('ElasticMembranePlateSection', int(surface_id+gtag), _E, _U, t_id, 0.0)
            else:
                ops.section('ElasticMembranePlateSection', int(surface_id+gtag), _E, _U, t_id, 0.0,Et)
                
                    
            for shell_id, _, i, j, k, l in self.mesh_cells[mesh_index]:
                idd = shell_id+gtag
                ops.element('ShellMITC4',int(idd), int(i), int(j), int(k), int(l), int(surface_id+gtag))

                m= self.mass_shell(i, j, k, l, _gamma_surf, t_id)
                
                index = np.where(masa[:,0] == int(i))[0][0]
                masa[index,1] += m
                index = np.where(masa[:,0] == int(j))[0][0]
                masa[index,1] += m
                index = np.where(masa[:,0] == int(k))[0][0]
                masa[index,1] += m
                index = np.where(masa[:,0] == int(l))[0][0]
                masa[index,1] += m
                if verbose:
                    print(f"the id :{shell_id}, with the nodes 1 :{i} , 2 : {j} , 3:{k}, 4:{l} @ with mass : {m}. surface :{surface_id}")
                         
        return masa 
         
    def shells_factory_andes(self,masa,verbose = False):
        gtag = self.global_surface_tag
        for surface_id , material_id , t_id,_ in self.surfaces:
            indx_surf_mat = np.where(self.surface_materials[:,0] == material_id)[0][0]
            _,_E,_G,_U,_gamma_surf = self.surface_materials[indx_surf_mat,:].tolist()
            mesh_index =  np.where(self.mesh_cells[:,1] == surface_id)
            for shell_id, _, i, j, k in self.mesh_cells[mesh_index]:
                idd = shell_id+gtag
                ops.element('ShellANDeS',idd,i,j,k,t_id,_E,0.3,0.0)
                m= self.mass_shell_triangle(i, j, k, _gamma_surf, t_id)
                
                index = np.where(masa[:,0] == int(i))[0][0]
                masa[index,1] += m
                index = np.where(masa[:,0] == int(j))[0][0]
                masa[index,1] += m
                index = np.where(masa[:,0] == int(k))[0][0]
                masa[index,1] += m
     
                if verbose:
                    print(f"the id :{shell_id}, with the nodes 1 :{i} , 2 : {j} , 3:{k} @ with mass : {m}. surface :{surface_id}")
                    
        return masa 
                
    """ Requires Modification """ 
    def internal_Forces(self, _member_id , cross_index ,rotation, E, G_mod, N):
        #This function creates: 
        #the recorders for each fucntions
        #the elastic section 
        #section('Elastic', secTag, E_mod, A, Iz, Iy, G_mod, Jxx)
        #the integrations points with Lobatos
        #beamIntegration('Lobatto', tag, secTag, N)
       
        if rotation != 0:
            A = self.members_prop[cross_index,4]
            Iz = self.members_prop[cross_index,3]
            Iy = self.members_prop[cross_index,2]
            Jxx = self.members_prop[cross_index,1]
        else:
            A = self.members_prop[cross_index,4]
            Iz = self.members_prop[cross_index,2]
            Iy = self.members_prop[cross_index,3]
            Jxx = self.members_prop[cross_index,1]            
        
        ops.section('Elastic',int(_member_id), E, A, Iz, Iy, G_mod, Jxx)
        ops.beamIntegration('Lobatto', int(_member_id),int( _member_id), N)  
    
    def set_members_properties(self,line ,section_id, E,G,N,con,masa,m,rotation):
        
        self.internal_Forces(line ,section_id,rotation, E,G,N)    
        ops.element('forceBeamColumn',int(line),*con,int(line),int(line) )
        index = np.where(masa[:,0] == con[0])[0][0]
        masa[index,1] += m
        index = np.where(masa[:,0] == con[1])[0][0]
        masa[index,1] += m
        return masa
    
# To do : fix 2 column with second name in idele
    def create_beam_elements(self, masa, z, gama, g, E, G, N, verbose=False):
        verbose = False
        for line,section_id,rotation in self.idele:
            if line in self.conect[:,0]:
                index_con = np.where(self.conect[:,0] == line )[0][0]
               
                # check for rigid memebers
                if not np.isnan(section_id):
                    index_mem_prop = np.where(self.members_prop[:,0]==section_id)[0][0]
                    # Get node tags and coordinates
                    node_tag_i = int(self.conect[index_con,1])
                    node_tag_j = int(self.conect[index_con,2])
                    
                    node_cord_i = ops.nodeCoord(node_tag_i)
                    node_cord_j = ops.nodeCoord(node_tag_j)
                    
                    xaxis = np.subtract(node_cord_i,node_cord_j)  
                    vecxz = np.cross(xaxis,z)
                    # Calculate mass 
                    L =np.linalg.norm(xaxis)
                    m =self.members_prop[index_mem_prop,4]*L*gama/2/g
                    # zip node tags
                    con = [node_tag_i ,node_tag_j]
                    vc2= [0.0,-1.0,0.0]
                    if np.linalg.norm(vecxz) == 0:
                        ops.geomTransf('Linear',int(line) ,*vc2)
                        masa = self.set_members_properties(line ,index_mem_prop, E,G,N,con,masa,m,rotation)
                    else:
                        
                        if node_cord_i[2]-node_cord_j[2] == 0:
                            ops.geomTransf('Linear',int(line),*vecxz)
                            masa =self.set_members_properties(line ,index_mem_prop, E,G,N,con,masa,m,rotation)
                            
                        else:
                            ops.geomTransf('Linear', int(line),*vecxz)
                            masa = self.set_members_properties(line ,index_mem_prop, E,G,N,con,masa,m,rotation)
                else:

                    ops.rigidLink('beam',node_tag_j,node_tag_i)
                    # ops.equalDOF(node_tag_i, node_tag_j,6)
                    print('creat a new rigid member ****')
                if verbose:
                    
                    print(f"line No {line}, crossection {section_id} wa created , with node tag {con}")
        return masa
                        
    def fix_model(self):   
        for i in range(len(self.nodes_w_support)):
            ops.fix(int(self.nodes_w_support[i]),*self.default_restrains)

    def assign_mass(self,masa):
        for i in range(len(masa)):
            ops.mass(int(masa[i, 0]), masa[i, 1], masa[i, 1], masa[i, 1], 0, 0, 0)

    def Modal_analysis(self, Nm):
        ops.constraints('Transformation')
        # ops.recorder('PVD', 'Dis_pvd','eigen',15)
        # ops.numberer('Plain')
        ops.numberer("RCM")
        ops.algorithm('Newton')
        freq = ops.eigen(Nm)
        ops.integrator('LoadControl',int(1))
        ops.analysis("Static")
        ops.analyze(1)
        # ops.remove('recorders')
        return freq
    
    def convert_load2mass(self,PZ):
        #Pz is a string , something it came with -P 
        # with int and float we get P 
        # we conver it to mas dividng N/g
        # it is assumed that the loas come in kN
        Pz_int = abs(float(PZ))
        m = Pz_int*1000/self.g
        return m
    
    def nodal_loads_mass(self):
        self.nodes_with_mass = []
        for load_id,_nodes,_, _, PZ, _,_,_ in self.nodal_loads:
            # print(PZ1)
            # the loads enter as string - this convert it to list/ints
            list_of_nodes = [int(i) for i in _nodes.split(',')]
            for node in list_of_nodes:
                m =  self.convert_load2mass(PZ)
                # index = np.where(masa[:,0] == node)[0][0]
                # masa[index,1] += m         
                self.nodes_with_mass.append([node,m])
                # print
                
    def get_mass_surface_loads(self,masa):
        
        for srf_lf_id , surface_ids , PZ in self.surface_loads:
            # list_of_surface = [int(i) for i in  surface_ids.split(',')]
            list_of_surface = ast.literal_eval(surface_ids)
            for surface in list_of_surface:
                m_meter = self.convert_load2mass(PZ)
                # print(surface)
                surface_loc = np.where(self.surfaces[:,0] == surface)[0][0]
                m = m_meter*self.surfaces[surface_loc,3]/1000000
                mesh_index =  np.where(self.mesh_cells[:,1] == surface)
                no_mesh = len(mesh_index[0])
                # load divided between number of cells , divided by 4 (quads nodes)
                m = m/no_mesh/4

                for shell_id, _, i, j, k, l in self.mesh_cells[mesh_index]:
                    # update masa 
                    index = np.where(masa[:,0] == int(i))[0][0]
                    masa[index,1] += m
                    index = np.where(masa[:,0] == int(j))[0][0]
                    masa[index,1] += m
                    index = np.where(masa[:,0] == int(k))[0][0]
                    masa[index,1] += m
                    index = np.where(masa[:,0] == int(l))[0][0]
                    masa[index,1] += m
               
        return masa 
                        
    def set_rigid_diaphragm(self,nodes,master):
        master_tag= master[0]
        ops.node(master_tag,*master[1:])
        ops.fix(master_tag,0,0,1,1,1,0)
        ops.rigidDiaphragm(3,master_tag, *nodes)
        
    def set_rigid_diaphragm_inclined(self,nodes,master_tag):
        for node in nodes:
            if not node == master_tag:
                ops.rigidLink('beam',master_tag,node)
            else:
                print('we catch ' , node)
           
    def assig_mass2special_nodes(self,masa):
        for node , point_mass in self.nodes_with_mass:
            index = np.where(masa[:,0] == node)[0][0]
            m0 = masa[index,1]
            m = m0+point_mass

            masa[index,1] = m
        return masa 
                        
    def create_model(self,verbose,hinges_lists=None,multiple_support = False, support_hinges = False,Et =None):
        ops.wipe()
        # Creates Opensees Model
        ops.model('basic','-ndm',3,'-ndf',6)
        # Z global axis reference
        z = [0,0,1]
        # integration points 
        N = 3
        # generate nodes and 
        G,gama,E = self.steel_properties
        # define gravity 
        g = self.g
        # Assign Mases 
        masa = self.create_nodes_mass()
        self.create_beam_elements( masa, z, gama, g, E, G, N, verbose=True)
        # self.create_mass_elements(masa, z, gama, g, E, G, N, verbose)
        #crate mass 
        if hinges_lists is not None:
            self.set_hinges(hinges_lists)
        
        if self.mesh_cells.size ==0:
            
            self.assign_mass(masa)
            print('Line 425',np.sum(masa[:,1]))
          
        else:
            masa = self.shells_factory( masa, verbose,Et)
            # self.assign_mass(masa)  
            # print('Mass Assigned to Shells')
            
        if self.surface_loads.size == 0:
            pass
        else:
            masa =  self.get_mass_surface_loads(masa)
            print('Surface Loads converted to mass')

        # assign self weight masses 
        self.nodal_loads_mass()
        masa = self.assig_mass2special_nodes(masa)    
        self.assign_mass(masa)         
        if multiple_support is not False:
            self.set_multiple_support(multiple_support)
        else:
            self.fix_model()
            
        if support_hinges is not False:
            self.semirigid_support(support_hinges)
            
        
        return ops , masa 

    def create_model_tri(self,verbose,hinges_lists=None,multiple_support = False,support_hinges = False):
        ops.wipe()
        # Creates Opensees Model
        ops.model('basic','-ndm',3,'-ndf',6)
        # Z global axis reference
        z = [0,0,1]
        # integration points 
        N = 3
        # generate nodes and 
        G,gama,E = self.steel_properties
        # define gravity 
        g = self.g
        # Assign Mases 
        masa = self.create_nodes_mass()
        self.create_beam_elements( masa, z, gama, g, E, G, N, verbose=True)
        # self.create_mass_elements(masa, z, gama, g, E, G, N, verbose)
        #crate mass 
        if hinges_lists is not None:
            self.set_hinges(hinges_lists)
        
        if self.mesh_cells.size ==0:
            
            self.assign_mass(masa)
            print('Line 425',np.sum(masa[:,1]))
          
        else:
            masa = self.shells_factory_andes( masa, verbose)
            # self.assign_mass(masa)  
            # print('Mass Assigned to Shells')
            
        if self.surface_loads.size == 0:
            pass
        else:
            masa =  self.get_mass_surface_loads(masa)
            print('Surface Loads converted to mass')

        # assign self weight masses 
        self.nodal_loads_mass()
        masa = self.assig_mass2special_nodes(masa)    
        self.assign_mass(masa)         
        if multiple_support is not False:
            self.set_multiple_support(multiple_support)
        else:
            self.fix_model()
            
        if support_hinges is not False:
            self.semirigid_support(support_hinges)

        return ops , masa 
      
