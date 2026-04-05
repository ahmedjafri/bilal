from datetime import datetime, timezone
from typing import List

from bilal.azan_config import AzanConfigLoader
from .praytimes import PrayTimes
from .azan_loader import AzanLoader, Azan, Salat


class CalcAzanLoader(AzanLoader):
    """Azan loader that calculates prayer times using praytimes.py"""

    def __init__(self, config_loader: AzanConfigLoader):
        """
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
        """
        self.config_loader = config_loader

        # Get timezone offset
        self.timezone = int(
            datetime.now(timezone.utc).astimezone().utcoffset().total_seconds() / 3600
        )

    def _get_pray_times(self) -> PrayTimes:
        return PrayTimes(self.config_loader.getConfig().calculation_method)

    def get_azans_for_day(self, date: datetime = datetime.now()) -> List[Azan]:
        """Calculate prayer times for a given date using praytimes.py"""
        # Get prayer times as a dictionary
        times = self._get_pray_times().getTimes(
            (date.year, date.month, date.day),
            (
                self.config_loader.getConfig().latitude,
                self.config_loader.getConfig().longitude,
            ),
            self.timezone,
        )

        # Convert to Azan objects
        return [
            Azan(Salat.FAJR, self._parse_time(date, times["fajr"])),
            Azan(Salat.ZUHR, self._parse_time(date, times["dhuhr"])),
            Azan(Salat.ASR, self._parse_time(date, times["asr"])),
            Azan(Salat.MAGHRIB, self._parse_time(date, times["maghrib"])),
            Azan(Salat.ISHA, self._parse_time(date, times["isha"])),
        ]

    def _parse_time(self, date: datetime, time_str: str) -> datetime:
        """Convert time string from praytimes to datetime"""
        hour, minute = map(int, time_str.split(":"))
        return datetime(date.year, date.month, date.day, hour, minute)
