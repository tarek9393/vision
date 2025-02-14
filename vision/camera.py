import cv2
import logging
import numpy as np
from typing import Optional, Tuple

class Camera:
    def __init__(self, camera_id: int = 0):
        """Initierar kameran
        
        Args:
            camera_id: ID för kameran att använda
        """
        self.logger = logging.getLogger(__name__)
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.frame_size = (1280, 720)
        self.brightness = 100
        self.contrast = 100
        self.auto_exposure = True
        
    def start(self) -> bool:
        """Startar kameran
        
        Returns:
            bool: True om kameran startades, False annars
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.logger.error(f"Kunde inte öppna kamera {self.camera_id}")
                return False
                
            # Sätt kamerainställningar
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1 if self.auto_exposure else 0)
            
            self.is_running = True
            self.logger.info("Kamera startad")
            return True
            
        except Exception as e:
            self.logger.error(f"Fel vid start av kamera: {str(e)}")
            return False
            
    def stop(self):
        """Stoppar kameran"""
        if self.cap is not None:
            self.cap.release()
            self.is_running = False
            self.logger.info("Kamera stoppad")
            
    def get_frame(self) -> Optional[np.ndarray]:
        """Hämtar en bild från kameran
        
        Returns:
            numpy.ndarray eller None: BGR-bild om lyckad, annars None
        """
        if not self.is_running:
            return None
            
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning("Kunde inte läsa bild från kamera")
                return None
                
            # Förbättra bildkvalitet
            frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Fel vid bildhämtning: {str(e)}")
            return None
            
    def set_frame_size(self, width: int, height: int):
        """Sätter bildstorleken
        
        Args:
            width: Bildbredd i pixlar
            height: Bildhöjd i pixlar
        """
        self.frame_size = (width, height)
        if self.is_running:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
    def set_brightness(self, value: int):
        """Sätter ljusstyrka (0-100)"""
        self.brightness = max(0, min(100, value))
        if self.is_running:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            
    def set_contrast(self, value: int):
        """Sätter kontrast (0-100)"""
        self.contrast = max(0, min(100, value))
        if self.is_running:
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            
    def set_auto_exposure(self, auto: bool):
        """Aktiverar/inaktiverar automatisk exponering"""
        self.auto_exposure = auto
        if self.is_running:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1 if auto else 0)
            
    def __del__(self):
        """Städar upp när objektet tas bort"""
        self.stop()
