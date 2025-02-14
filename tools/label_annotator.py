"""
GUI-verktyg för att annotera text i etikettbilder.
Använder PyQt5 för gränssnittet och sparar annoteringar i YOLO-format.
"""

import sys
import os
from pathlib import Path
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QComboBox, QListWidget,
                           QMessageBox, QFileDialog, QScrollArea, QLineEdit, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor

# Ladda klasser från data.yaml
import yaml
with open(Path(__file__).parent.parent.parent / 'dataset' / 'data.yaml', 'r') as f:
    config = yaml.safe_load(f)
    CLASS_NAMES = config['names']

class BoundingBox:
    def __init__(self, start, end, class_id):
        self.start = start
        self.end = end
        self.class_id = class_id
        
    def to_yolo(self, img_width, img_height):
        """Konvertera till YOLO-format (x_center, y_center, width, height)"""
        x1, y1 = min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y())
        x2, y2 = max(self.start.x(), self.end.x()), max(self.start.y(), self.end.y())
        
        # Normalisera koordinater
        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height
        
        return f"{self.class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        
    def contains_point(self, point, margin=5):
        """Kolla om en punkt är nära boxen"""
        x1, y1 = min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y())
        x2, y2 = max(self.start.x(), self.end.x()), max(self.start.y(), self.end.y())
        
        return (x1 - margin <= point.x() <= x2 + margin and 
                y1 - margin <= point.y() <= y2 + margin)

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.start_drawing(event.pos())
        elif event.button() == Qt.RightButton:
            self.parent.remove_box_at(event.pos())
            
    def mouseMoveEvent(self, event):
        self.parent.update_drawing(event.pos())
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.finish_drawing(event.pos())

class ImageAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Etikett Text Annotator")
        self.setGeometry(100, 100, 1400, 800)
        
        # Huvudwidget och layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Vänster panel för kontroller
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Status för annotering
        self.status_label = QLabel()
        left_layout.addWidget(self.status_label)
        
        # Sökfält för bilder
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Sök efter kund eller etikettnamn...")
        self.search_box.textChanged.connect(self.filter_images)
        left_layout.addWidget(QLabel("Sök:"))
        left_layout.addWidget(self.search_box)
        
        # Bildlista med kolumner
        self.image_list = QTreeWidget()
        self.image_list.setHeaderLabels(["Kund", "Etikettnamn"])
        self.image_list.setColumnWidth(0, 150)  # Bredd för kundkolumn
        self.image_list.currentItemChanged.connect(self.load_image)
        left_layout.addWidget(QLabel("Bilder:"))
        left_layout.addWidget(self.image_list)
        
        # Klasslista
        self.class_combo = QComboBox()
        self.class_combo.addItems(CLASS_NAMES)
        left_layout.addWidget(QLabel("Texttyp:"))
        left_layout.addWidget(self.class_combo)
        
        # Information om aktuell bild
        self.image_info = QLabel()
        self.image_info.setWordWrap(True)
        left_layout.addWidget(QLabel("Information:"))
        left_layout.addWidget(self.image_info)
        
        # Knappar
        self.save_btn = QPushButton("Spara annoteringar")
        self.save_btn.clicked.connect(self.save_annotations)
        self.next_btn = QPushButton("Nästa bild")
        self.next_btn.clicked.connect(self.next_image)
        self.prev_btn = QPushButton("Föregående bild")
        self.prev_btn.clicked.connect(self.prev_image)
        self.clear_btn = QPushButton("Rensa alla markeringar")
        self.clear_btn.clicked.connect(self.clear_boxes)
        
        # Instruktioner
        instructions = QLabel(
            "Instruktioner:\n"
            "1. Välj texttyp från listan\n"
            "2. Vänsterklicka och dra för att markera text\n"
            "3. Högerklicka på en markering för att ta bort den\n"
            "4. Spara innan du går till nästa bild"
        )
        instructions.setWordWrap(True)
        
        left_layout.addWidget(instructions)
        left_layout.addWidget(self.save_btn)
        left_layout.addWidget(self.clear_btn)
        left_layout.addWidget(self.next_btn)
        left_layout.addWidget(self.prev_btn)
        
        # Lägg till vänster panel
        layout.addWidget(left_panel, stretch=1)
        
        # Container för bildvisaren
        self.image_container = QWidget()
        self.image_container.setMinimumSize(800, 600)
        
        # Scroll area för stora bilder
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_container)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area, stretch=4)
        
        # Bildvisare
        self.image_label = ImageLabel(self)
        container_layout = QVBoxLayout(self.image_container)
        container_layout.addWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Variabler för ritning
        self.drawing = False
        self.current_box = None
        self.boxes = []
        self.current_image = None
        self.current_image_path = None
        self.scale_factor = 1.0
        
        # Ladda bilder
        self.load_image_list()
        
    def load_image_list(self):
        """Ladda lista över bilder från dataset/images/train"""
        dataset_dir = Path(__file__).parent.parent.parent / 'dataset' / 'images' / 'train'
        self.image_paths = []  # Spara alla sökvägar för filtrering
        self.total_images = 0
        self.annotated_images = 0
        
        # Skapa root items för olika kategorier
        pall_root = QTreeWidgetItem(["Palletiketter"])
        self.image_list.addTopLevelItem(pall_root)
        produkt_root = QTreeWidgetItem(["Produktetiketter"])
        self.image_list.addTopLevelItem(produkt_root)
        
        for img_file in dataset_dir.glob('*.jpg'):
            self.total_images += 1
            try:
                # Hitta originalsökvägen från Labels-mappen
                orig_path = Path(str(img_file).replace('dataset/images/train', 'Labels/Etikett JPG'))
                parts = list(orig_path.parts)
                
                # Hitta relevanta index
                etikett_index = parts.index('Etikett JPG')
                
                if len(parts) > etikett_index + 1:
                    customer = parts[etikett_index + 1]
                    
                    # Ta bort filändelse och rensa namnet
                    label_name = parts[-1].replace('.jpg', '')
                    
                    # Ta bort onödiga ord från etikettnamnet
                    remove_words = ['Kartong', 'Box', 'Låda', 'Etikett']
                    for word in remove_words:
                        label_name = label_name.replace(word, '').strip()
                    
                    # Bestäm om det är en palletikett eller produktetikett
                    is_pall = any(p.lower() == 'pall' for p in parts)
                    
                    # Skapa item med rätt information
                    item = QTreeWidgetItem([customer, label_name.strip()])
                    item.setData(0, Qt.UserRole, str(img_file))
                    
                    # Kolla om bilden redan är annoterad
                    label_path = img_file.parent.parent.parent / 'labels' / 'train' / (img_file.stem + '.txt')
                    if label_path.exists():
                        self.annotated_images += 1
                        item.setForeground(0, QColor('green'))
                        item.setForeground(1, QColor('green'))
                    
                    # Lägg till under rätt kategori
                    if is_pall:
                        pall_root.addChild(item)
                    else:
                        produkt_root.addChild(item)
                    
                    self.image_paths.append((str(img_file), customer, label_name, is_pall))
                    
            except (ValueError, IndexError) as e:
                print(f"Kunde inte parse:a sökväg för {img_file}: {e}")
                item = QTreeWidgetItem([img_file.parent.parent.name, img_file.stem])
                item.setData(0, Qt.UserRole, str(img_file))
                produkt_root.addChild(item)
                self.image_paths.append((str(img_file), img_file.parent.parent.name, img_file.stem, False))
        
        # Uppdatera status
        self.update_status()
        
        # Expandera alla kategorier
        self.image_list.expandAll()
        
    def update_status(self):
        """Uppdatera status för annotering"""
        remaining = max(0, min(100, self.total_images) - self.annotated_images)
        status = (f"Status: {self.annotated_images}/{self.total_images} bilder annoterade\n"
                 f"Rekommendation: Annotera minst {remaining} bilder till\n"
                 f"(Minst 100 bilder totalt rekommenderas för bra träning)")
        self.status_label.setText(status)
        
    def filter_images(self, text):
        """Filtrera bildlistan baserat på söktext"""
        search_text = text.lower()
        
        # Göm/visa items baserat på söktext
        def filter_items(root_item):
            visible_count = 0
            for i in range(root_item.childCount()):
                child = root_item.child(i)
                customer = child.text(0).lower()
                label = child.text(1).lower()
                
                if search_text in customer or search_text in label:
                    child.setHidden(False)
                    visible_count += 1
                else:
                    child.setHidden(True)
            return visible_count
        
        # Gå igenom alla root items
        for i in range(self.image_list.topLevelItemCount()):
            root = self.image_list.topLevelItem(i)
            visible_children = filter_items(root)
            root.setHidden(visible_children == 0)  # Göm kategorin om inga barn är synliga
        
    def next_image(self):
        """Gå till nästa bild i listan"""
        current_item = self.image_list.currentItem()
        if current_item:
            current_index = self.image_list.indexOfTopLevelItem(current_item)
            if current_index < self.image_list.topLevelItemCount() - 1:
                next_item = self.image_list.topLevelItem(current_index + 1)
                self.image_list.setCurrentItem(next_item)
            
    def prev_image(self):
        """Gå till föregående bild i listan"""
        current_item = self.image_list.currentItem()
        if current_item:
            current_index = self.image_list.indexOfTopLevelItem(current_item)
            if current_index > 0:
                prev_item = self.image_list.topLevelItem(current_index - 1)
                self.image_list.setCurrentItem(prev_item)
                
    def update_image(self):
        """Uppdatera bildvisningen med alla boxes"""
        if self.current_image is None:
            return
            
        # Kopiera bilden för att kunna rita på den
        display_image = self.current_image.copy()
        
        # Rita alla sparade boxar
        for box in self.boxes:
            x1, y1 = min(box.start.x(), box.end.x()), min(box.start.y(), box.end.y())
            x2, y2 = max(box.start.x(), box.end.x()), max(box.start.y(), box.end.y())
            
            # Rita box med klassens färg
            color = QColor.fromHsv(box.class_id * 30, 255, 255)
            cv2.rectangle(display_image, (x1, y1), (x2, y2), 
                        (color.red(), color.green(), color.blue()), 2)
            
            # Visa klassnamn
            cv2.putText(display_image, CLASS_NAMES[box.class_id], (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                       (color.red(), color.green(), color.blue()), 2)
        
        # Rita aktiv box om vi håller på att rita
        if self.drawing and self.current_box:
            x1, y1 = min(self.current_box.start.x(), self.current_box.end.x()), min(self.current_box.start.y(), self.current_box.end.y())
            x2, y2 = max(self.current_box.start.x(), self.current_box.end.x()), max(self.current_box.start.y(), self.current_box.end.y())
            
            color = QColor.fromHsv(self.class_combo.currentIndex() * 30, 255, 255)
            cv2.rectangle(display_image, (x1, y1), (x2, y2),
                        (color.red(), color.green(), color.blue()), 2)
        
        # Konvertera till QImage och visa
        height, width, channel = display_image.shape
        bytes_per_line = 3 * width
        q_img = QImage(display_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Visa bilden i full storlek
        self.image_label.setPixmap(QPixmap.fromImage(q_img))
        self.image_label.setFixedSize(width, height)
        
    def start_drawing(self, pos):
        """Börja rita en ny box"""
        if self.current_image is not None:
            self.drawing = True
            self.current_box = BoundingBox(pos, pos, self.class_combo.currentIndex())
        
    def update_drawing(self, pos):
        """Uppdatera boxen medan musen rör sig"""
        if self.drawing and self.current_box:
            self.current_box.end = pos
            self.update_image()
            
    def finish_drawing(self, pos):
        """Avsluta ritning av box"""
        if self.drawing:
            self.drawing = False
            if self.current_box:
                # Kontrollera att boxen har en minimal storlek
                x1, y1 = min(self.current_box.start.x(), self.current_box.end.x()), min(self.current_box.start.y(), self.current_box.end.y())
                x2, y2 = max(self.current_box.start.x(), self.current_box.end.x()), max(self.current_box.start.y(), self.current_box.end.y())
                if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                    self.boxes.append(self.current_box)
                self.current_box = None
                self.update_image()
                
    def remove_box_at(self, pos):
        """Ta bort box vid musposition"""
        for i, box in enumerate(self.boxes):
            if box.contains_point(pos):
                del self.boxes[i]
                self.update_image()
                break
                
    def clear_boxes(self):
        """Ta bort alla markeringar"""
        if self.boxes:
            reply = QMessageBox.question(self, 'Bekräfta', 
                                       'Är du säker på att du vill ta bort alla markeringar?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.boxes = []
                self.update_image()
                
    def save_annotations(self):
        """Spara annoteringar i YOLO-format"""
        if self.current_image is None:
            return
            
        # Skapa labels-mapp om den inte finns
        label_dir = self.current_image_path.parent.parent.parent / 'labels' / 'train'
        label_dir.mkdir(parents=True, exist_ok=True)
        
        # Spara annoteringar
        label_path = label_dir / (self.current_image_path.stem + '.txt')
        img_height, img_width = self.current_image.shape[:2]
        
        with open(label_path, 'w') as f:
            for box in self.boxes:
                f.write(box.to_yolo(img_width, img_height) + '\n')
        
        # Uppdatera status
        if not label_path.exists():
            self.annotated_images += 1
            self.update_status()
            
            # Uppdatera färg i listan
            current_item = self.image_list.currentItem()
            if current_item:
                current_item.setForeground(0, QColor('green'))
                current_item.setForeground(1, QColor('green'))
                
        QMessageBox.information(self, "Sparat", f"Annoteringar sparade till {label_path}")
        
    def load_image(self, current, previous):
        """Ladda vald bild och dess annoteringar"""
        if current is None:
            return
            
        # Hämta den sparade sökvägen
        img_path = current.data(0, Qt.UserRole)
        if not img_path:
            return
            
        self.current_image_path = Path(img_path)
        self.current_image = cv2.imread(str(self.current_image_path))
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        self.boxes = []
        
        # Uppdatera bildinformation
        customer = current.text(0)
        label_name = current.text(1)
        self.image_info.setText(f"Kund: {customer}\nEtikett: {label_name}")
        
        # Ladda existerande annoteringar om de finns
        label_path = self.current_image_path.parent.parent.parent / 'labels' / 'train' / (self.current_image_path.stem + '.txt')
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    class_id, x_center, y_center, width, height = map(float, line.strip().split())
                    img_height, img_width = self.current_image.shape[:2]
                    
                    # Konvertera från YOLO till pixel-koordinater
                    x1 = int((x_center - width/2) * img_width)
                    y1 = int((y_center - height/2) * img_height)
                    x2 = int((x_center + width/2) * img_width)
                    y2 = int((y_center + height/2) * img_height)
                    
                    self.boxes.append(BoundingBox(QPoint(x1, y1), QPoint(x2, y2), int(class_id)))
        
        self.update_image()
        
def main():
    app = QApplication(sys.argv)
    window = ImageAnnotator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
