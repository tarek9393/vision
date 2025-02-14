"""Kamerafönster för Label Vision System"""

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QGroupBox,
    QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

import cv2
from src.camera.camera_manager import CameraManager
from src.vision.vision_system import VisionSystem
from src.gui.styles import apply_style, STYLES

logger = logging.getLogger(__name__)

class CameraWindow(QMainWindow):
    """Fönster för kameravalidering"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_camera()
        self.reference_data = None
        self.validation_count = 0
        self.max_validation_attempts = 3
        
        # Aktivera debug-läge för utveckling
        if hasattr(self, 'vision_system'):
            self.vision_system.toggle_debug_mode(True)
        
    def init_ui(self):
        """Initiera användargränssnittet"""
        # Centralt widget med huvudlayout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Övre panel med information och kontroller
        top_panel = QFrame()
        top_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        top_layout = QVBoxLayout(top_panel)
        top_layout.setSpacing(10)
        
        # Informationsruta
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        self.info_label = QLabel("Kund: -\nEtikett: -")
        apply_style(self.info_label, 'label')
        self.info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label)
        
        # Status label
        self.status_label = QLabel("")
        apply_style(self.status_label, 'label')
        self.status_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.status_label)
        
        top_layout.addWidget(info_frame)
        
        # Kamerakontroller
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(10)
        
        # Kameraval med beskrivande text
        camera_layout = QVBoxLayout()
        camera_label = QLabel("Välj kamera:")
        apply_style(camera_label, 'label')
        camera_layout.addWidget(camera_label)
        
        self.camera_combo = QComboBox()
        apply_style(self.camera_combo, 'combo_box')
        self.camera_combo.setMinimumWidth(200)
        self.camera_combo.currentIndexChanged.connect(self.select_camera)
        camera_layout.addWidget(self.camera_combo)
        
        controls_layout.addLayout(camera_layout)
        controls_layout.addStretch()
        
        # Start/Stopp-knapp
        self.camera_button = QPushButton("Starta Kamera")
        apply_style(self.camera_button, 'action_button')
        self.camera_button.setMinimumWidth(150)
        self.camera_button.clicked.connect(self.toggle_camera)
        controls_layout.addWidget(self.camera_button)
        
        # Validera-knapp
        self.validate_button = QPushButton("Validera Etikett")
        apply_style(self.validate_button, 'action_button')
        self.validate_button.setMinimumWidth(150)
        self.validate_button.clicked.connect(self.validate_label)
        self.validate_button.setEnabled(False)
        controls_layout.addWidget(self.validate_button)
        
        top_layout.addWidget(controls_frame)
        main_layout.addWidget(top_panel)
        
        # Kameravy
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.camera_view = QLabel()
        self.camera_view.setMinimumSize(800, 600)
        self.camera_view.setAlignment(Qt.AlignCenter)
        apply_style(self.camera_view, 'camera_view')
        preview_layout.addWidget(self.camera_view)
        
        main_layout.addWidget(preview_frame)
        
        # Nedre panel med knappar
        bottom_panel = QFrame()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Tillbaka-knapp
        back_button = QPushButton("Tillbaka till start")
        apply_style(back_button, 'button')
        back_button.setMinimumWidth(150)
        back_button.clicked.connect(self.go_back)
        bottom_layout.addWidget(back_button)
        
        main_layout.addWidget(bottom_panel)
        
        # Applicera huvudfönstrets stil
        apply_style(self, 'main_window')
        
    def init_camera(self):
        """Initiera kamera"""
        try:
            self.camera_manager = CameraManager()
            self.vision_system = VisionSystem()
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.refresh_cameras()
        except Exception as e:
            logger.error(f"Fel vid initiering av kamera: {e}")
            QMessageBox.warning(self, "Varning", "Kunde inte initiera kamera")
            
    def refresh_cameras(self):
        """Uppdatera lista över tillgängliga kameror"""
        try:
            self.camera_combo.clear()
            cameras = self.camera_manager.get_available_cameras()
            self.camera_combo.addItems([f"Kamera {i}" for i in range(len(cameras))])
        except Exception as e:
            logger.error(f"Fel vid uppdatering av kameralista: {e}")
            
    def select_camera(self, index):
        """Välj kamera"""
        try:
            if self.timer.isActive():
                self.stop_camera()
            self.camera_manager.connect(index)
        except Exception as e:
            logger.error(f"Fel vid val av kamera: {e}")
            
    def toggle_camera(self):
        """Starta/stoppa kamera"""
        try:
            if self.timer.isActive():
                self.stop_camera()
            else:
                self.start_camera()
        except Exception as e:
            logger.error(f"Fel vid start/stopp av kamera: {e}")
            
    def start_camera(self):
        """Starta kamera"""
        try:
            if self.camera_manager.connect(self.camera_combo.currentIndex()):
                self.timer.start(30)  # ~30 FPS
                self.camera_button.setText("Stoppa Kamera")
                self.validate_button.setEnabled(True)
                logger.info("Kamera startad")
        except Exception as e:
            logger.error(f"Fel vid start av kamera: {e}")
            QMessageBox.warning(self, "Varning", "Kunde inte starta kamera")
            
    def stop_camera(self):
        """Stoppa kamera"""
        try:
            self.timer.stop()
            self.camera_manager.disconnect()
            self.camera_button.setText("Starta Kamera")
            self.validate_button.setEnabled(False)
            self.camera_view.clear()
            logger.info("Kamera stoppad")
        except Exception as e:
            logger.error(f"Fel vid stopp av kamera: {e}")
            
    def update_frame(self):
        """Uppdatera kamerabild"""
        try:
            frame = self.camera_manager.get_frame()
            if frame is not None:
                # Konvertera från BGR till RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(self.camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.camera_view.setPixmap(scaled_pixmap)
                
                # Spara senaste frame för validering
                self.current_frame = frame
        except Exception as e:
            logger.error(f"Fel vid uppdatering av kamerabild: {e}")
            self.stop_camera()
            
    def set_reference_data(self, customer_id, label_id):
        """Sätt referensdata för validering"""
        try:
            self.reference_data = {
                'customer_id': customer_id,
                'label_id': label_id
            }
            if hasattr(self, 'info_label'):
                self.info_label.setText(f"Kund: {customer_id}\nEtikett: {label_id}")
            self.validation_count = 0
            self.update_status("Klar att validera etikett", 'label')
        except Exception as e:
            logger.error(f"Fel vid uppdatering av info_label: {e}")
            
    def validate_label(self):
        """Validera etikett mot referensdata"""
        try:
            if not hasattr(self, 'current_frame'):
                self.update_status("Ingen kamerabild tillgänglig", 'status_error')
                return
                
            if not self.reference_data:
                self.update_status("Ingen referensetikett vald", 'status_error')
                return
                
            # Öka valideringsräknaren
            self.validation_count += 1
            
            # Utför validering med vision system
            result = self.vision_system.validate_label(
                self.current_frame,
                self.reference_data['label_id']
            )
            
            if result['valid']:
                self.update_status(
                    f" Etikett validerad!\n"
                    f"Likhet: {result['similarity']:.1%}",
                    'status_ok'
                )
                # TODO: Logga resultatet i databasen
            else:
                if self.validation_count >= self.max_validation_attempts:
                    error_details = (
                        f" Etikett ogiltig efter {self.max_validation_attempts} försök\n"
                        f"Fel: {result['error']}\n"
                        f"Likhet: {result.get('similarity', 0):.1%}"
                    )
                    if 'extracted' in result:
                        error_details += f"\nLäst text: {result['extracted'][:100]}..."
                    self.update_status(error_details, 'status_error')
                    # TODO: Logga felet i databasen
                else:
                    remaining = self.max_validation_attempts - self.validation_count
                    warning_details = (
                        f" Etikett ogiltig. {remaining} försök kvar\n"
                        f"Fel: {result['error']}\n"
                        f"Likhet: {result.get('similarity', 0):.1%}"
                    )
                    if 'extracted' in result:
                        warning_details += f"\nLäst text: {result['extracted'][:100]}..."
                    self.update_status(warning_details, 'status_warning')
                    
        except Exception as e:
            logger.error(f"Fel vid validering av etikett: {e}")
            self.update_status(f"Fel vid validering: {str(e)}", 'status_error')
            
    def update_status(self, message, style='label'):
        """Uppdatera statusmeddelande"""
        try:
            self.status_label.setText(message)
            apply_style(self.status_label, style)
        except Exception as e:
            logger.error(f"Fel vid uppdatering av status: {e}")
            
    def go_back(self):
        """Gå tillbaka till startsidan"""
        try:
            self.stop_camera()
            if self.parent():
                self.parent().stack.setCurrentIndex(0)
        except Exception as e:
            logger.error(f"Fel vid återgång till startsida: {e}")
            
    def closeEvent(self, event):
        """Hantera stängning av fönster"""
        try:
            self.stop_camera()
            event.accept()
        except Exception as e:
            logger.error(f"Fel vid stängning av fönster: {e}")
