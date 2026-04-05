from bilal.praytimes import PrayTimes


class TestPrayTimes:
    def test_get_times_returns_all_keys(self):
        pt = PrayTimes("MWL")
        times = pt.getTimes((2026, 4, 5), (47.6, -122.3), -7)
        expected_keys = {
            "imsak",
            "fajr",
            "sunrise",
            "dhuhr",
            "asr",
            "sunset",
            "maghrib",
            "isha",
            "midnight",
        }
        assert expected_keys == set(times.keys())

    def test_time_format(self):
        pt = PrayTimes("ISNA")
        times = pt.getTimes((2026, 6, 21), (47.6, -122.3), -7)
        # default 24h format should be HH:MM
        for key, val in times.items():
            assert ":" in val, f"{key} = {val} is not in HH:MM format"

    def test_methods_available(self):
        pt = PrayTimes()
        assert "MWL" in pt.methods
        assert "ISNA" in pt.methods
        assert "Jafari" in pt.methods

    def test_makkah_location(self):
        pt = PrayTimes("Makkah")
        times = pt.getTimes((2026, 1, 15), (21.4225, 39.8262), 3)
        # fajr should be in early morning hours
        hour = int(times["fajr"].split(":")[0])
        assert 4 <= hour <= 6
