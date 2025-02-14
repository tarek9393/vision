"""Valideringssida för etikettvalidering"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from .styles import STYLES
import cv2
import os

class ValidationPage(QWidget):
    """Huvudsida för etikettvalidering"""
    
    start_camera_signal = pyqtSignal()
    validate_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initierar användargränssnittet"""
        # Huvudlayout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Vänster container (kamera och detekterad etikett)
        left_container = QWidget()
        left_container.setObjectName("left_container")
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(15)
        
        # Kamerabild
        camera_frame = QFrame()
        camera_frame.setObjectName("camera_frame")
        camera_layout = QVBoxLayout(camera_frame)
        
        camera_title = QLabel("Kamerabild")
        camera_title.setProperty("title", True)
        camera_layout.addWidget(camera_title, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.camera_view = QLabel()
        self.camera_view.setMinimumSize(640, 480)
        self.camera_view.setStyleSheet("background-color: #1e2127;")
        camera_layout.addWidget(self.camera_view)
        
        left_layout.addWidget(camera_frame)
        
        # Detekterad etikett
        detected_frame = QFrame()
        detected_frame.setObjectName("detected_frame")
        detected_layout = QVBoxLayout(detected_frame)
        
        detected_title = QLabel("Detekterad etikett")
        detected_title.setProperty("title", True)
        detected_layout.addWidget(detected_title)
        
        self.detected_label = QLabel()
        self.detected_label.setMinimumHeight(100)
        self.detected_label.setStyleSheet("background-color: #1e2127;")
        detected_layout.addWidget(self.detected_label)
        
        left_layout.addWidget(detected_frame)
        
        # Höger container (referensetikett och kontroller)
        right_container = QWidget()
        right_container.setObjectName("right_container")
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(15)
        
        # Referensetikett
        reference_frame = QFrame()
        reference_frame.setObjectName("reference_frame")
        reference_layout = QVBoxLayout(reference_frame)
        
        reference_title = QLabel("Referensetikett")
        reference_title.setProperty("title", True)
        reference_layout.addWidget(reference_title)
        
        self.reference_label = QLabel()
        self.reference_label.setMinimumSize(300, 300)
        self.reference_label.setStyleSheet("background-color: #1e2127;")
        reference_layout.addWidget(self.reference_label)
        
        right_layout.addWidget(reference_frame)
        
        # Produktinformation
        product_info_frame = QFrame()
        product_info_frame.setObjectName("product_info_frame")
        product_info_layout = QVBoxLayout(product_info_frame)
        
        product_info_title = QLabel("Produktinformation")
        product_info_title.setProperty("title", True)
        product_info_layout.addWidget(product_info_title)
        
        self.product_info = QTextEdit()
        self.product_info.setReadOnly(True)
        product_info_layout.addWidget(self.product_info)
        
        right_layout.addWidget(product_info_frame)
        
        # Status och kontroller
        status_frame = QFrame()
        status_frame.setObjectName("status_frame")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)
        
        # Status
        self.status_label = QLabel("Status: Väntar på validering")
        self.status_label.setObjectName("status_label")
        self.status_label.setProperty("status", "waiting")
        status_layout.addWidget(self.status_label)
        
        # Matchningspoäng
        self.score_label = QLabel("Matchningspoäng: -")
        self.score_label.setObjectName("score_label")
        status_layout.addWidget(self.score_label)
        
        # Försök
        self.attempts_label = QLabel("Försök: 0/3")
        self.attempts_label.setObjectName("attempts_label")
        status_layout.addWidget(self.attempts_label)
        
        # Felmeddelande
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        status_layout.addWidget(self.error_label)
        
        # Knappar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_camera_btn = QPushButton("STARTA KAMERA")
        self.start_camera_btn.clicked.connect(self.start_camera_signal.emit)
        button_layout.addWidget(self.start_camera_btn)
        
        self.validate_btn = QPushButton("VALIDERA")
        self.validate_btn.clicked.connect(self.validate_signal.emit)
        self.validate_btn.setEnabled(False)
        button_layout.addWidget(self.validate_btn)
        
        status_layout.addLayout(button_layout)
        right_layout.addWidget(status_frame)
        
        # Lägg till containers i huvudlayouten
        main_layout.addWidget(left_container, stretch=60)
        main_layout.addWidget(right_container, stretch=40)
        
        self.setLayout(main_layout)
        
    def update_camera_frame(self, frame):
        """Uppdaterar kamerabilden"""
        self.camera_view.setPixmap(frame)
        
    def update_detected_label(self, frame):
        """Uppdaterar den detekterade etiketten"""
        self.detected_label.setPixmap(frame)
        
    def update_reference_label(self, frame):
        """Uppdaterar referensetiketten"""
        self.reference_label.setPixmap(frame)
        
    def update_product_info(self, product):
        """Uppdaterar produktinformationen"""
        if product:
            # Visa produktinformation
            info_text = f"""
            <h3>{product['name']}</h3>
            <p><b>Artikelnummer:</b> {product['article_number']}</p>
            <p><b>Kund:</b> {product['customer']}</p>
            <p><b>Beskrivning:</b> {product['description']}</p>
            """
            self.product_info.setText(info_text)
            
            # Visa referensbild om den finns
            if 'label' in product:
                label_path = os.path.join('labels', product['label'])
                if os.path.exists(label_path):
                    image = cv2.imread(label_path)
                    if image is not None:
                        # Konvertera från BGR till RGB
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        height, width = image.shape[:2]
                        
                        # Skapa QImage och visa i QLabel
                        bytes_per_line = 3 * width
                        q_image = QImage(image.data, width, height, 
                                       bytes_per_line, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(q_image)
                        
                        # Skala om bilden för att passa i labeln
                        scaled_pixmap = pixmap.scaled(
                            self.reference_label.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.reference_label.setPixmap(scaled_pixmap)
                    else:
                        self.reference_label.setText("Kunde inte ladda referensbild")
                else:
                    self.reference_label.setText("Referensbild saknas")
            else:
                self.reference_label.setText("Ingen referensbild tillgänglig")
        else:
            self.product_info.clear()
            self.reference_label.clear()
        
    def update_status(self, status: str, is_error: bool = False):
        """Uppdaterar statusmeddelandet"""
        self.status_label.setText(f"Status: {status}")
        self.status_label.setProperty(
            "status", 
            "error" if is_error else "success" if "Godkänd" in status else "waiting"
        )
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        
    def update_score(self, score: float):
        """Uppdaterar matchningspoängen"""
        self.score_label.setText(f"Matchningspoäng: {score:.1f}%")
        
    def update_attempts(self, current: int, max_attempts: int):
        """Uppdaterar antal försök"""
        self.attempts_label.setText(f"Försök: {current}/{max_attempts}")
        
    def show_error(self, message: str):
        """Visar ett felmeddelande"""
        self.error_label.setText(message)
        
    def clear_error(self):
        """Rensar felmeddelandet"""
        self.error_label.clear()
        
    def enable_validation(self, enable: bool):
        """Aktiverar/inaktiverar valideringsknappen"""
        self.validate_btn.setEnabled(enable)
