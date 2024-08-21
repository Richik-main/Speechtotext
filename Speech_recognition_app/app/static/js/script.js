// Get DOM elements
const recordButton = document.getElementById("recordButton");
const stopButton = document.getElementById("stopButton");
const audioPreview = document.getElementById("audioPreview");
const submitButton = document.getElementById("submitButton");
const audioDataInput = document.getElementById("audioData");
const transcribeButton = document.getElementById("transcribeButton");
const analyzeButton = document.getElementById("analyzeButton");
const translateButton = document.getElementById("translateButton");
const languageSelect = document.getElementById("languageSelect");
const uploadNotification = document.getElementById("uploadNotification");
const transcriptionResult = document.getElementById("transcriptionResult");
const sentimentResult = document.getElementById("sentimentResult");
const translateResult = document.getElementById("translateResult");

let recorder, audioContext, gumStream;

// Helper function to update the UI
function updateUI(element, message, color = "black") {
    element.style.display = "block";
    element.style.color = color;
    element.innerHTML = message;
}

// Helper function to make API requests
async function makeApiRequest(url, method = "POST", body = null) {
    const options = { method };
    if (body) {
        options.body = body;
    }
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
    }
    return response.json();
}

// Start recording
recordButton.addEventListener("click", async () => {
    try {
        gumStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new AudioContext();
        const input = audioContext.createMediaStreamSource(gumStream);
        recorder = new Recorder(input, { numChannels: 1 });
        recorder.record();

        stopButton.disabled = false;
        recordButton.disabled = true;
        updateUI(uploadNotification, "Recording started...", "green");
    } catch (error) {
        console.error("Error starting recording:", error);
        if (error.name === 'NotAllowedError') {
            updateUI(uploadNotification, "Microphone access denied. Please allow access.", "red");
        } else if (error.name === 'NotFoundError') {
            updateUI(uploadNotification, "No microphone found. Please ensure a microphone is connected.", "red");
        } else if (error.name === 'NotReadableError' || error.name === 'AbortError') {
            updateUI(uploadNotification, "Microphone is currently in use by another application.", "red");
        } else {
            updateUI(uploadNotification, "Unable to access microphone. Please try again.", "red");
        }
    }
});


// Stop recording and process audio
stopButton.addEventListener("click", () => {
    recorder.stop();
    gumStream.getAudioTracks()[0].stop();

    recorder.exportWAV(async (blob) => {
        const audioUrl = URL.createObjectURL(blob);
        audioPreview.src = audioUrl;
        submitButton.disabled = false;

        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            audioDataInput.value = reader.result;
        };
    });

    stopButton.disabled = true;
    recordButton.disabled = false;
});

// Handle form submission for audio upload
submitButton.addEventListener("click", async (event) => {
    event.preventDefault();
    try {
        const formData = new FormData();
        const blob = await getBlobFromAudioPreview(audioPreview.src);
        formData.append("audio_data", blob, "recording.wav");

        const data = await makeApiRequest("/upload_audio", "POST", formData);
        console.log(data);
        updateUI(uploadNotification, "Recording uploaded successfully.");
        transcribeButton.disabled = false;
    } catch (error) {
        console.error("Error uploading recording:", error);
        updateUI(uploadNotification, "An error occurred while uploading the recording.", "red");
    }
});

// Transcribe audio
transcribeButton.addEventListener("click", async () => {
    try {
        const data = await makeApiRequest("/transcribe");

        if (data.transcribed_text) {
            updateUI(transcriptionResult, data.transcribed_text);
            analyzeButton.disabled = false;
        } else {
            updateUI(transcriptionResult, `Transcription failed: ${data.error}`, "red");
        }
    } catch (error) {
        console.error("Error transcribing audio:", error);
        updateUI(transcriptionResult, "An error occurred while transcribing the recording.", "red");
    }
});

// Analyze sentiment
analyzeButton.addEventListener("click", async () => {
    try {
        const data = await makeApiRequest("/analyze_sentiment");

        if (data.sentiment) {
            const sentimentMessage = `
                Sentiment: ${data.sentiment}<br>
                Score: ${data.score.toFixed(2)}<br>
                Feeling: ${data.feeling}`;
            updateUI(sentimentResult, sentimentMessage);
            translateButton.disabled = false;
        } else {
            updateUI(sentimentResult, `Sentiment analysis failed: ${data.error}`, "red");
        }
    } catch (error) {
        console.error("Error analyzing sentiment:", error);
        updateUI(sentimentResult, "An error occurred while analyzing the sentiment.", "red");
    }
});

// Translate sentence
translateButton.addEventListener("click", async () => {
    const language = languageSelect.value;

    if (!language) {
        updateUI(translateResult, "Please select a language to translate.", "red");
        return;
    }

    const endpoints = {
        spanish: "/translate_to_spanish",
        french: "/translate_to_french",
        hindi: "/translate_to_hindi"
    };

    try {
        const data = await makeApiRequest(endpoints[language]);

        if (data.translation) {
            updateUI(translateResult, `Translation: ${data.translation}`);
        } else {
            updateUI(translateResult, `Translation failed: ${data.error}`, "red");
        }
    } catch (error) {
        console.error("Error translating sentence:", error);
        updateUI(translateResult, "An error occurred while translating the sentence.", "red");
    }
});

// Convert audio preview URL to a Blob
async function getBlobFromAudioPreview(audioUrl) {
    const response = await fetch(audioUrl);
    return await response.blob();
}
document.getElementById('resetButton').addEventListener('click', function() {
    // Reset form fields
    document.getElementById('uploadForm').reset();

    // Clear audio preview
    document.getElementById('audioPreview').src = '';

    // Clear transcription and sentiment results
    document.getElementById('transcriptionResult').innerHTML = '';
    document.getElementById('sentimentResult').innerHTML = '';
    document.getElementById('translateResult').innerHTML = '';

    // Disable buttons
    document.getElementById('submitButton').disabled = true;
    document.getElementById('transcribeButton').disabled = true;
    document.getElementById('analyzeButton').disabled = true;
    document.getElementById('translateButton').disabled = true;

    // Optionally reset any other states
});