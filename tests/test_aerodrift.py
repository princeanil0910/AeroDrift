from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.detection.drift_detector import detect_public_database_path


def test_mock_cloud_data():
    data = get_mock_cloud_data()

    assert "vpcs" in data
    assert "subnets" in data
    assert "ec2_instances" in data
    assert "security_groups" in data
    assert "databases" in data


def test_cloud_topology():
    data = get_mock_cloud_data()
    graph = build_cloud_topology(data)

    assert graph is not None
    assert len(graph.nodes) > 0


def test_public_database_detection():
    data = get_mock_cloud_data()
    graph = build_cloud_topology(data)

    result = detect_public_database_path(graph)

    assert result is not None