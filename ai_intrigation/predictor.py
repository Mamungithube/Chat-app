# import joblib
# import os

# # Absolute path তৈরি করুন
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

# # Model লোড করুন
# model = joblib.load(MODEL_PATH)

# # Prediction function তৈরি করুন
# def make_prediction(input_data):
#     # Ensure input is in 2D format if required
#     prediction = model.predict([input_data])
#     return prediction[0]


import joblib
import os

# Load model pipeline
MODEL_PATH = os.path.join(os.path.dirname(__file__), "pipeline_lg.joblib")
model = joblib.load(MODEL_PATH)

def make_prediction(features):
    """
    features: List of values [68, "White", "Married", ...]
    """
    prediction = model.predict([features]) 
    return prediction[0]

 