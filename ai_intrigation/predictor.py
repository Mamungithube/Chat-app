import joblib
import os

# Paths to saved model and encoder
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "pipeline_lr.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "one_hot_encoder.joblib")

# Load the model and encoder
model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

def make_prediction(features):
    """
    features: List of values [68, "White", "Married", ...]
    Returns: predicted class (e.g., 0 or 1)
    """
    try:
        # Reshape the input for a single row
        encoded_features = encoder.transform([features])
        prediction = model.predict(encoded_features)
        return prediction[0]
    except Exception as e:
        return f"Error during prediction: {str(e)}"



# import joblib
# import os

# # Load model pipeline
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "pipeline_lg.joblib")
# model = joblib.load(MODEL_PATH)

# def make_prediction(features):
#     """
#     features: List of values [68, "White", "Married", ...]
#     """
#     prediction = model.predict([features]) 
#     return prediction[0]

 