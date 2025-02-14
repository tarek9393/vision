"""Genererar testbilder för OCR"""

import cv2
import numpy as np
import os

def create_test_label(text: str, size: tuple = (800, 600)) -> np.ndarray:
    """Skapar en testbild med given text
    
    Args:
        text: Texten som ska läggas till i bilden
        size: Bildens storlek som (bredd, höjd)
        
    Returns:
        np.ndarray: Den genererade testbilden
    """
    # Skapa en vit bild
    image = np.ones((size[1], size[0], 3), dtype=np.uint8) * 255
    
    # Lägg till text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (0, 0, 0)  # Svart text
    
    # Dela upp texten i rader
    lines = text.split('\n')
    
    # Centrera varje rad
    y = 50
    for line in lines:
        # Beräkna textstorlek
        (text_width, text_height), _ = cv2.getTextSize(line, font, font_scale, thickness)
        x = (size[0] - text_width) // 2
        
        # Lägg till text
        cv2.putText(image, line, (x, y), font, font_scale, color, thickness)
        y += text_height + 20
    
    return image

def generate_test_labels():
    """Genererar en uppsättning testbilder"""
    # Skapa output-katalog
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'test_images')
    os.makedirs(output_dir, exist_ok=True)
    
    # Testdata
    test_labels = [
        {
            'text': 'PRODUKT: ABC-123\nBatch: 2024-01\nKvalitet: A',
            'filename': 'test_label_1.jpg'
        },
        {
            'text': 'PRODUKT: XYZ-789\nBatch: 2024-02\nKvalitet: B',
            'filename': 'test_label_2.jpg'
        }
    ]
    
    # Generera och spara bilder
    for label in test_labels:
        image = create_test_label(label['text'])
        output_path = os.path.join(output_dir, label['filename'])
        cv2.imwrite(output_path, image)
        print(f"Genererade testbild: {output_path}")

if __name__ == '__main__':
    generate_test_labels()
