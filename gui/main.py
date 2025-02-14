"""Huvudapplikation för Label Vision System"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from gui.vision_window import VisionWindow

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('label_vision.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Huvudfunktion för att starta applikationen"""
    try:
        app = QApplication(sys.argv)
        window = VisionWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
