import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


def visualize_topology(graph):
    """
    Create a visual representation of the cloud topology.
    """

    plt.figure(figsize=(10, 6))

    position = nx.spring_layout(
        graph,
        seed=42
    )

    nx.draw(
        graph,
        position,
        with_labels=True,
        node_size=2500,
        font_size=10,
        arrows=True
    )

    plt.title("AeroDrift Cloud Topology")

    reports_directory = Path("reports")
    reports_directory.mkdir(exist_ok=True)

    plt.savefig(
        reports_directory / "cloud_topology.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print("Topology visualization saved to: reports\\cloud_topology.png")