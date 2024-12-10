import cv2
import torch
import numpy as np
from datetime import datetime
import json
import os

class DetectionCamera:
    def __init__(self, model):
        """Initialize the camera with detection model."""
        self.video = cv2.VideoCapture(0)
        if not self.video.isOpened():
            raise ValueError("Could not open webcam")
        
        # Set camera properties
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.video.set(cv2.CAP_PROP_FPS, 30)
        
        self.model = model
        self.detection_threshold = 0.25
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        self.log_file = 'logs/pothole_coordinates.json'

    def __del__(self):
        """Clean up resources."""
        self.release()

    def release(self):
        """Release the video capture resource."""
        if self.video and self.video.isOpened():
            self.video.release()

    def preprocess_frame(self, frame):
        """Preprocess frame for model input."""
        # Resize frame
        frame_resized = cv2.resize(frame, (640, 640))
        
        # Convert to float and normalize
        frame_float = frame_resized.astype(np.float32) / 255.0
        
        # Convert to tensor and add batch dimension
        frame_tensor = torch.from_numpy(frame_float.transpose(2, 0, 1))
        frame_tensor = frame_tensor.unsqueeze(0)
        
        return frame_tensor

    def log_detection(self, detection):
        """Log detection coordinates to JSON file."""
        try:
            # Load existing logs or create new list
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new detection
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'confidence': float(detection['confidence']),
                'bbox': detection['bbox'],
                'center_x': (detection['bbox'][0] + detection['bbox'][2]) // 2,
                'center_y': (detection['bbox'][1] + detection['bbox'][3]) // 2
            })
            
            # Save updated logs
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            print(f"Error logging detection: {e}")

    def get_frame(self):
        """Get frame with detections."""
        success, frame = self.video.read()
        if not success:
            return None

        # Process frame if model is available
        if self.model:
            try:
                # Preprocess frame
                input_tensor = self.preprocess_frame(frame)
                
                # Run inference
                with torch.no_grad():
                    predictions = self.model(input_tensor)
                
                # Process predictions
                if isinstance(predictions, (list, tuple)):
                    predictions = predictions[0]
                
                # Draw detections
                for detection in predictions:
                    if len(detection) >= 6:  # x1, y1, x2, y2, confidence, class
                        confidence = float(detection[4])
                        if confidence > self.detection_threshold:
                            x1, y1, x2, y2 = map(int, detection[:4])
                            
                            # Draw bounding box in red
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            
                            # Add label with white background for better visibility
                            label = f'Pothole: {confidence:.2f}'
                            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                            cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), (255, 255, 255), -1)
                            cv2.putText(frame, label, (x1, y1 - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            
                            # Log detection
                            self.log_detection({
                                'confidence': confidence,
                                'bbox': [x1, y1, x2, y2]
                            })
            
            except Exception as e:
                print(f"Error processing frame: {e}")
        
        # Convert frame to JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()