"""Startsida för Label Vision System"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class StartPage(QWidget):
    """Startsida för applikationen"""
    
    def __init__(self, nicelabel_client):
        super().__init__()
        self.nicelabel_client = nicelabel_client
        self.labels = []
        self.init_ui()
        self.load_labels()
        
    def init_ui(self):
        """Initiera användargränssnittet"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Rubrik
        title = QLabel("Label Vision System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instruktioner
        instructions = QLabel(
            "Välj en etikett från listan nedan och klicka på 'Öppna Kamera' "
            "för att starta validering."
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(instructions)
        
        # Lista med etiketter
        self.label_list = QListWidget()
        self.label_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.label_list)
        
        # Knappar
        button_layout = QHBoxLayout()
        
        self.camera_button = QPushButton("Öppna Kamera")
        self.camera_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.camera_button)
        
        layout.addLayout(button_layout)
        
    def load_labels(self):
        """Ladda etiketter från NiceLabel"""
        try:
            self.labels = self.nicelabel_client.get_labels()
            self.label_list.clear()
            
            for label in self.labels:
                item = QListWidgetItem(label['name'])
                item.setData(Qt.UserRole, label)
                self.label_list.addItem(item)
                
            if self.labels:
                logger.info(f"Laddade {len(self.labels)} etiketter")
            else:
                logger.warning("Inga etiketter hittades")
                QMessageBox.warning(
                    self,
                    "Inga etiketter",
                    "Kunde inte hitta några etiketter. Kontrollera anslutningen till NiceLabel."
                )
                
        except Exception as e:
            logger.error(f"Fel vid laddning av etiketter: {e}")
            QMessageBox.critical(
                self,
                "Laddningsfel",
                f"Kunde inte ladda etiketter: {str(e)}"
            )
            
    def get_selected_label(self):
        """Hämta vald etikett"""
        current_item = self.label_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
