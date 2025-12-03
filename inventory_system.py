"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""
import character_manager
from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    # Check if inventory is full (>= MAX_INVENTORY_SIZE)
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot add item: Inventory is full.")
    
    # Add item_id to character['inventory'] list
    character['inventory'].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory

    Returns: True if removed successfully
    Raises: ItemNotFoundError if item is not found in inventory
    """
    # Check if item exists in inventory
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Cannot remove: Item '{item_id}' not found in inventory.")
    
    # Remove item from list
    character['inventory'].remove(item_id)
    return True

def has_item(character, item_id):
    return item_id in character['inventory']

def count_item(character, item_id):
    return character['inventory'].count(item_id)

def get_inventory_space_remaining(character):
   return MAX_INVENTORY_SIZE - len(character['inventory'])

def clear_inventory(character):
    # Save current inventory before clearing
    removed_items = character['inventory'].copy()
    
    # Clear character's inventory list
    character['inventory'].clear()
    
    return removed_items

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Cannot use: Item '{item_id}' not found.")

    # Check if item type is 'consumable'
    if item_data.get('type') != 'consumable':
        raise InvalidItemTypeError(f"Cannot use '{item_id}': It is not a consumable.")

    # Parse effect (format: "stat_name:value" e.g., "health:20")
    effect_str = item_data.get('effect', '')
    stat_name, value = parse_item_effect(effect_str)

    # Apply effect to character
    apply_stat_effect(character, stat_name, value)

    # Remove item from inventory
    remove_item_from_inventory(character, item_id)
    
    return f"Used {item_data.get('name', item_id)}. {stat_name} increased by {value}."

def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    Returns: Item ID that was unequipped, or None if no weapon equipped
    """
    weapon_id = character.get('equipped_weapon')
    
    if not weapon_id:
        return None

    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot unequip: Inventory is full.")

    # Remove stat bonuses
    if 'equipped_weapon_val' in character:
        stat_name, value = character['equipped_weapon_val']
        apply_stat_effect(character, stat_name, -value)
        del character['equipped_weapon_val']

    # Add weapon back to inventory
    character['inventory'].append(weapon_id)
    character['equipped_weapon'] = None
    
    return weapon_id

def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    Returns: Item ID that was unequipped, or None if no armor equipped
    """
    armor_id = character.get('equipped_armor')
    
    if not armor_id:
        return None

    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot unequip: Inventory is full.")

    # Remove stat bonuses
    if 'equipped_armor_val' in character:
        stat_name, value = character['equipped_armor_val']
        apply_stat_effect(character, stat_name, -value)
        del character['equipped_armor_val']

    # Add armor back to inventory
    character['inventory'].append(armor_id)
    character['equipped_armor'] = None
    
    return armor_id

def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    Returns: String describing equipment change
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Cannot equip: Item '{item_id}' not found.")
    
    if item_data.get('type') != 'weapon':
        raise InvalidItemTypeError(f"Cannot equip '{item_id}': It is not a weapon.")

    # Handle unequipping current weapon if exists
    unequip_msg = ""
    if character.get('equipped_weapon'):
        old_weapon = unequip_weapon(character)
        unequip_msg = f"Unequipped {old_weapon}. "

    # Parse effect and apply to character stats
    stat_name, value = parse_item_effect(item_data.get('effect', ''))
    apply_stat_effect(character, stat_name, value)

    # Store equipped_weapon
    character['equipped_weapon'] = item_id
    character['equipped_weapon_val'] = (stat_name, value)
    remove_item_from_inventory(character, item_id)
    
    return f"{unequip_msg}Equipped {item_data.get('name', item_id)}."

def equip_armor(character, item_id, item_data):
    """
    Equip armor
    Returns: String describing equipment change
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Cannot equip: Item '{item_id}' not found.")
    
    if item_data.get('type') != 'armor':
        raise InvalidItemTypeError(f"Cannot equip '{item_id}': It is not armor.")

    # Handle unequipping current armor if exists
    unequip_msg = ""
    if character.get('equipped_armor'):
        old_armor = unequip_armor(character)  # <--- This works now because unequip_armor is defined above
        unequip_msg = f"Unequipped {old_armor}. "

    # Parse effect and apply
    stat_name, value = parse_item_effect(item_data.get('effect', ''))
    apply_stat_effect(character, stat_name, value)

    # Store equipped_armor
    character['equipped_armor'] = item_id
    character['equipped_armor_val'] = (stat_name, value)
    remove_item_from_inventory(character, item_id)
    
    return f"{unequip_msg}Equipped {item_data.get('name', item_id)}."

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    cost = item_data.get('cost', 0)
    
    # Check if character has enough gold
    if character['gold'] < cost:
        raise InsufficientResourcesError(f"Cannot purchase: Need {cost} gold, have {character['gold']}.")
    
    # Check if inventory has space
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot purchase: Inventory is full.")
    
    # Subtract gold from character
    character_manager.add_gold(character, -cost)
    
    # Add item to inventory
    add_item_to_inventory(character, item_id)
    
    return True

def sell_item(character, item_id, item_data):
   # Check if character has item
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Cannot sell: Item '{item_id}' not found.")
        
    # Calculate sell price (cost // 2)
    cost = item_data.get('cost', 0)
    sell_value = cost // 2
    
    # Remove item from inventory
    remove_item_from_inventory(character, item_id)
    
    # Add gold to character
    character_manager.add_gold(character, sell_value)
    
    return sell_value

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    if not effect_string or ':' not in effect_string:
        return ("none", 0)
        
    # Split on ":"
    parts = effect_string.split(':')
    stat_name = parts[0].strip()
    
    try:
        value = int(parts[1].strip())
    except ValueError:
        value = 0
        
    return (stat_name, value)

def apply_stat_effect(character, stat_name, value):
    if stat_name not in character and stat_name != "none":
        return # invalid stat
        
    if stat_name == "health":
        # Handle healing logic
        character_manager.heal_character(character, value)
    elif stat_name == "max_health":
        # Increase max health
        character['max_health'] += value
        # If max health decreased (unequip), cap current health
        if character['health'] > character['max_health']:
            character['health'] = character['max_health']
    elif stat_name != "none":
        # Standard stats (strength, magic, etc)
        character[stat_name] += value

def display_inventory(character, item_data_dict):
    print(f"\nInventory ({len(character['inventory'])}/{MAX_INVENTORY_SIZE}):")
    
    if not character['inventory']:
        print("  (Empty)")
        return

    # Count unique items
    unique_items = set(character['inventory'])
    
    for item_id in unique_items:
        count = character['inventory'].count(item_id)
        
        # Get pretty name from data dict
        if item_id in item_data_dict:
            name = item_data_dict[item_id].get('name', item_id)
            type_str = item_data_dict[item_id].get('type', 'unknown')
        else:
            name = item_id
            type_str = "unknown"
            
        print(f"  - {name} (x{count}) [{type_str}]")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")

