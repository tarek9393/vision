import cv2
import numpy as np
from pathlib import Path
import random
import shutil

def load_existing_annotations(labels_dir):
    """Ladda existerande annoteringar för att lära sig mönster"""
    patterns = []
    for label_file in labels_dir.glob('*.txt'):
        if label_file.stat().st_size > 0:  # Skippa tomma filer
            with open(label_file, 'r') as f:
                boxes = []
                for line in f:
                    class_id, x_center, y_center, width, height = map(float, line.strip().split())
                    boxes.append({
                        'class_id': int(class_id),
                        'width': width,
                        'height': height
                    })
                if boxes:  # Bara spara om det finns annoteringar
                    patterns.append(boxes)
    return patterns

def auto_annotate_image(image_path, patterns, labels_dir):
    """Automatiskt annotera en bild baserat på tidigare mönster"""
    if not patterns:
        return False
        
    # Välj ett slumpmässigt mönster att applicera
    pattern = random.choice(patterns)
    
    # Läs bilden för att få dimensioner
    img = cv2.imread(str(image_path))
    if img is None:
        return False
    
    img_height, img_width = img.shape[:2]
    
    # Skapa label-fil
    label_path = labels_dir / (image_path.stem + '.txt')
    
    # Applicera mönstret med lite slumpmässig variation
    with open(label_path, 'w') as f:
        for box in pattern:
            # Lägg till lite slumpmässig variation i position och storlek
            x_center = random.uniform(0.2, 0.8)
            y_center = random.uniform(0.2, 0.8)
            width = box['width'] * random.uniform(0.9, 1.1)  # ±10% variation
            height = box['height'] * random.uniform(0.9, 1.1)  # ±10% variation
            
            # Säkerställ att boxen är inom bilden
            width = min(width, 2 * min(x_center, 1 - x_center))
            height = min(height, 2 * min(y_center, 1 - y_center))
            
            f.write(f"{box['class_id']} {x_center} {y_center} {width} {height}\n")
    
    return True

def main():
    # Sökvägar
    base_dir = Path(__file__).parent.parent.parent
    dataset_dir = base_dir / 'dataset'
    images_dir = dataset_dir / 'images' / 'train'
    labels_dir = dataset_dir / 'labels' / 'train'
    
    # Ladda existerande annoteringsmönster
    patterns = load_existing_annotations(labels_dir)
    if not patterns:
        print("Inga existerande annoteringar hittades att basera på")
        return
        
    # Hitta alla oannoterade bilder
    unannotated_images = []
    for img_path in images_dir.glob('*.jpg'):
        label_path = labels_dir / (img_path.stem + '.txt')
        if not label_path.exists() or label_path.stat().st_size == 0:
            unannotated_images.append(img_path)
    
    if not unannotated_images:
        print("Inga oannoterade bilder hittades")
        return
    
    # Välj slumpmässiga bilder att annotera
    num_to_annotate = min(len(unannotated_images), 100)  # Max 100 bilder
    selected_images = random.sample(unannotated_images, num_to_annotate)
    
    # Annotera bilderna
    success_count = 0
    for img_path in selected_images:
        if auto_annotate_image(img_path, patterns, labels_dir):
            success_count += 1
            print(f"Annoterade: {img_path.name}")
    
    print(f"\nKlar! Annoterade {success_count} av {num_to_annotate} bilder")

if __name__ == '__main__':
    main()
