import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Getting the training data
reference_data = pd.read_csv("data/Customer-Churn.csv")

#Copy the training data to a variable
current_data = reference_data.sample(frac=0.3, random_state=99).copy()

#Simulating the drift with 1.5 
current_data["tenure"] = current_data["tenure"] * 1.5

#Generating the report
report = Report(metrics=[DataDriftPreset()])
result = report.run(reference_data=reference_data, current_data=current_data)

#Saving the report
result.save_html("drift_report.html")
logger.info("Drift Report saved to drift_report.html")