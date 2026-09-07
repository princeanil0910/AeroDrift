from app.ingestion.mock_data import get_mock_cloud_data
from app.graph.topology import build_cloud_topology
from app.graph.visualize import visualize_topology
from app.detection.drift_detector import detect_public_database_path
from app.detection.report import save_drift_report

from app.remediation.remediation_engine import generate_remediation
from app.remediation.ast_remediation import (
    generate_remediation_code,
    validate_remediation_code
)
from app.remediation.mock_remediation import apply_mock_remediation
from app.remediation.audit_report import save_remediation_audit
from app.remediation.safety_check import validate_remediation


def main():

    # =================================================
    # STEP 1: Load Cloud Resource Data
    # =================================================

    cloud_data = get_mock_cloud_data()

    print()
    print("AeroDrift Cloud Resources")
    print("=" * 35)

    print(f"VPCs: {len(cloud_data['vpcs'])}")
    print(f"Subnets: {len(cloud_data['subnets'])}")
    print(f"EC2 Instances: {len(cloud_data['ec2_instances'])}")
    print(f"Security Groups: {len(cloud_data['security_groups'])}")
    print(f"Databases: {len(cloud_data['databases'])}")


    # =================================================
    # STEP 2: Build Cloud Topology
    # =================================================

    graph = build_cloud_topology(cloud_data)


    # =================================================
    # STEP 3: Visualize Cloud Topology
    # =================================================

    visualize_topology(graph)


    # =================================================
    # STEP 4: Detect Security Drift
    # =================================================

    results = detect_public_database_path(graph)

    print()
    print("AeroDrift Security Analysis")
    print("=" * 35)


    # =================================================
    # STEP 5: Display Drift Results
    # =================================================

    for result in results:

        print()
        print(f"Database: {result['database']}")
        print(f"Status: {result['status']}")
        print(f"Severity: {result['severity']}")
        print(f"Issue: {result['issue']}")

        if result["path"]:
            print("Risky Path:")
            print(" -> ".join(result["path"]))


    # =================================================
    # STEP 6: Save Drift Report
    # =================================================

    report_file = save_drift_report(results)

    print()
    print(f"JSON report saved to: {report_file}")


    # =================================================
    # STEP 7: Generate Remediation
    # =================================================

    remediation_records = []

    print()
    print("Remediation Plan")
    print("=" * 35)

    for result in results:

        # Keep original drift result for audit
        drift_result = result

        # Generate remediation plan
        remediation = generate_remediation(result)

        print()
        print(f"Action: {remediation['action']}")
        print(f"Target: {remediation.get('target')}")
        print(f"Source: {remediation.get('source')}")
        print(f"Status: {remediation['status']}")

        if remediation["action"] == "NO_ACTION":
            remediation_records.append(
                (
                    drift_result,
                    remediation,
                    {
                        "status": "SKIPPED",
                        "action": "NO_ACTION"
                    }
                )
            )
            continue


        # =================================================
        # STEP 8: Generate Remediation Code
        # =================================================

        generated_code = generate_remediation_code(
            remediation["target"],
            remediation["source"]
        )

        print()
        print("Generated Remediation Code")
        print("-" * 35)

        print(generated_code)


        # =================================================
        # STEP 9: AST Validation
        # =================================================

        is_valid, message = validate_remediation_code(
            generated_code
        )

        print()
        print(f"AST Validation: {message}")


        # =================================================
        # STEP 10: Safety Check
        # =================================================

        safety_result = validate_remediation(
            remediation
        )

        print()
        print("Remediation Safety Check")
        print("-" * 35)

        print(
            f"Approved: {safety_result['approved']}"
        )

        print(
            f"Reason: {safety_result['reason']}"
        )


        # =================================================
        # STEP 11: Apply Mock Remediation
        # =================================================

        if is_valid and safety_result["approved"]:

            remediation_result = apply_mock_remediation(
                cloud_data,
                remediation["target"]
            )

        else:

            remediation_result = {
                "status": "BLOCKED",
                "action": "REMEDIATION_NOT_EXECUTED"
            }


        print()
        print("Mock Remediation Result")
        print("-" * 35)

        print(
            f"Status: {remediation_result['status']}"
        )

        print(
            f"Action: {remediation_result['action']}"
        )


        # Store information for audit report
        remediation_records.append(
            (
                drift_result,
                remediation,
                remediation_result
            )
        )


    # =================================================
    # STEP 12: Rebuild Topology After Remediation
    # =================================================

    updated_graph = build_cloud_topology(
        cloud_data
    )


    # =================================================
    # STEP 13: Verify Remediation
    # =================================================

    updated_results = detect_public_database_path(
        updated_graph
    )

    print()
    print("Post-Remediation Verification")
    print("=" * 35)


    # =================================================
    # STEP 14: Display Verification Result
    # =================================================

    for index, result in enumerate(updated_results):

        print()
        print(f"Database: {result['database']}")
        print(f"Status: {result['status']}")

        if result["path"]:

            print("Remaining Risky Path:")
            print(" -> ".join(result["path"]))

        else:

            print("No Internet path detected.")


        # =================================================
        # STEP 15: Save Audit Report
        # =================================================

        if index < len(remediation_records):

            (
                drift_result,
                remediation,
                remediation_result
            ) = remediation_records[index]

            audit_file = save_remediation_audit(
                drift_result,
                remediation,
                remediation_result,
                result
            )

            print()
            print(
                f"Audit report saved to: {audit_file}"
            )


# =====================================================
# PROGRAM ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()