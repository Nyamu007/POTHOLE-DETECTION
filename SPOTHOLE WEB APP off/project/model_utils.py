import torch
import os

def load_model(model_path='model.tensors'):
    """Load and initialize the detection model."""
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model using TorchScript
        model = torch.jit.load(model_path)
        model.eval()
        
        return model
    
    except Exception as e:
        print(f"Error loading model: {e}")
        return None