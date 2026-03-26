# Study Snap Quest

> **발음으로 몬스터를 처치하는 영어 단어 학습 RPG**

교과서나 필기 사진을 찍으면 AI가 핵심 영단어를 추출하고, 그 단어들이 몬스터로 변신합니다.
단어를 올바르게 발음할수록 강한 공격이 되어 몬스터를 쓰러뜨릴 수 있습니다!

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **이미지 OCR** | 교과서·필기 사진을 업로드하면 Azure Document Intelligence가 텍스트를 추출 |
| **텍스트 입력** | 직접 텍스트를 붙여넣어 단어 학습 가능 |
| **AI 키워드 추출** | Azure OpenAI가 본문에서 중요 영단어 5~10개를 자동 선별, 난이도 분류 |
| **던전 RPG 게임** | 추출된 단어가 몬스터로 소환 — 발음 공격으로 HP를 0으로 만들면 처치! |
| **발음 평가** | Azure Speech의 발음 평가 기능으로 정확도·유창성·완성도를 100점 만점으로 채점 |
| **TTS 모범 발음** | 원어민(en-US Jenny Neural) 발음을 먼저 들어볼 수 있음 |
| **리더보드** | 처치한 몬스터 수를 기준으로 상위 10명의 기록을 저장 |

---

## 게임 플로우

```
1. 플레이어 이름 입력
2. 이미지 업로드 또는 텍스트 붙여넣기
3. AI가 영단어 5~10개 추출 → 몬스터 소환
4. [발음 듣기] 버튼으로 원어민 발음 청취
5. 마이크로 단어 발음 → 녹음 종료 시 자동 공격
6. 발음 점수에 따라 데미지 적용
7. 모든 몬스터 처치 시 던전 클리어 & 기록 저장
```

---

## 전투 시스템

### 몬스터 등급

| 레벨 | 이름 | HP | 단어 난이도 |
|------|------|----|------------|
| Lv.1 | 슬라임 | 100 | 쉬움 (easy) |
| Lv.2 | 고블린 | 150 | 보통 (medium) |
| Lv.3 | 오크 | 200 | 어려움 (hard) |

### 발음 점수 → 데미지

| 점수 범위 | 결과 | 데미지 |
|-----------|------|--------|
| 90점 이상 | 치명타! | 최대 HP × 60% |
| 70 ~ 89점 | 공격 성공 | 최대 HP × 35% |
| 70점 미만 | 빗나감 | 0 |

### 발음 평가 항목

- **정확도 (Accuracy)** — 음소(phoneme) 단위의 발음 정확성
- **유창성 (Fluency)** — 자연스러운 발화 흐름
- **완성도 (Completeness)** — 단어 전체를 빠짐없이 발음했는지
- **종합 (Overall)** — 위 항목을 종합한 최종 점수

---

## 기술 스택

| 역할 | 서비스 / 라이브러리 |
|------|-------------------|
| UI 프레임워크 | [Gradio](https://gradio.app/) |
| OCR | Azure Document Intelligence (`prebuilt-read`) |
| 키워드 추출 | Azure OpenAI (GPT-4o) |
| TTS | Azure Cognitive Services Speech — `en-US-JennyNeural` |
| 발음 평가 | Azure Cognitive Services Speech — Pronunciation Assessment |
| 공개 URL 터널링 | pyngrok |

---

### 시연
![Start](docs/dashboard_01_start.png)
![Battel](docs/dashboard_02_battle.png)
![Text_input](docs/dashboard_03_text_input.png)
![Goblin](docs/dashboard_04_goblin.png)
![Damage](docs/dashboard_05_damage.png)
![Leaderboard](docs/dashboard_06_leaderboard.png)

🎬 **[대시보드 시연 영상 보기](https://youtu.be/MbYR-KvhHWA)**

---

## 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/jimena1lee/miniproject-study-snap-quest.git
cd miniproject-study-snap-quest
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 만들고, 각 Azure 리소스 정보를 입력합니다.

```bash
cp .env.example .env
```

```env
# Azure Document Intelligence
VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
VISION_KEY=your_key_here

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Azure Speech
SPEECH_KEY=your_key_here
SPEECH_REGION=eastus
```

### 4. 앱 실행

```bash
python app.py
```

실행 후 터미널에 출력되는 **ngrok 공개 URL**로 접속하면 브라우저에서 바로 사용할 수 있습니다.

---

## 프로젝트 구조

```
miniproject-study-snap-quest/
├── app.py              # Gradio UI 및 이벤트 핸들러
├── game.py             # Monster / GameState 데이터 클래스
├── ocr.py              # Azure Document Intelligence OCR
├── openai_helper.py    # Azure OpenAI 키워드 추출
├── speech.py           # Azure Speech TTS & 발음 평가
├── leaderboard.py      # 점수 저장 및 리더보드 렌더링
├── requirements.txt    # Python 의존성
└── .env.example        # 환경 변수 템플릿
```

---

## Azure 리소스 준비

| 리소스 | 필요 이유 |
|--------|----------|
| **Azure Document Intelligence** | 이미지에서 텍스트 추출 (OCR) |
| **Azure OpenAI** | 본문에서 영단어 추출 및 난이도 분류 |
| **Azure Cognitive Services Speech** | 원어민 TTS 생성 및 발음 점수 계산 |

> 모든 서비스는 Azure Portal에서 생성 후 키와 엔드포인트를 `.env`에 입력하면 됩니다.

---

## 필요 조건

Python 3.10 이상
Azure 계정 (Document Intelligence, Speech Service)
OpenAI API 키
