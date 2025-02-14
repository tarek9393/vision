"""Test av vision-systemets funktioner"""

import cv2
import numpy as np
import os
import logging
from src.vision.image_processing import ImageProcessor
from src.camera.camera_manager import CameraManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Huvudfunktion för test"""
    try:
        # Initiera kamera och bildprocessor
        camera = CameraManager()
        processor = ImageProcessor()
        processor.debug_mode = True  # Aktivera felsökningsläge
        
        logger.info("Initierar kamera...")
        if not camera.connect():
            logger.error("Kunde inte ansluta till kamera")
            return
            
        logger.info("Tar testbild...")
        success, frame = camera.take_picture()
        if not success or frame is None:
            logger.error("Kunde inte ta bild")
            return
            
        # Skapa utdatamapp
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Spara originalbild
        cv2.imwrite(os.path.join(output_dir, "original.jpg"), frame)
        logger.info("Sparade originalbild")
        
        # Testa bildförbättring
        enhanced = processor.enhance_image(frame)
        cv2.imwrite(os.path.join(output_dir, "enhanced.jpg"), enhanced)
        logger.info("Sparade förbättrad bild")
        
        # Testa kantdetektering
        edges, contours = processor.detect_edges(frame)
        cv2.imwrite(os.path.join(output_dir, "edges.jpg"), edges)
        logger.info("Sparade kantdetektering")
        
        # Testa OCR
        text = processor.extract_text(frame)
        logger.info(f"Extraherad text: {text}")
        
        # Testa perspektivkorrigering
        corrected = processor.correct_perspective(frame)
        cv2.imwrite(os.path.join(output_dir, "perspective_corrected.jpg"), corrected)
        logger.info("Sparade perspektivkorrigerad bild")
        
        # Testa bildkvalitetsanalys
        metrics = processor.analyze_image_quality(frame)
        logger.info(f"Bildkvalitetsmetrik: {metrics}")
        
        # Testa felsökningsvisualisering
        debug_view = processor.debug_visualization(frame)
        cv2.imwrite(os.path.join(output_dir, "debug_view.jpg"), debug_view)
        logger.info("Sparade felsökningsvy")
        
        # Visa resultat i fönster
        cv2.imshow("Original", frame)
        cv2.imshow("Enhanced", enhanced)
        cv2.imshow("Edges", edges)
        cv2.imshow("Debug View", debug_view)
        
        logger.info("Tryck på valfri tangent för att avsluta...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        logger.error(f"Fel under test: {str(e)}")
    finally:
        camera.disconnect()
        logger.info("Test avslutat")

if __name__ == "__main__":
    main()
