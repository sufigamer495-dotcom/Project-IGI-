import pytest
from weather_manager import WeatherManager, Seasons

def test_weather_seasons():
    wm = WeatherManager()

    # Check Winter
    wm.set_season(Seasons.WINTER)
    assert wm.current_season == Seasons.WINTER
    assert wm.profiles[Seasons.WINTER]['particles'] == 'snow'
    assert len(wm.snow_particles) > 0
    assert len(wm.leaf_particles) == 0

    # Check Spring
    wm.set_season(Seasons.SPRING)
    assert wm.current_season == Seasons.SPRING
    assert wm.profiles[Seasons.SPRING]['particles'] == 'none'
    assert len(wm.snow_particles) == 0
    assert len(wm.leaf_particles) == 0

    # Check Summer
    wm.set_season(Seasons.SUMMER)
    assert wm.current_season == Seasons.SUMMER
    assert wm.profiles[Seasons.SUMMER]['particles'] == 'none'

    # Check Autumn
    wm.set_season(Seasons.AUTUMN)
    assert wm.current_season == Seasons.AUTUMN
    assert wm.profiles[Seasons.AUTUMN]['particles'] == 'leaves'
    assert len(wm.leaf_particles) > 0
    assert len(wm.snow_particles) == 0
