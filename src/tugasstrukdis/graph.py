from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
import gcol
import networkx as nx


class Graph:
    def __init__(self, adj_matrix: defaultdict[str, dict[str, bool]]) -> None:
        self.graph = nx.Graph()
        for v1, item in adj_matrix.items():
            for v2, adjacent in item.items():
                if v1 != v2 and adjacent:
                    self.graph.add_edge(v1, v2)
        self.node_colors: dict[str, int] = gcol.node_coloring(self.graph, opt_alg=1)

    def get_figure(self) -> plt.Figure:
        fig, ax = plt.subplots()
        nx.draw(
            self.graph,
            with_labels=True,
            ax=ax,
            node_color=gcol.get_node_colors(self.graph, self.node_colors),
        )

        return fig

    def get_colors(self) -> dict[str, int]:
        return self.node_colors

    def get_chromatic_number(self) -> int:
        return max(self.node_colors.values()) + 1
