import json
from pathlib import Path


def save_drift_report(results):
    """
    Save drift detection results as a JSON report.
    """

    report_directory = Path("reports")
    report_directory.mkdir(exist_ok=True)

    report_file = report_directory / "drift_report.json"

    report_data = {
        "project": "AeroDrift",
        "report_type": "Cloud Drift Detection",
        "results": results
    }

    with open(report_file, "w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4)

    return report_file