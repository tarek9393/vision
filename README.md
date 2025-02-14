# Label Vision System

Ett avancerat system för etikettinspektion med maskininlärning och bildbehandling.

## Installation

1. Installera Python 3.8 eller högre
2. Installera beroenden:
```bash
pip install -r requirements.txt
```
3. Installera Tesseract OCR:
   - Ladda ner från: https://github.com/UB-Mannheim/tesseract/wiki
   - Installera till: `C:\Program Files\Tesseract-OCR`

## Träna modellen

För bästa resultat behöver YOLO-modellen tränas på dina specifika etiketter:

1. Samla bilder på etiketter i `dataset/images/train` och `dataset/images/val`
2. Annotera bilderna med [CVAT](https://www.cvat.ai/) eller [LabelImg](https://github.com/tzutalin/labelImg)
3. Kör träningsscriptet:
```bash
python train_yolo.py
```

Modellen kommer att sparas i `runs/detect/label_detection/weights/best.pt`

## Användning

1. Starta systemet:
```bash
python start.py
```

2. Använd gränssnittet för att:
   - Välja kamera
   - Starta/stoppa inspektion
   - Se resultat och statistik i realtid

## Funktioner

- Automatisk etikettdetektering med YOLO
- OCR-textigenkänning med Tesseract
- Streckkodsavläsning
- Realtidsvisualisering
- Statistik och loggning

## Felsökning

Om inga detektioner hittas:
1. Kontrollera att kameran är korrekt ansluten
2. Träna modellen på dina specifika etiketter
3. Justera belysning och kameraposition

## Utveckling

För att bidra till projektet:
1. Forka repositoryt
2. Skapa en feature branch
3. Commita dina ändringar
4. Öppna en pull request
