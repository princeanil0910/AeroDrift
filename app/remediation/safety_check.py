def validate_remediation(remediation):
    """
    Validate whether a remediation plan is safe to execute.
    """

    required_fields = [
        "action",
        "target",
        "source"
    ]

    for field in required_fields:
        if not remediation.get(field):
            return {
                "approved": False,
                "reason": f"Missing required field: {field}"
            }

    if remediation["action"] != "REVOKE_PUBLIC_ACCESS":
        return {
            "approved": False,
            "reason": "Unknown remediation action"
        }

    if remediation["source"] != "0.0.0.0/0":
        return {
            "approved": False,
            "reason": "Unexpected source rule"
        }

    return {
        "approved": True,
        "reason": "Remediation passed safety checks"
    }