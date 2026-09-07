import json

from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.detection.drift_detector import detect_public_database_path
from app.detection.report import save_drift_report
from app.remediation.remediation_engine import generate_remediation
from app.remediation.safety_check import validate_remediation
from app.remediation.ast_remediation import (
    generate_remediation_code,
    validate_remediation_code,
)
from app.remediation.mock_remediation import apply_mock_remediation
from app.remediation.audit_report import save_remediation_audit


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
    assert graph.has_edge("internet", "sg-001")
    assert graph.has_edge("sg-001", "ec2-001")
    assert graph.has_edge("ec2-001", "db-001")


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


def test_public_database_detection_after_access_is_removed():
    data = get_mock_cloud_data()
    data["security_groups"][0]["inbound_rules"][0]["source"] = "REMOVED"
    graph = build_cloud_topology(data)

    result = detect_public_database_path(graph)

    assert result[0]["status"] == "SAFE"
    assert result[0]["severity"] == "NONE"
    assert result[0]["path"] == []


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


def test_safety_check_reports_missing_fields():
    safety_result = validate_remediation({
        "action": "REVOKE_PUBLIC_ACCESS",
        "target": "sg-001",
    })

    assert safety_result["approved"] is False
    assert safety_result["reason"] == "Missing required field: source"


def test_generated_remediation_code_is_valid():
    code = generate_remediation_code("sg-001", "0.0.0.0/0")

    is_valid, message = validate_remediation_code(code)

    assert is_valid is True
    assert message == "AST validation successful"


def test_ast_validation_rejects_invalid_python():
    is_valid, message = validate_remediation_code("def broken(:")

    assert is_valid is False
    assert message.startswith("Invalid Python code:")


def test_ast_validation_requires_remediate_function():
    is_valid, message = validate_remediation_code("def unrelated():\n    pass")

    assert is_valid is False
    assert message == "remediate() function not found"


def test_mock_remediation_revokes_public_access():
    data = get_mock_cloud_data()

    result = apply_mock_remediation(data, "sg-001")

    assert result["status"] == "REMEDIATED"
    assert data["security_groups"][0]["inbound_rules"][0]["source"] == "REMOVED"


def test_mock_remediation_reports_unknown_security_group():
    data = get_mock_cloud_data()

    result = apply_mock_remediation(data, "sg-missing")

    assert result == {
        "status": "FAILED",
        "security_group": "sg-missing",
        "action": "SECURITY_GROUP_NOT_FOUND",
    }


def test_drift_report_contains_project_metadata(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    report_path = save_drift_report([{"status": "SAFE"}])

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["project"] == "AeroDrift"
    assert report["report_type"] == "Cloud Drift Detection"
    assert report["results"] == [{"status": "SAFE"}]


def test_audit_report_contains_verification_result(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    report_path = save_remediation_audit(
        {
            "database": "db-001",
            "status": "DRIFT_DETECTED",
            "severity": "CRITICAL",
            "issue": "Public path",
            "path": ["internet", "db-001"],
        },
        {
            "action": "REVOKE_PUBLIC_ACCESS",
            "target": "sg-001",
            "source": "0.0.0.0/0",
            "status": "REMEDIATION_READY",
        },
        {"status": "REMEDIATED", "action": "PUBLIC_ACCESS_REVOKED"},
        {"status": "SAFE", "path": []},
    )

    report = json.loads((tmp_path / report_path).read_text(encoding="utf-8"))
    assert report["database"] == "db-001"
    assert report["execution"]["status"] == "REMEDIATED"
    assert report["verification"]["status"] == "SAFE"