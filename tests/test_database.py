"""Tester för databashantering"""

import unittest
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from models.database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Körs före varje test"""
        self.test_db_path = "test_label_vision.db"
        self.db = Database(self.test_db_path)
        
    def tearDown(self):
        """Körs efter varje test"""
        # Stäng alla databasanslutningar
        self.db = None
        
        # Ta bort testdatabasen
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def test_log_validation_success(self):
        """Testa att logga en lyckad validering"""
        self.db.log_validation(
            label_id="TEST001",
            status=True,
            confidence=0.95,
            error_message=None,
            image_path="test.jpg"
        )
        
        # Hämta historik och verifiera
        history = self.db.get_validation_history(limit=1)
        self.assertEqual(len(history), 1)
        
        record = history[0]
        self.assertEqual(record[1], "TEST001")  # label_id
        self.assertTrue(record[2])  # status
        self.assertAlmostEqual(record[3], 0.95)  # confidence
        
    def test_log_validation_failure(self):
        """Testa att logga en misslyckad validering"""
        error_msg = "Kunde inte hitta text"
        self.db.log_validation(
            label_id="TEST002",
            status=False,
            confidence=0.3,
            error_message=error_msg
        )
        
        history = self.db.get_validation_history(limit=1)
        self.assertEqual(len(history), 1)
        
        record = history[0]
        self.assertEqual(record[1], "TEST002")
        self.assertFalse(record[2])
        self.assertEqual(record[4], error_msg)
        
    def test_get_validation_history_with_filter(self):
        """Testa att filtrera valideringshistorik"""
        # Lägg till några testdata
        self.db.log_validation("LABEL1", True, 0.9)
        self.db.log_validation("LABEL2", True, 0.8)
        self.db.log_validation("LABEL1", False, 0.4)
        
        # Filtrera på LABEL1
        history = self.db.get_validation_history(label_id="LABEL1")
        self.assertEqual(len(history), 2)
        for record in history:
            self.assertEqual(record[1], "LABEL1")
            
    def test_get_statistics(self):
        """Testa statistikfunktionen"""
        # Lägg till blandade resultat
        self.db.log_validation("TEST1", True, 0.9)
        self.db.log_validation("TEST2", True, 0.8)
        self.db.log_validation("TEST3", False, 0.3, "Fel 1")
        self.db.log_validation("TEST4", False, 0.2, "Fel 2")
        self.db.log_validation("TEST5", False, 0.1, "Fel 1")
        
        stats = self.db.get_statistics(days=1)
        
        self.assertEqual(stats['total_validations'], 5)
        self.assertEqual(stats['successful_validations'], 2)
        self.assertAlmostEqual(stats['success_rate'], 40.0)
        self.assertGreater(stats['average_confidence'], 0)
        
        # Kontrollera vanligaste felen
        common_errors = dict(stats['common_errors'])
        self.assertEqual(common_errors['Fel 1'], 2)
        self.assertEqual(common_errors['Fel 2'], 1)
        
    def test_cleanup_old_records(self):
        """Testa borttagning av gamla poster"""
        # Lägg till några poster med olika datum
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            
            # En gammal post (100 dagar)
            old_date = (datetime.now() - timedelta(days=100)).isoformat()
            cursor.execute("""
                INSERT INTO label_validations 
                (timestamp, label_id, status, confidence)
                VALUES (?, ?, ?, ?)
            """, (old_date, "OLD", True, 0.9))
            
            # En ny post (dagens datum)
            new_date = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO label_validations 
                (timestamp, label_id, status, confidence)
                VALUES (?, ?, ?, ?)
            """, (new_date, "NEW", True, 0.9))
            
            conn.commit()
            
        # Rensa poster äldre än 30 dagar
        self.db.cleanup_old_records(days=30)
        
        # Verifiera att bara den nya posten finns kvar
        history = self.db.get_validation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][1], "NEW")
        
    def test_database_error_handling(self):
        """Testa felhantering vid databasfel"""
        # Skapa en trasig databasanslutning
        broken_db = Database("nonexistent/path/db.sqlite")
        
        # Testa att funktionerna hanterar fel korrekt
        broken_db.log_validation("TEST", True, 0.9)  # Ska inte krascha
        history = broken_db.get_validation_history()  # Ska returnera tom lista
        self.assertEqual(history, [])
        
        stats = broken_db.get_statistics()  # Ska returnera standardvärden
        self.assertEqual(stats['total_validations'], 0)
        self.assertEqual(stats['success_rate'], 0)

if __name__ == '__main__':
    unittest.main()
