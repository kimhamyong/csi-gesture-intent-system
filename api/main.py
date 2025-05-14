from fastapi import FastAPI, HTTPException
from schemas import CsiSequenceRequest
from preprocessing import predict_from_sequence

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "OK"}

@app.post("/predict")
def predict_sequence(req: CsiSequenceRequest):
    try:
        result = predict_from_sequence(req.sequence)
        return result
    except Exception as e:
        print(f"[예외 발생] {e}")
        raise HTTPException(status_code=400, detail=str(e))
