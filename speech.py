import os, uuid, tempfile
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

SPEECH_KEY    = os.environ["SPEECH_KEY"]
SPEECH_REGION = os.environ["SPEECH_REGION"]

def text_to_speech(word: str) -> str:
    """단어를 TTS로 변환해 임시 wav 파일 경로를 반환합니다."""
    config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    config.speech_synthesis_voice_name = "en-US-JennyNeural"

    out_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.wav")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=out_path)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=audio_config
    )
    synthesizer.speak_text_async(word).get()
    return out_path


def assess_pronunciation(audio_path: str, reference_text: str) -> dict:
    """녹음 파일과 정답 단어를 비교해 발음 점수를 반환합니다."""
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "en-US"

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme
    )

    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )
    pronunciation_config.apply_to(recognizer)

    result = recognizer.recognize_once_async().get()
    assessment = speechsdk.PronunciationAssessmentResult(result)

    return {
        "accuracy":    round(assessment.accuracy_score),
        "fluency":     round(assessment.fluency_score),
        "completeness": round(assessment.completeness_score),
        "overall":     round(assessment.pronunciation_score)
    }