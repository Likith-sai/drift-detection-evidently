# drift-detection-evidently

Lightweight examples demonstrating simple data-drift checks using PSI
and an Evidently data-drift report. The project uses a sample
Customer-Churn dataset (in `data/Customer-Churn.csv`) to show how to:

- compute Population Stability Index (PSI) between reference and
	current distributions (`psi_check.py`)
- pull online features from a Feast online store and compute PSI
	(`feast_drift_check.py`) — requires a configured Feast feature repo
- generate an Evidently HTML drift report (`generate_drift_report.py`)

Files and functionality
- `psi_check.py`: Implements `calculate_psi(reference, current, bins=5)`
	which computes the Population Stability Index using percentile-based
	bins. Includes a `__main__` demo that samples the local CSV and
	simulates drift for basic testing and logging.
- `feast_drift_check.py`: Samples customer IDs from
	`data/Customer-Churn.csv`, fetches `tenure`, `MonthlyCharges`, and
	`TotalCharges` from a Feast online store (repo path is
	`../feast/Feast-Project/feature_repo`) and computes PSI per feature
	using `calculate_psi` from `psi_check.py`. Logs PSI and a simple
	`DRIFT`/`OK` status against a threshold (`PSI_THRESHOLD = 0.2`).
- `generate_drift_report.py`: Uses Evidently's `DataDriftPreset` to
	compare reference and simulated current data, and saves an HTML
	report to `drift_report.html`.
- `drift_report.html`: Output HTML produced by
	`generate_drift_report.py` (if generated).
- `data/Customer-Churn.csv`: Reference dataset used by the examples.

Quickstart
1. Create and activate a Python environment (recommended).

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install required packages:

```bash
pip install pandas numpy feast evidently
```

3. Run the PSI demo (local example):

```bash
python psi_check.py
```

4. Generate an Evidently HTML drift report:

```bash
python generate_drift_report.py
# opens drift_report.html in the project root
```

5. Run the Feast online-store check (requires Feast repo & online store):

```bash
python feast_drift_check.py
```

Notes / Pre-requisites
- The `feast_drift_check.py` script expects a configured Feast feature
	repository at `../feast/Feast-Project/feature_repo` and an operational
	Feast online store. Adjust `repo_path` in the script if your repo is
	elsewhere.
- `psi_check.py` uses a smoothing floor (0.0001) when a bin count is
	zero; this helps avoid division-by-zero but can over-penalize a
	single empty bin for small sample sizes.

## Limitations & Lessons Learned

Initial drift checks with a 50-sample batch from Feast's online store
showed TotalCharges PSI=0.8253 (flagged as DRIFT), while tenure and
MonthlyCharges showed normal PSI values from the same 50 customers.

Root cause: one of the 10 percentile bins received 0/50 samples by
random chance. PSI's smoothing floor (0.0001) over-penalizes empty
bins when sample size is small relative to bin count — a single empty
bin contributed 0.69 of the total 0.8253 PSI.

Fix: increased sample size from 50 to 200. All features then showed
PSI < 0.03 (no drift), confirming the original alert was a statistical
artifact, not real drift.

Production implication: drift monitoring batch windows must be sized
relative to the number of bins used. A daily batch of 50 predictions
with 10 bins would produce frequent false-positive drift alerts.
Recommended: minimum ~20 samples per bin (200+ samples for 10 bins).