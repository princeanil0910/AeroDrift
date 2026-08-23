import networkx as nx


def detect_public_database_path(graph):
    """
    Detect whether the Internet can reach a database.
    """

    internet_node = "internet"

    database_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "Database"
    ]

    drift_results = []

    for database in database_nodes:

        if nx.has_path(graph, internet_node, database):

            path = nx.shortest_path(
                graph,
                internet_node,
                database
            )

            drift_results.append({
                "database": database,
                "status": "DRIFT_DETECTED",
                "severity": "CRITICAL",
                "issue": "Private database is reachable from the Internet",
                "source": "0.0.0.0/0",
                "path": path
            })

        else:

            drift_results.append({
                "database": database,
                "status": "SAFE",
                "severity": "NONE",
                "issue": "No Internet path detected",
                "source": None,
                "path": []
            })

    return drift_results