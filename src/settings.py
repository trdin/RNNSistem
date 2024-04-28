import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow_tracking_username = os.getenv("MLFLOW_TRACKING_USERNAME")
mlflow_tracking_password = os.getenv("MLFLOW_TRACKING_PASSWORD")

# Now you can use these variables in your script
print(f"MLflow Tracking URI: {mlflow_tracking_uri}")
print(f"MLflow Tracking Username: {mlflow_tracking_username}")
print(f"MLflow Tracking Password: {mlflow_tracking_password}")