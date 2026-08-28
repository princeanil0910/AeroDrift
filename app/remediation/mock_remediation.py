def apply_mock_remediation(cloud_data, security_group_id):
    """
    Simulate revoking public access from a security group.
    """

    for security_group in cloud_data["security_groups"]:

        if security_group["id"] == security_group_id:

            for rule in security_group["inbound_rules"]:

                if rule["source"] == "0.0.0.0/0":
                    rule["source"] = "REMOVED"

            return {
                "status": "REMEDIATED",
                "security_group": security_group_id,
                "action": "PUBLIC_ACCESS_REVOKED"
            }

    return {
        "status": "FAILED",
        "security_group": security_group_id,
        "action": "SECURITY_GROUP_NOT_FOUND"
    }