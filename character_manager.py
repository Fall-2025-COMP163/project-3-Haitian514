"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
import json
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError,
    InsufficientResourcesError
)

def _get_save_path(character_name, save_directory):
    return os.path.join(save_directory, f"{character_name}_save.json")
# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================


def create_character(name, character_class):
    class_stats = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage":    {"health": 80,  "strength": 8,  "magic": 20},
        "Rogue":   {"health": 90,  "strength": 12, "magic": 10},
        "Cleric":  {"health": 100, "strength": 10, "magic": 15}
    }

    # Validate character_class first (case-insensitive)
    formatted_class = character_class.title()

    if formatted_class not in class_stats:
        raise InvalidCharacterClassError(f"'{character_class}' is not a valid class.")

    base = class_stats[formatted_class]
    
    # All characters start with standard defaults
    new_character = {
        "name": name,
        "class": formatted_class,
        "level": 1,
        "health": base["health"],
        "max_health": base["health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    
    return new_character

def save_character(character, save_directory="data/save_games"):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    file_path = _get_save_path(character['name'], save_directory)
    
    # Validate character data before saving
    validate_character_data(character)

    try:
        with open(file_path, 'w') as f:
            json.dump(character, f, indent=4)
        return True
    except (IOError, PermissionError) as e:
        # Re-raise file system errors if necessary
        raise e

def load_character(character_name, save_directory="data/save_games"):
    file_path = _get_save_path(character_name, save_directory)
    
    # Check if file exists → CharacterNotFoundError
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"No save file found for '{character_name}'")

    character_data = None
    
    try:
        # Try to read file → SaveFileCorruptedError
        with open(file_path, 'r') as f:
            character_name = json.load(f)
    except json.JSONDecodeError as e:
        raise SaveFileCorruptedError(f"Save file for '{character_name}' is corrupted or unreadable.")
    except IOError as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")

    # Validate data format → InvalidSaveDataError
    try:
        validate_character_data(character_data)
    except InvalidSaveDataError as e:
        # Re-raise with context that loading failed due to invalid data
        raise InvalidSaveDataError(f"Data in save file for '{character_name}' is invalid: {e}")
        

def list_saved_characters(save_directory="data/save_games"):
    if not os.path.exists(save_directory):
        return []

    try:
        files = os.listdir(save_directory)
        character_names = []
        for filename in files:
            if filename.endswith("_save.json"):
                # Extract character name by removing '_save.json'
                name = filename[:-10] 
                character_names.append(name)
        return character_names
    except OSError:
        # Handle cases where directory exists but is inaccessible
        return []
  
def delete_character(character_name, save_directory="data/save_games"):
    file_path = _get_save_path(character_name, save_directory)

    # Verify file exists before attempting deletion
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Cannot delete: No save file found for '{character_name}'")
    
    try:
        os.remove(file_path)
        return True
    except OSError as e:
        # Catch unexpected filesystem errors during deletion
        print(f"Error deleting file {file_path}: {e}")
        return False
# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    if is_character_dead(character):
        raise CharacterDeadError(f"{character['name']} is dead and cannot gain experience.")

    # Add experience
    character['experience'] += xp_amount
    
    while True:
        level_up_xp = character['level'] * 100
        
        # Check for level up
        if character['experience'] >= level_up_xp:
            # Update stats on level up
            character['level'] += 1
            character['experience'] -= level_up_xp
            character['max_health'] += 10
            character['strength'] += 2
            character['magic'] += 2
            
            # Restore health to max_health
            character['health'] = character['max_health']
        else:
            break

def add_gold(character, amount):
    new_gold = character['gold'] + amount
    
    # Check that result won't be negative (Needed for test_character_gold_management)
    if new_gold < 0:
        raise InsufficientResourcesError(
            f"Insufficient gold. Cannot spend {abs(amount)} gold. Current: {character['gold']}"
        )
        # Note: The test file uses 'ValueError', but in a real system, 
        # 'InsufficientResourcesError' or similar is better, assuming it inherits from ValueError 
        # or the test is wrong. Using InsufficientResourcesError as per the test file structure.

    character['gold'] = new_gold
    return character['gold']

def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    # TODO: Implement healing
    current_health = character['health']
    max_health = character['max_health']
    
    # Calculate how much healing is needed/possible
    needed_healing = max_health - current_health
    actual_heal = min(amount, needed_healing)
    
    # Update character health
    character['health'] += actual_heal
    
    return actual_heal

def is_character_dead(character):
    return character['health'] <= 0

def revive_character(character):
    if not is_character_dead(character):
        return False
        
    # Restore health to half of max_health
    revive_health = character['max_health'] // 2
    character['health'] = revive_health
    
    return True

# ============================================================================
# VALIDATION
# ============================================================================
def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    # TODO: Implement validation
    required_fields = {
        "name": str, "class": str, "level": int, "health": int, 
        "max_health": int, "strength": int, "magic": int, 
        "experience": int, "gold": int, "inventory": list,
        "active_quests": list, "completed_quests": list
    }

    for field, expected_type in required_fields.items():
        # Check all required keys exist
        if field not in character:
            raise InvalidSaveDataError(f"Missing required field: '{field}'")
        
        value = character[field]
        
        # Check that types match
        if not isinstance(value, expected_type):
             raise InvalidSaveDataError(f"Field '{field}' has wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Additional check for numeric fields to ensure they aren't negative (where appropriate)
        if expected_type in (int, float) and field not in ('gold', 'experience'):
            if value < 0:
                 raise InvalidSaveDataError(f"Numeric field '{field}' must be non-negative.")

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

