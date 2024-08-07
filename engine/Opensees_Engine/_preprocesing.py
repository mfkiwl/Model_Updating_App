import numpy as np  
import matplotlib.pyplot as plt 
from matplotlib.path import Path

from shapely.geometry import Point, Polygon
from matplotlib.transforms import Affine2D

class Preprocesor:
    def __init__(self,model):
        
        self.nodes = model.nodes
        self.conect = model.conect
        self.idele = model.idele
        self.members_prop = model.members_prop
        self.names = model.names
        self.nodal_loads = model.nodal_loads
        
        if model.surfaces.size:
            self.surface = model.surfaces 
            self.surface_materials = model.surface_materials
            self.mesh_cells = model.mesh_cells
            self.surface_loads = model.surface_loads
        

    def get_nodes_in_plane(self, list_of_node_tags, master):
        # Get the coordinates of the nodes
        coords = self.get_node_coords(list_of_node_tags)
        
        # Compute plane equation
        plane_eq = self.get_plane_equation(coords)
        
        # Get nodes in plane
        nodes_in_plane = [node[0] for node in self.nodes if self.is_point_in_plane(node[1:], plane_eq)]
        
        # Compute the centroid of the boundary nodes (in the plane)
        centroid_xy = np.mean(coords, axis=0)[:2]  # Averages the x and y coordinates
    
        # We use the plane equation to solve for the z-coordinate
        A, B, C, D = plane_eq
        x_centroid, y_centroid = centroid_xy
        z_centroid = -(A*x_centroid + B*y_centroid + D) / C
    
        # Construct the centroid node
        centroid_nodes = [master, x_centroid, y_centroid, z_centroid]
    
        return nodes_in_plane, centroid_nodes
        
    @staticmethod
    def get_plane_equation(node_coords):
        p1, p2, p3, p4 = node_coords  # Unpack the four points

        # Compute two vectors that lie in the plane
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)

        # Compute the normal vector of the plane (this is orthogonal to the plane)
        normal = np.cross(v1, v2)

        # Compute D
        D = -np.dot(normal, p1)

        return (*normal, D)

    @staticmethod
    def is_point_in_plane(point, plane_equation):
        A, B, C, D = plane_equation
        x, y, z = point

        # Compute the left-hand side of the plane equation
        lhs = A*x + B*y + C*z + D

        # If this is very close to zero, then the point is in the plane
        return np.isclose(lhs, 0, atol=1e-6)  # Use an appropriate tolerance

    
    def get_nodes_between_boundaries(self, list_of_node_tag, master=None):
        # Get the coordinates of the four nodes
        coords = self.get_node_coords(list_of_node_tag)
        
        # Extract only the x and y coordinates
        polygon_coords = [(cord[0], cord[1]) for cord in coords]
        polygon = Polygon(polygon_coords)
        
        if master:
            centroid = polygon.centroid
            # Average the z-values of the polygon's nodes for the new node
            z_value_centroid = np.mean([cord[2] for cord in coords])
            centroid_nodes = [master, centroid.x, centroid.y, z_value_centroid]
        
        # Assume that the z coordinate of all nodes should be the same as the first node
        z_value = coords[0][2]
        z_tolerance = 0.01  # Define an appropriate value based on your data
        
        # Iterate over all nodes and check if they are within the polygon
        nodes_in_polygon = []
        for node in self.nodes:
            # Consider only nodes with the same z value
            if abs(node[3] - z_value) < z_tolerance:
                point = Point(node[1], node[2])
                if polygon.contains(point) or polygon.touches(point):
                    nodes_in_polygon.append(node[0])
        
        # Add boundary nodes to the result
        # nodes_in_polygon.extend(list_of_node_tag)
        
        if master:
            return nodes_in_polygon, centroid_nodes
        else:
            return nodes_in_polygon

    
    def get_node_coords(self, list_of_node_tag):
        return [self.nodes[self.get_node_cord(tag), 1:] for tag in list_of_node_tag]
    
    def get_node_cord(self, node_tag):
        tag_loc = np.where(self.nodes[:,0]==node_tag)[0][0]
        return tag_loc

    def plot_nodes(self, node_tags):
        # Get the coordinates of the nodes
        coords = self.get_node_coords(node_tags)
    
        # Create arrays of x, y, and z coordinates
        xs = [cord[0] for cord in coords]
        ys = [cord[1] for cord in coords]
        zs = [cord[2] for cord in coords]
        
        # Create a 3D scatter plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        plt.show()
