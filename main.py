"""AeroDrift application entry point."""


def main() -> None:
    """Run the AeroDrift application."""
    print("AeroDrift")


if __name__ == "__main__":
    main()
from app.ingestion.mock_data import get_mock_cloud_data


def main():
    cloud_data = get_mock_cloud_data()

    print("AeroDrift Cloud Resources")
    print("=" * 30)

    print(f"VPCs: {len(cloud_data['vpcs'])}")
    print(f"Subnets: {len(cloud_data['subnets'])}")
    print(f"EC2 Instances: {len(cloud_data['ec2_instances'])}")
    print(f"Security Groups: {len(cloud_data['security_groups'])}")
    print(f"Databases: {len(cloud_data['databases'])}")


if __name__ == "__main__":
    main()   
from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.graph.visualize import visualize_topology

def main():
    cloud_data = get_mock_cloud_data()

    graph = build_cloud_topology(cloud_data)

    print("AeroDrift Cloud Topology")
    print("=" * 30)

    print(f"Total Nodes: {graph.number_of_nodes()}")
    print(f"Total Connections: {graph.number_of_edges()}")

    print("\nConnections:")

    for source, target in graph.edges():
        print(f"{source} -> {target}")


if __name__ == "__main__":
    main()
from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.detection.drift_detector import detect_public_database_path


def main():

    cloud_data = get_mock_cloud_data()

    graph = build_cloud_topology(cloud_data)

    visualize_topology(graph)

    results = detect_public_database_path(graph)

    print("AeroDrift Drift Detection")
    print("=" * 35)

    for result in results:

        print(f"\nDatabase: {result['database']}")
        print(f"Status: {result['status']}")

        if result["path"]:
            print("Risky Path:")
            print(" -> ".join(result["path"]))


if __name__ == "__main__":
    main()   
from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.detection.drift_detector import detect_public_database_path
from app.detection.report import save_drift_report


def main():

    cloud_data = get_mock_cloud_data()

    graph = build_cloud_topology(cloud_data)

    results = detect_public_database_path(graph)

    print()
    print("AERODRIFT SECURITY ANALYSIS")
    print("=" * 35)

    for result in results:

        print()
        print(f"Database: {result['database']}")
        print(f"Status: {result['status']}")
        print(f"Severity: {result['severity']}")
        print(f"Issue: {result['issue']}")

        if result["path"]:
            print("Risky Path:")
            print(" -> ".join(result["path"]))

    report_file = save_drift_report(results)

    print()
    print(f"JSON report saved to: {report_file}")


if __name__ == "__main__":
    main()     