import pandas as pd
from feast import FeatureStore
from psi_check import calculate_psi
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

store = FeatureStore(repo_path="../feast/Feast-Project/feature_repo")

reference_data = pd.read_csv("data/Customer-Churn.csv")
reference_data["TotalCharges"] = pd.to_numeric(reference_data["TotalCharges"], errors="coerce").fillna(0)

sample_customer_ids = reference_data["customerID"].sample(200, random_state=42).tolist() if "customerID" in reference_data.columns else []

entity_rows = [{"customerID": cid} for cid in sample_customer_ids]

online_features = store.get_online_features(
    features = [
        "churn_features:tenure",
        "churn_features:MonthlyCharges",
        "churn_features:TotalCharges",
    ],
    entity_rows = entity_rows
).to_df()


logger.info(f"Pulled {len(online_features)} records from online store")

PSI_THRESHOLD = 0.2
for feature in ["tenure", "MonthlyCharges", "TotalCharges"]:
    psi = calculate_psi(reference_data[feature], online_features[feature].dropna())
    status = "DRIFT" if psi > PSI_THRESHOLD else "OK"
    logger.info(f"{feature}: PSI={psi:.4f} [{status}]")