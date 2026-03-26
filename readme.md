# Study Snap Quest👽

교과서 사진을 찍으면 단어 몬스터가 소환됩니다. 발음으로 처치하세요!

## 주요 기능
- 교과서 사진 업로드 → Azure OCR로 텍스트 추출
- Azure OpenAI가 핵심 영단어 자동 선별 + 난이도 분류
- Azure TTS로 원어민 발음 재생
- 마이크로 따라 말하면 Azure 발음 평가 API로 점수 산출
- 발음 점수 = 몬스터 공격력 (RPG 게임 방식)
- 실시간 리더보드

## 기술 스택
- Azure Document Intelligence (OCR)
- Azure OpenAI (GPT-4o)
- Azure Speech Service (TTS + STT + Pronunciation Assessment)
- Gradio + Python

## 실행 방법

1. 패키지 설치
pip install -r requirements.txt

2. .env 파일 생성 후 키 입력
VISION_ENDPOINT=https://...
VISION_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=...
SPEECH_KEY=...
SPEECH_REGION=...

3. 실행
python app.py
