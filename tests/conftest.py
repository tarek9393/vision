"""Test configuration for pytest"""

import os
import sys
from pathlib import Path

# Lägg till src-mappen i Python-sökvägen
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))
