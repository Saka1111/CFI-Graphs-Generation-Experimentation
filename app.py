import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from itertools import combinations
from typing import Dict, List, Set, Tuple, Any
import json

app = Flask(__name__)

# Example graphs that users can select from
EXAMPLE_GRAPHS = {
    "Triangle": {
        "x": ["y", "z"],
        "y": ["x", "z"],
        "z": ["x", "y"]
    },
    "4-clique": {
        "x": ["a", "b", "c"],
        "a": ["x", "b", "c"],
        "b": ["x", "a", "c"],
        "c": ["x", "a", "b"]
    },
    "5-clique": {
        "x": ["a", "b", "c", "d"],
        "a": ["x", "b", "c", "d"],
        "b": ["x", "a", "c", "d"],
        "c": ["x", "a", "b", "d"],
        "d": ["x", "a", "b", "c"]
    },
    "6-clique": {
        "x": ["a", "b", "c", "d", "e"],
        "a": ["x", "b", "c", "d", "e"],
        "b": ["x", "a", "c", "d", "e"],
        "c": ["x", "a", "b", "d", "e"],
        "d": ["x", "a", "b", "c", "e"],
        "e": ["x", "a", "b", "c", "d"]
    },
    "7-clique": {
        "x": ["a", "b", "c", "d", "e", "f"],
        "a": ["x", "b", "c", "d", "e", "f"],
        "b": ["x", "a", "c", "d", "e", "f"],
        "c": ["x", "a", "b", "d", "e", "f"],
        "d": ["x", "a", "b", "c", "e", "f"],
        "e": ["x", "a", "b", "c", "d", "f"],
        "f": ["x", "a", "b", "c", "d", "e"]
    },
    "8-clique": {
        "x": ["a", "b", "c", "d", "e", "f", "g"],
        "a": ["x", "b", "c", "d", "e", "f", "g"],
        "b": ["x", "a", "c", "d", "e", "f", "g"],
        "c": ["x", "a", "b", "d", "e", "f", "g"],
        "d": ["x", "a", "b", "c", "e", "f", "g"],
        "e": ["x", "a", "b", "c", "d", "f", "g"],
        "f": ["x", "a", "b", "c", "d", "e", "g"],
        "g": ["x", "a", "b", "c", "d", "e", "f"]
    },
    "Frucht":{
        "x": ["b", "c", "d"],
        "b": ["x", "e", "f"],
        "c": ["x", "g", "h"],
        "d": ["x", "i", "j"],
        "e": ["b", "g", "k"],
        "f": ["b", "i", "l"],
        "g": ["c", "e", "h"],
        "h": ["c", "g", "k"],
        "i": ["d", "f", "j"],
        "j": ["d", "i", "l"],
        "k": ["e", "h", "l"],
        "l": ["f", "j", "k"]
    }

}

class CFI:
    # Initialising the graphs χ(G,∅) & χ(G,{x})
    def __init__(self, graph: Dict[Any, List[Any]]):
        self.graph = graph
        self.cfi_empty = self.generate(set()) # 𝜒(G, ∅)
        self.cfi_x = self.generate({'x'}) # 𝜒(G, {x})

    # Getting the neighbours of neighbours
    def subset(self, neighbour: List[Any]) -> List[Set]:
        s = list(neighbour)
        # Returning set of all possible subsets
        return [set(combo) for length in range(len(s) + 1) 
                for combo in combinations(s, length)]

    # Generating the CFI graphs
    def generate(self, U: Set[Any]) -> Dict[Tuple[Any, frozenset], List[Tuple[Any, frozenset]]]:
        # Helper function to get neighbours of vertices
        def N(v: Any) -> List[Any]:
            return self.graph[v]
        
        # Generating vertices of 𝜒(G,U)
        vertices = []
        for v in self.graph:
            # Getting all possible subsets of neighbours
            neighbor_subsets = self.subset(N(v))
            # Filtering subsets based on even or odd condition
            valid_subsets = [
                S for S in neighbor_subsets
                if (v in U and len(S) % 2 == 1) or # Odd if v in U
                   (v not in U and len(S) % 2 == 0) # Even if v not in U
            ]
            # Adding valid vertices of 𝜒(G,U)
            vertices.extend((v, frozenset(S)) for S in valid_subsets)
        
        edges = {}
        for v1, S1 in vertices:
            edges[(v1, S1)] = []
            for v2, S2 in vertices:
                # Checking if v1 and v2 are adjacent in the original graph
                if v2 in self.graph[v1]:
                    # Checking the condition v1 ∈ S2 <=> v2 ∈ S1
                    if (v1 in S2) == (v2 in S1):
                        edges[(v1, S1)].append((v2, S2))
        return edges
    
    # Creating the graphs into NetworkX graphs
    def create(self) -> Tuple[nx.Graph, nx.Graph]:
        G1 = nx.Graph()
        G2 = nx.Graph()
        
        # Adding edges to both graphs
        for v1, neighbours in self.cfi_empty.items():
            for v2 in neighbours:
                G1.add_edge(v1, v2)
                
        for v1, neighbours in self.cfi_x.items():
            for v2 in neighbours:
                G2.add_edge(v1, v2)
                
        return G1, G2

    # Labelling vertices without frozenset
    def label(self, vertex: Tuple[Any, frozenset]) -> str:
        v, S = vertex
        if len(S) == 0:
            return f"{v},∅"
        else:
            set_elements = sorted(S)
            set_str = ','.join(set_elements)
            return f"{v},{{{set_str}}}"

    # Visualising the graphs
    def visualisation(self) -> Dict[str, str]:
        G1, G2 = self.create()
        
        # Creating the figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Using Kamada-Kawai layout for consistent drawings
        pos1 = nx.kamada_kawai_layout(G1)
        pos2 = nx.kamada_kawai_layout(G2)
        
        # Drawing graph χ(G,∅)
        nx.draw_networkx_nodes(G1, pos1, node_color='lightgreen', node_size=2000, edgecolors='green', ax=ax1)
        nx.draw_networkx_edges(G1, pos1, ax=ax1)
        labels1 = {vertex: self.label(vertex) for vertex in G1.nodes()}
        nx.draw_networkx_labels(G1, pos1, labels1, font_size=20, font_weight='bold', ax=ax1)
        
        # Drawing graph χ(G,{x})
        nx.draw_networkx_nodes(G2, pos2, node_color='lightblue', node_size=2000, edgecolors='blue', ax=ax2)
        nx.draw_networkx_edges(G2, pos2, ax=ax2)
        labels2 = {vertex: self.label(vertex) for vertex in G2.nodes()}
        nx.draw_networkx_labels(G2, pos2, labels2, font_size=20, font_weight='bold', ax=ax2)
        
        # Setting the titles
        ax1.set_title("CFI graph χ(G,∅)", fontsize=18, fontweight='bold')
        ax2.set_title("CFI graph χ(G,{x})", fontsize=18, fontweight='bold')
        
        # Removing the borders
        ax1.axis('off')
        ax2.axis('off')

        # Saving the figure
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return {'image': base64.b64encode(buf.getvalue()).decode()}
    
    # Evaluating the properties of the CFI pair
    def evaluate_properties(self) -> Dict[str, Any]:

        G1, G2 = self.create()
        
        # Evaluating properties for both graphs
        # isomorphic = nx.is_isomorphic(G1, G2)
        wl_hash_G1 = nx.weisfeiler_lehman_graph_hash(G1)
        wl_hash_G2 = nx.weisfeiler_lehman_graph_hash(G2)
        wl_isomorphic = wl_hash_G1 == wl_hash_G2
        
        # Calculating all properties
        return {
            # 'isomorphic': isomorphic,
            'wl_isomorphic': wl_isomorphic,
            'wl_hash_G1': wl_hash_G1,
            'wl_hash_G2': wl_hash_G2,
            # 'same': isomorphic == wl_isomorphic,
            'nodes_G1': G1.number_of_nodes(),
            'edges_G1': G1.number_of_edges(),
            'cycles_G1': len(nx.cycle_basis(G1)),
            'clustering_G1': nx.average_clustering(G1),
            'connectivity_G1': nx.is_connected(G1),
            'diameter_G1': nx.diameter(G1) if nx.is_connected(G1) else None,
            'bridges_G1': len(list(nx.bridges(G1))),
            'is_chordal_G1': nx.is_chordal(G1),
            'eulerian_G1': nx.is_eulerian(G1),
            'regular_G1': nx.is_regular(G1),
            'max_clique_G1': max(len(c) for c in nx.find_cliques(G1)),
            'nodes_G2': G2.number_of_nodes(),
            'edges_G2': G2.number_of_edges(),
            'cycles_G2': len(nx.cycle_basis(G2)),
            'clustering_G2': nx.average_clustering(G2),
            'connectivity_G2': nx.is_connected(G2),
            'diameter_G2': nx.diameter(G2) if nx.is_connected(G2) else None,
            'bridges_G2': len(list(nx.bridges(G2))),
            'is_chordal_G2': nx.is_chordal(G2),
            'eulerian_G2': nx.is_eulerian(G2),
            'regular_G2': nx.is_regular(G2),
            'max_clique_G2': max(len(c) for c in nx.find_cliques(G2))
        }
        

# Creating the routes
@app.route('/')
def home():
    return render_template('index.html', example_graphs=EXAMPLE_GRAPHS)

@app.route('/get_example_graph/<name>')
def get_example_graph(name):
    if name in EXAMPLE_GRAPHS:
        return jsonify({'success': True, 'graph': EXAMPLE_GRAPHS[name]})
    return jsonify({'success': False, 'error': 'Graph not found'})

@app.route('/visualise', methods=['POST'])
def visualise():
    try:
        data = request.json
        try:
            graph = json.loads(data['textInput'])
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid JSON format'})

        if 'x' not in graph:
            return jsonify({'success': False, 'error': 'Graph must include a node named "x"'})

        cfi = CFI(graph)
        result = cfi.visualisation()
        
        return jsonify({
            'success': True,
            'image': result['image']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/properties', methods=['POST'])
def properties():
    try:
        data = request.json
        try:
            graph = json.loads(data['textInput'])
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid JSON format'})

        if 'x' not in graph:
            return jsonify({'success': False, 'error': 'Graph must include a node named "x"'})

        cfi = CFI(graph)
        result = cfi.evaluate_properties()
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

if __name__ == '__main__':
    app.run(debug=True)