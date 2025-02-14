"""Avancerad bildbehandling för Label Vision System"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Hanterar avancerad bildbehandling och analys"""
    
    def __init__(self):
        self.last_error = None
        self.debug_mode = False
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Förbehandla bild för bättre OCR-resultat"""
        try:
            # Konvertera till gråskala
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Brusreducering
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Kantförstärkning
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # Adaptiv tröskling
            binary = cv2.adaptiveThreshold(
                sharpened,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            return binary
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
            
    def detect_edges(self, image: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Detektera kanter och konturer"""
        try:
            # Konvertera till gråskala
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Kantdetektering med Canny
            edges = cv2.Canny(gray, 50, 150)
            
            # Hitta konturer
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Sortera efter area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            return edges, contours
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error detecting edges: {str(e)}")
            return np.zeros_like(image), []
            
    def extract_text(self, image: np.ndarray) -> str:
        """Extrahera text från bild med OCR"""
        try:
            # Förbehandla bild
            preprocessed = self.preprocess_image(image)
            
            # Konvertera till PIL Image
            pil_image = Image.fromarray(preprocessed)
            
            # Utför OCR
            text = pytesseract.image_to_string(
                pil_image,
                lang='eng+swe',
                config='--psm 6'
            )
            
            return text.strip()
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error extracting text: {str(e)}")
            return ""
            
    def detect_barcode(self, image: np.ndarray) -> Optional[str]:
        """Detektera och avkoda streckkod"""
        try:
            # Förbehandla bild
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Brusreducering
            blurred = cv2.GaussianBlur(gray, (9, 9), 0)
            
            # Tröskling
            _, binary = cv2.threshold(
                blurred,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            
            # Hitta och avkoda streckkod med zbar
            # Implementera streckkodssökning här
            
            return None
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error detecting barcode: {str(e)}")
            return None
            
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Förbättra bildkvalitet"""
        try:
            # Justera kontrast och ljusstyrka
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # CLAHE på L-kanalen
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            
            # Kombinera kanaler
            enhanced_lab = cv2.merge((cl,a,b))
            
            # Konvertera tillbaka till BGR
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error enhancing image: {str(e)}")
            return image
            
    def analyze_image_quality(self, image: np.ndarray) -> dict:
        """Analysera bildkvalitet"""
        try:
            metrics = {
                'brightness': np.mean(image),
                'contrast': np.std(image),
                'blur': cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var(),
                'size': image.shape
            }
            
            return metrics
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error analyzing image quality: {str(e)}")
            return {}
            
    def correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """Korrigera perspektiv"""
        try:
            # Hitta kanter och konturer
            edges, contours = self.detect_edges(image)
            
            if not contours:
                return image
                
            # Hitta största konturen
            largest_contour = contours[0]
            
            # Approximera polygon
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            if len(approx) == 4:
                # Sortera hörn
                pts = np.float32(approx.reshape(4, 2))
                rect = np.zeros((4, 2), dtype=np.float32)
                
                s = pts.sum(axis=1)
                rect[0] = pts[np.argmin(s)]  # Övre vänstra
                rect[2] = pts[np.argmax(s)]  # Nedre högra
                
                diff = np.diff(pts, axis=1)
                rect[1] = pts[np.argmin(diff)]  # Övre högra
                rect[3] = pts[np.argmax(diff)]  # Nedre vänstra
                
                # Beräkna ny bredd och höjd
                width = int(max(
                    np.linalg.norm(rect[0] - rect[1]),
                    np.linalg.norm(rect[2] - rect[3])
                ))
                height = int(max(
                    np.linalg.norm(rect[0] - rect[3]),
                    np.linalg.norm(rect[1] - rect[2])
                ))
                
                dst = np.array([
                    [0, 0],
                    [width-1, 0],
                    [width-1, height-1],
                    [0, height-1]
                ], dtype=np.float32)
                
                # Beräkna transformationsmatris
                matrix = cv2.getPerspectiveTransform(rect, dst)
                
                # Applicera transformation
                warped = cv2.warpPerspective(image, matrix, (width, height))
                
                return warped
                
            return image
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error correcting perspective: {str(e)}")
            return image
            
    def debug_visualization(self, image: np.ndarray) -> np.ndarray:
        """Skapa visualisering för felsökning"""
        try:
            if not self.debug_mode:
                return image
                
            # Kopiera original
            debug_image = image.copy()
            
            # Lägg till kanter
            edges, contours = self.detect_edges(image)
            cv2.drawContours(debug_image, contours, -1, (0,255,0), 2)
            
            # Lägg till text från OCR
            text = self.extract_text(image)
            cv2.putText(
                debug_image,
                f"OCR: {text[:30]}...",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                2
            )
            
            # Lägg till kvalitetsmetrik
            metrics = self.analyze_image_quality(image)
            y = 60
            for key, value in metrics.items():
                if isinstance(value, tuple):
                    value_str = f"{key}: {value}"
                else:
                    value_str = f"{key}: {value:.2f}"
                    
                cv2.putText(
                    debug_image,
                    value_str,
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,0,0),
                    1
                )
                y += 20
                
            return debug_image
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error creating debug visualization: {str(e)}")
            return image
