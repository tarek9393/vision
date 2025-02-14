"""Huvudfönster för Label Vision System"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGroupBox, QComboBox,
    QTextEdit
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

class MainWindow(QMainWindow):
    def __init__(self, camera=None, model=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Spara kamera och modell
        self.camera = camera
        self.model = model
        
        # Konfigurera fönstret
        self.setWindowTitle("Label Vision System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Skapa huvudwidget och layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Vänster panel (kamera och kontroller)
        left_panel = QWidget()
        layout.addWidget(left_panel, stretch=2)
        left_layout = QVBoxLayout(left_panel)
        
        # Kameravy
        self.image_label = QLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.image_label)
        
        # Kontrollpanel
        control_box = QGroupBox("Kontroller")
        control_layout = QVBoxLayout()
        
        # Kamerakontroller
        camera_layout = QHBoxLayout()
        self.camera_button = QPushButton("Stoppa kamera")
        self.camera_button.clicked.connect(self.toggle_camera)
        camera_layout.addWidget(self.camera_button)
        control_layout.addLayout(camera_layout)
        
        # Kundval och etikettval
        selection_layout = QHBoxLayout()
        
        # Kundval
        customer_layout = QVBoxLayout()
        customer_label = QLabel("Kund:")
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("Välj kund...")
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_combo)
        selection_layout.addLayout(customer_layout)
        
        # Etikettval
        label_layout = QVBoxLayout()
        label_type_label = QLabel("Etiketttyp:")
        self.label_type_combo = QComboBox()
        self.label_type_combo.addItem("Kartongetikett")
        label_layout.addWidget(label_type_label)
        label_layout.addWidget(self.label_type_combo)
        selection_layout.addLayout(label_layout)
        
        control_layout.addLayout(selection_layout)
        
        # Valideringsknapp
        self.validate_button = QPushButton("Validera etikett")
        self.validate_button.clicked.connect(self.validate_label)
        control_layout.addWidget(self.validate_button)
        
        control_box.setLayout(control_layout)
        left_layout.addWidget(control_box)
        
        # Höger panel (resultat)
        right_panel = QWidget()
        layout.addWidget(right_panel, stretch=1)
        right_layout = QVBoxLayout(right_panel)
        
        # Status
        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Status: Väntar...")
        status_layout.addWidget(self.status_label)
        status_box.setLayout(status_layout)
        right_layout.addWidget(status_box)
        
        # OCR-resultat
        ocr_box = QGroupBox("Detekterad text:")
        ocr_layout = QVBoxLayout()
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setFont(QFont('Arial', 12))
        ocr_layout.addWidget(self.text_result)
        ocr_box.setLayout(ocr_layout)
        right_layout.addWidget(ocr_box)
        
        # Valideringsresultat
        validation_box = QGroupBox("Validering:")
        validation_layout = QVBoxLayout()
        self.validation_result = QTextEdit()
        self.validation_result.setReadOnly(True)
        validation_layout.addWidget(self.validation_result)
        validation_box.setLayout(validation_layout)
        right_layout.addWidget(validation_box)
        
        # Timer för kamerauppdatering
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Uppdatera var 30:e millisekund
        
        # Starta kameran
        if self.camera:
            self.camera.start()
            
        self.logger.info("MainWindow initialized")
        
    def update_frame(self):
        """Uppdaterar kameravyn med senaste bilden"""
        try:
            # Ta en bild
            success, frame = self.camera.take_picture()
            if not success or frame is None:
                self.logger.error("Failed to capture frame")
                return
                
            self.logger.info("Frame captured successfully")
            
            # Kör bildanalys
            if self.model:
                result = self.model.detect(frame)
                self.logger.info(f"Detection result: {result}")
                
                # Använd den annoterade bilden om den finns
                if result and 'annotated_image' in result:
                    display_frame = result['annotated_image']
                    
                    # Uppdatera GUI med resultatet
                    self.update_display(display_frame, result)
                else:
                    self.logger.error("No annotated image in result")
                    self.update_display(frame)
            else:
                self.logger.warning("No model available")
                self.update_display(frame)
                
        except Exception as e:
            self.logger.error(f"Error in update_frame: {str(e)}")
            
    def update_display(self, frame: np.ndarray, result: Dict = None):
        """Uppdaterar GUI:t med bild och resultat
        
        Args:
            frame: Bildruta att visa
            result: Detektionsresultat från modellen
        """
        try:
            if frame is None:
                self.logger.error("No frame to display")
                return
                
            # Konvertera bilden till QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Skala bilden till rätt storlek
            scaled_pixmap = QPixmap.fromImage(q_img).scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Uppdatera bilden
            self.image_label.setPixmap(scaled_pixmap)
            
            # Uppdatera textresultat
            if result and result.get('success', False):
                # Visa detekterad text
                full_text = result.get('full_text', '')
                self.logger.info(f"Detected text: {full_text}")
                self.text_result.setPlainText(full_text)
                
                # Uppdatera status
                if full_text.strip():
                    self.status_label.setText("Status: OK")
                    self.status_label.setStyleSheet("color: green")
                else:
                    self.status_label.setText("Status: Ingen text hittad")
                    self.status_label.setStyleSheet("color: red")
            else:
                self.logger.warning("Detection failed or no result")
                self.status_label.setText("Status: Fel vid textdetektering")
                self.status_label.setStyleSheet("color: red")
                self.text_result.clear()
                
        except Exception as e:
            self.logger.error(f"Error in update_display: {str(e)}")
            
    def toggle_camera(self):
        """Växlar kameran mellan på/av"""
        if self.timer.isActive():
            self.timer.stop()
            self.camera_button.setText("Starta kamera")
        else:
            self.timer.start(30)
            self.camera_button.setText("Stoppa kamera")
            
    def validate_label(self):
        """Validerar den nuvarande etiketten"""
        # TODO: Implementera etikettvalidering
        pass
        
    def closeEvent(self, event):
        """Hanterar stängning av fönstret"""
        if self.camera:
            self.camera.stop()
        event.accept()
