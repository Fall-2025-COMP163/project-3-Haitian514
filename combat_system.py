"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
    random
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type.

    Returns: Enemy dictionary with keys:
             name, health, max_health, strength, magic, xp_reward, gold_reward

    Raises: InvalidTargetError if enemy_type not recognized
    """
    et = enemy_type.lower()
    if et == "goblin":
        e = {"name": "goblin", "health": 50, "max_health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10}
    elif et == "orc":
        e = {"name": "orc", "health": 80, "max_health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25}
    elif et == "dragon":
        e = {"name": "dragon", "health": 200, "max_health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    else:
        raise InvalidTargetError("Unknown enemy type: {}".format(enemy_type))
    return e


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level.

    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
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

    Uses non-interactive, deterministic turns:
    - Player attacks first each round (basic attack)
    - Enemy attacks if still alive
    - No input() calls so tests can run deterministically
    """

    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        # store shallow copies (we mutate the passed dicts intentionally)
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turns = 0

    def start_battle(self):
        """
        Start the combat loop

        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}

        Raises: CharacterDeadError if character is already dead
        """
        if int(self.character.get("health", 0)) <= 0:
            raise CharacterDeadError("Character is dead and cannot enter battle")

        # loop until someone dies or combat is flagged inactive (escape)
        while True:
            self.turns += 1

            # Player's turn: basic attack
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
            # grant rewards
            xp = int(self.enemy.get("xp_reward", 0))
            gold = int(self.enemy.get("gold_reward", 0))
            self.character["experience"] = self.character.get("experience", 0) + xp
            self.character["gold"] = self.character.get("gold", 0) + gold
            display_battle_log("You defeated the {}!".format(self.enemy.get("name", "enemy")))
            return {"winner": "player", "xp_gained": xp, "gold_gained": gold}
        elif result == "enemy":
            display_battle_log("You were defeated by the {}...".format(self.enemy.get("name", "enemy")))
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}
        else:
            # escaped / combat ended without a winner
            display_battle_log("Combat ended without a decisive winner.")
            return {"winner": "none", "xp_gained": 0, "gold_gained": 0}

    def player_turn(self):
        """
        Handle player's turn - non-interactive basic attack.
        Raises CombatNotActiveError if called outside of battle
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
        Raises CombatNotActiveError if called outside of battle
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
        Minimum damage: 1

        For magical attacks (used by mage special), attacker may use 'magic' stat externally.
        """
        # attacker and defender must have 'strength' keys
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

        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if int(self.enemy.get("health", 0)) <= 0:
            return "player"
        if int(self.character.get("health", 0)) <= 0:
            return "enemy"
        return None

    def attempt_escape(self):
        """
        Try to escape from battle

        50% success chance

        Returns: True if escaped, False if failed
        """
        if not self.combat_active:
            # no fight to escape from
            return False
        success = random.choice([True, False])
        if success:
            self.combat_active = False
            display_battle_log("{} successfully escaped!".format(self.character.get("name", "Player")))
            return True
        else:
            display_battle_log("{} failed to escape.".format(self.character.get("name", "Player")))
            return False

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability.

    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently (not implemented here)
    """
    cls = character.get("class", "")
    if cls == "Warrior":
        return warrior_power_strike(character, enemy)
    elif cls == "Mage":
        return mage_fireball(character, enemy)
    elif cls == "Rogue":
        return rogue_critical_strike(character, enemy)
    elif cls == "Cleric":
        return cleric_heal(character)
    else:
        raise InvalidTargetError("Unknown character class for special ability: {}".format(cls))


def warrior_power_strike(character, enemy):
    """Warrior special ability: 2x strength damage"""
    base = int(character.get("strength", 0))
    damage = base * 2
    # account for defender mitigation similarly to calculate_damage
    mitigation = int(enemy.get("strength", 0)) // 4
    damage = damage - mitigation
    if damage < 1:
        damage = 1
    enemy["health"] = max(0, int(enemy.get("health", 0)) - damage)
    msg = "{} uses Power Strike dealing {} damage to {}".format(character.get("name", "Player"), damage, enemy.get("name", "Enemy"))
    display_battle_log(msg)
    return msg


def mage_fireball(character, enemy):
    """Mage special ability: 2x magic damage"""
    base_magic = int(character.get("magic", 0))
    damage = base_magic * 2
    # reduce by part of enemy's strength to keep consistent
    mitigation = int(enemy.get("strength", 0)) // 4
    damage = damage - mitigation
    if damage < 1:
        damage = 1
    enemy["health"] = max(0, int(enemy.get("health", 0)) - damage)
    msg = "{} casts Fireball for {} damage to {}".format(character.get("name", "Player"), damage, enemy.get("name", "Enemy"))
    display_battle_log(msg)
    return msg


def rogue_critical_strike(character, enemy):
    """Rogue special ability: 50% chance for triple strength damage"""
    base = int(character.get("strength", 0))
    chance = random.choice([True, False])  # 50% chance
    if chance:
        damage = base * 3
        reason = "critical!"
    else:
        damage = base
        reason = "normal hit"
    mitigation = int(enemy.get("strength", 0)) // 4
    damage = damage - mitigation
    if damage < 1:
        damage = 1
    enemy["health"] = max(0, int(enemy.get("health", 0)) - damage)
    msg = "{} uses Critical Strike ({}) for {} damage to {}".format(character.get("name", "Player"), reason, damage, enemy.get("name", "Enemy"))
    display_battle_log(msg)
    return msg


def cleric_heal(character):
    """Cleric special ability: restore 30 health (not exceeding max)"""
    before = int(character.get("health", 0))
    max_h = int(character.get("max_health", before))
    heal_amt = 30
    new = before + heal_amt
    if new > max_h:
        new = max_h
    character["health"] = new
    actual = new - before
    msg = "{} casts Heal and restores {} HP".format(character.get("name", "Player"), actual)
    display_battle_log(msg)
    return msg

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    Returns: True if health > 0
    """
    return int(character.get("health", 0)) > 0


def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    Returns: Dictionary with 'xp' and 'gold'
    """
    xp = int(enemy.get("xp_reward", 0))
    gold = int(enemy.get("gold_reward", 0))
    return {"xp": xp, "gold": gold}


def display_combat_stats(character, enemy):
    """
    Display current combat status: character and enemy health/stats
    """
    print("\n{}: HP={}/{}".format(character.get("name", "Player"), character.get("health", 0), character.get("max_health", 0)))
    print("{}: HP={}/{}".format(enemy.get("name", "Enemy"), enemy.get("health", 0), enemy.get("max_health", 0)))


def display_battle_log(message):
    """
    Display a formatted battle message
    """
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

