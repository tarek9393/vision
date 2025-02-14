"""Vision system för etikettinspektion"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import pytesseract
from pyzbar.pyzbar import decode
from ultralytics import YOLO
import os
import logging
from datetime import datetime
from labelvision.camera.camera_manager import CameraManager
from labelvision.utils.test_image_generator import create_test_label

@dataclass
class InspectionResult:
    """Resultat från en inspektion"""
    success: bool = False
    confidence: float = 0.0
    text: str = ""
    barcode: str = ""
    error: str = ""
    objects: List[Dict] = None
    label_type: str = ""
    position: Tuple[int, int, int, int] = (0, 0, 0, 0)

class VisionSystem:
    """Hanterar bildanalys och inspektion"""
    
    def __init__(self, use_test_image: bool = False):
        """Initierar vision-systemet"""
        self.logger = logging.getLogger(__name__)
        self.total_inspections = 0
        self.passed_inspections = 0
        self.use_test_image = use_test_image
        
        # Initiera kamera
        self.camera = CameraManager(use_test_image=use_test_image)
        self.camera.start()
        self.logger.debug("Kamera initierad")
        
        # Försök hitta Tesseract
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            # Testa om Tesseract fungerar
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
        except Exception as e:
            print(f"Varning: Tesseract är inte tillgängligt: {e}")
            print("Installera Tesseract från: https://github.com/UB-Mannheim/tesseract/wiki")
            self.tesseract_available = False
        
        # Försök ladda YOLO-modell
        try:
            model_path = 'runs/detect/label_detection/weights/best.pt'
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
                self.model_available = True
            else:
                print("Varning: YOLO-modell saknas. Använder förtränad modell.")
                self.model = YOLO('yolov8n.pt')  # Använd förtränad modell
                self.model_available = True
        except Exception as e:
            print(f"Varning: Kunde inte ladda YOLO-modell: {e}")
            self.model_available = False
        
        # Bildbehandlingsparametrar
        self.min_confidence = 30.0
        self.blur_kernel = (5, 5)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        
        # Klassnamn för detektioner
        self.class_names = {
            0: 'label',
            1: 'barcode',
            2: 'text'
        }
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Förbättrad förbehandling av bilden för bättre OCR"""
        # Konvertera till gråskala
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Adaptiv thresholding för bättre kontrast
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 21, 11
        )
        
        # Brusreducering
        denoised = cv2.fastNlMeansDenoising(binary)
        
        # Förbättra kontraster
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Kantförbättring
        kernel = np.array([[-1,-1,-1],
                         [-1, 9,-1],
                         [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
        
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """Detekterar objekt i bilden med YOLO"""
        if not self.model_available:
            return []
        
        results = self.model(image)
        detected_objects = []
        
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > 0.5:  # Minimum konfidens
                    x1, y1, x2, y2 = box.xyxy[0]
                    detected_objects.append({
                        'class': cls,
                        'confidence': conf * 100,
                        'box': (int(x1), int(y1), int(x2-x1), int(y2-y1))
                    })
                    
        return detected_objects
        
    def find_label_position(self, image: np.ndarray) -> Tuple[bool, Tuple[int, int, int, int]]:
        """Hittar etikettens position i bilden"""
        # Förbehandla bilden
        processed = self.preprocess_image(image)
        
        # Kantdetektering
        edges = cv2.Canny(processed, 50, 150)
        
        # Hitta konturer
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False, (0, 0, 0, 0)
            
        # Hitta största konturen som kan vara en etikett
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Kontrollera om proportionerna är rimliga för en etikett
        aspect_ratio = w / h
        if 0.5 <= aspect_ratio <= 2.0:  # Rimliga proportioner för en etikett
            return True, (x, y, w, h)
            
        return False, (0, 0, 0, 0)
        
    def detect_text(self, image: np.ndarray) -> str:
        """Förbättrad OCR-funktion med optimerade inställningar"""
        if not self.tesseract_available:
            return ""
            
        # Förbehandla bilden
        processed_image = self.preprocess_image(image)
        
        try:
            # Utför OCR
            text = pytesseract.image_to_string(processed_image, lang='swe+eng')
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR-fel: {str(e)}")
            return ""
            
    def get_camera_frame(self) -> Optional[np.ndarray]:
        """Hämtar en bild från kameran"""
        try:
            frame = self.camera.get_frame()
            if frame is not None:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return None
        except Exception as e:
            self.logger.error(f"Fel vid hämtning av kamerabild: {str(e)}")
            return None
            
    def inspect_image(self, image: np.ndarray) -> InspectionResult:
        """Inspekterar en bild och returnerar resultat"""
        try:
            result = InspectionResult()
            
            # Hitta objekt med YOLO
            result.objects = self.detect_objects(image)
            
            # Hitta etikettens position
            found, position = self.find_label_position(image)
            if not found:
                result.error = "Kunde inte hitta etikett"
                self.update_statistics(False)
                return result
                
            result.position = position
            x, y, w, h = position
            
            # Extrahera etikettområdet
            label_roi = image[y:y+h, x:x+w]
            
            # OCR-analys
            result.text = self.detect_text(label_roi)
            
            # Beräkna OCR-konfidens
            if result.text:
                result.confidence = self.calculate_confidence(result.text)
                
            # Streckkodsavläsning
            barcodes = decode(label_roi)
            if barcodes:
                result.barcode = barcodes[0].data.decode('utf-8')
                barcode_confidence = 100.0
            else:
                barcode_confidence = 0.0
                
            # Beräkna total konfidens
            if result.text and result.barcode:
                result.confidence = (result.confidence + barcode_confidence) / 2
            elif result.text:
                result.confidence = result.confidence
            elif result.barcode:
                result.confidence = barcode_confidence
                
            # Bestäm om inspektionen lyckades
            result.success = bool(result.text or result.barcode) and result.confidence >= self.min_confidence
            
            # Uppdatera statistik
            self.update_statistics(result.success)
            
            return result
            
        except Exception as e:
            result = InspectionResult(
                success=False,
                confidence=0.0,
                error=str(e)
            )
            self.update_statistics(False)
            return result
            
    def update_statistics(self, success: bool):
        """Uppdaterar inspektionsstatistik"""
        self.total_inspections += 1
        if success:
            self.passed_inspections += 1
        else:
            self.failed_inspections += 1
            
    def get_statistics(self) -> Dict:
        """Returnerar inspektionsstatistik"""
        error_rate = (self.failed_inspections / self.total_inspections * 100.0 
                     if self.total_inspections > 0 else 0.0)
                     
        return {
            'total': self.total_inspections,
            'passed': self.passed_inspections,
            'failed': self.failed_inspections,
            'error_rate': error_rate
        }
        
    def annotate_image(self, image: np.ndarray, result: InspectionResult) -> np.ndarray:
        """Markerar detektioner i bilden"""
        annotated = image.copy()
        
        # Rita detekterade objekt
        if result.objects:
            for obj in result.objects:
                x, y, w, h = obj['box']
                conf = obj['confidence']
                cv2.rectangle(annotated, (x, y), (x+w, y+h), (255, 255, 0), 2)
                cv2.putText(annotated, f"Object ({conf:.1f}%)",
                           (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
        # Rita etikettrektangel
        x, y, w, h = result.position
        color = (0, 255, 0) if result.success else (0, 0, 255)
        cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)
        
        # Lägg till text
        if result.text:
            cv2.putText(annotated, result.text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                       
        # Markera streckkod
        if result.barcode:
            cv2.putText(annotated, f"Barcode: {result.barcode}",
                       (x, y+h+25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                       
        return annotated

    def calculate_confidence(self, text):
        """Beräknar konfidensnivå för OCR-resultatet"""
        if not text:
            return 0.0
            
        # Kontrollera textlängd
        if len(text) < 10:
            return 0.2
            
        # Kontrollera om texten innehåller förväntade nyckelord
        keywords = ['Schulstad', 'Vaadelmadonis', 'Donut']
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text.lower())
        
        # Beräkna grundläggande konfidens
        base_confidence = min(0.3 + (keyword_matches * 0.2), 1.0)
        
        # Kontrollera om texten innehåller siffror (t.ex. artikelnummer)
        if any(c.isdigit() for c in text):
            base_confidence += 0.1
            
        return min(base_confidence, 1.0)
