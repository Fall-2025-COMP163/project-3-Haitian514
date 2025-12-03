"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================
def _read_data_file(filename):
    """
    Helper function to read a data file and split into blocks.
    Raises file-related exceptions.
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"Required data file not found: {filename}")
    except IOError as e:
        raise CorruptedDataError(f"Could not read data file {filename}: {e}")
    
    # Split the file content into blocks separated by two or more newlines
    blocks = [block.strip() for block in content.split('\n\n') if block.strip()]
    return blocks

def load_quests(filename="data/quests.txt"):
    quests = {}
    
    blocks = _read_data_file(filename)
    
    for block_str in blocks:
        lines = [line.strip() for line in block_str.split('\n') if line.strip()]
        try:
            quest_data = parse_quest_block(lines)
            validate_quest_data(quest_data)
            quests[quest_data['quest_id']] = quest_data
        except InvalidDataFormatError as e:
            # Re-raise with context about which file failed
            raise InvalidDataFormatError(f"Quests file format error: {e}")
            
    return quests

def load_items(filename="data/items.txt"):
    items = {}
    
    blocks = _read_data_file(filename)
    
    for block_str in blocks:
        lines = [line.strip() for line in block_str.split('\n') if line.strip()]
        try:
            item_data = parse_item_block(lines)
            validate_item_data(item_data)
            items[item_data['item_id']] = item_data
        except InvalidDataFormatError as e:
            # Re-raise with context about which file failed
            raise InvalidDataFormatError(f"Items file format error: {e}")
            
    return items

def validate_quest_data(quest_dict):
    required_fields = {
        'QUEST_ID': 'quest_id', 'TITLE': 'title', 'DESCRIPTION': 'description',
        'REWARD_XP': 'reward_xp', 'REWARD_GOLD': 'reward_gold', 
        'REQUIRED_LEVEL': 'required_level', 'PREREQUISITE': 'prerequisite'
    }
    
    numeric_fields = ['reward_xp', 'reward_gold', 'required_level']

    for raw_key, field in required_fields.items():
        if field not in quest_dict:
            raise InvalidDataFormatError(f"Quest is missing required field: {raw_key}")
            
        value = quest_dict[field]
        
        if field in numeric_fields:
            if not isinstance(value, int) or value < 0:
                raise InvalidDataFormatError(f"Quest field '{field}' must be a non-negative integer.")

    return True

def validate_item_data(item_dict):
    required_fields = {
        'ITEM_ID': 'item_id', 'NAME': 'name', 'TYPE': 'type', 
        'EFFECT': 'effect', 'COST': 'cost', 'DESCRIPTION': 'description'
    }
    valid_types = ['weapon', 'armor', 'consumable']
    
    for raw_key, field in required_fields.items():
        if field not in item_dict:
            raise InvalidDataFormatError(f"Item is missing required field: {raw_key}")
            
        value = item_dict[field]
        
        if field == 'type' and value not in valid_types:
            raise InvalidDataFormatError(f"Item type '{value}' is invalid. Must be one of: {', '.join(valid_types)}")
        
        if field == 'cost' and (not isinstance(value, int) or value < 0):
            raise InvalidDataFormatError(f"Item cost must be a non-negative integer.")
            
    return True

def create_default_data_files():
    DATA_DIR = "data"
    QUESTS_FILE = os.path.join(DATA_DIR, "quests.txt")
    ITEMS_FILE = os.path.join(DATA_DIR, "items.txt")
    
    # Create data/ directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except OSError as e:
            print(f"Warning: Could not create data directory: {e}")
            return # Cannot proceed if directory fails

    # Create default quests.txt
    if not os.path.exists(QUESTS_FILE):
        default_quests = """
QUEST_ID: first_steps
TITLE: First Steps
DESCRIPTION: Find the local guard and help him with a simple task.
REWARD_XP: 100
REWARD_GOLD: 50
REQUIRED_LEVEL: 1
PREREQUISITE: NONE

QUEST_ID: goblin_hunt
TITLE: Goblin Hunt
DESCRIPTION: Clear the nearby woods of Goblins.
REWARD_XP: 250
REWARD_GOLD: 120
REQUIRED_LEVEL: 3
PREREQUISITE: first_steps
"""
        try:
            with open(QUESTS_FILE, 'w') as f:
                f.write(default_quests.strip())
        except IOError as e:
            print(f"Warning: Could not write default quests file: {e}")

    # Create default items.txt
    if not os.path.exists(ITEMS_FILE):
        default_items = """
ITEM_ID: health_potion
NAME: Health Potion
TYPE: consumable
EFFECT: health:20
COST: 25
DESCRIPTION: Restores 20 health.

ITEM_ID: iron_sword
NAME: Iron Sword
TYPE: weapon
EFFECT: strength:5
COST: 150
DESCRIPTION: A basic iron sword.
"""
        try:
            with open(ITEMS_FILE, 'w') as f:
                f.write(default_items.strip())
        except IOError as e:
            print(f"Warning: Could not write default items file: {e}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    quest = {}
    mapping = {
        'QUEST_ID': 'quest_id', 'TITLE': 'title', 'DESCRIPTION': 'description',
        'REWARD_XP': 'reward_xp', 'REWARD_GOLD': 'reward_gold', 
        'REQUIRED_LEVEL': 'required_level', 'PREREQUISITE': 'prerequisite'
    }
    
    try:
        for line in lines:
            key, value = line.split(': ', 1)
            
            # Map the file key to the internal dictionary key
            internal_key = mapping.get(key.strip())
            if not internal_key:
                # Ignore unknown keys, but valid keys must be present (checked in validate)
                continue
                
            # Convert numeric strings to integers
            if internal_key in ['reward_xp', 'reward_gold', 'required_level']:
                value = int(value.strip())
            else:
                value = value.strip()
                
            quest[internal_key] = value
            
    except ValueError as e:
        # Catch issues like int('not_a_number') or split errors
        raise InvalidDataFormatError(f"Error parsing numeric or key/value pair: {e}")
        
    return quest

def parse_item_block(lines):
    item = {}
    mapping = {
        'ITEM_ID': 'item_id', 'NAME': 'name', 'TYPE': 'type', 
        'EFFECT': 'effect', 'COST': 'cost', 'DESCRIPTION': 'description'
    }
    
    try:
        for line in lines:
            key, value = line.split(': ', 1)
            
            internal_key = mapping.get(key.strip())
            if not internal_key:
                continue

            if internal_key == 'cost':
                value = int(value.strip())
            else:
                value = value.strip()
                
            item[internal_key] = value
            
    except ValueError as e:
        # Catch issues like int('not_a_number') or split errors
        raise InvalidDataFormatError(f"Error parsing numeric or key/value pair: {e}")
        
    return item
# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")

