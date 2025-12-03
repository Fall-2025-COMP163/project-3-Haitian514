"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Fixed

Name: [Sean Telemaque]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type.
    Note: Names are capitalized to pass test_combat_system_basic_battle
    """
    et = enemy_type.lower()
    if et == "goblin":
        e = {"name": "Goblin", "health": 50, "max_health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10}
    elif et == "orc":
        e = {"name": "Orc", "health": 80, "max_health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25}
    elif et == "dragon":
        e = {"name": "Dragon", "health": 200, "max_health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    elif et == "skeleton":
        e = {"name": "Skeleton", "health": 40, "max_health": 40, "strength": 10, "magic": 0, "xp_reward": 20, "gold_reward": 5}
    else:
        raise InvalidTargetError("Unknown enemy type: {}".format(enemy_type))
    return e


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level.
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif 3 <= character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system.
    """

    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turns = 0

    def start_battle(self):
        """
        Start the combat loop
        """
        if int(self.character.get("health", 0)) <= 0:
            raise CharacterDeadError("Character is dead and cannot enter battle")

        # loop until someone dies or combat is flagged inactive (escape)
        result = None
        while True:
            self.turns += 1

            # Player's turn
            self.player_turn()

            # Check after player's attack
            result = self.check_battle_end()
            if result is not None:
                break

            # Enemy's turn
            self.enemy_turn()

            # Check after enemy's attack
            result = self.check_battle_end()
            if result is not None:
                break

            # If combat was turned off by something (escape), stop
            if not self.combat_active:
                result = None
                break

        # finalize
        self.combat_active = False

        if result == "player":
            return "VICTORY"
        elif result == "enemy":
            display_battle_log("You were defeated by the {}...".format(self.enemy.get("name", "enemy")))
            return "DEFEAT"
        else:
            display_battle_log("Combat ended without a decisive winner.")
            return "FLED"

    def player_turn(self):
        """
        Handle player's turn - non-interactive basic attack.
        """
        if not self.combat_active:
            raise CombatNotActiveError("No active combat")

        # Basic attack uses character 'strength'
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)
        display_battle_log("{} attacks {} for {} damage".format(self.character.get("name", "Player"), self.enemy.get("name", "Enemy"), damage))
        return damage

    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI (enemy always attacks)
        """
        if not self.combat_active:
            raise CombatNotActiveError("No active combat")

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log("{} attacks {} for {} damage".format(self.enemy.get("name", "Enemy"), self.character.get("name", "Player"), damage))
        return damage

    def calculate_damage(self, attacker, defender):
        """
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        """
        atk = int(attacker.get("strength", 0))
        dfn = int(defender.get("strength", 0))
        damage = atk - (dfn // 4)
        if damage < 1:
            damage = 1
        return damage

    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy. Prevent negative health.
        """
        current = int(target.get("health", 0))
        new = current - int(damage)
        if new < 0:
            new = 0
        target["health"] = new
        return new

    def check_battle_end(self):
        """
        Check if battle is over
        """
        if int(self.enemy.get("health", 0)) <= 0:
            return "player"
        if int(self.character.get("health", 0)) <= 0:
            return "enemy"
        return None

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    Returns: Dictionary with 'xp' and 'gold'
    """
    xp = int(enemy.get("xp_reward", 0))
    gold = int(enemy.get("gold_reward", 0))
    return {"xp": xp, "gold": gold}

def display_battle_log(message):
    print(">>> {}".format(message))

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    # try:
    #     goblin = create_enemy("goblin")
    #     print(f"Created {goblin['name']}")
    # except InvalidTargetError as e:
    #     print(f"Invalid enemy: {e}")
    
    # Test battle
    # test_char = {
    #     'name': 'Hero',
    #     'class': 'Warrior',
    #     'health': 120,
    #     'max_health': 120,
    #     'strength': 15,
    #     'magic': 5
    # }
    #
    # battle = SimpleBattle(test_char, goblin)
    # try:
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")

