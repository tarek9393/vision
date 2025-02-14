"""
Förbereder bilder för annotering och träning av YOLO-modell.
Detta script:
1. Kopierar bilder från Labels-mappen till dataset/images
2. Delar upp bilderna i train/val/test set
3. Skapar en struktur för annoteringar
"""

import os
import shutil
import random
from pathlib import Path
import logging
import cv2

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatasetPreparer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.labels_dir = self.base_dir / "Labels"
        self.dataset_dir = self.base_dir / "dataset"
        self.train_dir = self.dataset_dir / "images" / "train"
        self.val_dir = self.dataset_dir / "images" / "val"
        self.test_dir = self.dataset_dir / "images" / "test"
        
        # Skapa alla nödvändiga mappar
        for dir in [self.train_dir, self.val_dir, self.test_dir]:
            dir.mkdir(parents=True, exist_ok=True)
            
    def collect_images(self):
        """Samla alla bilder från Labels-mappen"""
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png']:
            image_files.extend(list(self.labels_dir.rglob(f'*{ext}')))
        return image_files
        
    def prepare_image(self, image_path):
        """Förbereder en bild för annotering"""
        try:
            # Läs bilden
            img = cv2.imread(str(image_path))
            if img is None:
                logger.error(f"Kunde inte läsa bild: {image_path}")
                return None
                
            # Standardisera storlek (behåll proportioner)
            max_size = 1024
            height, width = img.shape[:2]
            if height > max_size or width > max_size:
                if height > width:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                else:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                img = cv2.resize(img, (new_width, new_height))
                
            return img
            
        except Exception as e:
            logger.error(f"Fel vid bildbehandling av {image_path}: {e}")
            return None
            
    def split_dataset(self, images, train_split=0.7, val_split=0.2):
        """Dela upp bilder i train/val/test"""
        random.shuffle(images)
        n = len(images)
        train_n = int(n * train_split)
        val_n = int(n * val_split)
        
        train_images = images[:train_n]
        val_images = images[train_n:train_n + val_n]
        test_images = images[train_n + val_n:]
        
        return train_images, val_images, test_images
        
    def copy_and_prepare_images(self, image_list, target_dir):
        """Kopiera och förbered bilder till målmappen"""
        for img_path in image_list:
            try:
                # Förbered bilden
                prepared_img = self.prepare_image(img_path)
                if prepared_img is None:
                    continue
                    
                # Skapa nytt filnamn
                new_name = f"{img_path.parent.name}_{img_path.name}"
                target_path = target_dir / new_name
                
                # Spara bilden
                cv2.imwrite(str(target_path), prepared_img)
                logger.info(f"Sparade {new_name} i {target_dir.name}")
                
            except Exception as e:
                logger.error(f"Fel vid kopiering av {img_path}: {e}")
                
    def prepare_dataset(self):
        """Huvudfunktion för att förbereda datasetet"""
        try:
            # Samla alla bilder
            logger.info("Samlar bilder...")
            images = self.collect_images()
            
            if not images:
                logger.error("Inga bilder hittades!")
                return
                
            logger.info(f"Hittade {len(images)} bilder")
            
            # Dela upp i train/val/test
            train_imgs, val_imgs, test_imgs = self.split_dataset(images)
            
            # Kopiera och förbered bilder
            logger.info("Kopierar och förbereder träningsbilder...")
            self.copy_and_prepare_images(train_imgs, self.train_dir)
            
            logger.info("Kopierar och förbereder valideringsbilder...")
            self.copy_and_prepare_images(val_imgs, self.val_dir)
            
            logger.info("Kopierar och förbereder testbilder...")
            self.copy_and_prepare_images(test_imgs, self.test_dir)
            
            logger.info("Dataset förberett och klart!")
            logger.info(f"Train: {len(train_imgs)} bilder")
            logger.info(f"Val: {len(val_imgs)} bilder")
            logger.info(f"Test: {len(test_imgs)} bilder")
            
        except Exception as e:
            logger.error(f"Ett fel uppstod: {e}")

if __name__ == "__main__":
    preparer = DatasetPreparer()
    preparer.prepare_dataset()
