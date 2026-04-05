import subprocess
import platform
import os
from logging import Logger
from threading import Lock
from typing import List, Optional
from datetime import datetime
import random
from importlib import resources

from bilal.azan_config import AzanConfigLoader

class AzanPlayer:
    azans_file_path: str
    logger: Logger

    """
    A class responsible for managing the playback of Azans.

    Attributes:
        file_path (str): The file path to the Azan audio files.
        logger (Logger): The logger instance for logging messages.
        azan_config (AzanConfig): Configuration settings for Azan playback.
    """
    def __init__(self, config_loader: AzanConfigLoader, logger: Logger):
        self.logger = logger
        self.config_loader = config_loader
        self.azan_play_process = None
        self.azan_play_process_lock = Lock()

    def list_azan_filenames(self) -> List[str]:
        # Access the package's 'audio_files' folder
        audio_files_path = resources.files('bilal').joinpath('audio_files')

        # List all files in the 'audio_files' directory within the package
        return [
            f.name  # f.name will give you the file name (not the full path)
            for f in audio_files_path.iterdir()  # This lists all files in the directory
        ]

    def stop_azan(self):
        with self.azan_play_process_lock:
            if (
                self.azan_play_process is not None
                and self.azan_play_process.poll() is None
            ):
                self.azan_play_process.kill()


    def play_azan(
        self,
        bypass_quiet_hours: bool = False,
        azan_file: Optional[str] = None):
        if azan_file is None:
            # pick azan randomly
            azans = self.list_azan_filenames()
            azan_file = random.choice(azans)

        self.logger.info(f"Playing azan. file={azan_file}")
        with self.azan_play_process_lock:
            if (
                self.azan_play_process is not None
                and self.azan_play_process.poll() is None
            ):
                self.logger.warn("Couldn't play azan. There is already an azan playing")
                return

            if self.is_quiet_time(datetime.now()) and not bypass_quiet_hours:
                self.logger.warn("Observing quiet hours. Not playing azan.")
                return

            if "Linux" == platform.system():
                full_file_path = os.path.join(self.config_loader.getConfig().azan_audio_files_dir, azan_file)
                self.azan_play_process = subprocess.Popen(
                    ["aplay", "-Ddefault", full_file_path]
                )
            elif "Darwin" == platform.system():  # MacOS
                full_file_path = os.path.join(self.config_loader.getConfig().azan_audio_files_dir, azan_file)
                self.azan_play_process = subprocess.Popen(["afplay", full_file_path])

    def is_quiet_time(self, dt: datetime) -> bool:
                # check if weekday is 1..5
                if dt.isoweekday() in range(1, 6) and dt.hour in self.config_loader.getConfig().get_quiet_times():
                    return True
                else:
                    return False
