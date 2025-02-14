import os
import shutil
import logging
from src.models.nicelabel_manager import NiceLabelManager

def setup_logging():
    """Konfigurerar loggning"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('export_references.log')
        ]
    )
    return logging.getLogger(__name__)

def export_labels(source_dir: str, target_dir: str, logger: logging.Logger):
    """Exporterar alla .nlbl filer som PNG-bilder
    
    Args:
        source_dir: Källmapp med .nlbl filer
        target_dir: Målmapp för PNG-filer
        logger: Logger för att spåra framsteg
    """
    nlm = NiceLabelManager()
    
    # Räkna totalt antal filer för framstegsindikator
    total_files = sum(1 for root, _, files in os.walk(source_dir) 
                     for f in files if f.endswith('.nlbl'))
    processed_files = 0
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.nlbl'):
                # Skapa samma mappstruktur i målmappen
                rel_path = os.path.relpath(root, source_dir)
                target_path = os.path.join(target_dir, rel_path)
                os.makedirs(target_path, exist_ok=True)
                
                # Generera sökvägar
                source_file = os.path.join(root, file)
                target_file = os.path.join(
                    target_path,
                    os.path.splitext(file)[0] + '.png'
                )
                
                try:
                    # Exportera etiketten som PNG
                    preview = nlm.read_label_preview(source_file)
                    if preview:
                        with open(target_file, 'wb') as f:
                            f.write(preview)
                        logger.info(f"Exporterade: {target_file}")
                    else:
                        logger.error(f"Kunde inte exportera: {source_file}")
                except Exception as e:
                    logger.error(f"Fel vid export av {source_file}: {str(e)}")
                
                # Uppdatera framsteg
                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f"\rFramsteg: {progress:.1f}% ({processed_files}/{total_files})", 
                      end='', flush=True)
    
    print("\nExport klar!")

def main():
    logger = setup_logging()
    
    # Definiera sökvägar
    label_dir = "Labels"
    reference_dir = "References"
    
    # Skapa målmappen om den inte finns
    os.makedirs(reference_dir, exist_ok=True)
    
    logger.info(f"Startar export från {label_dir} till {reference_dir}")
    export_labels(label_dir, reference_dir, logger)
    logger.info("Export slutförd")

if __name__ == '__main__':
    main()
