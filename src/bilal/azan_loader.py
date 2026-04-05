from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List
from enum import Enum


class Salat(Enum):
    FAJR = 1
    ZUHR = 2
    ASR = 3
    MAGHRIB = 4
    ISHA = 5


class Azan:
    salat: Salat
    azan_time: datetime

    def __init__(self, salat: Salat, azan_time: datetime):
        self.azan_time = azan_time
        self.salat = salat

    def to_dict(self) -> Dict:
        return {
            "salat": self.salat.name,  # Convert Enum to string (e.g., "FAJR")
            "azan_time": self.azan_time.isoformat(),  # Convert datetime to string
        }

    def __str__(self):
        return f"{self.salat} @ {self.azan_time}"


class AzanLoader(ABC):
    @abstractmethod
    def get_azans_for_day(self, date: datetime = datetime.now()) -> List[Azan]:
        """Get all the azans for a day"""
        pass

    def get_next_azan(self, dt: datetime = datetime.now()) -> Azan:
        """Get the next azan time relative to current_datetime"""
        todays_azans = self.get_azans_for_day(dt)

        # Sort azans by time
        sorted_azans = sorted(todays_azans, key=lambda a: a.azan_time)

        # Find next azan today
        for azan in sorted_azans:
            if azan.azan_time > dt:
                return azan

        # If no azans left today, get first azan tomorrow
        tomorrow = dt + timedelta(days=1)
        tomorrows_azans = self.get_azans_for_day(tomorrow)
        return tomorrows_azans[0]
