import os
import json
import pytest

def test_levels_json_structure():
    json_path = "levels.json"
    assert os.path.exists(json_path), "levels.json file does not exist."

    with open(json_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, list), "levels.json should contain a list of levels."
    assert len(data) == 20, f"Expected 20 unique mission levels, found {len(data)}."

    valid_objective_types = {"HACK_TERMINAL", "ELIMINATE_TARGET", "RETRIEVE_INTEL", "DESTROY_OBJECTIVE"}
    valid_seasons = {"Winter", "Spring", "Summer", "Autumn"}

    level_numbers = set()
    for lvl in data:
        assert "level" in lvl
        assert lvl["level"] not in level_numbers, f"Duplicate level number {lvl['level']}"
        level_numbers.add(lvl["level"])

        assert "name" in lvl and len(lvl["name"]) > 0
        assert "season" in lvl and lvl["season"] in valid_seasons
        assert "objective_type" in lvl and lvl["objective_type"] in valid_objective_types
        assert "objective_text" in lvl and len(lvl["objective_text"]) > 0
        assert "player_spawn" in lvl and len(lvl["player_spawn"]) == 3
        assert "extraction_pos" in lvl and len(lvl["extraction_pos"]) == 3
        assert "structures" in lvl and len(lvl["structures"]) > 0
        assert "enemies" in lvl and len(lvl["enemies"]) > 0

        for st in lvl["structures"]:
            assert "type" in st
            assert "pos" in st and len(st["pos"]) == 3
            assert "scale" in st and len(st["scale"]) == 3

        for en in lvl["enemies"]:
            assert "pos" in en and len(en["pos"]) == 3
            assert "waypoints" in en and len(en["waypoints"]) >= 1
