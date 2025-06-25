import whisper
import tempfile
from app.services.ai_mood_analysis import analyze_text_mood

# Load Whisper model once
model = whisper.load_model("base")

def detect_mood_from_audio(file):
    # Save audio to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    # Transcribe using Whisper
    result = model.transcribe(tmp_path)
    transcript = result.get("text", "")

    # Analyze transcript for emotion
    mood_result = analyze_text_mood(transcript)

    return {
        "transcript": transcript,
        "emotion": mood_result["emotion"],
        "confidence": mood_result["confidence"],
        "original_label": mood_result["original_label"]
    }
  