from fastapi import FastAPI
from schemas import GesturePredictionRequest
from preprocessing import preprocess_input
from model.loader import load_model
from model.predictor import predict

app = FastAPI()
model = load_model()

@app.post("/predict")
def predict_intent(data: GesturePredictionRequest):
    features = preprocess_input(data)
    intent, confidence = predict(model, features)
    return {
        "predicted_intent": intent,
        "confidence": confidence
    }
