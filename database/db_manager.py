"""Databashanterare för Label Vision System"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Hanterar databasoperationer för Label Vision System"""
    
    def __init__(self, db_path: str = "data/label_vision.db"):
        """Initiera databashanteraren"""
        try:
            # Säkerställ att databaskatalogen finns
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            self.db_path = db_path
            self.init_database()
            logger.info(f"Initialized database at: {db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
            
    def init_database(self):
        """Initiera databasschema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Skapa tabell för valideringsresultat
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    label_name TEXT NOT NULL,
                    customer_id TEXT NOT NULL,
                    expected_text TEXT,
                    detected_text TEXT,
                    is_valid BOOLEAN NOT NULL,
                    confidence REAL NOT NULL,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Skapa index för snabbare sökningar
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_validation_customer 
                ON validation_results(customer_id)
                """)
                
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_validation_timestamp 
                ON validation_results(timestamp)
                """)
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database schema: {str(e)}")
            raise
            
    def save_validation_result(self, result: Dict) -> int:
        """Spara ett valideringsresultat till databasen"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Konvertera metadata till JSON
                metadata = json.dumps(result.get('metadata', {}))
                
                cursor.execute("""
                INSERT INTO validation_results (
                    timestamp, image_path, label_name, customer_id,
                    expected_text, detected_text, is_valid, confidence,
                    error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result['timestamp'],
                    result['image_path'],
                    result['label_name'],
                    result['customer_id'],
                    result.get('expected_text', ''),
                    result.get('detected_text', ''),
                    result['valid'],
                    result['confidence'],
                    result.get('error', ''),
                    metadata
                ))
                
                result_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Saved validation result with ID: {result_id}")
                return result_id
                
        except Exception as e:
            logger.error(f"Error saving validation result: {str(e)}")
            raise
            
    def get_validation_results(self, 
                             customer_id: Optional[str] = None,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             valid_only: bool = False,
                             limit: int = 100) -> List[Dict]:
        """Hämta valideringsresultat med filter"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM validation_results WHERE 1=1"
                params = []
                
                if customer_id:
                    query += " AND customer_id = ?"
                    params.append(customer_id)
                    
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)
                    
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)
                    
                if valid_only:
                    query += " AND is_valid = 1"
                    
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Konvertera rader till dictionary
                results = []
                for row in rows:
                    result = dict(row)
                    result['metadata'] = json.loads(result['metadata'])
                    results.append(result)
                    
                logger.info(f"Retrieved {len(results)} validation results")
                return results
                
        except Exception as e:
            logger.error(f"Error getting validation results: {str(e)}")
            raise
            
    def get_statistics(self, 
                      customer_id: Optional[str] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> Dict:
        """Hämta statistik över valideringsresultat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_valid THEN 1 ELSE 0 END) as valid_count,
                    AVG(CASE WHEN is_valid THEN 1 ELSE 0 END) * 100 as success_rate,
                    AVG(confidence) as avg_confidence
                FROM validation_results 
                WHERE 1=1
                """
                
                params = []
                
                if customer_id:
                    query += " AND customer_id = ?"
                    params.append(customer_id)
                    
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)
                    
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)
                    
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                stats = {
                    'total_validations': row[0],
                    'valid_count': row[1],
                    'success_rate': round(row[2], 2),
                    'average_confidence': round(row[3], 2)
                }
                
                logger.info(f"Retrieved statistics: {stats}")
                return stats
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise
            
    def delete_old_results(self, days: int = 30) -> int:
        """Ta bort gamla valideringsresultat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Beräkna datum för borttagning
                cutoff_date = (datetime.now()
                             .replace(hour=0, minute=0, second=0, microsecond=0)
                             .timestamp() - (days * 24 * 60 * 60))
                
                cursor.execute("""
                DELETE FROM validation_results 
                WHERE strftime('%s', timestamp) < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Deleted {deleted_count} old validation results")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error deleting old results: {str(e)}")
            raise
