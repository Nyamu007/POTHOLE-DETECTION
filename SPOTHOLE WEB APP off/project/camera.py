import cv2
import numpy as np
import os
import json
from datetime import datetime

class VideoCamera:
    def __init__(self):
        """Initialize webcam capture and detection parameters."""
        self.video = cv2.VideoCapture(0)  # Use webcam (device ID 0)
        if not self.video.isOpened():
            raise ValueError("Could not open webcam")
            
        # Set webcam properties for better quality
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.video.set(cv2.CAP_PROP_FPS, 30)
            
        # Detection parameters
        self.classes = ['pothole']
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        self.frame_count = 0
        
        # Create directories for outputs
        self.output_dir = 'detected_potholes'
        self.log_dir = 'logs'
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize coordinate log
        self.log_file = os.path.join(self.log_dir, 'pothole_coordinates.json')
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def __del__(self):
        """Release video resource on deletion."""
        self.stop()

    def stop(self):
        """Stop the video capture."""
        if self.video and self.video.isOpened():
            self.video.release()

    def get_frame(self, net):
        """Process and return a video frame with pothole detection."""
        try:
            success, frame = self.video.read()
            if not success:
                raise ValueError("Failed to read frame from webcam")

            frame = self.process_frame(frame, net)
            
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()

        except Exception as e:
            print(f"Error in get_frame: {str(e)}")
            return None

    def process_frame(self, frame, net):
        """Process a single frame for pothole detection."""
        try:
            height, width = frame.shape[:2]

            # Create blob from frame
            blob = cv2.dnn.blobFromImage(
                frame, 
                1/255.0, 
                (416, 416), 
                swapRB=True, 
                crop=False
            )
            net.setInput(blob)

            # Get detections
            layer_outputs = net.forward(net.getUnconnectedOutLayersNames())
            
            # Process detections
            return self.process_detections(frame, layer_outputs, height, width)

        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return frame

    def process_detections(self, frame, layer_outputs, height, width):
        """Process YOLO detection outputs and draw results."""
        boxes = []
        confidences = []
        class_ids = []
        detections_count = 0

        # Extract detection information
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.25:  # Confidence threshold
                    # Scale coordinates to frame size
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Calculate corner coordinates
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.2)
        
        if len(indices) > 0:
            detections = []
            for i in indices.flatten():
                try:
                    # Draw detection box
                    x, y, w, h = boxes[i]
                    confidence = confidences[i]
                    color = self.colors[class_ids[i]]

                    # Draw rectangle and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f'Pothole {confidence:.2f}', 
                              (x, y - 10), self.font, 0.6, color, 1)

                    # Calculate center coordinates
                    center_x = x + w//2
                    center_y = y + h//2
                    
                    # Add coordinates to detections
                    detections.append({
                        'timestamp': datetime.now().isoformat(),
                        'center_x': center_x,
                        'center_y': center_y,
                        'confidence': float(confidence),
                        'width': w,
                        'height': h
                    })

                    # Draw center point
                    cv2.circle(frame, (center_x, center_y), 4, color, -1)
                    
                    detections_count += 1

                except Exception as e:
                    print(f"Error drawing detection: {str(e)}")
                    continue
            
            # Log detections
            self.log_detections(detections)

        # Add detection count
        cv2.putText(frame, f'Detections: {detections_count}', 
                   (10, 30), self.font, 1, (255, 255, 255), 2)

        return frame

    def log_detections(self, detections):
        """Log detection coordinates to JSON file."""
        try:
            # Read existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Add new detections
            logs.extend(detections)
            
            # Write updated logs
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Error logging detections: {str(e)}")