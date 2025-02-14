"""Startsida för Label Vision System"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QFrame, QPushButton,
                           QScrollArea, QGridLayout, QLabel, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from .vision_window import VisionWindow

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Label Vision System")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        self.setup_theme()
        
    def setup_ui(self):
        """Skapar användargränssnittet"""
        # Huvudwidget och layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Vänster panel med trädvy
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Trädvy för etikettval
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Etiketter")
        self.setup_tree()
        left_layout.addWidget(self.tree)
        
        # Höger panel med etikettförhandsvisning
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        
        # Scrollområde för etikettgrid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scrollArea")
        
        # Grid för etikettförhandsvisning
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(20)
        scroll.setWidget(grid_widget)
        right_layout.addWidget(scroll)
        
        # Lägg till paneler till huvudlayout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Skapa exempel-etiketter
        self.populate_grid()
        
    def setup_tree(self):
        """Skapar trädstrukturen för etikettval"""
        # Huvudkategorier
        categories = {
            "Bake & Take": ["Munkar", "Bröd", "Kakor"],
            "Lantmännen": ["Unibake DK", "Unibake SE", "Unibake NO"],
            "Övriga": ["Max Burgers", "McDonalds"]
        }
        
        for category, subcategories in categories.items():
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, category)
            for subcat in subcategories:
                child = QTreeWidgetItem(parent)
                child.setText(0, subcat)
        
        self.tree.itemClicked.connect(self.on_tree_select)
        
    def populate_grid(self):
        """Fyller griden med etikettförhandsvisningar"""
        # Exempel-etiketter (ersätt med riktiga senare)
        labels = [
            {"name": "Munkhallon", "id": "62865"},
            {"name": "Vaniljmunk", "id": "62862"},
            {"name": "Chokladmunk", "id": "62864"},
            {"name": "Jordgubbsmunk", "id": "62866"}
        ]
        
        row = 0
        col = 0
        for label in labels:
            frame = QFrame()
            frame.setObjectName("labelFrame")
            layout = QVBoxLayout(frame)
            
            # Etikettpanel
            preview = QLabel()
            preview.setFixedSize(200, 150)
            preview.setStyleSheet("background-color: #ffffff;")
            layout.addWidget(preview)
            
            # Etikettinformation
            info = QLabel(f"{label['name']}\nID: {label['id']}")
            info.setAlignment(Qt.AlignCenter)
            layout.addWidget(info)
            
            # Knapp för att starta vision
            btn = QPushButton("Starta Vision")
            btn.clicked.connect(lambda checked, lid=label['id']: self.start_vision(lid))
            layout.addWidget(btn)
            
            self.grid_layout.addWidget(frame, row, col)
            
            col += 1
            if col > 2:  # 3 etiketter per rad
                col = 0
                row += 1
                
    def start_vision(self, label_id):
        """Startar vision-systemet för vald etikett"""
        try:
            # Skapa ett nytt vision-fönster som barn till detta fönster
            self.vision_window = VisionWindow(label_id=label_id, parent=self)
            self.vision_window.setWindowModality(Qt.NonModal)  # Gör fönstret icke-modalt
            self.vision_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Fel", f"Kunde inte starta vision-systemet: {str(e)}")
            
    def on_tree_select(self, item, column):
        """Hanterar val i trädvyn"""
        # Uppdatera grid baserat på val
        pass
        
    def setup_theme(self):
        """Sätter upp färgtema och stilar"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QFrame {
                border-radius: 10px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
            }
            
            #leftPanel {
                background-color: #252525;
                padding: 10px;
                margin: 5px;
            }
            
            #rightPanel {
                background-color: #252525;
                padding: 10px;
                margin: 5px;
            }
            
            QTreeWidget {
                background-color: #2d2d2d;
                border: none;
                color: #ffffff;
            }
            
            QTreeWidget::item {
                padding: 5px;
                border-radius: 5px;
            }
            
            QTreeWidget::item:selected {
                background-color: #2196F3;
            }
            
            #labelFrame {
                background-color: #363636;
                padding: 15px;
                margin: 5px;
            }
            
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
            }
            
            QLabel {
                color: #ffffff;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 10px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: #404040;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
