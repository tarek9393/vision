"""API-integration med NiceLabel"""

import requests
from typing import Dict, Optional
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Ladda miljövariabler
load_dotenv()

class LabelAPI:
    """Hanterar kommunikation med NiceLabel API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initierar API-klienten"""
        self.base_url = base_url or os.getenv('NICELABEL_API_URL', 'http://localhost:5000/api')
        self.api_key = os.getenv('NICELABEL_API_KEY')
        
    def get_label_data(self, label_id: str) -> Dict:
        """Hämtar etikettdata från NiceLabel"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            response = requests.get(
                f"{self.base_url}/labels/{label_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Fel vid hämtning av etikettdata: {str(e)}")
            
    def validate_label(self, label_id: str, detected_text: str, detected_barcode: Optional[str] = None) -> Dict:
        """Validerar detekterad etikettdata mot NiceLabel"""
        try:
            data = {
                'label_id': label_id,
                'detected_text': detected_text,
                'detected_barcode': detected_barcode,
                'timestamp': datetime.now().isoformat()
            }
            
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            response = requests.post(
                f"{self.base_url}/validate",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Fel vid validering av etikett: {str(e)}")
            
    def report_inspection(self, inspection_data: Dict) -> Dict:
        """Rapporterar inspektionsresultat till NiceLabel"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            response = requests.post(
                f"{self.base_url}/inspections",
                json=inspection_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Fel vid rapportering av inspektion: {str(e)}")
            
class APIError(Exception):
    """Anpassat fel för API-relaterade problem"""
    pass
