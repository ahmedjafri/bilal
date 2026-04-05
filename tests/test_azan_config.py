import json
import os
import tempfile
from bilal.azan_config import AzanConfig, AzanConfigLoader


class TestAzanConfig:
    def test_default_config(self):
        config = AzanConfig.defaultConfig()
        assert config.latitude == 47.606209
        assert config.longitude == -122.332069
        assert config.calculation_method == "MWL"
        assert config.quiet_times_start == 9
        assert config.quiet_times_end == 18

    def test_get_quiet_times(self):
        config = AzanConfig.defaultConfig()
        quiet = config.get_quiet_times()
        assert 9 in quiet
        assert 17 in quiet
        assert 18 not in quiet

    def test_equality(self):
        a = AzanConfig.defaultConfig()
        b = AzanConfig.defaultConfig()
        assert a == b
        b.latitude = 0.0
        assert a != b


class TestAzanConfigLoader:
    def test_loads_default_when_file_missing(self):
        loader = AzanConfigLoader("/nonexistent/config.json")
        config = loader.getConfig()
        assert config.calculation_method == "MWL"

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({}, f)
            tmp_path = f.name

        try:
            loader = AzanConfigLoader(tmp_path)
            config = loader.getConfig()
            config.latitude = 21.4225
            config.longitude = 39.8262
            loader.setConfig(config)

            loader2 = AzanConfigLoader(tmp_path)
            config2 = loader2.getConfig()
            assert config2.latitude == 21.4225
            assert config2.longitude == 39.8262
        finally:
            os.unlink(tmp_path)

    def test_load_partial_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"latitude": 33.0}, f)
            tmp_path = f.name

        try:
            loader = AzanConfigLoader(tmp_path)
            config = loader.getConfig()
            assert config.latitude == 33.0
            # other fields should have defaults
            assert config.calculation_method == "MWL"
        finally:
            os.unlink(tmp_path)
