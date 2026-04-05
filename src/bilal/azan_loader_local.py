import os
from datetime import datetime
from logging import Logger
from typing import Dict, List
from bilal.azan_loader import AzanLoader, Azan, Salat


class LocalAzanLoader(AzanLoader):

    def __init__(self, file_path: str, city: str, logger: Logger):
        self.azan_time_file_path = file_path
        self.city = city
        self.logger = logger
        self.year_cache: Dict[int, Dict[int, List[Azan]]] = {}
        ## We pick 2024 here because it's a leap year. The year section in the dates are
        ## irrelevant
        self._build_year_cache(2024)

    def _build_year_cache(self, year: int):
        """Build cache for all months in the year"""
        for month in range(1, 13):  # Months are 1-12
            self.year_cache[month] = self._get_month_azans(month, year)

    def _get_month_times_raw(self, month: int) -> Dict[int, Dict[Salat, str]]:
        """Get raw prayer times for a month from file"""
        month_name = datetime(2024, month, 1).strftime("%B").lower()
        file_name = f"{month_name}_{self.city}.txt"
        full_file_name = os.path.join(self.azan_time_file_path, file_name)
        monthy_time_dict: Dict[int, Dict[Salat, str]] = {}

        with open(full_file_name, "r") as f:
            for line in f:
                times = line.split(' ')
                day_times: Dict[Salat, str] = {
                    Salat.FAJR: f"{times[1]}:{times[2]}",
                    ## Sunrise skipped
                    Salat.ZUHR: f"{times[5]}:{times[6]}",
                    Salat.ASR: f"{times[7]}:{times[8]}",
                    Salat.MAGHRIB: f"{times[9]}:{times[10]}",
                    Salat.ISHA: f"{times[11]}:{times[12].rstrip()}"
                }
                monthy_time_dict[int(times[0])] = day_times

        return monthy_time_dict

    def get_azans_for_day(self, date: datetime = datetime.now()) -> List[Azan]:
        """Get all the azans for a specific day"""
        azans: List[Azan] = self.year_cache[date.month].get(date.day, [])

        # Adjust the year to match the passed in date
        for azan in azans:
            azan.azan_time = azan.azan_time.replace(year=date.year)

        return azans

    def _get_month_azans(self, month: int, year: int) -> Dict[int, List[Azan]]:
        """Get all azans for a month and cache them"""
        month_times = self._get_month_times_raw(month)
        azan_dict = {}

        for day, times in month_times.items():
            azan_dict[day] = []

            for salat in Salat:
                time_str = times[salat]
                time_parts = time_str.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                if len(time_parts
                       ) > 2 and time_parts[2] == "PM" and hour != 12:
                    hour += 12

                azan_time = datetime(year, month, day, hour, minute)
                azan_dict[day].append(Azan(salat, azan_time))

        return azan_dict
