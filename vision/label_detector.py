import cv2
import numpy as np
import pytesseract
import logging
from ultralytics import YOLO
from typing import Optional, Tuple, List, Dict
import os

class LabelDetector:
    def __init__(self):
        """Initierar etikettdetektorn"""
        self.logger = logging.getLogger(__name__)
        
        # Ladda YOLO-modellen
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "yolov8n.pt")
            self.model = YOLO(model_path)
            self.logger.info("YOLO-modell laddad")
        except Exception as e:
            self.logger.error(f"Kunde inte ladda YOLO-modell: {str(e)}")
            self.model = None
            
        # Konfigurera Tesseract
        try:
            pytesseract.get_tesseract_version()
            self.logger.info("Tesseract initierad")
        except Exception as e:
            self.logger.error(f"Kunde inte initiera Tesseract: {str(e)}")
            
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Förbehandlar bilden för bättre OCR
        
        Args:
            image: BGR-bild
            
        Returns:
            Förbehandlad bild
        """
        # Konvertera till gråskala
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Brusreducering
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Kantdetektering
        edges = cv2.Canny(denoised, 100, 200)
        
        # Morfologiska operationer för att förbättra text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Binarisering med Otsu's metod
        _, binary = cv2.threshold(dilated, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
        
    def detect_labels(self, image: np.ndarray) -> List[Dict]:
        """Detekterar etiketter i bilden med YOLO
        
        Args:
            image: BGR-bild
            
        Returns:
            Lista med detekterade etiketter och deras positioner
        """
        if self.model is None:
            self.logger.error("Ingen YOLO-modell tillgänglig")
            return []
            
        try:
            results = self.model(image, conf=0.25)[0]
            detections = []
            
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                detection = {
                    'bbox': (int(x1), int(y1), int(x2), int(y2)),
                    'confidence': score,
                    'class': results.names[int(class_id)]
                }
                detections.append(detection)
                
            return detections
            
        except Exception as e:
            self.logger.error(f"Fel vid etikettdetektering: {str(e)}")
            return []
            
    def extract_text(self, image: np.ndarray, bbox: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Extraherar text från bilden med OCR
        
        Args:
            image: BGR-bild
            bbox: Begränsningsruta (x1, y1, x2, y2) eller None för hela bilden
            
        Returns:
            Extraherad text
        """
        try:
            # Klipp ut region of interest om bbox anges
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                roi = image[y1:y2, x1:x2]
            else:
                roi = image
                
            # Förbehandla bilden
            processed = self.preprocess_image(roi)
            
            # Utför OCR
            text = pytesseract.image_to_string(processed, lang='swe+eng')
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Fel vid textextraktion: {str(e)}")
            return ""
            
    def validate_label(self, image: np.ndarray, reference_text: str) -> Tuple[bool, float]:
        """Validerar en etikett mot referenstext
        
        Args:
            image: BGR-bild av etiketten
            reference_text: Text att validera mot
            
        Returns:
            (bool, float): Validering OK/NOK och matchningspoäng
        """
        try:
            # Detektera etiketter
            detections = self.detect_labels(image)
            if not detections:
                return False, 0.0
                
            # Använd den mest sannolika detektionen
            best_detection = max(detections, key=lambda x: x['confidence'])
            
            # Extrahera text från detektionen
            detected_text = self.extract_text(image, best_detection['bbox'])
            
            # Beräkna matchningspoäng
            score = self._calculate_similarity(detected_text, reference_text)
            
            # Validera mot tröskelvärde
            threshold = 0.8  # Kan justeras efter behov
            is_valid = score >= threshold
            
            return is_valid, score
            
        except Exception as e:
            self.logger.error(f"Fel vid validering: {str(e)}")
            return False, 0.0
            
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Beräknar likhet mellan två texter
        
        Args:
            text1: Första texten
            text2: Andra texten
            
        Returns:
            Likhetspoäng mellan 0 och 1
        """
        # Implementera lämplig likhetsberäkning här
        # Till exempel Levenshtein-avstånd eller annan metrik
        return 0.0  # Placeholder
