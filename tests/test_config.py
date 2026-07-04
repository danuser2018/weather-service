import pytest
from app.config.config import Settings

def test_config_missing_latitude_raises():
    settings = Settings(LATITUDE=None, LONGITUDE=-3.7038)
    with pytest.raises(ValueError) as excinfo:
        settings.validate_required()
    assert "LATITUDE and LONGITUDE must be configured" in str(excinfo.value)

def test_config_missing_longitude_raises():
    settings = Settings(LATITUDE=40.4168, LONGITUDE=None)
    with pytest.raises(ValueError) as excinfo:
        settings.validate_required()
    assert "LATITUDE and LONGITUDE must be configured" in str(excinfo.value)

def test_config_valid():
    settings = Settings(LATITUDE=40.4168, LONGITUDE=-3.7038)
    # Should not raise any exception
    settings.validate_required()
