"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

import os
import random

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def _get_input(prompt, valid_options=None):
    """Helper for getting and validating string input."""
    while True:
        choice = input(f"{prompt} ").strip()
        if not valid_options:
            return choice
        if choice in valid_options:
            return choice
        print(f"Invalid choice. Please enter one of: {', '.join(valid_options)}")

def _get_int_input(prompt, min_val=None, max_val=None):
    """Helper for getting and validating integer input."""
    while True:
        try:
            value = int(input(f"{prompt} ").strip())
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")
# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    def main_menu():
        print("\n--- Main Menu ---")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        
        choice = _get_input("Choose an option (1-3): ", ['1', '2', '3'])
        return int(choice)

def new_game():
    global current_character
    
    print("\n--- New Game ---")
    
    # Get character name from user
    char_name = _get_input("Enter your character's name: ")
    
    # Get character class from user
    while True:
        char_class = _get_input("Choose your class (Warrior/Mage/Rogue): ").title()
        try:
            # Try to create character with character_manager.create_character()
            current_character = character_manager.create_character(char_name, char_class)
            break
        except InvalidCharacterClassError as e:
            print(f"Error: {e}")
    
    # Save character
    save_game()
    
    print(f"\nWelcome, {current_character['name']} the {current_character['class']}!")
    # Start game loop
    game_loop()

def load_game():
    global current_character
    
    print("\n--- Load Game ---")
    
    saved_chars = character_manager.get_saved_characters()
    
    if not saved_chars:
        print("No saved games found.")
        return
        
    print("Available Characters:")
    for i, name in enumerate(saved_chars):
        print(f"  {i+1}. {name}")
    
    # Get user choice
    choice = _get_int_input(f"Select a character (1-{len(saved_chars)}): ", 1, len(saved_chars))
    char_name = saved_chars[choice - 1]

    try:
        # Try to load character with character_manager.load_character()
        current_character = character_manager.load_character(char_name)
        print(f"Game loaded for {current_character['name']}.")
        
        # Start game loop
        game_loop()    
    except CharacterNotFoundError:
        print(f"Error: Character '{char_name}' not found.")
    except SaveFileCorruptedError as e:
        print(f"Error loading game: {e}")
    except InvalidSaveDataError as e:
        print(f"Error loading game: {e}")

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    global game_running, current_character
    game_running = True
    
    while game_running:
        
        # Check for death first
        if current_character['health'] <= 0:
            handle_character_death()
            if not game_running: # If player quits after death
                return

        print("\n" + "=" * 30)
        print(f"Area: Town | Lvl {current_character['level']}")
        print(f"HP: {current_character['health']}/{current_character['max_health']} | Gold: {current_character['gold']}")
        print("=" * 30)
        
        choice = game_menu()
        
        try:
            if choice == 1:
                view_character_stats()
            elif choice == 2:
                view_inventory()
            elif choice == 3:
                quest_menu()
            elif choice == 4:
                explore()
            elif choice == 5:
                shop()
            elif choice == 6:
                print("Saving game...")
                save_game()
                game_running = False
                print("Game saved. Quitting to main menu.")
            
            # Save game after each action 
            if game_running and choice != 6:
                save_game() 
                
        except GameError as e:
            print(f"\n[Error] {e}")
        except Exception as e:
            print(f"\n[Fatal Error] An unexpected error occurred: {e}")

def game_menu():
    print("\n--- Game Menu ---")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")
    
    choice = _get_input("Choose action (1-6): ", ['1', '2', '3', '4', '5', '6'])
    return int(choice)

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    global current_character
    print("\n--- Character Stats ---")
    print(f"Name: {current_character['name']} ({current_character['class']})")
    print(f"Level: {current_character['level']} (XP: {current_character['experience']}/{current_character['xp_to_next_level']})")
    print(f"Health: {current_character['health']}/{current_character['max_health']}")
    print(f"Gold: {current_character['gold']}")
    print(f"Strength: {current_character['strength']}")
    print(f"Magic: {current_character['magic']}")
    
    equipped_w = current_character.get('equipped_weapon', 'None')
    equipped_a = current_character.get('equipped_armor', 'None')
    
    print(f"Equipped Weapon: {equipped_w}")
    print(f"Equipped Armor: {equipped_a}")

    # Show quest progress
    quest_handler.display_quest_progress(current_character)
    print("-" * 25)

def view_inventory():
    global current_character, all_items
    
    while True:
        print("\n--- Inventory ---")
        inventory_system.display_inventory(current_character, all_items)
        print(f"Gold: {current_character['gold']}")
        
        print("\nOptions:")
        print("1. Use/Equip Item")
        print("2. Unequip Weapon")
        print("3. Unequip Armor")
        print("4. Back to Game Menu")
        
        choice = _get_input("Choose action (1-4): ", ['1', '2', '3', '4'])
        
        if choice == '4':
            break
            
        elif choice == '1':
            item_id = _get_input("Enter Item ID (e.g., health_potion) to Use/Equip: ").lower()
            if item_id not in all_items:
                print("Invalid item ID.")
                continue

            item_data = all_items[item_id]
            item_type = item_data.get('type')

            try:
                if item_type == 'consumable':
                    result = inventory_system.use_item(current_character, item_id, item_data)
                    print(f"-> {result}")
                elif item_type == 'weapon':
                    result = inventory_system.equip_weapon(current_character, item_id, item_data)
                    print(f"-> {result}")
                elif item_type == 'armor':
                    result = inventory_system.equip_armor(current_character, item_id, item_data)
                    print(f"-> {result}")
                else:
                    print("This item cannot be used or equipped.")
                    
            except GameError as e:
                print(f"[Inventory Error] {e}")

        elif choice == '2':
            try:
                unequipped = inventory_system.unequip_weapon(current_character)
                print(f"Unequipped {unequipped}.") if unequipped else print("No weapon equipped.")
            except InventoryFullError as e:
                print(f"[Inventory Error] {e}")

        elif choice == '3':
            try:
                unequipped = inventory_system.unequip_armor(current_character)
                print(f"Unequipped {unequipped}.") if unequipped else print("No armor equipped.")
            except InventoryFullError as e:
                print(f"[Inventory Error] {e}")

def quest_menu():
    global current_character, all_quests
    
    while True:
        print("\n--- Quest Menu ---")
        print("1. View Active Quests")
        print("2. View Available Quests (and Accept)")
        print("3. Complete Quest (Manual ID)") 
        print("4. Back to Game Menu")
        
        choice = _get_input("Choose action (1-4): ", ['1', '2', '3', '4'])
        
        if choice == '4':
            break
            
        elif choice == '1':
            active = quest_handler.get_active_quests(current_character, all_quests)
            print("\nActive Quests:")
            if active:
                for quest in active:
                    print(f"  [{quest.get('id', 'N/A')}] {quest.get('title', 'Untitled')}")
            else:
                print("  (No active quests)")
        
        elif choice == '2':
            available = quest_handler.get_available_quests(current_character, all_quests)
            print("\nAvailable Quests:")
            if available:
                for quest in available:
                    req_level = all_quests.get(quest['id'], {}).get('required_level', 'N/A')
                    print(f"  [{quest['id']}] {quest['title']} (Req Lvl: {req_level})")
            else:
                print("  (No new quests available)")
            
            # Offer to accept a quest
            accept_choice = _get_input("Accept a quest? (y/n): ", ['y', 'n']).lower()
            if accept_choice == 'y':
                quest_id = _get_input("Enter Quest ID to accept: ")
                try:
                    quest_handler.accept_quest(current_character, quest_id, all_quests)
                    print(f"Accepted quest: {quest_id}")
                except QuestError as e:
                    print(f"[Quest Error] {e}")
                    
        elif choice == '3':
            quest_id = _get_input("Enter Quest ID to COMPLETE: ")
            try:
                rewards = quest_handler.complete_quest(current_character, quest_id, all_quests)
                character_manager.gain_experience(current_character, rewards['xp'])
                character_manager.add_gold(current_character, rewards['gold'])
                print(f"Quest {quest_id} completed!")
                print(f"Rewards: {rewards['xp']} XP, {rewards['gold']} Gold.")
            except QuestError as e:
                print(f"[Quest Error] {e}")

def explore():
    """Find and fight random enemies"""
    global current_character
    
    print("\n-=- Exploring the Wilds -=-")
    
    # Simple enemy selection based on character level
    enemy_options = ['goblin', 'skeleton']
    selected_enemy = random.choice(enemy_options)
    
    try:
        enemy = combat_system.create_enemy(selected_enemy)
    except InvalidTargetError as e:
        print(f"[Combat Error] Could not find suitable enemy: {e}")
        return

    battle = combat_system.SimpleBattle(current_character, enemy)
    result = battle.start_battle()

    if result == "VICTORY":
        rewards = combat_system.get_victory_rewards(enemy)
        
        print("\n--- Victory! ---")
        character_manager.gain_experience(current_character, rewards['xp'])
        character_manager.add_gold(current_character, rewards['gold'])
        print(f"Gained {rewards['xp']} XP and {rewards['gold']} Gold.")
        
    elif result == "DEFEAT":
        print("You were defeated in battle!")
    elif result == "FLED":
        print("You successfully fled the battle.")

def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items
    
    shop_inventory = all_items 
    
    while True:
        print("\n--- Shop Menu ---")
        print(f"Your Gold: {current_character['gold']}")
        
        print("\n1. Buy Item")
        print("2. Sell Item")
        print("3. Back to Game Menu")
        
        choice = _get_input("Choose action (1-3): ", ['1', '2', '3'])
        
        if choice == '3':
            break
            
        elif choice == '1': # Buy Item
            print("\nItems for Sale (ID: Name [Type] - Cost):")
            for item_id, data in shop_inventory.items():
                print(f"  {item_id}: {data['name']} [{data['type']}] - {data['cost']} Gold")
            
            item_id = _get_input("Enter Item ID to Buy: ").lower()
            if item_id in shop_inventory:
                try:
                    inventory_system.purchase_item(current_character, item_id, shop_inventory[item_id])
                    print(f"Purchased {shop_inventory[item_id]['name']} for {shop_inventory[item_id]['cost']} gold.")
                except GameError as e:
                    print(f"[Shop Error] {e}")
            else:
                print("Invalid item ID.")
                
        elif choice == '2': # Sell Item
            inventory_system.display_inventory(current_character, all_items)
            item_id = _get_input("Enter Item ID to Sell (Half Price): ").lower()
            
            # Check if item is in inventory before trying to sell
            if item_id in all_items and item_id in current_character['inventory']:
                try:
                    gold_gained = inventory_system.sell_item(current_character, item_id, all_items[item_id])
                    print(f"Sold {all_items[item_id]['name']} for {gold_gained} gold.")
                except ItemNotFoundError as e:
                    print(f"[Shop Error] {e}")
            else:
                print("Invalid item ID or item not in inventory.")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    global current_character
    if current_character:
        try:
            character_manager.save_character(current_character)
        except Exception as e:
            print(f"Warning: Failed to save game: {e}")

def load_game_data():
    global all_quests, all_items
    
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except MissingDataFileError as e:
        # If files missing, create defaults and retry loading
        print(f"Error: {e}")
        print("Attempting to create default game data...")
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()

def handle_character_death():
    """Handle character death"""
    global current_character, game_running
    
    print("\n" + "#" * 30)
    print("      YOU HAVE BEEN DEFEATED!")
    print("#" * 30)
    
    revive_cost = 100 
    
    print(f"\nYour quest ends here, {current_character['name']}.")
    print(f"Current Gold: {current_character['gold']}")
    print(f"1. Revive (Cost: {revive_cost} Gold)")
    print("2. Quit to Main Menu")
    
    if current_character['gold'] >= revive_cost:
        revive_option = _get_input("Choose action (1 or 2): ", ['1', '2'])
    else:
        print("Not enough gold to revive.")
        revive_option = '2'

    if revive_option == '1':
        try:
            character_manager.revive_character(current_character, revive_cost)
            print("\nCharacter revived! You lose some gold.")
        except InsufficientResourcesError:
            # Should be handled by the check above
            print("Failed to revive. Quitting.")
            game_running = False
    elif revive_option == '2':
        print("\nQuitting game...")
        game_running = False

def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()

