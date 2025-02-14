"""Verktyg för att annotera etikettbilder för YOLO-träning"""

import cv2
import numpy as np
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple, Optional

class LabelAnnotator:
    def __init__(self):
        self.current_image_index = 0
        self.image_files: List[Path] = []
        self.current_image: Optional[np.ndarray] = None
        self.display_image: Optional[np.ndarray] = None
        self.scale_factor = 1.0
        self.drawing = False
        self.boxes: List[Tuple[int, int, int, int]] = []  # x1,y1,x2,y2
        self.current_box: Optional[Tuple[int, int, int, int]] = None
        self.window_name = "Label Annotator"
        
        # Skapa Tkinter root window
        self.root = tk.Tk()
        self.root.withdraw()  # Göm huvudfönstret
        
        # Hämta skärmupplösning
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
    def load_images(self, directory: str) -> bool:
        """Laddar alla bilder från en mapp"""
        try:
            self.image_files = list(Path(directory).glob("*.jpg"))
            if not self.image_files:
                messagebox.showerror("Fel", f"Inga bilder hittades i {directory}")
                return False
            print(f"Hittade {len(self.image_files)} bilder")
            return True
        except Exception as e:
            messagebox.showerror("Fel", f"Kunde inte ladda bilder: {str(e)}")
            return False
        
    def resize_image(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Anpassar bildstorleken till skärmen"""
        max_width = self.screen_width - 100  # Lämna lite marginal
        max_height = self.screen_height - 100
        
        height, width = image.shape[:2]
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h, 1.0)  # Förminska bara, förstora aldrig
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height))
            return resized, scale
        return image.copy(), 1.0
        
    def load_current_image(self) -> bool:
        """Laddar aktuell bild"""
        if self.current_image_index >= len(self.image_files):
            return False
            
        try:
            image_path = self.image_files[self.current_image_index]
            # Använd raw string för att hantera specialtecken
            self.current_image = cv2.imdecode(
                np.fromfile(str(image_path), dtype=np.uint8),
                cv2.IMREAD_COLOR
            )
            if self.current_image is None:
                messagebox.showerror("Fel", f"Kunde inte ladda bild: {image_path}")
                return False
                
            # Anpassa bildstorlek
            self.display_image, self.scale_factor = self.resize_image(self.current_image)
                
            # Ladda eventuella existerande annoteringar
            label_path = image_path.parent.parent / "labels" / (image_path.stem + ".txt")
            self.boxes = []
            if label_path.exists():
                with open(label_path, 'r') as f:
                    for line in f:
                        class_id, x_center, y_center, width, height = map(float, line.strip().split())
                        h, w = self.current_image.shape[:2]
                        x1 = int((x_center - width/2) * w)
                        y1 = int((y_center - height/2) * h)
                        x2 = int((x_center + width/2) * w)
                        y2 = int((y_center + height/2) * h)
                        # Skala om koordinaterna
                        x1 = int(x1 * self.scale_factor)
                        y1 = int(y1 * self.scale_factor)
                        x2 = int(x2 * self.scale_factor)
                        y2 = int(y2 * self.scale_factor)
                        self.boxes.append((x1, y1, x2, y2))
                        
            # Rita existerande boxar
            self.draw_boxes()
            return True
            
        except Exception as e:
            messagebox.showerror("Fel", f"Fel vid laddning av bild: {str(e)}")
            return False
            
    def draw_boxes(self):
        """Ritar alla boxar på bilden"""
        if self.display_image is None:
            return
            
        img_copy = self.display_image.copy()
        for box in self.boxes:
            cv2.rectangle(img_copy,
                        (box[0], box[1]),
                        (box[2], box[3]),
                        (0, 255, 0), 2)
        cv2.imshow(self.window_name, img_copy)
        
    def mouse_callback(self, event, x, y, flags, param):
        """Hanterar musklick och dragning"""
        if self.display_image is None:
            return
            
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.current_box = (x, y, x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                img_copy = self.display_image.copy()
                self.current_box = (self.current_box[0], self.current_box[1], x, y)
                # Rita alla existerande boxar
                for box in self.boxes:
                    cv2.rectangle(img_copy,
                                (box[0], box[1]),
                                (box[2], box[3]),
                                (0, 255, 0), 2)
                # Rita den aktiva boxen
                cv2.rectangle(img_copy,
                            (self.current_box[0], self.current_box[1]),
                            (self.current_box[2], self.current_box[3]),
                            (255, 0, 0), 2)
                cv2.imshow(self.window_name, img_copy)
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                if self.current_box:
                    # Normalisera koordinater (se till att x1 < x2 och y1 < y2)
                    x1 = min(self.current_box[0], self.current_box[2])
                    x2 = max(self.current_box[0], self.current_box[2])
                    y1 = min(self.current_box[1], self.current_box[3])
                    y2 = max(self.current_box[1], self.current_box[3])
                    self.boxes.append((x1, y1, x2, y2))
                    self.draw_boxes()
                
    def save_annotations(self):
        """Sparar annoteringar i YOLO-format"""
        if not self.boxes or self.current_image is None:
            return
            
        try:
            # Konvertera till YOLO-format (normaliserade koordinater)
            display_h, display_w = self.display_image.shape[:2]
            h, w = self.current_image.shape[:2]
            yolo_boxes = []
            
            for box in self.boxes:
                # Konvertera tillbaka till originalbildens koordinater
                x1 = int(box[0] / self.scale_factor)
                y1 = int(box[1] / self.scale_factor)
                x2 = int(box[2] / self.scale_factor)
                y2 = int(box[3] / self.scale_factor)
                
                # Normalisera koordinater
                x_center = ((x1 + x2) / 2) / w
                y_center = ((y1 + y2) / 2) / h
                width = abs(x2 - x1) / w
                height = abs(y2 - y1) / h
                
                # YOLO-format: <class> <x_center> <y_center> <width> <height>
                yolo_boxes.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
            
            # Spara till fil
            image_path = self.image_files[self.current_image_index]
            label_path = image_path.parent.parent / "labels" / (image_path.stem + ".txt")
            label_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(label_path, 'w') as f:
                f.write('\n'.join(yolo_boxes))
                
            print(f"Sparade annoteringar för: {image_path.name}")
            
        except Exception as e:
            messagebox.showerror("Fel", f"Kunde inte spara annoteringar: {str(e)}")
        
    def run(self):
        """Kör annoteringsverktyget"""
        try:
            # Välj mapp med bilder
            image_dir = filedialog.askdirectory(
                title="Välj mapp med bilder att annotera",
                initialdir="dataset/train/images"
            )
            
            if not image_dir or not self.load_images(image_dir):
                print("Ingen mapp vald eller inga bilder hittades.")
                return
                
            cv2.namedWindow(self.window_name)
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
            
            print("\nInstruktioner:")
            print("1. Klicka och dra för att markera etiketter")
            print("2. Tryck 'r' för att ta bort senaste markeringen")
            print("3. Tryck 's' för att spara och gå till nästa bild")
            print("4. Tryck 'b' för att gå tillbaka till föregående bild")
            print("5. Tryck 'q' för att avsluta")
            
            while True:
                if not self.load_current_image():
                    print("Inga fler bilder att annotera!")
                    break
                    
                while True:
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        return
                        
                    elif key == ord('r'):
                        if self.boxes:
                            self.boxes.pop()
                            self.draw_boxes()
                            
                    elif key == ord('s'):
                        self.save_annotations()
                        self.current_image_index += 1
                        self.boxes = []
                        break
                        
                    elif key == ord('b'):
                        if self.current_image_index > 0:
                            self.current_image_index -= 1
                            self.boxes = []
                            break
            
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("Fel", f"Ett fel uppstod: {str(e)}")
            cv2.destroyAllWindows()

def main():
    annotator = LabelAnnotator()
    annotator.run()

if __name__ == "__main__":
    main()
