# CFI Graph Generator & Analyser

A Python-based system for generating, visualising, and analysing Cai–Fürer–Immerman (CFI) graph pairs. This tool is designed to investigate the theoretical limitations of Graph Neural Networks (GNNs) by creating graph pairs that are indistinguishable by the 1-Weisfeiler–Leman (1-WL) algorithm but are structurally non-isomorphic.

---

## Features

- **CFI Graph Generation**: Implements the precise mathematical construction of CFI graphs, producing both the untwisted (χ(G, Ø)) and twisted (χ(G, {x})) variants from a base graph *G*.  
- **Dual Input Methods**:  
  - **JSON Input**: Define your graph structure in a precise JSON format.  
  - **Visual Builder**: An intuitive drag-and-drop interface built with *vis.js* for constructing graphs interactively.  
- **Visualisation**: High-quality side-by-side visualisation of CFI pairs using NetworkX and Matplotlib, with custom labelling for clarity.  
- **Comprehensive Property Evaluation**: Analyses a wide range of graph properties for both CFI graphs, including:  
  - Standard isomorphism test (`networkx.is_isomorphic`)  
  - Weisfeiler–Leman graph hash (1-WL algorithm)  
  - Number of nodes, edges, and cycles  
  - Clustering coefficient, connectivity, and diameter  
  - Maximal clique size  
- **GNN Limitation Analysis**: Demonstrates the inability of 1-WL and, by equivalence, 1-GNNs to distinguish the generated CFI pairs. Provides empirical evidence through clique evaluation that the WL dimension for computing the maximal clique function is high.

---

## Installation & Requirements

Clone the repository:

```bash
git clone <your-repo-url>
cd cfi-graph-generator
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**Core dependencies:**
- Python 3.x  
- Flask  
- NetworkX  
- Matplotlib  

---

## Usage

Run the Flask application:

```bash
python app.py
```

### Input a Base Graph *G*:

- **JSON Method**: Paste a JSON object where keys are node names and values are lists of neighbours. The graph must contain a node named `x`. Example for a triangle:  

```json
{
  "x": ["y", "z"],
  "y": ["x", "z"],
  "z": ["x", "y"]
}
```

- **Visual Builder**: Use the interactive canvas to add nodes and edges. The first node created is automatically named `x`.

### Generate and Analyse:
Use the buttons to generate the CFI graphs, visualise them, and compute their properties.

---

## Implementation Overview

The core functionality is encapsulated in the **CFI** class (`cfi.py`):

- `__init__(self, graph)`: Initialises the generator with a base graph *G* and immediately generates both CFI variants.  
- `subset(self, neighbours)`: Generates all possible subsets of a vertex’s neighbours (*complexity O(2^n)*).  
- `generate(self, U)`: Core function that constructs the CFI graph χ(G, U) by creating vertices that satisfy the “mod S condition” and edges that satisfy the “membership condition”.  
- `create(self)`: Converts the internal graph representation into NetworkX graph objects for analysis.  
- `visualisation(self)`: Generates a side-by-side plot of the CFI pair using the Kamada–Kawai layout algorithm.  
- `evaluate_properties(self)`: Computes and returns a comprehensive dictionary of graph properties for both CFI graphs.

---

## Key Findings & Evaluation

- **WL/GNN Equivalence**: The system confirms that the 1-WL algorithm (and thus 1-GNNs) produces identical hashes for non-isomorphic CFI pairs, exemplifying their fundamental limitation.  
- **Clique Analysis**: For a base graph *G* that is a *k*-clique, the maximal clique size of χ(G, Ø) is *k*, while for χ(G, {x}) it is *k*–1. This proves that the function *F* (maximal clique) has a WL dimension of at least *k*–1, meaning GNNs of order lower than *k*–1 cannot compute it.  
- **Computational Limit**: Due to the NP-complete nature of the maximal clique problem, practical evaluation was limited to *k* ≤ 8.

---

---

## References

This project is based on the theoretical work of:

- Cai, J.Y., Fürer, M. & Immerman, N. (1992)  
- Morris, C. et al. (2019) *Weisfeiler and Leman Go Neural: Higher-Order Graph Neural Networks*  
- Roberson, D.E. (2022) *Oddomorphisms and homomorphism indistinguishability over graphs of bounded degree*  
