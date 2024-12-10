from flask import Flask, render_template, request, Response, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import time
import json
from datetime import datetime
import cv2
import numpy as np

from camera_utils import DetectionCamera
from model_utils import load_model
from upload_utils import process_upload, allowed_file

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'runs/detect'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}

# Create required directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Initialize model and camera
model = load_model()
camera = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the uploaded file
        results = process_upload(filepath, model)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_webcam')
def start_webcam():
    global camera
    if camera is None:
        try:
            camera = DetectionCamera(model)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'status': 'already running'})

@app.route('/stop_webcam')
def stop_webcam():
    global camera
    if camera:
        camera.release()
        camera = None
    return jsonify({'status': 'success'})

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            if camera:
                frame = camera.get_frame()
                if frame is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(0.033)  # ~30 FPS

    if not camera:
        return "Camera not initialized", 500

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/api/coordinates')
def get_coordinates():
    try:
        log_file = os.path.join('logs', 'pothole_coordinates.json')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                coordinates = json.load(f)
            return jsonify(coordinates)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)