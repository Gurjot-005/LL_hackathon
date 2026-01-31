# visualization.py

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx


class Visualizer:
    """
    Generates visual artifacts:
    - Correlation heatmap
    - Inferred fronthaul topology graph
    """

    def save_heatmap(self, corr_df, output_path):
        """
        Saves a correlation heatmap image
        """
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_df, cmap="coolwarm", square=True)
        plt.title("Cell Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    def save_topology_graph(self, link_map, confidences, output_path):
        """
        Draws and saves the inferred topology as a network graph

        Nodes = Cells
        Edges = Shared Ethernet links
        Color = Link confidence
        """
        G = nx.Graph()

        # Add nodes and edges
        for link, cells in link_map.items():
            for cell in cells:
                G.add_node(cell)

            # Fully connect cells inside same link group
            for i in range(len(cells)):
                for j in range(i + 1, len(cells)):
                    G.add_edge(cells[i], cells[j], link=link)

        if G.number_of_nodes() == 0:
            print("⚠️ No nodes to draw in topology graph")
            return

        # Layout for clean visualization
        pos = nx.spring_layout(G, seed=42)

        # Node colors based on confidence of their link
        node_colors = []
        for node in G.nodes():
            link_id = next(
                (l for l, cells in link_map.items() if node in cells),
                None
            )
            conf = confidences.get(link_id, 0.0)
            node_colors.append(conf)

        # Draw graph
        plt.figure(figsize=(12, 9))

        nodes = nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colors,
            cmap=plt.cm.viridis,
            node_size=700
        )

        nx.draw_networkx_edges(G, pos, alpha=0.5)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

        plt.title("Inferred Fronthaul Topology (Color = Link Confidence)")
        plt.colorbar(nodes, label="Confidence Score (0 = Low, 1 = High)")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()


