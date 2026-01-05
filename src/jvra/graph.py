from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import gcol


class Graph:
    def __init__(self, adj_matrix: defaultdict[str, dict[str, bool]]) -> None:
        self.graph: nx.Graph = nx.Graph()
        for v1, item in adj_matrix.items():
            self.graph.add_node(v1)
            for v2, adjacent in item.items():
                if v1 != v2 and adjacent:
                    self.graph.add_edge(v1, v2)

        self.colors: dict[str, int] = gcol.node_coloring(self.graph, opt_alg=1)

        self.chromatic_number: int = (
            max(self.colors.values() if self.colors else [0]) + 1
        )

        self.figure, ax = plt.subplots()
        nx.draw(
            self.graph,
            nx.shell_layout(self.graph),
            with_labels=True,
            ax=ax,
            node_color=gcol.get_node_colors(self.graph, self.colors),
        )
