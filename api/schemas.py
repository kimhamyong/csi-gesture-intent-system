from pydantic import BaseModel
from typing import List

class CsiSequenceRequest(BaseModel):
    sequence: List[List[str]]  # 복소수 문자열 리스트 (T, 64)

class PredictResponse(BaseModel):
    gesture: str
    confidence: float