# Author: Daniel Calbick
# Date: 2023-09-21

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from noise import pnoise1
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import imageio
import random 

def spherical_to_cartesian(r, theta, phi):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return x, y, z

def rotate_3D(points, angles):
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(angles[0]), -np.sin(angles[0])],
        [0, np.sin(angles[0]), np.cos(angles[0])]
    ])
    Ry = np.array([
        [np.cos(angles[1]), 0, np.sin(angles[1])],
        [0, 1, 0],
        [-np.sin(angles[1]), 0, np.cos(angles[1])]
    ])
    Rz = np.array([
        [np.cos(angles[2]), -np.sin(angles[2]), 0],
        [np.sin(angles[2]), np.cos(angles[2]), 0],
        [0, 0, 1]
    ])
    R = np.dot(Rz, np.dot(Ry, Rx))
    return np.dot(points, R.T)

class baseCluster:
    def __init__(self, n, k, p, color, center, radius=0.1, sparsity=0.1):
        self.G = nx.watts_strogatz_graph(n, k, p)
        self.color = color
        self.center = np.array(center)
        self.radius = radius
        self.theta_phi = {node: (np.random.uniform(0, np.pi), np.random.uniform(0, 2 * np.pi)) for node in self.G.nodes}
        self.scale_factors = {node: np.random.uniform(0.8, 1.2) for node in self.G.nodes}
        
        # Initialize offsets
        self.x_offset = np.random.rand() * 1000
        self.y_offset = np.random.rand() * 1000
        self.z_offset = np.random.rand() * 1000
        
        # Initialize positions dictionary
        self.positions = {}
        
        # Modify connectivity based on sparsity
        for node1 in self.G.nodes:
            for node2 in self.G.nodes:
                if node1 >= node2:  # Skip duplicate pairs and self-loops
                    continue
                if random.random() < sparsity:
                    self.G.add_edge(node1, node2)
                else:
                    if self.G.has_edge(node1, node2):
                        self.G.remove_edge(node1, node2)
        
        self.update_positions(0)  # Initialize positions

class GraphCluster:
    def __init__(self, n, k, p, color, center, radius=0.1, sparsity=0.1):
        self.G = nx.watts_strogatz_graph(n, k, p)
        self.color = color
        self.center = np.array(center)
        self.radius = radius
        self.theta_phi = {node: (np.random.uniform(0, np.pi), np.random.uniform(0, 2 * np.pi)) for node in self.G.nodes}
        self.scale_factors = {node: np.random.uniform(0.8, 1.2) for node in self.G.nodes}
        
        # Initialize offsets
        self.x_offset = np.random.rand() * 1000
        self.y_offset = np.random.rand() * 1000
        self.z_offset = np.random.rand() * 1000
        
        # Initialize positions dictionary
        self.positions = {}
        
        # Modify connectivity based on sparsity
        for node1 in self.G.nodes:
            for node2 in self.G.nodes:
                if node1 >= node2:  # Skip duplicate pairs and self-loops
                    continue
                if random.random() < sparsity:
                    self.G.add_edge(node1, node2)
                else:
                    if self.G.has_edge(node1, node2):
                        self.G.remove_edge(node1, node2)
        
        self.update_positions(0)  # Initialize positions


    def update_positions(self, increment):
        # Update centroid
        self.center += np.array([pnoise1(self.x_offset, 5) * 0.005, pnoise1(self.y_offset, 5) * 0.005, pnoise1(self.z_offset, 5) * 0.005])
        
        # Update node positions relative to centroid
        for node in self.G.nodes:
            theta, phi = self.theta_phi[node]
            
            # Update theta and phi slightly for organic movement
            theta += pnoise1(self.x_offset + node, 1) * 0.01
            phi += pnoise1(self.y_offset + node, 1) * 0.01
            
            r = self.radius * self.scale_factors[node]
            
            x_new, y_new, z_new = spherical_to_cartesian(r, theta, phi)
            
            # Update the position relative to the drifting center
            self.G.nodes[node]['pos'] = tuple(self.center + np.array([x_new, y_new, z_new]))
            self.positions[node] = self.G.nodes[node]['pos']
            
            # Update theta and phi for the next iteration
            self.theta_phi[node] = (theta, phi)
        
        self.x_offset += increment
        self.y_offset += increment
        self.z_offset += increment

        # # Apply rotation
        # angles = [pnoise1(self.x_offset, 1) * 0.1, pnoise1(self.y_offset, 1) * 0.1, pnoise1(self.z_offset, 1) * 0.1]
        # rotated_positions = rotate_3D(np.array(list(self.positions.values())), angles)
        # self.positions = {node: tuple(pos) for node, pos in zip(self.G.nodes, rotated_positions)}
        # nx.set_node_attributes(self.G, self.positions, 'pos')  # Update the NetworkX graph object


    def project_to_2D(self):
        return {node: (x, y) for node, (x, y, z) in self.positions.items()}

class CombinedGraph:
    def __init__(self, graph_clusters, interconnect_probabilities):
        self.graph_clusters = graph_clusters
        self.G = nx.disjoint_union_all([cluster.G for cluster in graph_clusters])
        self.interconnects = self.create_interconnects(interconnect_probabilities)
    
    def create_interconnects(self, interconnect_probabilities):
        interconnects = nx.Graph()
        for i, cluster1 in enumerate(self.graph_clusters):
            for j, cluster2 in enumerate(self.graph_clusters):
                if i >= j:  # Skip duplicate pairs and self-connections
                    continue

                nodes_in_c1 = random.sample(list(cluster2.G.nodes), int(len(cluster2.G.nodes) * interconnect_probabilities[i][j]))
                nodes_in_c2 = random.sample(list(cluster2.G.nodes), int(len(cluster2.G.nodes) * interconnect_probabilities[i][j]))
                for node1 in nodes_in_c1:
                    for node2 in nodes_in_c2:
                        if random.random() < interconnect_probabilities[i]:
                            interconnects.add_edge(node1, node2)
        return interconnects
    
    def update_positions(self, increment):
        for cluster in self.graph_clusters:
            cluster.update_positions(increment)
        self.update_interconnects()

    def update_interconnects(self):
        for edge in self.interconnects.edges:
            node1, node2 = edge
            pos1, pos2 = None, None
            
            # Find which cluster each node belongs to and get its position
            for cluster in self.graph_clusters:
                if node1 in cluster.G.nodes:
                    pos1 = cluster.positions[node1]
                if node2 in cluster.G.nodes:
                    pos2 = cluster.positions[node2]
            
            # Update the position attribute for the edge in interconnects
            if pos1 is not None and pos2 is not None:
                self.interconnects[node1][node2]['pos1'] = pos1
                self.interconnects[node1][node2]['pos2'] = pos2



class Interconnects:
    def __init__(self, clusters, density):
        self.clusters = clusters
        self.density = density
        self.edges = []
        self.initialize_edges()

    def initialize_edges(self):
        for i in range(len(self.clusters) - 1):
            cluster1 = self.clusters[i]
            cluster2 = self.clusters[i + 1]
            density = self.density[i]
            n_interconnections = int(density * len(cluster1.G.nodes))
            
            for _ in range(n_interconnections):
                node1 = random.choice(list(cluster1.G.nodes))
                node2 = random.choice(list(cluster2.G.nodes))
                self.edges.append((node1, node2))

    def update_edges(self):
        # Update the edges based on the new positions of the clusters
        pass

def create_frame(combined_graph, increment):
    fig, ax = plt.subplots(figsize=(6, 6))
    combined_graph.update_positions(increment)
    for cluster in combined_graph.graph_clusters:
        nx.draw(cluster.G, pos=cluster.project_to_2D(), ax=ax, with_labels=False, node_size=20, node_color=cluster.color)
    
    # Draw interconnecting edges
    for node1, node2 in combined_graph.interconnects.edges:
        try:
            x1, y1 = combined_graph.graph_clusters[0].project_to_2D()[node1]
            x2, y2 = combined_graph.graph_clusters[1].project_to_2D()[node2]
            plt.plot([x1, x2], [y1, y2], color='grey')
        except KeyError as e:
            print(f"KeyError encountered for node {e}")
    
    canvas = FigureCanvas(fig)
    canvas.draw()
    frame = np.frombuffer(canvas.buffer_rgba(), dtype='uint8').reshape(fig.canvas.get_width_height()[::-1] + (4,))[:, :, :3]
    plt.close()
    return frame


def main():
    colors = ['blue', 'green', 'red', 'purple']
    centers = [(0.5, 0.5, 0.5), (0.7, 0.3, 0.6), (0.2, 0.8, 0.4), (0.9, 0.1, 0.2)]
    numnodes = [50, 100, 30, 15]
    radii = [0.1, 0.15, 0.12, 0.08]  # Different sizes for each cluster
    
    # Define interconnect probabilities between each pair of clusters
    interconnect_probabilities = [
        [0, 0.1, 0.05, 0.02],  # Probabilities for cluster 0 (blue) connecting to other clusters
        [0, 0, 0.1, 0.05],     # Probabilities for cluster 1 (green) connecting to other clusters
        [0, 0, 0, 0.1],        # Probabilities for cluster 2 (red) connecting to other clusters
        [0, 0, 0, 0]           # Probabilities for cluster 3 (purple) connecting to other clusters
    ]
    
    graph_clusters = [GraphCluster(n, 6, 0.2, color, center, radius) for n, color, center, radius in zip(numnodes, colors, centers, radii)]
    combined_graph = CombinedGraph(graph_clusters, interconnect_probabilities)
    
    increment = 0.01
    frames = []
    
    for _ in range(50):
        frame = create_frame(combined_graph, increment)
        frames.append(frame)
    
    # Save the frames as a GIF
    imageio.mimsave('animated_network_3D_effect.gif', frames, duration=0.1)


if __name__ == "__main__":
    main()
