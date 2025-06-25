from deepface import DeepFace
import tempfile
import shutil
from fastapi import UploadFile
import os

def detect_emotion_from_image(image_path: str):
    from deepface import DeepFace
    print("[DEBUG] DeepFace running on:", image_path)

    analysis = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
    emotion = analysis[0]['dominant_emotion']
    return emotion
 