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
    # Construct the full file path for a character's save file.
    return os.path.join(save_directory, f"{character_name}_save.json")

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    # Define base stats for each character class.
    class_stats = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage":    {"health": 80,  "strength": 8,  "magic": 20},
        "Rogue":   {"health": 90,  "strength": 12, "magic": 10},
        "Cleric":  {"health": 100, "strength": 10, "magic": 15}
    }

    # Format the class input for case-insensitive validation.
    formatted_class = character_class.title()

    # Check if the provided class is defined.
    if formatted_class not in class_stats:
        raise InvalidCharacterClassError(f"'{character_class}' is not a valid class.")

    # Get the base stats for the chosen class.
    base = class_stats[formatted_class]
    
    # All characters start with Level 1 and base resources.
    new_character = {
        'name': name.strip(),
        'class': formatted_class,
        'level': 1,
        'experience': 0,
        'gold': 100,
        
        # Current and Maximum health are set by the base stats.
        'health': base['health'],
        'max_health': base['health'], 
        'strength': base['strength'],
        'magic': base['magic'],
        
        # Initialize empty game lists.
        'inventory': [],
        'active_quests': [],
        'completed_quests': [],
        'equipped_weapon': None # Store ID of equipped item
    }
    
    return new_character

def save_character(character, save_directory="data/save_games"):
    # Ensure the save directory exists; create it if it doesn't.
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Validate the character data structure before saving.
    validate_character_data(character)

    # Get the full file path for saving.
    file_path = _get_save_path(character['name'], save_directory)

    # Open the file in write mode and dump the character dictionary as JSON.
    with open(file_path, 'w') as f:
        # Use indent=4 for readable, pretty-printed JSON.
        json.dump(character, f, indent=4)

    return True

def load_character(character_name, save_directory="data/save_games"):
    # Get the full file path for loading.
    file_path = _get_save_path(character_name, save_directory)

    # Check if the save file exists.
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Character '{character_name}' not found.")

    try:
        # Open the file in read mode.
        with open(file_path, 'r') as f:
            # Load the character data from the JSON file.
            character_data = json.load(f)
            
    # Handle JSON parsing errors (file structure is broken).
    except json.JSONDecodeError:
        raise SaveFileCorruptedError(f"Save file for '{character_name}' is corrupted (Invalid JSON).")
    # Handle file reading errors (e.g., permission issues).
    except IOError:
        raise SaveFileCorruptedError(f"Could not read save file for '{character_name}'.")

    # Validate the loaded data structure to ensure game stability.
    validate_character_data(character_data)
    
    return character_data

def get_saved_characters(save_directory="data/save_games"):
    # Check if the save directory exists.
    if not os.path.exists(save_directory):
        return []

    # Get a list of all files in the save directory.
    files = os.listdir(save_directory)

    # Filter the list to only include files ending in '_save.json'.
    # Strip the '_save.json' suffix to get the character name.
    # Return the list of names, sorted alphabetically.
    return sorted([f[:-10] for f in files if f.endswith("_save.json")])


# ============================================================================
# STAT & RESOURCE MANAGEMENT
# ============================================================================

def gain_experience(character, xp_amount):
    # Ensure XP amount is positive.
    if xp_amount <= 0:
        return

    # Add the earned XP to the character's total.
    character['experience'] += xp_amount
    
    leveled_up = False
    
    # Loop to handle multiple level-ups if the gained XP is large.
    while True:
        # Calculate XP required for the NEXT level (current level * 100).
        level_up_xp = character['level'] * 100 
        
        # Check if the character has enough XP to level up.
        if character['experience'] >= level_up_xp:
            leveled_up = True
            
            # Increment level and deduct the required XP.
            character['level'] += 1
            character['experience'] -= level_up_xp 
            
            # Apply stat bonuses for leveling up.
            character['max_health'] += 10
            character['strength'] += 2
            character['magic'] += 2
            
            # Restore current health to maximum health.
            character['health'] = character['max_health']
            
            # Print a level-up message.
            print(f"*** {character['name']} has leveled up to Level {character['level']}! ***")
        else:
            # Exit the loop if no more level-ups are possible.
            break
            
    return leveled_up

def spend_gold(character, amount):
    # Ensure amount is non-negative.
    if amount < 0:
        raise ValueError("Gold amount to spend must be non-negative.")

    # Check for sufficient gold.
    if character['gold'] < amount:
        raise InsufficientResourcesError(f"Need {amount} gold, but only have {character['gold']}.")
        
    # Deduct the gold.
    character['gold'] -= amount
    return True

def add_gold(character, amount):
    # Ensure amount is non-negative.
    if amount < 0:
        raise ValueError("Gold amount to add must be non-negative.")
        
    # Add the gold.
    character['gold'] += amount
    return True

def is_character_dead(character):
    # Returns True if health is 0 or less.
    return character.get("health", 0) <= 0

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(char_dict):
    # Define required fields and their expected data types for a character dictionary.
    required_fields = {
        'name': str, 'class': str, 'level': int, 'experience': int, 'gold': int, 
        'health': int, 'max_health': int, 'strength': int, 'magic': int,
        'inventory': list, 'active_quests': list, 'completed_quests': list,
        'equipped_weapon': (str, type(None))
    }

    # Iterate through each required field.
    for field, expected_type in required_fields.items():
        # Check if the field is missing.
        if field not in char_dict:
            raise InvalidSaveDataError(f"Missing required field: '{field}'")
            
        value = char_dict[field]

        # Handle the case where the value is None (for optional fields like equipped_weapon).
        if value is None and expected_type is not type(None):
             raise InvalidSaveDataError(f"Field '{field}' cannot be None.")

        # Check if the value's type matches the expected type (allowing for a tuple of types).
        if not isinstance(value, expected_type):
            raise InvalidSaveDataError(f"Field '{field}' has wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Additional check for numeric fields to ensure they aren't negative (except gold/experience).
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

