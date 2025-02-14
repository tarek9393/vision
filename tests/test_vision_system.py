"""Test av Label Vision System"""

import sys
import os
import cv2
import numpy as np
import unittest
from pathlib import Path

# Lägg till src till Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.vision.image_processing import ImageProcessor
from src.vision.object_detection import ObjectDetector
from src.camera.camera_manager import CameraManager
from src.nicelabel.client import NiceLabelClient

class TestVisionSystem(unittest.TestCase):
    """Testfall för vision system"""
    
    def setUp(self):
        """Förbered test"""
        self.image_processor = ImageProcessor()
        self.object_detector = ObjectDetector()
        self.camera_manager = CameraManager()
        self.nicelabel_client = NiceLabelClient()
        
        # Skapa testmapp om den inte finns
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
    def test_camera_connection(self):
        """Testa kameraanslutning"""
        # Testa anslutning
        connected = self.camera_manager.connect()
        self.assertTrue(connected, "Kunde inte ansluta till kamera")
        
        # Testa inställningar
        settings = {
            'exposure': -6,
            'brightness': 50
        }
        self.camera_manager.update_settings(settings)
        current_settings = self.camera_manager.get_settings()
        self.assertEqual(current_settings['exposure'], -6)
        self.assertEqual(current_settings['brightness'], 50)
        
        # Testa bildtagning
        frame = self.camera_manager.get_frame()
        self.assertIsNotNone(frame, "Kunde inte ta bild")
        self.assertEqual(len(frame.shape), 3, "Bilden har fel format")
        
    def test_image_processing(self):
        """Testa bildbehandling"""
        # Skapa testbild
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), 2)
        
        # Testa kantdetektering
        edges, _ = self.image_processor.detect_edges(test_image)
        self.assertIsNotNone(edges, "Kantdetektering misslyckades")
        
        # Testa perspektivkorrigering
        corrected = self.image_processor.correct_perspective(test_image)
        self.assertIsNotNone(corrected, "Perspektivkorrigering misslyckades")
        
        # Testa debug-visualisering
        debug_view = self.image_processor.debug_visualization(test_image)
        self.assertIsNotNone(debug_view, "Debug-visualisering misslyckades")
        
    def test_object_detection(self):
        """Testa objektdetektering"""
        # Skapa testbild med streckkod
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Testa streckkodsläsning
        barcodes = self.object_detector.read_barcodes(test_image)
        self.assertIsInstance(barcodes, list, "Streckkodsläsning returnerade fel typ")
        
        # Testa YOLO-modell (om tillgänglig)
        if self.object_detector.model is not None:
            detections = self.object_detector.detect_objects(test_image)
            self.assertIsInstance(detections, list, "Objektdetektering returnerade fel typ")
            
    def test_nicelabel_integration(self):
        """Testa NiceLabel-integration"""
        # Testa anslutning
        self.assertTrue(self.nicelabel_client.test_connection(), "Kunde inte ansluta till NiceLabel")
        
        # Testa hämtning av etikettlista
        labels = self.nicelabel_client.get_label_list()
        self.assertIsInstance(labels, list, "Kunde inte hämta etikettlista")
        
        # Om det finns etiketter, testa hämtning av data
        if labels:
            label_data = self.nicelabel_client.get_label_data(labels[0])
            self.assertIsInstance(label_data, dict, "Kunde inte hämta etikettdata")
            
    def test_full_validation_flow(self):
        """Testa hela valideringsflödet"""
        # Anslut kamera
        self.camera_manager.connect()
        
        # Ta bild
        frame = self.camera_manager.get_frame()
        self.assertIsNotNone(frame, "Kunde inte ta bild")
        
        # Bearbeta bild
        processed = frame.copy()
        if self.image_processor:
            edges, _ = self.image_processor.detect_edges(processed)
            processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
        # Detektera objekt och streckkoder
        detections = []
        if self.object_detector:
            detections.extend(self.object_detector.read_barcodes(processed))
            if self.object_detector.model:
                detections.extend(self.object_detector.detect_objects(processed))
                
        # Validera mot NiceLabel
        if detections and self.nicelabel_client:
            # Simulera validering mot första detektionen
            detection = detections[0]
            if 'data' in detection:  # Om det är en streckkod
                result = self.nicelabel_client.validate_label(detection['data'])
                self.assertIsInstance(result, bool, "Validering returnerade fel typ")
                
    def tearDown(self):
        """Städa upp efter test"""
        self.camera_manager.disconnect()
        
if __name__ == '__main__':
    unittest.main()
