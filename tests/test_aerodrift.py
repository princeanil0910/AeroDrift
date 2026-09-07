from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.detection.drift_detector import detect_public_database_path
from app.remediation.remediation_engine import generate_remediation
from app.remediation.safety_check import validate_remediation


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
    assert "internet" in graph
    assert "db-001" in graph


def test_public_database_detection():
    data = get_mock_cloud_data()
    graph = build_cloud_topology(data)

    result = detect_public_database_path(graph)

    assert len(result) == 1
    assert result[0]["database"] == "db-001"
    assert result[0]["status"] == "DRIFT_DETECTED"
    assert result[0]["severity"] == "CRITICAL"
    assert result[0]["path"] == [
        "internet",
        "sg-001",
        "ec2-001",
        "db-001",
    ]


def test_remediation_plan_for_detected_drift():
    remediation = generate_remediation({
        "status": "DRIFT_DETECTED",
        "database": "db-001",
        "severity": "CRITICAL",
        "issue": "Private database is reachable from the Internet",
    })

    assert remediation["action"] == "REVOKE_PUBLIC_ACCESS"
    assert remediation["target"] == "sg-001"
    assert remediation["status"] == "REMEDIATION_READY"


def test_safe_result_requires_no_remediation():
    remediation = generate_remediation({"status": "SAFE"})

    assert remediation == {
        "action": "NO_ACTION",
        "reason": "No drift detected",
    }


def test_safety_check_rejects_unexpected_source():
    safety_result = validate_remediation({
        "action": "REVOKE_PUBLIC_ACCESS",
        "target": "sg-001",
        "source": "10.0.0.0/8",
    })

    assert safety_result["approved"] is False
    assert safety_result["reason"] == "Unexpected source rule"