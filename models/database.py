"""Databashantering för Label Vision System"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
import json
from pathlib import Path

class Database:
    """Hanterar databasoperationer för vision-systemet"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initierar databasen"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vision_system.db')
            
        # Skapa data-katalogen om den inte finns
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._create_tables()
        
    def _create_tables(self):
        """Skapar nödvändiga tabeller"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Skapa inspektionstabellen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    label_id TEXT,
                    status TEXT NOT NULL,
                    confidence REAL,
                    detected_text TEXT,
                    detected_barcode TEXT,
                    error_message TEXT,
                    image_path TEXT,
                    metadata TEXT
                )
            ''')
            
            # Skapa statistiktabellen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_inspections INTEGER DEFAULT 0,
                    passed_inspections INTEGER DEFAULT 0,
                    failed_inspections INTEGER DEFAULT 0,
                    average_confidence REAL DEFAULT 0.0,
                    UNIQUE(date)
                )
            ''')
            
            conn.commit()
            
    def log_inspection(self, inspection_data: Dict) -> int:
        """Loggar ett inspektionsresultat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Konvertera metadata till JSON
            if 'metadata' in inspection_data and isinstance(inspection_data['metadata'], dict):
                inspection_data['metadata'] = json.dumps(inspection_data['metadata'])
                
            # Sätt timestamp om det inte finns
            if 'timestamp' not in inspection_data:
                inspection_data['timestamp'] = datetime.now().isoformat()
                
            # Bygg SQL-frågan dynamiskt
            fields = ', '.join(inspection_data.keys())
            placeholders = ', '.join(['?' for _ in inspection_data])
            values = tuple(inspection_data.values())
            
            cursor.execute(
                f'INSERT INTO inspections ({fields}) VALUES ({placeholders})',
                values
            )
            
            # Uppdatera statistik
            self._update_statistics(
                inspection_data['status'] == 'OK',
                inspection_data.get('confidence', 0.0)
            )
            
            return cursor.lastrowid
            
    def _update_statistics(self, passed: bool, confidence: float):
        """Uppdaterar statistik för dagens datum"""
        today = datetime.now().date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Försök uppdatera befintlig statistik
            cursor.execute('''
                INSERT INTO statistics (date, total_inspections, passed_inspections,
                                     failed_inspections, average_confidence)
                VALUES (?, 1, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_inspections = total_inspections + 1,
                    passed_inspections = passed_inspections + ?,
                    failed_inspections = failed_inspections + ?,
                    average_confidence = (average_confidence * total_inspections + ?) /
                                       (total_inspections + 1)
            ''', (today, int(passed), int(not passed), confidence,
                  int(passed), int(not passed), confidence))
                  
    def get_statistics(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict:
        """Hämtar statistik för ett datumintervall"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM statistics'
            params = []
            
            if start_date or end_date:
                query += ' WHERE'
                if start_date:
                    query += ' date >= ?'
                    params.append(start_date.date())
                if end_date:
                    if start_date:
                        query += ' AND'
                    query += ' date <= ?'
                    params.append(end_date.date())
                    
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return {
                'total_inspections': sum(row[2] for row in rows),
                'passed_inspections': sum(row[3] for row in rows),
                'failed_inspections': sum(row[4] for row in rows),
                'average_confidence': sum(row[5] * row[2] for row in rows) /
                                   sum(row[2] for row in rows) if rows else 0.0
            }
            
    def get_recent_inspections(self, limit: int = 100) -> List[Dict]:
        """Hämtar de senaste inspektionerna"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM inspections
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
    def save_inspection_image(self, image_path: str, inspection_id: int):
        """Sparar sökväg till inspektionsbild"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inspections
                SET image_path = ?
                WHERE id = ?
            ''', (image_path, inspection_id))
            
    def get_inspection_by_id(self, inspection_id: int) -> Optional[Dict]:
        """Hämtar en specifik inspektion"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM inspections WHERE id = ?', (inspection_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
