# AeroDrift

AeroDrift project workspace.

## Structure

```text
AeroDrift/
├── app/
│   ├── ingestion/
│   ├── graph/
│   ├── detection/
│   ├── remediation/
│   ├── dashboard/
│   └── database/
├── data/
├── reports/
├── tests/
├── main.py
└── requirements.txt
```

## Run

Create and activate a virtual environment, then install the dependencies:

```powershell
	python -m venv venv
	.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the mock cloud drift analysis:

```powershell
python main.py
```

Run the tests:

```powershell
python -m pytest
```

The run writes the topology visualization and JSON audit reports to `reports/`.
