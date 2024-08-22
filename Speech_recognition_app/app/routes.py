from flask import render_template, request, app, jsonify, send_from_directory, redirect, url_for
from app import application
import os
import speech_recognition as sr
from transformers import pipeline
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
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

@application.route('/functionality_image')
def functionality_image():
    return render_template('functionality_image.html')

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

## Work with the image
###########################


# Load the CLIP model and processor once at the start
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

@application.route('/functionality_image', methods=['GET', 'POST'])
def functionality_image_upload():
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Save the file to the upload folder
                file_path = os.path.join(application.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                return render_template('functionality_image.html', filename=file.filename, message="Image uploaded successfully!")
        
        if 'classify' in request.form:
            filename = request.form.get('filename')
            if filename:
                file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
                # Perform image classification
                classification_result = classify_image(file_path)
                return render_template('functionality_image.html', filename=filename, classification_result=classification_result)
    
    return render_template('functionality_image.html')

@application.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve the file from the UPLOAD_FOLDER
    return send_from_directory(application.config['UPLOAD_FOLDER'], filename)

def classify_image(image_path):
    # Load and process the image
    image = Image.open(image_path)

    # Define candidate labels
    labels = ["a cat", "a dog", "a car", "a tree", "a yeti","a cow"]

    # Encode the image and some candidate texts
    inputs = processor(text=labels, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)

    # Get the logits (higher is better) for each text
    logits_per_image = outputs.logits_per_image
    best_match_index = logits_per_image.argmax()  # Get the index of the highest score
    predicted_label = labels[best_match_index]  # Find the corresponding label

    # Return the classification result
    return f"The image is classified as: {predicted_label}"