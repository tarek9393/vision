from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QFrame, QGridLayout, QToolBar,
                           QStatusBar, QTreeWidget, QTreeWidgetItem, QDialog,
                           QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon
import cv2
import logging
import time
from datetime import datetime
from vision.vision_system import VisionSystem
from models.database import Database

class VisionWindow(QMainWindow):
    """Huvudfönster för vision-systemet"""
    
    inspection_started = pyqtSignal(bool)
    
    def __init__(self, vision_system, label_id=None, parent=None):
        """Initierar VisionWindow"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initierar VisionWindow")
        
        self.vision_system = vision_system
        self.logger.debug("Vision system initierat")
        
        self.database = Database()
        self.logger.debug("Databas initierad")
        
        self.label_id = label_id
        self.inspection_active = False
        self.inspection_results = {}
        self.start_time = None
        
        # Hämta etikettdata direkt
        try:
            if self.label_id is not None:
                self.label_info = self.vision_system.get_label_data(label_id)
                self.vision_system.set_current_label(self.label_info)
            else:
                self.label_info = None
        except Exception as e:
            self.logger.error(f"Kunde inte hämta etikettdata: {str(e)}")
            self.label_info = None
            
        self.init_ui()
        self.setup_camera()
        
    def init_ui(self):
        """Initierar användargränssnittet"""
        self.setWindowTitle('Etikett Vision System')
        self.setGeometry(100, 100, 1200, 800)
        
        # Skapa huvudwidget och layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Vänster panel
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Mitten sektion
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 4)
        
        # Höger panel
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # Skapa verktygsfält
        self.create_toolbar()
        
        # Skapa statusfält
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Anslut signaler
        self.inspection_started.connect(self.on_inspection_started)
        
    def create_left_panel(self):
        """Skapar vänster panel med resultat"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Resultatträd
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(['Resultat', 'Värde'])
        
        # Lägg till resultatgrupper
        self.result_groups = {
            'Analysresultat': ['Mönster', 'Alfanumeriska tecken', 'Streckkod'],
            'Position': ['Dödmärkeposition', 'Övre sensor', 'OCR Övre text']
        }
        
        self.result_items = {}
        for group_name, items in self.result_groups.items():
            group = QTreeWidgetItem([group_name])
            self.results_tree.addTopLevelItem(group)
            for item in items:
                item_widget = QTreeWidgetItem(group, [item, ''])
                self.result_items[item] = item_widget
                
        layout.addWidget(self.results_tree)
        return panel
        
    def create_center_panel(self):
        """Skapar mittenpanel med kamerabild och detaljvy"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Kamerabild
        self.camera_view = QLabel()
        self.camera_view.setMinimumSize(800, 500)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("background-color: black;")
        layout.addWidget(self.camera_view)
        
        # Nedre panel med detaljerade resultat
        bottom_panel = QFrame()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Skapa resultatvyer
        self.detail_views = {}
        results = ['Streckkod', 'Gradering', 'OCR Övre text']
        for result in results:
            result_frame = QFrame()
            result_layout = QVBoxLayout(result_frame)
            
            # Resultatbild
            image_label = QLabel()
            image_label.setFixedSize(150, 100)
            image_label.setStyleSheet("background-color: white;")
            result_layout.addWidget(image_label)
            
            # Resultattext
            text_label = QLabel(result)
            text_label.setAlignment(Qt.AlignCenter)
            result_layout.addWidget(text_label)
            
            self.detail_views[result] = {
                'frame': image_label,
                'text': text_label
            }
            
            bottom_layout.addWidget(result_frame)
            
        layout.addWidget(bottom_panel)
        return panel
        
    def create_right_panel(self):
        """Skapar höger panel med inspektionsdetaljer"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Inspektionsresultat
        self.inspection_label = QLabel('Inspektion')
        self.inspection_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.inspection_label)
        
        # Status och tidsinfo
        self.time_labels = {}
        status_info = [
            ('Förfluten tid:', '0 ms'),
            ('Svarstid:', '0 ms'),
            ('Beslutstid:', '0 ms')
        ]
        
        for label, value in status_info:
            info_layout = QHBoxLayout()
            label_widget = QLabel(label)
            value_widget = QLabel(value)
            info_layout.addWidget(label_widget)
            info_layout.addWidget(value_widget)
            layout.addLayout(info_layout)
            self.time_labels[label] = value_widget
            
        layout.addStretch()
        return panel
        
    def create_toolbar(self):
        """Skapar verktygsfältet"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Skapa actions med ikoner och funktioner
        actions = {
            'Start': self.toggle_inspection,
            'Inspektion': self.show_inspection_settings,
            'Info': self.show_info,
            'Konfiguration': self.show_configuration,
            'Referenser': self.manage_references,
            'Statistik': self.show_statistics,
            'Inställningar': self.show_settings,
            'Logg': self.show_log
        }
        
        for name, func in actions.items():
            action = toolbar.addAction(name)
            action.triggered.connect(func)
            
    def setup_camera(self):
        """Initierar kameran och timer för uppdatering"""
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera)
        self.camera_timer.start(30)  # Uppdatera var 30:e millisekund
        
    def update_camera(self):
        """Uppdaterar kamerabilden och analysresultat"""
        try:
            frame = self.vision_system.get_camera_frame()
            if frame is not None:
                # Konvertera frame till QImage
                height, width = frame.shape[:2]
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                # Skala om bilden för att passa i vyn
                scaled_pixmap = QPixmap.fromImage(q_image).scaled(
                    self.camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.camera_view.setPixmap(scaled_pixmap)
                
                # Uppdatera resultat om inspektion är aktiv
                if self.inspection_active and self.label_info:
                    self.inspection_results = self.vision_system.analyze_frame(frame)
                    self.update_results(self.inspection_results)
                    
        except Exception as e:
            self.logger.error(f"Fel vid kamerauppdatering: {str(e)}")
            
    def update_results(self, results):
        """Uppdaterar resultatvyn med nya resultat"""
        if not results:
            return
            
        # Uppdatera resultatträdet
        for key, value in results.items():
            if key in self.result_items:
                self.result_items[key].setText(1, str(value))
                
        # Uppdatera detaljvyer
        for view_name, view in self.detail_views.items():
            if view_name in results:
                # Här skulle vi uppdatera bilderna för varje detaljvy
                view['text'].setText(f"{view_name}: {results[view_name]}")
                
        # Uppdatera tidsinformation
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_labels['Förfluten tid:'].setText(f"{int(elapsed * 1000)} ms")
            
    def toggle_inspection(self):
        """Växlar inspektion på/av"""
        self.inspection_active = not self.inspection_active
        if self.inspection_active:
            self.start_time = time.time()
            self.statusBar.showMessage("Inspektion startad")
            self.inspection_started.emit(True)
        else:
            self.start_time = None
            self.statusBar.showMessage("Inspektion stoppad")
            self.inspection_started.emit(False)
            
    def on_inspection_started(self, started):
        """Hanterar när inspektion startas/stoppas"""
        if started:
            self.inspection_label.setStyleSheet("color: green;")
            self.inspection_label.setText("Inspektion aktiv")
        else:
            self.inspection_label.setStyleSheet("color: black;")
            self.inspection_label.setText("Inspektion")
            
    def show_inspection_settings(self):
        """Visar inställningar för inspektion"""
        QMessageBox.information(self, "Inspektionsinställningar", 
                              "Här kommer inställningar för inspektion")
        
    def show_info(self):
        """Visar information om systemet"""
        QMessageBox.information(self, "Systeminformation", 
                              f"Etikett Vision System\nVald etikett: {self.label_id}")
        
    def show_configuration(self):
        """Visar konfigurationsinställningar"""
        QMessageBox.information(self, "Konfiguration", 
                              "Här kommer konfigurationsinställningar")
        
    def manage_references(self):
        """Hanterar referenser"""
        QMessageBox.information(self, "Referenser", 
                              "Här kommer referenshantering")
        
    def show_statistics(self):
        """Visar statistik"""
        QMessageBox.information(self, "Statistik", 
                              "Här kommer statistik över inspektioner")
        
    def show_settings(self):
        """Visar systeminställningar"""
        QMessageBox.information(self, "Inställningar", 
                              "Här kommer systeminställningar")
        
    def show_log(self):
        """Visar systemloggen"""
        QMessageBox.information(self, "Systemlogg", 
                              "Här kommer systemloggen")
        
    def save_inspection_result(self):
        """Sparar inspektionsresultat till databasen"""
        if self.inspection_results:
            try:
                self.database.save_inspection_result(
                    label_id=self.label_id,
                    timestamp=datetime.now(),
                    results=self.inspection_results
                )
            except Exception as e:
                self.logger.error(f"Kunde inte spara inspektionsresultat: {str(e)}")
                
    def closeEvent(self, event):
        """Hanterar stängning av fönstret"""
        self.camera_timer.stop()
        self.inspection_active = False
        event.accept()
