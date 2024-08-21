from flask import render_template, request,app, jsonify
from app import application
import os
import speech_recognition as sr
from transformers import pipeline



# Initialize recognizer class (for recognizing the speech)
recognizer = sr.Recognizer()

import wave

def is_valid_wav(file_path):
    try:
        with wave.open(file_path, 'rb') as wav_file:
            wav_file.getparams()
        return True
    except wave.Error as e:
        print(f"Wave Error: {e}")
        return False


@application.route('/')
def index():
    print("Index page accessed")
    return render_template('index.html')

@application.route('/functionality')
def functionality():
    return render_template('functionality.html')

@application.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        return 'No audio data provided', 400
    
    audio_file = request.files['audio_data']
    audio_path = os.path.join(application.config['UPLOAD_FOLDER'], 'recording.wav')

    # Save the file directly
    audio_file.save(audio_path)

    # Validate if the file is a proper WAV file
    if not is_valid_wav(audio_path):
        return jsonify({"error": "Uploaded file is not a valid WAV file"}), 400

    # Once the file is validated, convert it to text
    return transcribe_audio(audio_path)


def transcribe_audio(audio_path):
    try:
        # Load the audio file
        with sr.AudioFile(audio_path) as source:
            # Listen to the audio file
            audio_data = recognizer.record(source)
            # Convert speech to text
            text = recognizer.recognize_google(audio_data)
            print("Text from audio:", text)

            # Save the transcribed text to a file
            transcript_path = os.path.join(application.config['UPLOAD_FOLDER'], 'transcribed_script.txt')
            with open(transcript_path, 'w') as file:
                file.write(text)
            print("Text has been saved to transcribed_script.txt")

            # Return the transcribed text as a JSON response
            return jsonify({"transcribed_text": text, "message": "File uploaded and transcribed successfully"}), 200

    except sr.UnknownValueError:
        # Specific exception when speech recognition doesn't understand the audio
        return jsonify({"error": "Google Speech Recognition could not understand the audio"}), 400

    except sr.RequestError as e:
        # Specific exception for API request errors
        return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e), "message": "An error occurred during transcription"}), 500

@application.route('/transcribe', methods=['POST'])
def transcribe():
    audio_path = os.path.join(application.config['UPLOAD_FOLDER'], 'recording.wav')
    if os.path.exists(audio_path):
        return transcribe_audio(audio_path)
    else:
        return jsonify({"error": "No audio file found for transcription"}), 400
    

@application.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    transcript_path = os.path.join(application.config['UPLOAD_FOLDER'], 'transcribed_script.txt')
    
    if not os.path.exists(transcript_path):
        return jsonify({"error": "No transcribed text found. Please transcribe audio first."}), 400
    
    # Load the sentiment-analysis pipeline
    classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
    sentimentana = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
    with open(transcript_path, 'r') as file:
        sentence = file.read()
    
    prompted_sentence = f"The emotion expressed in the following text: '{sentence}' is"

    # Perform sentiment analysis
    result = classifier(sentence)
    result2=sentimentana(prompted_sentence)
    # Mapping from model output labels to sentiment categories
    label_mapping = {
        'LABEL_0': 'Negative',
        'LABEL_1': 'Neutral',
        'LABEL_2': 'Positive'
    }
    
    # Extract the label and score from the output
    predicted_label = result[0]['label']
    predicted_score = result[0]['score']
    category = result2[0]['label']
    # Map the label to its corresponding sentiment
    sentiment = label_mapping.get(predicted_label, "Unknown label")
    print("Result from sentimentana:", category)

    # Return the sentiment result as a JSON response
    return jsonify({
        "sentiment": sentiment, 
        "score": predicted_score, 
        "feeling": category
    }), 200

@application.route('/translate_to_hindi', methods=['POST'])
def translate_to_hindi():
    transcript_path = os.path.join(application.config['UPLOAD_FOLDER'], 'transcribed_script.txt')
    
    if not os.path.exists(transcript_path):
        return jsonify({"error": "No transcribed text found. Please transcribe audio first."}), 400
    
    translator = pipeline("translation_en_to_hi", model="Helsinki-NLP/opus-mt-en-hi")
    with open(transcript_path, 'r') as file:
        sentence = file.read()
    result=translator(sentence)
    trans=result[0]['translation_text']
    print(trans)
    return jsonify({
        "translation": trans
    }), 200


@application.route('/translate_to_spanish', methods=['POST'])
def translate_to_spanish():
    transcript_path = os.path.join(application.config['UPLOAD_FOLDER'], 'transcribed_script.txt')
    
    if not os.path.exists(transcript_path):
        return jsonify({"error": "No transcribed text found. Please transcribe audio first."}), 400
    
    # Use a public model for translation from English to Spanish
    translator = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")
    
    with open(transcript_path, 'r') as file:
        sentence = file.read()
    
    result = translator(sentence)
    trans = result[0]['translation_text']
    
    print(trans)
    return jsonify({
        "translation": trans
    }), 200

@application.route('/translate_to_french', methods=['POST'])
def translate_to_french():
    transcript_path = os.path.join(application.config['UPLOAD_FOLDER'], 'transcribed_script.txt')
    
    if not os.path.exists(transcript_path):
        return jsonify({"error": "No transcribed text found. Please transcribe audio first."}), 400
    
    # Use a public model for translation from English to French
    translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")
    
    with open(transcript_path, 'r') as file:
        sentence = file.read()
    
    result = translator(sentence)
    trans = result[0]['translation_text']
    
    print(trans)
    return jsonify({
        "translation": trans
    }), 200