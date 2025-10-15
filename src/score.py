import os
import json
import joblib
import traceback
import pandas as pd
from features import transform_features_single
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

model = None
logger = logging.getLogger(__name__)
if os.getenv('AML_APP_INSIGHTS_KEY'):
    logger.addHandler(AzureLogHandler(connection_string=f'InstrumentationKey={os.getenv("AML_APP_INSIGHTS_KEY")}'))
logger.setLevel(logging.INFO)

def init():
    """Called once at container startup in managed endpoints.
    Loads the model from the AZUREML_MODEL_DIR environment variable that Azure
    sets when mounting registered models.
    """
    global model
    model_dir = os.getenv("AZUREML_MODEL_DIR", None)
    print(f"AZUREML_MODEL_DIR: {model_dir}")
    try:
        if model_dir is None:
            raise RuntimeError("AZUREML_MODEL_DIR environment variable is not set.")
        # List files for debugging
        try:
            print("Model directory contents:", os.listdir(model_dir))
            for root, dirs, files in os.walk(model_dir):
                print(root, "->", files)
        except Exception as e:
            print("Could not list model dir contents:", e)

        model_path = os.path.join(model_dir, "model.joblib")
        print(f"Trying to load model from: {model_path}")
        model = joblib.load(model_path)
        print("Model loaded successfully.")
    except Exception as e:
        print("Failed to load model:", str(e))
        traceback.print_exc()
        # Re-raise to let Azure show failure in logs
        raise


def run(raw_request):
    """Called for each HTTP request. raw_request is JSON string or bytes.

    Expected input: {"features": {"col1": val1, "col2": val2, ...}}
    Returns: JSON string
    """
    try:
        logger.info(f"Raw request: {raw_request}")
        if isinstance(raw_request, (bytes, bytearray)):
            raw_request = raw_request.decode("utf-8")
        data = json.loads(raw_request)
        features = data.get("features")
        if features is None:
            return json.dumps({"error": "Missing 'features' key"})

        # Attempt to load optional scaler located in the code bundle (if you ship it)
        scaler = None
        scaler_path = os.path.join("data", "features", "scaler.joblib")
        try:
            if os.path.exists(scaler_path):
                scaler = joblib.load(scaler_path)
                print(f"Loaded scaler from {scaler_path}")
        except Exception as se:
            print("Failed to load scaler (continuing without it):", se)

        # Build single-row DataFrame using shared logic
        df = transform_features_single(features, scaler=scaler)

        # Align to model feature order if available
        if model is not None and hasattr(model, "feature_names_in_"):
            cols = list(model.feature_names_in_)
            df = df.reindex(columns=cols, fill_value=0)
        
        # Predict
        proba = float(model.predict_proba(df)[0, 1]) if hasattr(model, "predict_proba") else float(model.predict(df)[0])
        result = {"pred_proba": float(proba)}
        logger.info(f"Prediction result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in run(): {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}
