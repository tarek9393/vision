from src.models.nicelabel_manager import NiceLabelManager
from PIL import Image
import io

def test_preview():
    nlm = NiceLabelManager()
    label_path = r'Labels/Kartongetiketter/Baxt/100541 Hallonmunk SG Baxt.nlbl'
    preview = nlm.read_label_preview(label_path)
    if preview:
        Image.open(io.BytesIO(preview)).show()
        print("Förhandsgranskning skapad")
    else:
        print("Kunde inte skapa förhandsgranskning")

if __name__ == '__main__':
    test_preview()
