from flask import Flask, request, send_file, render_template, jsonify
from flask_cors import CORS
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torch
import scipy.io.wavfile
import io

app = Flask(__name__)
CORS(app)

# Load model using the same code that worked on Colab
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "facebook/musicgen-small"

print(f"Loading {model_id} onto {device}...")
processor = AutoProcessor.from_pretrained(model_id)
model = MusicgenForConditionalGeneration.from_pretrained(model_id).to(device)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutUs.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', 'lo-fi music')
    
    # Get duration from request (default 10s if missing, max 600s)
    try:
        duration_sec = int(data.get('duration', 10))
        if duration_sec > 600:
            duration_sec = 600
        elif duration_sec < 1:
            duration_sec = 10
    except (ValueError, TypeError):
        duration_sec = 10

    # Calculate tokens based on duration
    # MusicGen produces ~50 tokens per second (256 tokens ~= 5 seconds)
    # Formula: seconds * 51.2
    max_tokens = int(duration_sec * 51.2)

    print(f"Generating {duration_sec} seconds ({max_tokens} tokens) for prompt: {prompt}")

    # Colab logic: Tokenize and Generate
    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    
    with torch.no_grad():
        audio_values = model.generate(**inputs, max_new_tokens=max_tokens)

    # Convert to WAV in memory
    sampling_rate = model.config.audio_encoder.sampling_rate
    audio_data = audio_values[0, 0].cpu().numpy()
    
    byte_io = io.BytesIO()
    scipy.io.wavfile.write(byte_io, rate=sampling_rate, data=audio_data)
    byte_io.seek(0)

    return send_file(byte_io, mimetype="audio/wav")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)