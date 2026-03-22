import os
import io
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import your custom modules
from pdf_processor import process_pdf
from rag_engine import generate_response, generate_quiz, generate_mindmap
from tts_stt import text_to_speech, speech_to_text

# Create the 'static' directory if it doesn't exist
os.makedirs("static", exist_ok=True)

app = FastAPI()

# Mount the 'static' directory to serve files like CSS, JS, and audio
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for type-hinting and validating request bodies
class AskRequest(BaseModel):
    query: str
    pdfText: str
    mode: str = 'explain'

class TTSRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serves the main HTML page."""
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    """Handles PDF file uploads, processes the file, and returns its text content."""
    if not pdf or not pdf.filename or not pdf.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    try:
        # process_pdf expects a file-like object, which pdf.file is
        text = process_pdf(pdf.file)
        # Return a snippet of the text for the frontend to store
        return JSONResponse({'message': 'PDF processed successfully', 'content': text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.post("/ask")
async def ask_question(request: AskRequest):
    """Handles user queries and generates responses based on the selected mode."""
    try:
        if request.mode == 'quiz':
            result = generate_quiz(request.pdfText)
        elif request.mode == 'mindmap':
            result = generate_mindmap(request.pdfText)
        else:
            result = generate_response(request.query, request.pdfText)
        return JSONResponse({'response': result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/tts")
async def tts(request: TTSRequest):
    """Converts text to speech and returns the path to the audio file."""
    try:
        file_path = text_to_speech(request.text)
        return JSONResponse({'audio': file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@app.post("/stt")
async def stt(audio: UploadFile = File(...)):
    """Converts speech from an audio file to text."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
    try:
        # Read audio file into a byte stream for processing
        audio_bytes = await audio.read()
        text = speech_to_text(io.BytesIO(audio_bytes))
        return JSONResponse({'text': text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

# To run the app, save your files and use the command in your terminal:
# uvicorn app:app --reload