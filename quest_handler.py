"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Final Implementation

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError,
    GameError
)

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' not found.")
        
    quest = quest_data_dict[quest_id]
    
    # Check if already completed or active (using safe tracking functions)
    if is_quest_completed(character, quest_id) or is_quest_active(character, quest_id):
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' is already active or completed.")

    # Check level requirement
    required_level = quest.get('required_level', 1)
    if character['level'] < required_level:
        raise InsufficientLevelError(f"Level too low ({character['level']}). Requires level {required_level}.")
        
    # Check prerequisite
    prereq_id = quest.get('prerequisite', 'NONE')
    if prereq_id != 'NONE' and not is_quest_completed(character, prereq_id):
        raise QuestRequirementsNotMetError(f"Prerequisite quest '{prereq_id}' must be completed first.")
        
    # FIX: Use setdefault() to ensure 'active_quests' list exists before appending
    character.setdefault('active_quests', []).append(quest_id)
    
    return True

def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' not found.")
        
    # FIX: Use setdefault() to ensure both lists exist for safe modification
    active_quests = character.setdefault('active_quests', [])
    completed_quests = character.setdefault('completed_quests', [])
    
    # Check quest is active
    if quest_id not in active_quests:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not currently active.")
        
    quest = quest_data_dict[quest_id]
    
    # Remove from active_quests and add to completed_quests
    active_quests.remove(quest_id)
    completed_quests.append(quest_id)
    
    # Return reward summary
    rewards = {
        'xp': quest.get('reward_xp', 0),
        'gold': quest.get('reward_gold', 0)
    }
    return rewards

def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    """
    # FIX: Use setdefault() to ensure the 'active_quests' list exists
    active_quests = character.setdefault('active_quests', [])
    
    if quest_id not in active_quests:
        raise QuestNotActiveError(f"Quest ID '{quest_id}' is not an active quest.")
        
    active_quests.remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    """
    # Use .get() for safe reading
    active_ids = character.get('active_quests', [])
    return [quest_data_dict[qid] for qid in active_ids if qid in quest_data_dict]

def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    """
    # Use .get() for safe reading
    completed_ids = character.get('completed_quests', [])
    return [quest_data_dict[qid] for qid in completed_ids if qid in quest_data_dict]

def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    """
    available_quests = []
    
    for quest_id, quest_data in quest_data_dict.items():
        if can_accept_quest(character, quest_id, quest_data_dict):
            available_quests.append(quest_data)
            
    return available_quests

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed.
    (Uses .get() for safe reading)
    """
    return quest_id in character.get('completed_quests', [])

def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active.
    (Uses .get() for safe reading)
    """
    return quest_id in character.get('active_quests', [])

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    """
    if quest_id not in quest_data_dict:
        return False
        
    quest = quest_data_dict[quest_id]
    
    # 1. Check if already completed or active
    if is_quest_completed(character, quest_id) or is_quest_active(character, quest_id):
        return False

    # 2. Check level requirement
    required_level = quest.get('required_level', 1)
    if character['level'] < required_level:
        return False
        
    # 3. Check prerequisite
    prereq_id = quest.get('prerequisite', 'NONE')
    if prereq_id != 'NONE' and not is_quest_completed(character, prereq_id):
        return False
        
    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' not found.")
        
    chain = []
    current_id = quest_id
    
    while current_id != 'NONE':
        quest = quest_data_dict.get(current_id)
        if not quest:
            raise GameError(f"Prerequisite chain broken at non-existent quest: {current_id}")
            
        chain.append(current_id)
        current_id = quest.get('prerequisite', 'NONE')
        
        if current_id in chain and current_id != 'NONE':
            raise GameError(f"Circular prerequisite dependency detected involving: {current_id}")

    return chain[::-1]

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    """
    total_quests = len(quest_data_dict)
    completed_quests = len(character.get('completed_quests', []))
    
    if total_quests == 0:
        return 0.0
        
    percentage = (completed_quests / total_quests) * 100
    return round(percentage, 2)

def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    """
    total_xp = 0
    total_gold = 0
    
    completed_quests_data = get_completed_quests(character, quest_data_dict)
    
    for quest in completed_quests_data:
        total_xp += quest.get('reward_xp', 0)
        total_gold += quest.get('reward_gold', 0)
        
    return {'total_xp': total_xp, 'total_gold': total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    """
    return [
        quest for quest in quest_data_dict.values()
        if min_level <= quest.get('required_level', 1) <= max_level
    ]

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    """
    print("\n" + "=" * 30)
    print(f"  QUEST: {quest_data.get('title', 'Unknown Title')}")
    print("=" * 30)
    print(f"ID: {quest_data.get('id', 'N/A')}")
    print(f"Required Level: {quest_data.get('required_level', 1)}")
    print(f"Prerequisite: {quest_data.get('prerequisite', 'None')}")
    print("-" * 30)
    print(f"Description: {quest_data.get('description', 'No description provided.')}")
    print("-" * 30)
    print("Rewards:")
    print(f"  XP: {quest_data.get('reward_xp', 0)}")
    print(f"  Gold: {quest_data.get('reward_gold', 0)}")
    print("-" * 30)

def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    """
    if not quest_list:
        print("  (No quests to display.)")
        return
        
    print("\n[ID] - Title (Lvl Req | Rewards)")
    print("-" * 50)
    for quest in quest_list:
        title = quest.get('title', 'Untitled Quest')
        req_lvl = quest.get('required_level', 1)
        xp = quest.get('reward_xp', 0)
        gold = quest.get('reward_gold', 0)
        qid = quest.get('id', 'N/A')
        print(f"[{qid}] - {title} (Lvl {req_lvl} | {xp} XP, {gold} Gold)")
    print("-" * 50)

def display_quest_progress(character):
    """
    Display a summary of quest progress (used by main.py and view_character_stats).
    """
    active_count = len(character.get('active_quests', []))
    completed_count = len(character.get('completed_quests', []))
    
    print(f"\nQuest Summary:")
    print(f"  Active Quests: {active_count}")
    print(f"  Completed Quests: {completed_count}")

def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    """
    rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    percentage = get_quest_completion_percentage(character, quest_data_dict)
    
    print("\n--- Quest Statistics ---")
    display_quest_progress(character)
    print(f"  Completion Percentage: {percentage}%")
    print(f"  Total XP from Quests: {rewards['total_xp']}")
    print(f"  Total Gold from Quests: {rewards['total_gold']}")
    print("-" * 28)

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    """
    for quest_id, quest in quest_data_dict.items():
        prereq = quest.get('prerequisite', 'NONE')
        if prereq != 'NONE' and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{quest_id}' requires missing prerequisite: '{prereq}'.")
            
    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")

