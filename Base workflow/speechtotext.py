import speech_recognition as sr

# Initialize recognizer class (for recognizing the speech)
recognizer = sr.Recognizer()

# Load your audio file
audio_file = "output.wav"

# Convert the .wav file to text
with sr.AudioFile(audio_file) as source:
    # Listen to the audio file
    audio_data = recognizer.record(source)
    # Convert speech to text
    text = recognizer.recognize_google(audio_data)
    print("Text from audio:", text)

with open('transcribed_script.txt','w') as file:
    file.write(text)
print("Text has been saved to transcribed_script.txt")