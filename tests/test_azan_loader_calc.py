from datetime import datetime
from bilal.azan_loader_calc import CalcAzanLoader
from bilal.azan_loader import Salat
from bilal.azan_config import AzanConfig


class FakeConfigLoader:
    """Config loader that doesn't need a file."""

    def __init__(self, config: AzanConfig):
        self._config = config

    def getConfig(self):
        return self._config

    def setConfig(self, config):
        self._config = config


def _make_config(lat=47.606209, lng=-122.332069, method="MWL"):
    config = AzanConfig.defaultConfig()
    config.latitude = lat
    config.longitude = lng
    config.calculation_method = method
    return config


class TestCalcAzanLoader:
    def test_returns_five_prayers(self):
        config = _make_config()
        loader = CalcAzanLoader(FakeConfigLoader(config))
        azans = loader.get_azans_for_day(datetime(2026, 4, 5))
        assert len(azans) == 5

    def test_prayer_order(self):
        config = _make_config()
        loader = CalcAzanLoader(FakeConfigLoader(config))
        azans = loader.get_azans_for_day(datetime(2026, 4, 5))
        salats = [a.salat for a in azans]
        assert salats == [Salat.FAJR, Salat.ZUHR, Salat.ASR, Salat.MAGHRIB, Salat.ISHA]

    def test_different_methods_produce_different_fajr(self):
        loader_mwl = CalcAzanLoader(FakeConfigLoader(_make_config(method="MWL")))
        loader_isna = CalcAzanLoader(FakeConfigLoader(_make_config(method="ISNA")))

        azans_mwl = loader_mwl.get_azans_for_day(datetime(2026, 4, 5))
        azans_isna = loader_isna.get_azans_for_day(datetime(2026, 4, 5))

        # MWL uses 18 deg for fajr, ISNA uses 15 deg — times should differ
        assert azans_mwl[0].azan_time != azans_isna[0].azan_time
