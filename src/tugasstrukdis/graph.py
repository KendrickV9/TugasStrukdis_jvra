from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx


class Graph:
    def __init__(self, adj_matrix: defaultdict[str, dict[str, bool]]) -> None:
        self.graph = nx.Graph()
        for v1, item in adj_matrix.items():
            for v2, adjacent in item.items():
                if adjacent:
                    self.graph.add_edge(v1, v2)

    def get_figure(self) -> plt.Figure:
        fig, ax = plt.subplots()
        nx.draw(self.graph, with_labels=True, ax=ax)
        return fig

    def get_colors(self) -> dict[str, int]:
        return {}
