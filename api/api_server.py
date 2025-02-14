"""NiceLabel API Server"""

from flask import Flask, jsonify, request
import logging
import os
import json
from pathlib import Path

app = Flask(__name__)

# Konfigurera loggning
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ladda mockdata från JSON-fil
def load_mock_data():
    try:
        data_path = Path(__file__).parent / "mock_data.json"
        if not data_path.exists():
            # Skapa mock-data om filen inte finns
            mock_data = {
                "customers": [
                    {"id": "1", "name": "Lantmännen Unibake SV"},
                    {"id": "2", "name": "Lantmännen Unibake NO"},
                    {"id": "3", "name": "Lantmännen Unibake Polen"},
                    {"id": "4", "name": "Lantmännen Unibake Baltic"}
                ],
                "labels": {
                    "1": [
                        {"id": "101", "name": "226580 YD Vanilj-Kanelbulle", "text": "Vanilj-Kanelbulle\nVikt: 100g\nBäst före: 2024-12-31"},
                        {"id": "102", "name": "226581 YD Kanelbulle", "text": "Kanelbulle\nVikt: 90g\nBäst före: 2024-12-31"}
                    ],
                    "2": [
                        {"id": "201", "name": "326580 YD Skillingsbolle", "text": "Skillingsbolle\nVekt: 95g\nBest før: 2024-12-31"}
                    ],
                    "3": [
                        {"id": "301", "name": "426580 YD Bulka Cynamonowa", "text": "Bulka Cynamonowa\nWaga: 95g\nNajlepiej przed: 2024-12-31"}
                    ],
                    "4": [
                        {"id": "401", "name": "526580 YD Cinnamon Roll", "text": "Cinnamon Roll\nWeight: 95g\nBest before: 2024-12-31"}
                    ]
                }
            }
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(mock_data, f, ensure_ascii=False, indent=4)
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fel vid laddning av mock-data: {e}")
        return {"customers": [], "labels": {}}

# Ladda mock-data
MOCK_DATA = load_mock_data()

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Hämta alla kunder"""
    return jsonify(MOCK_DATA["customers"])

@app.route('/api/customers/<customer_id>/labels', methods=['GET'])
def get_customer_labels(customer_id):
    """Hämta etiketter för en specifik kund"""
    if customer_id in MOCK_DATA["labels"]:
        return jsonify(MOCK_DATA["labels"][customer_id])
    return jsonify([])

@app.route('/api/labels/<label_id>', methods=['GET'])
def get_label_data(label_id):
    """Hämta data för en specifik etikett"""
    for labels in MOCK_DATA["labels"].values():
        for label in labels:
            if label["id"] == label_id:
                return jsonify(label)
    return jsonify({"error": "Label not found"}), 404

if __name__ == '__main__':
    app.run(port=5000)
