// ---------- Global Variables ----------
let pdfText = ''; // Holds the full text content of the uploaded PDF

// ---------- PDF Upload ----------
async function uploadPDF() {
    const fileInput = document.getElementById('pdfInput');
    const uploadStatus = document.getElementById('uploadStatus');
    
    if (fileInput.files.length === 0) {
        uploadStatus.innerText = 'Please select a PDF file first.';
        uploadStatus.style.color = '#cf6679'; // Red for errors
        return;
    }

    uploadStatus.innerText = 'Uploading and processing PDF...';
    uploadStatus.style.color = '#bb86fc'; // Purple for processing

    const formData = new FormData();
    formData.append('pdf', fileInput.files[0]);

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();

        if (res.ok) {
            pdfText = data.content; // Store PDF text
            uploadStatus.innerText = '✅ PDF uploaded successfully!';
            uploadStatus.style.color = '#03dac6'; // Green for success
            document.getElementById('querySection').style.display = 'block';
        } else {
            throw new Error(data.detail || 'Failed to upload PDF.');
        }
    } catch (error) {
        console.error('Upload Error:', error);
        uploadStatus.innerText = `Error: ${error.message}`;
        uploadStatus.style.color = '#cf6679';
    }
}

// ---------- Speech-to-Text ----------
const micBtn = document.getElementById("micBtn");
const queryInput = document.getElementById("query");

let recognition;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => micBtn.classList.add("active");
    recognition.onend = () => micBtn.classList.remove("active");

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        queryInput.value = transcript;
    };
} else {
    micBtn.disabled = true;
    micBtn.title = "Speech Recognition not supported in this browser";
}

micBtn.addEventListener("click", () => {
    if (recognition) recognition.start();
});

// ---------- Ask AI / Generate Quiz ----------
async function askAI(mode) {
    const query = queryInput.value.trim();
    const responseElement = document.getElementById('response');
    const responseSection = document.getElementById('responseSection');

    if (mode === 'explain' && !query) {
        alert('Please enter a question in the text box.');
        return;
    }
    if (!pdfText) {
        alert('Please upload a PDF first.');
        return;
    }

    responseSection.style.display = 'block';
    responseElement.innerText = 'AI is thinking...';

    try {
        const res = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, pdfText, mode })
        });

        const data = await res.json();

        if (res.ok) {
            responseElement.innerText = data.response;
        } else {
            throw new Error(data.detail || 'An error occurred.');
        }
    } catch (error) {
        console.error('AI Error:', error);
        responseElement.innerText = `Error: ${error.message}`;
    }
}
