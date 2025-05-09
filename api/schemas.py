from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class GesturePredictionRequest(BaseModel):
    device_id: str = Field(..., example="bedroom_01")
    timestamp: datetime = Field(..., example="2025-05-09T10:00:00")
    gesture: str = Field(..., example="hand_up")
    prev_action: str = Field(..., example="still")
    csi: List[float] = Field(..., min_items=30, max_items=30)
