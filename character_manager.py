"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
   valid_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15},
    }

    if character_class not in valid_classes:
        raise InvalidCharacterClassError("Invalid character class: {}".format(character_class))

    base = valid_classes[character_class]

    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": base["health"],
        "max_health": base["health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],           # list of item names (strings)
        "active_quests": [],       # list of quest ids
        "completed_quests": [],    # list of quest ids
    }

    return character

def _ensure_save_dir(save_directory):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

def _list_to_csv(lst):
    if not lst:
        return ""
    return ",".join(lst)

def _csv_to_list(s):
    if s is None:
        return []
    s = s.strip()
    if s == "":
        return []
    return [item for item in s.split(",") if item != ""]

def save_character(character, save_directory="data/save_games"):
  _ensure_save_dir(save_directory)

    filename = os.path.join(save_directory, "{}_save.txt".format(character["name"]))

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("NAME: {}\n".format(character.get("name", "")))
            f.write("CLASS: {}\n".format(character.get("class", "")))
            f.write("LEVEL: {}\n".format(character.get("level", 1)))
            f.write("HEALTH: {}\n".format(character.get("health", 0)))
            f.write("MAX_HEALTH: {}\n".format(character.get("max_health", 0)))
            f.write("STRENGTH: {}\n".format(character.get("strength", 0)))
            f.write("MAGIC: {}\n".format(character.get("magic", 0)))
            f.write("EXPERIENCE: {}\n".format(character.get("experience", 0)))
            f.write("GOLD: {}\n".format(character.get("gold", 0)))
            f.write("INVENTORY: {}\n".format(_list_to_csv(character.get("inventory", []))))
            f.write("ACTIVE_QUESTS: {}\n".format(_list_to_csv(character.get("active_quests", []))))
            f.write("COMPLETED_QUESTS: {}\n".format(_list_to_csv(character.get("completed_quests", []))))
        return True
    except (PermissionError, IOError):
        raise

def load_character(character_name, save_directory="data/save_games"):
  filename = os.path.join(save_directory, "{}_save.txt".format(character_name))

    if not os.path.exists(filename):
        raise CharacterNotFoundError("Save file not found for '{}'".format(character_name))

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except Exception:
        raise SaveFileCorruptedError("Unable to read save file for '{}'".format(character_name))

    # Parse lines of form "KEY: value"
    data = {}
    for line in raw_lines:
        line = line.rstrip("\n")
        if ":" not in line:
            # invalid format
            raise InvalidSaveDataError("Invalid line in save file: '{}'".format(line))
        parts = line.split(":", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        data[key] = value

    try:
        # Required keys
        required_keys = [
            "NAME", "CLASS", "LEVEL", "HEALTH", "MAX_HEALTH",
            "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD",
            "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"
        ]
        for rk in required_keys:
            if rk not in data:
                raise InvalidSaveDataError("Missing field '{}' in save file".format(rk))

        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
            "experience": int(data["EXPERIENCE"]),
            "gold": int(data["GOLD"]),
            "inventory": _csv_to_list(data.get("INVENTORY", "")),
            "active_quests": _csv_to_list(data.get("ACTIVE_QUESTS", "")),
            "completed_quests": _csv_to_list(data.get("COMPLETED_QUESTS", "")),
        }

        # Validate structure and types
        validate_character_data(character)

        return character

    except ValueError:
        # int() conversion failure
        raise InvalidSaveDataError("Numeric value invalid in save for '{}'".format(character_name))
    except InvalidSaveDataError:
        raise
    except Exception:
        raise InvalidSaveDataError("Unexpected error parsing save for '{}'".format(character_name))


def list_saved_characters(save_directory="data/save_games"):
   if not os.path.exists(save_directory):
        return []

    try:
        files = os.listdir(save_directory)
    except Exception:
        return []

    names = []
    for fname in files:
        if fname.endswith("_save.txt"):
            # strip suffix
            name = fname[:-len("_save.txt")]
            names.append(name)
    return names

def delete_character(character_name, save_directory="data/save_games"):
    filename = os.path.join(save_directory, "{}_save.txt".format(character_name))
    if not os.path.exists(filename):
        raise CharacterNotFoundError("No save file for '{}'".format(character_name))

    try:
        os.remove(filename)
        return True
    except Exception:
        raise

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    if is_character_dead(character):
        raise CharacterDeadError("Cannot gain experience: character is dead")

    if not isinstance(xp_amount, int):
        # keep simple type rules (chapters 2-12)
        raise ValueError("xp_amount must be an integer")

    character["experience"] += xp_amount

    while character["experience"] >= character["level"] * 100:
        needed = character["level"] * 100
        character["experience"] -= needed
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]

    return character["level"]

def add_gold(character, amount):
    if not isinstance(amount, int):
        raise ValueError("amount must be integer")

    new_total = character.get("gold", 0) + amount
    if new_total < 0:
        raise ValueError("Gold would become negative")

    character["gold"] = new_total
    return character["gold"]

def heal_character(character, amount):
    if amount <= 0:
        return 0

    before = character.get("health", 0)
    max_h = character.get("max_health", before)
    new_h = before + amount
    if new_h > max_h:
        new_h = max_h
    character["health"] = new_h
    return character["health"] - before

def is_character_dead(character):
    return int(character.get("health", 0)) <= 0

def revive_character(character):
       if not is_character_dead(character):
        return False

    half = character.get("max_health", 0) // 2
    if half <= 0:
        half = 1
    character["health"] = half
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
     required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for key in required_fields:
        if key not in character:
            raise InvalidSaveDataError("Missing required field: '{}'".format(key))

    numeric_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]
    for key in numeric_fields:
        if not isinstance(character[key], int):
            raise InvalidSaveDataError("Field '{}' must be an integer".format(key))

    list_fields = ["inventory", "active_quests", "completed_quests"]
    for key in list_fields:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError("Field '{}' must be a list".format(key))

    if character["level"] < 1:
        raise InvalidSaveDataError("Level must be >= 1")

    if character["max_health"] <= 0:
        raise InvalidSaveDataError("max_health must be > 0")

    if character["health"] < 0 or character["health"] > character["max_health"]:
        raise InvalidSaveDataError("health must be between 0 and max_health")

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")

