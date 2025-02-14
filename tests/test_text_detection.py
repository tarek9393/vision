import cv2
import os
import numpy as np
from src.vision.text_detector import TextDetector
import logging

# Konfigurera logging
logging.basicConfig(level=logging.DEBUG)

def test_text_detection(image_path):
    # Kontrollera att bilden finns
    if not os.path.exists(image_path):
        print(f"Kunde inte hitta bilden: {image_path}")
        return
        
    # Läs in bilden
    print(f"Läser bild från: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print("Kunde inte läsa bilden")
        return
        
    # Initiera textdetektorn
    print("Initierar TextDetector...")
    detector = TextDetector()
    detector.toggle_debug_mode(True)  # Aktivera debug-läge
    
    # Visa originalbilden
    cv2.imshow('Original', image)
    
    # Detektera och läs text
    print("\nAnalyserar bild...")
    result = detector.detect_and_read(image)
    
    # Visa resultatet
    print("\n=== DETEKTERAD TEXT ===")
    print("Fullständig text:")
    print("-" * 50)
    print(result['full_text'])
    print("-" * 50)
    print("\nTextregioner:")
    print("-" * 50)
    
    # Kopiera bilden för att rita på
    display_image = image.copy()
    
    # Skapa en svart bakgrund för textvisning
    text_display = 255 * np.ones((400, 800, 3), dtype=np.uint8)
    y_offset = 30
    
    for i, region in enumerate(result['regions'], 1):
        # Rita rektangel runt texten
        x1, y1, x2, y2 = region['bbox']
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Hämta text och konfidens
        text = region['text']
        conf = region['confidence']
        
        # Visa text på bilden
        cv2.putText(display_image, f"{i}", (x1, y1-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Visa detaljerad information i text-displayen
        cv2.putText(text_display, f"Text {i}: {text}", (20, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(text_display, f"Konfidens: {conf:.2f}", (20, y_offset + 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        y_offset += 60
        
        # Skriv ut i terminalen
        print(f"Region {i}:")
        print(f"  Text: {text}")
        print(f"  Konfidens: {conf:.2f}")
        print(f"  Position: ({x1}, {y1}) till ({x2}, {y2})")
        print("-" * 50)
    
    # Visa bilderna
    cv2.imshow('Detekterad text', display_image)
    cv2.imshow('Text information', text_display)
    
    print("\nTryck på valfri tangent för att avsluta...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Använd en testbild från test_images mappen
    image_path = os.path.join("test_images", "test_label.jpg")
    test_text_detection(image_path)
