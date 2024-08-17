import sounddevice as sd
import soundfile as sf

# Set recording parameters
fs = 44100  # Sample rate
seconds = 10  # Duration of recording

print("Recording...")

# Record audio
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()  # Wait until recording is finished

print("Finished recording.")

# Save the recorded audio as a WAV file
sf.write("output.wav", myrecording, fs)
