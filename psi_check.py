import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_psi(reference: pd.Series, current: pd.Series, bins: int=5) -> float:
    breakpoints = np.linspace(0, 100, bins+1)
    ref_percentiles = np.percentile(reference, breakpoints)
    ref_percentiles[0] = -np.inf
    ref_percentiles[-1] = np.inf

    ref_counts, _ = np.histogram(reference, bins=ref_percentiles)
    cur_counts, _ = np.histogram(current, bins=ref_percentiles)

    ref_pct = ref_counts / len(reference)
    cur_pct = cur_counts / len(current)

    ref_pct = np.where(ref_pct == 0, 0.0001, ref_pct)
    cur_pct = np.where(cur_pct == 0, 0.0001, cur_pct)

    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct/ref_pct))
    return psi


if __name__ == "__main__":
    reference_data = pd.read_csv("data/Customer-Churn.csv")
    current_data = reference_data.sample(frac=0.3, random_state=99).copy()
    current_data["tenure"] = current_data["tenure"] * 1.5

    numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
    reference_data["TotalCharges"] = pd.to_numeric(reference_data["TotalCharges"], errors="coerce").fillna(0)
    current_data["TotalCharges"] = pd.to_numeric(current_data["TotalCharges"], errors="coerce").fillna(0)
    PSI_THRESHOLD = 0.2
    drift_detected = False

    for feature in numeric_features:
        psi = calculate_psi(reference_data[feature], current_data[feature])
        status = "DRIFT" if psi > PSI_THRESHOLD else "OK"
        if psi > PSI_THRESHOLD:
            drift_detected = True
        logger.info(f"{feature}: PSI= {psi:.4f} [{status}]")

    if drift_detected:
        logger.warning("Drift detected - Re-training pipeline should be triggered")
    else:
        logger.info("No Significant drifts -- Model is Stable.")