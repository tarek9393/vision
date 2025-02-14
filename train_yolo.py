"""Script för att träna YOLO-modellen på etikettdata"""

import os
import cv2
import yaml
from ultralytics import YOLO
from pathlib import Path

def create_dataset_structure():
    """Skapar mappar för dataset"""
    dataset_path = Path("dataset")
    (dataset_path / "images" / "train").mkdir(parents=True, exist_ok=True)
    (dataset_path / "images" / "val").mkdir(parents=True, exist_ok=True)
    (dataset_path / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (dataset_path / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
def create_data_yaml():
    """Skapar data.yaml för träning"""
    data = {
        'path': './dataset',
        'train': 'images/train',
        'val': 'images/val',
        'names': {
            0: 'label',
            1: 'barcode',
            2: 'text'
        }
    }
    
    with open('dataset/data.yaml', 'w') as f:
        yaml.dump(data, f)
        
def prepare_training():
    """Förbereder för träning"""
    print("Förbereder träningsdata...")
    create_dataset_structure()
    create_data_yaml()
    
    # Här skulle du lägga till din kod för att:
    # 1. Samla in bilder på etiketter
    # 2. Annotera bilderna (markera etiketter, streckkoder, text)
    # 3. Konvertera annoteringar till YOLO-format
    # 4. Dela upp i tränings- och valideringsset
    
def train_model():
    """Tränar YOLO-modellen"""
    print("Startar träning...")
    
    # Ladda en förtränad modell
    model = YOLO('yolov8n.pt')
    
    # Träna modellen
    results = model.train(
        data='dataset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        name='label_detection',
        patience=20,
        save=True,
        device='cpu'  # Ändra till 'cuda' om GPU finns
    )
    
    print("Träning slutförd!")
    print(f"Bästa modell sparad som: {results.best}")
    
def main():
    """Huvudfunktion"""
    prepare_training()
    train_model()
    
if __name__ == "__main__":
    main()
