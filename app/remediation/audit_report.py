import json
from datetime import datetime
from pathlib import Path


def save_remediation_audit(
    drift_result,
    remediation,
    remediation_result,
    verification_result
):
    """
    Save the complete remediation process as an audit report.
    """

    audit_data = {
        "timestamp": datetime.now().isoformat(),

        "database": drift_result["database"],

        "drift": {
            "status": drift_result["status"],
            "severity": drift_result["severity"],
            "issue": drift_result["issue"],
            "risky_path": drift_result["path"]
        },

        "remediation": {
            "action": remediation["action"],
            "target": remediation.get("target"),
            "source": remediation.get("source"),
            "status": remediation["status"]
        },

        "execution": {
            "status": remediation_result["status"],
            "action": remediation_result["action"]
        },

        "verification": {
            "status": verification_result["status"],
            "risky_path": verification_result.get("path")
        }
    }

    reports_directory = Path("reports")
    reports_directory.mkdir(exist_ok=True)

    report_path = reports_directory / "remediation_audit.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(audit_data, file, indent=4)

    return str(report_path)