import winsound
import threading
import logging
from typing import Optional

class SoundManager:
    def __init__(self):
        """Initierar ljudhanteraren"""
        self.logger = logging.getLogger(__name__)
        self._current_thread: Optional[threading.Thread] = None
        
    def play_error(self):
        """Spelar upp ett felljud"""
        try:
            if self._current_thread and self._current_thread.is_alive():
                return
                
            self._current_thread = threading.Thread(
                target=self._play_error_sound,
                daemon=True
            )
            self._current_thread.start()
            
        except Exception as e:
            self.logger.error(f"Kunde inte spela upp felljud: {str(e)}")
            
    def _play_error_sound(self):
        """Spelar upp Windows felljud"""
        try:
            winsound.PlaySound(
                "SystemHand",
                winsound.SND_ALIAS | winsound.SND_ASYNC
            )
        except Exception as e:
            self.logger.error(f"Fel vid uppspelning av ljud: {str(e)}")
            
    def play_success(self):
        """Spelar upp ett godkänt-ljud"""
        try:
            if self._current_thread and self._current_thread.is_alive():
                return
                
            self._current_thread = threading.Thread(
                target=self._play_success_sound,
                daemon=True
            )
            self._current_thread.start()
            
        except Exception as e:
            self.logger.error(f"Kunde inte spela upp godkänt-ljud: {str(e)}")
            
    def _play_success_sound(self):
        """Spelar upp Windows godkänt-ljud"""
        try:
            winsound.PlaySound(
                "SystemAsterisk",
                winsound.SND_ALIAS | winsound.SND_ASYNC
            )
        except Exception as e:
            self.logger.error(f"Fel vid uppspelning av ljud: {str(e)}")
