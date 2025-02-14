import sys
import logging
import os
from PyQt5.QtWidgets import QApplication
from labelvision.gui.vision_window import VisionWindow
from labelvision.vision.vision_system import VisionSystem

def setup_logging():
    """Konfigurerar loggning"""
    # Skapa logs-katalogen om den inte finns
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,  # Ändra till DEBUG för mer detaljerad loggning
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/label_vision.log'),
            logging.StreamHandler()  # Lägg till console output
        ]
    )

def main():
    """Huvudfunktion för att starta systemet"""
    # Konfigurera loggning
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Skapa QApplication
        app = QApplication(sys.argv)
        
        # Initiera vision system
        vision_system = VisionSystem(use_test_image=True)
        
        # Skapa och visa huvudfönstret
        window = VisionWindow(vision_system)
        window.show()
        
        # Starta applikationen
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Fel vid start av systemet: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
