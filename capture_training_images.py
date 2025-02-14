"""Script för att samla in träningsbilder från kameran"""

import cv2
import os
from pathlib import Path
from datetime import datetime
from src.models.camera_manager import CameraManager

def create_directories():
    """Skapar nödvändiga mappar"""
    dataset_path = Path("dataset")
    train_path = dataset_path / "images" / "train"
    val_path = dataset_path / "images" / "val"
    
    train_path.mkdir(parents=True, exist_ok=True)
    val_path.mkdir(parents=True, exist_ok=True)
    
    return train_path, val_path

def main():
    """Huvudfunktion för bildinsamling"""
    print("Startar bildinsamling för träning...")
    
    # Skapa mappar
    train_path, val_path = create_directories()
    
    # Initiera kamera
    camera = CameraManager()
    camera.set_camera(-1)  # Använd simulerad kamera
    
    image_count = 0
    validation_interval = 5  # Var 5:e bild går till validering
    
    print("\nKontroller:")
    print("SPACE: Ta bild")
    print("ESC: Avsluta")
    
    while True:
        # Hämta frame
        frame = camera.get_frame()
        if frame is None:
            print("Kunde inte hämta bild från kameran")
            break
            
        # Visa frame
        cv2.imshow("Capture Training Images", frame)
        
        # Hantera knapptryckningar
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            # Generera filnamn
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"label_{timestamp}.jpg"
            
            # Bestäm om bilden ska till träning eller validering
            if image_count % validation_interval == 0:
                save_path = val_path / filename
                set_type = "validering"
            else:
                save_path = train_path / filename
                set_type = "träning"
                
            # Spara bilden
            cv2.imwrite(str(save_path), frame)
            image_count += 1
            print(f"Sparade bild {image_count} till {set_type}set: {filename}")
            
    cv2.destroyAllWindows()
    print(f"\nInsamling slutförd. Totalt {image_count} bilder sparade.")
    print(f"Träningsbilder: {image_count - image_count//validation_interval}")
    print(f"Valideringsbilder: {image_count//validation_interval}")
    
if __name__ == "__main__":
    main()
