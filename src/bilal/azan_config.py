import copy
import json
from typing import List

class AzanConfig:
    # Hours between which to play azan quietly
    # Not inclusive. If end is 18 then it means that an azan at
    # 18:15 would not be in quiet hours
    quiet_times_start: int
    quiet_times_end: int

    azan_audio_files_dir: str
    azan_loader_local_dir: str
    calculation_method: str
    latitude: float
    longitude: float

    # equality operator
    def __eq__(self, other) :
        return self.__dict__ == other.__dict__

    def get_quiet_times(self) -> range:
        return range(self.quiet_times_start, self.quiet_times_end)

    @staticmethod
    def defaultConfig():
        config: AzanConfig = AzanConfig()
        config.quiet_times_start = 9
        config.quiet_times_end = 18
        config.azan_audio_files_dir = "./audio_files/"
        config.azan_loader_local_dir = "./prayer_times/"
        config.calculation_method = "MWL"

        # seattle
        config.latitude = 47.606209
        config.longitude = -122.332069

        return config

class AzanConfigLoader:
    _config: AzanConfig
    _config_file_path: str

    def __init__(self, config_file_path):
        self._config_file_path = config_file_path

        # load from file
        self._config = self._load_config()

    def _load_config(self) -> AzanConfig:
        try:
            with open(self._config_file_path, 'r') as config_file:
                config_dict = json.load(config_file)
                config = AzanConfig.defaultConfig()
                config.__dict__.update(config_dict)
                return config
        except (FileNotFoundError):
            return AzanConfig.defaultConfig()

    def _save_config(self):
        with open(self._config_file_path, 'w') as config_file:
            json.dump(self._config.__dict__, config_file, indent=2)

    def getConfig(self) -> AzanConfig:
        self._load_config()
        return copy.copy(self._config)

    def setConfig(self, config: AzanConfig):
        if self._config != self._load_config():
            raise Exception("Config has changed since last loaded")


        self._config = config
        self._save_config()
