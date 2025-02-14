import cv2
import numpy as np
from pyzbar import pyzbar
import logging
from typing import Tuple, Optional

class BarcodeReader:
    """Hanterar streckkodsläsning från bilder"""
    
    def __init__(self):
        """Initierar streckkodsläsaren"""
        self.logger = logging.getLogger(__name__)
        
    def preprocess_barcode(self, image: np.ndarray) -> np.ndarray:
        """Förbehandlar bilden för bättre streckkodsläsning"""
        # Konvertera till gråskala
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Brusreducering
        denoised = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptiv thresholding
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Morfologisk operation för att förbättra streckkoden
        kernel = np.ones((3,3), np.uint8)
        morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return morphed
        
    def detect_barcode(self, image: np.ndarray) -> Tuple[bool, str, float]:
        """Detekterar streckkod i bilden"""
        try:
            # Förbehandla bilden
            processed = self.preprocess_barcode(image)
            
            # Sök efter streckkoder
            barcodes = pyzbar.decode(processed)
            
            if barcodes:
                # Ta den första streckkoden som hittas
                barcode = barcodes[0]
                
                # Beräkna kvalitet baserat på streckkodens area
                quality = min(100.0, (barcode.rect.width * barcode.rect.height) / 1000)
                
                return True, barcode.data.decode('utf-8'), quality
                
            return False, "", 0.0
            
        except Exception as e:
            self.logger.error(f"Fel vid streckkodsläsning: {str(e)}")
            return False, "", 0.0
            
    def get_barcode_regions(self, image: np.ndarray) -> list:
        """Hittar regioner med streckkoder i bilden"""
        try:
            # Förbehandla bilden
            processed = self.preprocess_barcode(image)
            
            # Hitta streckkoder
            barcodes = pyzbar.decode(processed)
            
            regions = []
            for barcode in barcodes:
                # Få streckkodens position
                rect = barcode.rect
                polygon = barcode.polygon
                
                regions.append({
                    'type': barcode.type,
                    'data': barcode.data.decode('utf-8'),
                    'rect': (rect.left, rect.top, rect.width, rect.height),
                    'polygon': polygon
                })
                
            return regions
            
        except Exception as e:
            self.logger.error(f"Fel vid identifiering av streckkodsregioner: {str(e)}")
            return []
            
    def draw_barcode_regions(self, image: np.ndarray, regions: list) -> np.ndarray:
        """Ritar ut streckkodsregioner på bilden"""
        annotated = image.copy()
        
        for region in regions:
            # Rita polygon runt streckkoden
            points = np.array(region['polygon'], np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.polylines(annotated, [points], True, (0, 255, 0), 2)
            
            # Visa streckkodsdata
            x, y = region['rect'][0], region['rect'][1]
            cv2.putText(
                annotated,
                f"{region['type']}: {region['data']}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
            
        return annotated
