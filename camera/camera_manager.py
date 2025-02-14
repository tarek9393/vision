"""Hantering av kamera och bildtagning"""

import cv2
import logging
import numpy as np
from typing import Optional, Tuple, Dict
from labelvision.utils.test_image_generator import create_test_label

logger = logging.getLogger(__name__)

class CameraManager:
    """Hanterar kameraoperationer och inställningar"""
    
    def __init__(self, camera_id: int = 0, use_test_image: bool = False):
        self.camera = None
        self.camera_id = camera_id
        self.settings = {
            'exposure': 0,
            'brightness': 50,
            'contrast': 50,
            'saturation': 50
        }
        self.use_test_image = use_test_image
        self.test_image = None
        
        if use_test_image:
            self.test_image = create_test_label(
                text="PRODUKT: Testprodukt XYZ\nArt.nr: 12345-ABC\nBatch: 2024-01-24"
            )
            
    def start(self) -> bool:
        """Startar kameran
        
        Returns:
            True om kameran startades framgångsrikt
        """
        if self.use_test_image:
            return True
            
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            if not self.camera.isOpened():
                logger.error("Kunde inte öppna kameran")
                return False
                
            # Sätt kamerainställningar
            for setting, value in self.settings.items():
                self.set_camera_setting(setting, value)
                
            return True
            
        except Exception as e:
            logger.error(f"Fel vid start av kamera: {str(e)}")
            return False
            
    def stop(self) -> None:
        """Stoppar kameran"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            
    def get_available_cameras(self) -> list:
        """Hitta tillgängliga kameror"""
        available_cameras = []
        for i in range(3):  # Kolla de första 3 kamerorna
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(f"Kamera {i}")
                cap.release()
        return available_cameras
        
    def connect(self, camera_id: int = 0) -> bool:
        """Anslut till kamera"""
        try:
            self.camera_id = camera_id
            self.camera = cv2.VideoCapture(camera_id)
            
            if self.camera.isOpened():
                # Sätt standardinställningar
                self.apply_settings(self.settings)
                logger.info(f"Connected to camera {camera_id}")
                return True
            else:
                logger.error(f"Failed to open camera {camera_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to camera: {str(e)}")
            return False
            
    def disconnect(self):
        """Koppla från kamera"""
        try:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                logger.info("Disconnected from camera")
                
        except Exception as e:
            logger.error(f"Error disconnecting camera: {str(e)}")
            
    def get_frame(self) -> Optional[np.ndarray]:
        """Hämta en bildruta från kameran"""
        try:
            if self.use_test_image:
                return self.test_image.copy()
                
            if self.camera is None or not self.camera.isOpened():
                return None
                
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting frame: {str(e)}")
            return None
            
    def take_picture(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Tar en bild från kameran
        
        Returns:
            Tuple med (framgång, bild)
        """
        if self.use_test_image:
            # Konvertera bilden till RGB för att säkerställa korrekt färgformat
            if self.test_image is not None:
                rgb_image = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2RGB)
                return True, rgb_image
            return False, None
            
        if self.camera is None or not self.camera.isOpened():
            return False, None
            
        success, frame = self.camera.read()
        if success:
            # Konvertera kamerabilden till RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return success, frame

    def apply_settings(self, settings: Dict[str, int]):
        """Applicera kamerainställningar"""
        try:
            if self.camera is None:
                return
                
            # Exponering
            if 'exposure' in settings:
                self.camera.set(cv2.CAP_PROP_EXPOSURE, settings['exposure'])
                
            # Ljusstyrka
            if 'brightness' in settings:
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, settings['brightness'])
                
            # Kontrast
            if 'contrast' in settings:
                self.camera.set(cv2.CAP_PROP_CONTRAST, settings['contrast'])
                
            # Färgmättnad
            if 'saturation' in settings:
                self.camera.set(cv2.CAP_PROP_SATURATION, settings['saturation'])
                
            self.settings.update(settings)
            logger.info("Applied camera settings")
            
        except Exception as e:
            logger.error(f"Error applying camera settings: {str(e)}")
            
    def get_settings(self) -> Dict[str, int]:
        """Hämta aktuella kamerainställningar"""
        return self.settings.copy()
        
    def is_connected(self) -> bool:
        """Kontrollera om kameran är ansluten"""
        return self.camera is not None and self.camera.isOpened()
        
    def set_camera_setting(self, setting: str, value: int) -> bool:
        """Ställer in en kamerainställning
        
        Args:
            setting: Inställningens namn
            value: Inställningens värde
            
        Returns:
            True om inställningen kunde sättas
        """
        if self.camera is None:
            return False
            
        setting_map = {
            'exposure': cv2.CAP_PROP_EXPOSURE,
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION
        }
        
        if setting in setting_map:
            try:
                self.camera.set(setting_map[setting], value)
                return True
            except Exception as e:
                logger.error(f"Kunde inte sätta {setting}: {str(e)}")
                
        return False
        
    def get_camera_setting(self, setting: str) -> Optional[int]:
        """Hämtar värdet för en kamerainställning
        
        Args:
            setting: Inställningens namn
            
        Returns:
            Inställningens värde eller None om det inte kunde hämtas
        """
        if self.camera is None:
            return None
            
        setting_map = {
            'exposure': cv2.CAP_PROP_EXPOSURE,
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION
        }
        
        if setting in setting_map:
            try:
                return int(self.camera.get(setting_map[setting]))
            except Exception as e:
                logger.error(f"Kunde inte hämta {setting}: {str(e)}")
                
        return None
