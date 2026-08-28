def generate_remediation(drift_result):
    """
    Generate a remediation plan for detected cloud drift.
    """

    if drift_result["status"] != "DRIFT_DETECTED":
        return {
            "action": "NO_ACTION",
            "reason": "No drift detected"
        }

    database = drift_result["database"]

    remediation = {
        "database": database,
        "severity": drift_result["severity"],
        "issue": drift_result["issue"],
        "action": "REVOKE_PUBLIC_ACCESS",
        "target": "sg-001",
        "source": "0.0.0.0/0",
        "status": "REMEDIATION_READY"
    }

    return remediation