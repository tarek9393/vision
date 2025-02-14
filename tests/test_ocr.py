"""Test OCR på etiketter"""

import cv2
import os
import numpy as np
from src.models.tesseract_model import TesseractModel

def main():
    # Initiera OCR
    ocr_model = TesseractModel()
    
    # Testa en specifik bild från Labels-mappen
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, 'Labels', 'Kartongetiketter', 'Image', '16b5bd17-cd62-4785-9a0c-993b59e5672c_rw_1200.jpg')
    
    if not os.path.exists(image_path):
        print(f"Kunde inte hitta bilden: {image_path}")
        return
    
    print(f"Testar: {os.path.basename(image_path)}")
    print(f"Sökväg: {image_path}")
    print("-" * 50)
    
    # Läs bilden
    image = cv2.imread(image_path)
    if image is None:
        print("Kunde inte läsa bilden")
        return
    
    # Visa originalbilden
    cv2.imshow('Original', image)
    cv2.waitKey(1)  # Kort paus för att visa bilden
    
    # Kör OCR
    result = ocr_model.detect(image)
    
    if result['success']:
        print("\nDetekterade fält:")
        for field, value in result['fields'].items():
            if value:  # Visa bara fält som har ett värde
                print(f"{field:15}: {value}")
        
        print(f"\nTotal konfidens: {result['confidence']:.1f}%")
        
        # Visa bilden med detektioner
        cv2.imshow('Detektioner', result['annotated_image'])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Ingen text hittades eller ett fel uppstod")
        if 'error' in result:
            print(f"Fel: {result['error']}")

if __name__ == '__main__':
    main()
