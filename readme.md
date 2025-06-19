# Wi-Fi CSI 기반 머신러닝 제스처 인식 시스템

고령자 맞춤형 스마트홈 환경을 위한 Wi-Fi CSI(Channel State Information) 기반 비접촉 제스처 인식 시스템,  
별도의 착용형 센서 없이 기존 Wi-Fi 인프라를 활용한 실시간 동작 감지 및 분류 기능 제공


- ESP32 기반 UDP 트래픽 송신 (802.11n, 100 packets/sec)
- Raspberry Pi 수신기 및 Nexmon CSI 툴 기반 CSI 수집
- 복소수 CSI → 진폭(amplitude) 변환
- 서브캐리어별 통계 feature(평균, 표준편차, 최댓값, 최솟값) 추출
- 256차원 feature vector 생성 및 정규화 처리
- PyTorch 기반 MLP 분류 모델 입력 및 실시간 예측 수행
- FastAPI 서버를 통한 제스처 라벨 및 신뢰도 반환

## 실험 환경 및 기술 스택

- 실내 환경 구성: 4m × 3m 공간, 송수신 거리 2.5m 고정
- 실험 제스처 구성:
  1. 욕실에서 박수 (bathroom_clap)
  2. 욕실에서 두 팔 들어 올리기 (bathroom_raise)
  3. 침대에서 박수 (bedroom_clap)
  4. 침대에서 두 팔 들어 올리기 (bedroom_raise)
- 제스처당 평균 수집 패킷 수: 약 200개
- 수집된 CSI → GCP 서버 실시간 전송 → 분류 결과 API 반환

### 실험 장비

- 송신기: ESP32 (802.11n 지원)
- 수신기: Raspberry Pi 4B
  - OS: Raspbian GNU/Linux 11 (bullseye)
  - 커널: 5.10.92-v7l+
  - 아키텍처: ARMv7l
  - 무선 칩셋: Broadcom BCM43455c0
- CSI 수집 툴: Nexmon CSI Tool

### 소프트웨어 스택

| 구성 요소       | 사용 기술                         |
|----------------|------------------------------------|
| 데이터 수집     | ESP32, Nexmon CSI Tool            |
| 수신 장치       | Raspberry Pi 4B                   |
| 전처리 및 특징  | Python, NumPy, pandas             |
| 모델 학습       | PyTorch (MLPClassifier)           |
| API 서버        | FastAPI, Uvicorn                  |
| 서버 배포       | Docker, GCP Cloud Run             |

## 전처리 및 모델 학습

### 전처리 과정

- 복소수 CSI → 진폭 변환 (서브캐리어 단위)
- 결측값 및 파싱 오류 항목 → 0 대체 처리
- 서브캐리어별 통계 feature(평균, 표준편차, 최대, 최소) 계산
- 256차원 feature vector 구성
- StandardScaler 기반 정규화 처리

### 모델 구성 및 학습 조건

- 모델 구조: 입력층(256) → 은닉층(64, ReLU) → 출력층
- 손실 함수: CrossEntropyLoss
- 최적화 알고리즘: Adam, 학습률 0.001
- 학습 조건: 50 epoch, batch size 32
- 데이터 분할: 학습:테스트 = 8:2
- 프레임워크: PyTorch

### 성능 평가

- 테스트셋 정확도: 97.5%
- Stratified 5-Fold 교차검증 평균 정확도: 95.9%
- 평가 지표: Precision, Recall, F1-score
- train/val loss 안정적 수렴
- 혼동 행렬 기반 오분류 분석 가능

## API 서버 사용 방법

1. 로컬 실행

```bash
cd api/
pip install -r requirements.txt
uvicorn main:app --reload
```

2. Docker 실행

```bash
docker build -t csi-api .
docker run -p 8000:8000 csi-api
```

3. 예측 요청 예시

```http
POST /predict
Content-Type: application/json

{
  "features": [0.12, 0.34, ..., ]
}
```

3. 응답 예시
```json
{
  "label": "wave_hands_bath",
  "confidence": 0.94
}
```
