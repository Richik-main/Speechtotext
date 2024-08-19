let recordButton = document.getElementById("recordButton");
let stopButton = document.getElementById("stopButton");
let audioPreview = document.getElementById("audioPreview");
let submitButton = document.getElementById("submitButton");
let audioDataInput = document.getElementById("audioData");
let transcribeButton = document.getElementById("transcribeButton");
let sentimentResult = document.getElementById("sentimentResult");

let recorder;
let audioContext;
let gumStream;

recordButton.addEventListener("click", function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioContext = new AudioContext();
            gumStream = stream;

            const input = audioContext.createMediaStreamSource(stream);
            recorder = new Recorder(input, { numChannels: 1 });
            recorder.record();

            stopButton.disabled = false;
            recordButton.disabled = true;
        });
});

stopButton.addEventListener("click", function() {
    recorder.stop();

    // Stop the audio stream
    gumStream.getAudioTracks()[0].stop();

    // Create WAV download link
    recorder.exportWAV(function(blob) {
        const audioUrl = URL.createObjectURL(blob);
        audioPreview.src = audioUrl;

        // Enable the submit button
        submitButton.disabled = false;

        // Optional: Convert Blob to Base64 if you want to use it elsewhere in your form
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            audioDataInput.value = reader.result;
        };

        // Handle form submission
        document.getElementById("uploadForm").addEventListener("submit", function(event) {
            event.preventDefault();

            // Create a new FormData object
            const formData = new FormData();
            formData.append("audio_data", blob, "recording.wav");

            // Send the POST request
            fetch("/upload_audio", {
                method: "POST",
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                console.log(data);

                // Show a success message on the page
                const uploadNotification = document.getElementById("uploadNotification");
                uploadNotification.style.display = "block";
                uploadNotification.innerHTML = "Recording uploaded successfully.";
        
                // Enable the transcribe button after a successful upload
                transcribeButton.disabled = false;
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while uploading the recording.");
            });
        });
    });

    stopButton.disabled = true;
    recordButton.disabled = false;
});
transcribeButton.addEventListener("click", function() {
    fetch("/transcribe", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcribed_text) {
            // Display the transcribed text in the transcriptionResult div
            transcriptionResult.innerHTML = `<p>${data.transcribed_text}</p>`;
            
            // Enable the sentiment analysis button
            analyzeButton.disabled = false;  
        } else {
            // Display the error message in red color
            transcriptionResult.innerHTML = `<p style="color: red;">Transcription failed: ${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        // Display a generic error message
        transcriptionResult.innerHTML = `<p style="color: red;">An error occurred while transcribing the recording.</p>`;
    });
});

analyzeButton.addEventListener("click", function() {
    fetch("/analyze_sentiment", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.sentiment) {
            sentimentResult.innerHTML = `<p>Sentiment: ${data.sentiment}, Score: ${data.score.toFixed(2)}</p>`;
        } else {
            sentimentResult.innerHTML = `<p style="color: red;">Sentiment analysis failed: ${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        sentimentResult.innerHTML = `<p style="color: red;">An error occurred while analyzing the sentiment.</p>`;
    });
});
// Enable the transcribe button after upload
submitButton.addEventListener("click", function() {
    transcribeButton.disabled = false;
});
