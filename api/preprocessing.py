import numpy as np
import pandas as pd
import re
import torch
import joblib
import json
import os
import torch.nn as nn
import math

MODEL_DIR = "model"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# MLP 모델 클래스 정의
class MLPClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.model(x)

# 모델 구성 파라미터 (학습 시와 동일하게 유지)
INPUT_DIM = 256
HIDDEN_DIM = 64
OUTPUT_DIM = 4  # 예: 클래스 수 (동적으로 불러올 경우 아래에서 조정 가능)

# 라벨맵 로딩
with open(os.path.join(MODEL_DIR, "label_map.json")) as f:
    reverse_label_map = json.load(f)
index_to_label = {v: k for k, v in reverse_label_map.items()}
OUTPUT_DIM = len(index_to_label)

# 모델, 스케일러 로딩
model = MLPClassifier(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM).to(device)
model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "model.pth"), map_location=device))
model.eval()

scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

def extract_amplitude_features(df: pd.DataFrame) -> np.ndarray:
    amplitude_matrix = []
    for col in df.columns:
        if re.match(r'^_\d+$', col):
            cleaned = []
            for val in df[col].dropna():
                try:
                    c = complex(str(val).replace("(", "").replace(")", "").replace(" ", "").replace("nan", "0"))
                    cleaned.append(abs(c))
                except Exception:
                    cleaned.append(np.nan)
            amplitude_matrix.append(np.array(cleaned))
    return np.array(amplitude_matrix).T if amplitude_matrix else np.array([])

def generate_feature_vector(sequence: list) -> np.ndarray:
    df = pd.DataFrame(sequence, columns=[f"_{i}" for i in range(64)])
    amp = extract_amplitude_features(df)
    if amp.shape[1] != 64:
        raise ValueError(f"Expected 64 columns, got {amp.shape[1]}")
    return np.concatenate([
        amp.mean(axis=0),
        amp.std(axis=0),
        np.max(amp, axis=0),
        np.min(amp, axis=0)
    ])

def predict_from_sequence(sequence: list) -> dict:
    features = generate_feature_vector(sequence)
    x_scaled = scaler.transform([features])
    x_tensor = torch.tensor(x_scaled, dtype=torch.float32).to(device)
    with torch.no_grad():
        logits = model(x_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        pred = int(np.argmax(probs))
        confidence = float(probs[pred])

    # NaN 방지
    if math.isnan(confidence):
        print("[예측 실패] Confidence is NaN")
        return {
            "gesture": "unknown",
            "confidence": 0.0
        }

    print(f"Gesture: {index_to_label.get(pred, 'unknown')}, Confidence: {confidence:.4f}")

    return {
        "gesture": index_to_label.get(pred, "unknown"),
        "confidence": confidence
    }
