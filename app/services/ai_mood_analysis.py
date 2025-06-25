from transformers import pipeline
import spacy

# Load sentiment model and NLP processor
nlp_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", framework="pt")
spacy_nlp = spacy.load("en_core_web_sm")

def analyze_text_mood(text: str):
    # Clean with SpaCy
    doc = spacy_nlp(text)
    cleaned_text = " ".join([token.lemma_ for token in doc if not token.is_stop])

    # Run BERT sentiment analysis
    result = nlp_pipe(cleaned_text)[0]
    label = result["label"]
    score = result["score"]

    # Map BERT label to emotion
    if label == "POSITIVE":
        emotion = "motivated"
    elif label == "NEGATIVE":
        emotion = "stressed"
    else:
        emotion = "neutral"

    return {
        "emotion": emotion,
        "confidence": round(score, 2),
        "original_label": label 
    } 
