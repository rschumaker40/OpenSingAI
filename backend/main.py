import torch
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles  # Import this earlier
from pydantic import BaseModel
from scipy.io.wavfile import write
from scipy.signal import butter, filtfilt
from transformers import VitsModel, AutoProcessor
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin (change this for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Mount file-serving endpoint AFTER initializing FastAPI
app.mount("/files", StaticFiles(directory="."), name="files")

# Load a better singing AI model
model_id = "rinna/japanese-stable-vits"  # More natural-sounding model
model = VitsModel.from_pretrained(model_id)
processor = AutoProcessor.from_pretrained(model_id)

class LyricsRequest(BaseModel):
    text: str
    
def apply_lowpass_filter(audio, cutoff=3000, fs=44100, order=6):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, audio)

@app.post("/generate")
def generate_vocals(request: LyricsRequest):
    try:
        print(f"Received lyrics: {request.text}")

        inputs = processor(text=request.text, return_tensors="pt")
        print("Processed input text.")

        with torch.no_grad():
            audio_array = model(**inputs).waveform.cpu().numpy().squeeze()

        print("Generated raw audio waveform.")

        # Normalize audio
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            audio_array = audio_array / max_val

        # Apply smoothing (low-pass filter to reduce harshness)
        audio_array = apply_lowpass_filter(audio_array)

        # Convert to 16-bit PCM range
        audio_array = (audio_array * 32767).astype(np.int16)

        # Save as WAV
        filename = "generated_song.wav"
        write(filename, 44100, audio_array)  # Increased sample rate
        print(f"Saved audio file: {filename}")

        return {"audio_url": f"http://127.0.0.1:8000/files/{filename}"}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating vocals: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "OpenSingAI Backend Running"}
