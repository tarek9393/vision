"""Träna en YOLO-modell för textdetektering"""

import logging
from pathlib import Path
from ultralytics import YOLO

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_model():
    try:
        # Sökvägar
        data_yaml = Path(r"c:\Users\tarek.ziyad\Downloads\WordsDetector_V1.v1i.yolov11\data.yaml")
        output_dir = Path(__file__).parent / "models"
        output_dir.mkdir(exist_ok=True)
        
        # Validera att data.yaml finns
        if not data_yaml.exists():
            raise FileNotFoundError(f"Kunde inte hitta {data_yaml}")
            
        # Ladda en liten modell för snabbare träning
        model = YOLO('yolov8n.pt')
        
        # Träningskonfiguration
        results = model.train(
            data=str(data_yaml),
            epochs=50,  # Färre epoker för snabbare träning
            imgsz=640,  # Bildstorlek
            batch=16,   # Mindre batch-storlek
            patience=10,  # Early stopping
            device='cpu',  # Använd CPU
            verbose=True,
            project=str(output_dir),
            name='text_detection',
            # Augmentering för bättre generalisering
            flipud=0.0,      # Ingen vertikal flip för text
            fliplr=0.5,      # 50% chans för horisontell flip
            mosaic=0.5,      # 50% chans för mosaic
            mixup=0.0,       # Ingen mixup för text
            degrees=15.0,    # Rotera max 15 grader
            translate=0.2,   # Translatera upp till 20%
            scale=0.5,      # Skala mellan 50-150%
            shear=0.0,      # Ingen shear för text
            perspective=0.0, # Ingen perspektivförändring
            # Optimering
            optimizer='AdamW',  # Använd AdamW optimerare
            lr0=0.001,         # Startlärrate
            lrf=0.01,          # Slutlärrate
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3.0,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            # Regularisering
            box=7.5,  # Box loss gain
            cls=0.5,  # Cls loss gain (lägre eftersom vi bara har en klass)
            dfl=1.5,  # DFL loss gain
        )
        
        # Spara den tränade modellen
        results.save(str(output_dir / 'text_detection.pt'))
        logger.info(f"Träning slutförd. Modell sparad i {output_dir}")
        
    except Exception as e:
        logger.error(f"Ett fel uppstod under träning: {e}")
        raise

if __name__ == "__main__":
    train_model()
