"""Base class for vision models"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any

class BaseVisionModel(ABC):
    """Abstrakt basklass för vision-modeller"""
    
    def __init__(self):
        """Initierar basmodellen"""
        pass
        
    @abstractmethod
    def detect(self, image: np.ndarray) -> Dict[str, Any]:
        """Detekterar objekt/text i en bild
        
        Args:
            image: OpenCV-bild att analysera
            
        Returns:
            Dictionary med detektionsresultat
        """
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """Returnerar modellens namn
        
        Returns:
            Modellens namn som sträng
        """
        pass
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Förbehandlar en bild innan detektering
        
        Args:
            image: OpenCV-bild att förbehandla
            
        Returns:
            Förbehandlad bild
        """
        return image
