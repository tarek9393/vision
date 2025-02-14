"""Objektdetektering och streckkodsläsning för Label Vision System"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from ultralytics import YOLO
from pyzbar import pyzbar
from datetime import datetime

logger = logging.getLogger(__name__)

class ObjectDetector:
    """Hanterar objektdetektering och streckkodsläsning"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initiera objektdetektorn"""
        self.model = None
        self.last_error = None
        self.confidence_threshold = 0.5
        
        if model_path:
            self.load_model(model_path)
            
    def load_model(self, model_path: str) -> bool:
        """Ladda YOLO-modell"""
        try:
            self.model = YOLO(model_path)
            logger.info(f"Loaded YOLO model from {model_path}")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error loading YOLO model: {str(e)}")
            return False
            
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """Detektera objekt i bild med YOLO"""
        try:
            if self.model is None:
                return []
                
            # Kör inferens
            results = self.model(image)[0]
            detections = []
            
            # Bearbeta resultat
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                
                if score > self.confidence_threshold:
                    detection = {
                        'box': (int(x1), int(y1), int(x2), int(y2)),
                        'confidence': score,
                        'class': results.names[int(class_id)]
                    }
                    detections.append(detection)
                    
            return detections
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error detecting objects: {str(e)}")
            return []
            
    def read_barcodes(self, image: np.ndarray) -> List[Dict]:
        """Läs streckkoder och QR-koder"""
        try:
            # Konvertera till gråskala
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Läs streckkoder
            barcodes = pyzbar.decode(gray)
            results = []
            
            for barcode in barcodes:
                # Extrahera information
                (x, y, w, h) = barcode.rect
                barcode_type = barcode.type
                barcode_data = barcode.data.decode("utf-8")
                
                result = {
                    'box': (x, y, x + w, y + h),
                    'type': barcode_type,
                    'data': barcode_data,
                    'points': barcode.polygon
                }
                results.append(result)
                
            return results
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading barcodes: {str(e)}")
            return []
            
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Rita ut detekterade objekt"""
        try:
            output = image.copy()
            
            for det in detections:
                if 'box' in det:
                    x1, y1, x2, y2 = det['box']
                    
                    # Rita rektangel
                    cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Lägg till text
                    text = ""
                    if 'class' in det:
                        text = f"{det['class']} {det['confidence']:.2f}"
                    elif 'type' in det:
                        text = f"{det['type']}: {det['data']}"
                        
                    cv2.putText(
                        output,
                        text,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )
                    
                    # Rita ut punkter för streckkoder
                    if 'points' in det:
                        points = np.array(det['points'])
                        cv2.polylines(
                            output,
                            [points],
                            True,
                            (0, 0, 255),
                            2
                        )
                        
            return output
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error drawing detections: {str(e)}")
            return image
            
    def save_detection(self, image: np.ndarray, detection: Dict, save_dir: str) -> Optional[str]:
        """Spara detekterad region"""
        try:
            if 'box' not in detection:
                return None
                
            # Extrahera region
            x1, y1, x2, y2 = detection['box']
            roi = image[y1:y2, x1:x2]
            
            # Skapa filnamn
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            det_type = detection.get('class', detection.get('type', 'unknown'))
            filename = f"{save_dir}/detection_{det_type}_{timestamp}.jpg"
            
            # Spara bild
            cv2.imwrite(filename, roi)
            logger.info(f"Saved detection to {filename}")
            
            return filename
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error saving detection: {str(e)}")
            return None
            
    def set_confidence_threshold(self, threshold: float):
        """Sätt tröskelvärde för konfidens"""
        try:
            self.confidence_threshold = max(0.0, min(1.0, threshold))
            logger.info(f"Set confidence threshold to {self.confidence_threshold}")
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error setting confidence threshold: {str(e)}")
            
    def get_model_info(self) -> Dict:
        """Hämta information om modellen"""
        try:
            if self.model is None:
                return {
                    'loaded': False,
                    'error': self.last_error
                }
                
            return {
                'loaded': True,
                'type': type(self.model).__name__,
                'confidence_threshold': self.confidence_threshold
            }
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error getting model info: {str(e)}")
            return {
                'loaded': False,
                'error': str(e)
            }
