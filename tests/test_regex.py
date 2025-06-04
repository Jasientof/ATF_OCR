import pytest
from pathlib import Path
import re
import json


def load_regex_patterns():
    """Load regex patterns from the JSON configuration."""
    cfg_path = Path(__file__).resolve().parents[1] / "src" / "config.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: re.compile(v) for k, v in data["regex_patterns"].items()}


regex_patterns = load_regex_patterns()

@pytest.mark.parametrize("test_id,should_match", [
    ("01A1234", True),
    ("O1B1C2D", True),
    ("99ZAB12", True),
    ("O1ABCD", False),
    ("Z9A1234", False),
    ("01a1234", False),
])
def test_man_regex(test_id, should_match):
    pattern = regex_patterns["MAN"]
    assert bool(pattern.fullmatch(test_id)) is should_match

@pytest.mark.parametrize("test_id,should_match", [
    ("2345678", True),
    ("5345678", True),
    ("5999999", True),
    ("6345678", False),
    ("2A34567", False),
    ("234567", False),
])
def test_scania_regex(test_id, should_match):
    pattern = regex_patterns["SCANIA"]
    assert bool(pattern.fullmatch(test_id)) is should_match

@pytest.mark.parametrize("test_id,should_match", [
    ("1234567890", True),
    ("1999999999", True),
    ("1223456789", True),
    ("2234567890", False),
    ("1A23456789", False),
    ("12345678901", False),
])
def test_mercedes_regex(test_id, should_match):
    pattern = regex_patterns["MERCEDES"]
    assert bool(pattern.fullmatch(test_id)) is should_match

@pytest.mark.parametrize("test_id,should_match", [
    ("A123456", True),
    ("B654321", True),
    ("A000000", True),
    ("C123456", False),
    ("A12345", False),
    ("A1234567", False),
])
def test_volvo_regex(test_id, should_match):
    pattern = regex_patterns["VOLVO"]
    assert bool(pattern.fullmatch(test_id)) is should_match
