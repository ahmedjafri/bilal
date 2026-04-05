from datetime import datetime
from bilal.azan_loader import Azan, AzanLoader, Salat


class StubAzanLoader(AzanLoader):
    """Concrete loader returning fixed times for testing."""

    def __init__(self, azans_by_day: dict):
        self._azans_by_day = azans_by_day

    def get_azans_for_day(self, date: datetime = datetime.now()):
        key = (date.year, date.month, date.day)
        return self._azans_by_day.get(key, [])


def _make_azan(salat, year, month, day, hour, minute):
    return Azan(salat, datetime(year, month, day, hour, minute))


class TestSalat:
    def test_enum_values(self):
        assert Salat.FAJR.value == 1
        assert Salat.ISHA.value == 5
        assert len(Salat) == 5


class TestAzan:
    def test_to_dict(self):
        azan = _make_azan(Salat.FAJR, 2026, 4, 5, 5, 30)
        d = azan.to_dict()
        assert d["salat"] == "FAJR"
        assert d["azan_time"] == "2026-04-05T05:30:00"

    def test_str(self):
        azan = _make_azan(Salat.MAGHRIB, 2026, 4, 5, 19, 45)
        assert "MAGHRIB" in str(azan)


class TestAzanLoader:
    def _day_azans(self, year, month, day):
        return [
            _make_azan(Salat.FAJR, year, month, day, 5, 0),
            _make_azan(Salat.ZUHR, year, month, day, 12, 30),
            _make_azan(Salat.ASR, year, month, day, 16, 0),
            _make_azan(Salat.MAGHRIB, year, month, day, 19, 30),
            _make_azan(Salat.ISHA, year, month, day, 21, 0),
        ]

    def test_get_next_azan_returns_upcoming(self):
        azans = {(2026, 4, 5): self._day_azans(2026, 4, 5)}
        loader = StubAzanLoader(azans)

        now = datetime(2026, 4, 5, 13, 0)
        next_azan = loader.get_next_azan(now)
        assert next_azan.salat == Salat.ASR

    def test_get_next_azan_wraps_to_tomorrow(self):
        today = (2026, 4, 5)
        tomorrow = (2026, 4, 6)
        azans = {
            today: self._day_azans(*today),
            tomorrow: self._day_azans(*tomorrow),
        }
        loader = StubAzanLoader(azans)

        now = datetime(2026, 4, 5, 22, 0)  # after isha
        next_azan = loader.get_next_azan(now)
        assert next_azan.salat == Salat.FAJR
        assert next_azan.azan_time.day == 6

    def test_get_next_azan_first_prayer(self):
        azans = {(2026, 4, 5): self._day_azans(2026, 4, 5)}
        loader = StubAzanLoader(azans)

        now = datetime(2026, 4, 5, 3, 0)  # before fajr
        next_azan = loader.get_next_azan(now)
        assert next_azan.salat == Salat.FAJR
