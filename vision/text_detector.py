"""Text detection using YOLO and OCR"""

import cv2
import numpy as np
import logging
from ultralytics import YOLO
import pytesseract
from pathlib import Path

logger = logging.getLogger(__name__)

class TextDetector:
    """Detekterar och läser text från bilder"""
    
    def __init__(self):
        """Initiera textdetektorn"""
        try:
            # Konfigurera Tesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self.tesseract_config = r'--oem 3 --psm 6 -l swe+eng'  # Använd svenska och engelska
            
            # Ladda YOLO-modellen för textdetektering
            model_path = Path(__file__).parent.parent.parent / "models" / "text_detection.pt"
            if not model_path.exists():
                model_path = "yolov8n.pt"
                logger.warning(f"Ingen specialtränad modell hittades, använder {model_path}")
            
            self.model = YOLO(str(model_path))
            logger.info(f"Laddade YOLO-modell: {model_path}")
            
            # Debug-läge
            self.debug_mode = False
            
        except Exception as e:
            logger.error(f"Fel vid initiering av TextDetector: {e}")
            raise
            
    def toggle_debug_mode(self, enabled=True):
        """Aktivera/inaktivera debug-läge"""
        self.debug_mode = enabled
        
    def enhance_image(self, image):
        """Förbättra bildkvaliteten för bättre OCR"""
        try:
            # Konvertera till gråskala
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Adaptiv histogramutjämning för bättre kontrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Brusreducering med bilateral filter
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # Skärpa bilden
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            if self.debug_mode:
                debug_path = Path("debug_images")
                debug_path.mkdir(exist_ok=True)
                cv2.imwrite(str(debug_path / "1_gray.png"), gray)
                cv2.imwrite(str(debug_path / "2_enhanced.png"), enhanced)
                cv2.imwrite(str(debug_path / "3_denoised.png"), denoised)
                cv2.imwrite(str(debug_path / "4_sharpened.png"), sharpened)
            
            return sharpened
            
        except Exception as e:
            logger.error(f"Fel vid bildförbättring: {e}")
            return image
            
    def detect_text_regions(self, image):
        """Detektera textregioner i bilden med YOLO"""
        try:
            # Förbättra bilden först
            enhanced_image = self.enhance_image(image)
            
            # Kör YOLO-detektering
            results = self.model(enhanced_image, conf=0.4)
            
            # Extrahera och filtrera bounding boxes
            boxes = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    class_id = box.cls[0].item()
                    
                    # Beräkna area och proportioner
                    width = x2 - x1
                    height = y2 - y1
                    area = width * height
                    aspect_ratio = width / height if height > 0 else 0
                    
                    # Filtrera bort orimliga detekteringar
                    if (area > 100 and  # Minsta area
                        aspect_ratio > 0.1 and  # Inte för smal
                        aspect_ratio < 10 and  # Inte för bred
                        confidence > 0.4):  # Tillräckligt säker
                        
                        boxes.append({
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'confidence': confidence,
                            'class_id': class_id
                        })
            
            if self.debug_mode:
                logger.debug(f"Hittade {len(boxes)} textregioner")
            
            return boxes
            
        except Exception as e:
            logger.error(f"Fel vid textdetektering: {e}")
            return []
            
    def get_text_orientation(self, image):
        """Avgör textens orientering"""
        try:
            # Kör OCR med orientation och script detection
            osd = pytesseract.image_to_osd(image)
            angle = int(osd.split('\nRotate: ')[1].split('\n')[0])
            return angle
        except:
            return 0
            
    def rotate_image(self, image, angle):
        """Rotera bilden till rätt orientering"""
        if angle == 0:
            return image
            
        try:
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            
            # Skapa rotationsmatris
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Utför rotation
            rotated = cv2.warpAffine(image, matrix, (width, height),
                                   flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REPLICATE)
            
            return rotated
        except Exception as e:
            logger.error(f"Fel vid bildrotering: {e}")
            return image
            
    def extract_text(self, image, boxes):
        """Extrahera text från detekterade regioner"""
        try:
            texts = []
            enhanced_image = self.enhance_image(image)
            
            for box in boxes:
                x1, y1, x2, y2 = box['bbox']
                
                # Lägg till padding runt regionen
                padding = 5
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(image.shape[1], x2 + padding)
                y2 = min(image.shape[0], y2 + padding)
                
                # Extrahera region
                region = enhanced_image[y1:y2, x1:x2]
                if region.size == 0:
                    continue
                    
                # Kontrollera orientering och rotera vid behov
                angle = self.get_text_orientation(region)
                if angle != 0:
                    region = self.rotate_image(region, angle)
                
                # OCR på regionen
                text = pytesseract.image_to_string(
                    region,
                    config=self.tesseract_config
                ).strip()
                
                # Filtrera och rensa texten
                if text and len(text) > 1:  # Ignorera enstaka tecken
                    # Ta bort oönskade tecken
                    text = ''.join(c for c in text if c.isalnum() or c.isspace())
                    # Ta bort extra mellanslag
                    text = ' '.join(text.split())
                    
                    if text:  # Om det fortfarande finns text efter rensning
                        texts.append({
                            'text': text,
                            'bbox': box['bbox'],
                            'confidence': box['confidence'],
                            'angle': angle
                        })
                        
            if self.debug_mode:
                logger.debug(f"Extraherade text från {len(texts)} regioner")
                
            return texts
            
        except Exception as e:
            logger.error(f"Fel vid textextraktion: {e}")
            return []
            
    def detect_and_read(self, image):
        """Detektera och läs all text i bilden"""
        try:
            # Detektera textregioner
            boxes = self.detect_text_regions(image)
            
            # Extrahera text från regionerna
            texts = self.extract_text(image, boxes)
            
            # Sortera texterna baserat på y-position (uppifrån och ner)
            texts.sort(key=lambda x: x['bbox'][1])
            
            # Sammanfoga all text med radbrytningar mellan regioner
            full_text = '\n'.join(t['text'] for t in texts)
            
            return {
                'full_text': full_text,
                'regions': texts
            }
            
        except Exception as e:
            logger.error(f"Fel vid text detection och läsning: {e}")
            return {
                'full_text': '',
                'regions': []
            }
