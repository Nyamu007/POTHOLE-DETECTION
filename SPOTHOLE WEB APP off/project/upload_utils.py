import cv2
import torch
import numpy as np
from datetime import datetime
import os

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_image(image_path, model):
    """Process an image file with the detection model."""
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read image file")
    
    # Preprocess image
    img = cv2.resize(image, (640, 640))
    img = img.astype(np.float32) / 255.0
    img = torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0)
    
    # Run inference
    with torch.no_grad():
        predictions = model(img)
    
    if isinstance(predictions, (list, tuple)):
        predictions = predictions[0]
    
    # Process detections
    detections = []
    for pred in predictions:
        if len(pred) >= 6 and float(pred[4]) > 0.25:  # confidence threshold
            x1, y1, x2, y2 = map(int, pred[:4])
            confidence = float(pred[4])
            
            detections.append({
                'bbox': [x1, y1, x2, y2],
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            })
            
            # Draw on image
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            label = f'Pothole: {confidence:.2f}'
            cv2.putText(image, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Save processed image
    output_path = os.path.join('runs/detect', os.path.basename(image_path))
    cv2.imwrite(output_path, image)
    
    return {
        'detections': detections,
        'output_path': output_path
    }

def process_video(video_path, model):
    """Process a video file with the detection model."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Prepare output video
    output_path = os.path.join('runs/detect', os.path.basename(video_path))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    detections = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 5th frame for performance
        if frame_count % 5 == 0:
            # Preprocess frame
            img = cv2.resize(frame, (640, 640))
            img = img.astype(np.float32) / 255.0
            img = torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0)
            
            # Run inference
            with torch.no_grad():
                predictions = model(img)
            
            if isinstance(predictions, (list, tuple)):
                predictions = predictions[0]
            
            # Process detections
            frame_detections = []
            for pred in predictions:
                if len(pred) >= 6 and float(pred[4]) > 0.25:
                    x1, y1, x2, y2 = map(int, pred[:4])
                    confidence = float(pred[4])
                    
                    frame_detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'frame': frame_count,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Draw on frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    label = f'Pothole: {confidence:.2f}'
                    cv2.putText(frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            detections.extend(frame_detections)
        
        out.write(frame)
        frame_count += 1
    
    cap.release()
    out.release()
    
    return {
        'detections': detections,
        'output_path': output_path
    }

def process_upload(file_path, model):
    """Process uploaded file based on its type."""
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return process_image(file_path, model)
    elif file_path.lower().endswith('.mp4'):
        return process_video(file_path, model)
    else:
        raise ValueError("Unsupported file type")