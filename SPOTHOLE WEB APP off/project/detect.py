import argparse
import sys
import time
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
import os

class PotholeDetector:
    def __init__(self, weights='model.safetensors', imgsz=640, conf_thres=0.25):
        self.weights = weights
        self.imgsz = imgsz
        self.conf_thres = conf_thres
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model()

    def load_model(self):
        model = torch.jit.load(self.weights)
        model.to(self.device)
        model.eval()
        return model

    def process_frame(self, frame):
        # Preprocess frame
        img = cv2.resize(frame, (self.imgsz, self.imgsz))
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = torch.from_numpy(img).to(self.device)
        img = img.float() / 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        pred = self.model(img)
        
        # Process predictions
        if isinstance(pred, (list, tuple)):
            pred = pred[0]
        
        # Draw detections
        for det in pred:
            if len(det) >= 6 and float(det[4]) > self.conf_thres:
                x1, y1, x2, y2 = map(int, det[:4])
                conf = float(det[4])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Pothole: {conf:.2f}', 
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 2)

        return frame

    def run_webcam(self):
        cap = cv2.VideoCapture(0)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = self.process_frame(frame)
            
            cv2.imshow('Pothole Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def run_detection(source=0, weights='model.safetensors'):
    detector = PotholeDetector(weights=weights)
    if source == 0:
        detector.run_webcam()
    return "Detection completed"