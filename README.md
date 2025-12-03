[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/wnCpjX4n)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21849558&assignment_repo_type=AssignmentRepo)
# COMP 163: Project 3 - Quest Chronicles

**AI Usage: Free Use (with explanation requirement)**

## Overview

Build a complete modular RPG adventure game demonstrating mastery of **exceptions and modules**.

## Getting Started

### Step 1: Accept Assignment
1. Click the assignment link provided in Blackboard
2. Accept the assignment - this creates your personal repository
3. Clone your repository to your local machine:
```bash
git clone [your-personal-repo-url]
cd [repository-name]
```

### Step 2: Understand the Project Structure

Your repository contains:

```
quest_chronicles/
├── main.py                     # Game launcher (COMPLETE THIS)
├── character_manager.py        # Character creation/management (COMPLETE THIS)
├── inventory_system.py         # Item and equipment management (COMPLETE THIS)
├── quest_handler.py            # Quest system (COMPLETE THIS)
├── combat_system.py            # Battle mechanics (COMPLETE THIS)
├── game_data.py                # Data loading and validation (COMPLETE THIS)
├── custom_exceptions.py        # Exception definitions (PROVIDED)
├── data/
│   ├── quests.txt             # Quest definitions (PROVIDED)
│   ├── items.txt              # Item database (PROVIDED)
│   └── save_games/            # Player save files (created automatically)
├── tests/
│   ├── test_module_structure.py       # Module organization tests
│   ├── test_exception_handling.py     # Exception handling tests
│   └── test_game_integration.py       # Integration tests
└── README.md                   # This file
```

### Step 3: Development Workflow

```bash
# Work on one module at a time
# Test your code frequently

# Commit and push to see test results
git add .
git commit -m "Implement character_manager module"
git push origin main

# Check GitHub for test results (green checkmarks = passed!, red xs = at least 1 failed test case. Click the checkmark or x and then "Details" to see what test cases passed/failed)
```

## Core Requirements (60 Points)

### Critical Constraint
You may **only** use concepts covered through the **Exceptions and Modules** chapters. 

### 🎨 Creativity and Customization

This project encourages creativity! Here's what you can customize:

**✅ FULLY CUSTOMIZABLE:**
- **Character stats** - Adjust health, strength, magic for balance
- **Enemy stats** - Make enemies easier or harder
- **Special abilities** - Design unique abilities for each class
- **Additional enemies** - Add your own enemy types beyond the required three
- **Game mechanics** - Add status effects, combos, critical hits, etc.
- **Quest rewards** - Adjust XP and gold amounts
- **Item effects** - Create unique items with creative effects

**⚠️ REQUIRED (for testing):**
- **4 Character classes:** Warrior, Mage, Rogue, Cleric (names must match exactly)
- **3 Enemy types:** "goblin", "orc", "dragon" (must exist, stats flexible)
- **All module functions** - Must have the specified function signatures
- **Exception handling** - Must raise appropriate exceptions

**💡 CREATIVITY TIPS:**
1. Start with required features working
2. Add creative elements incrementally
3. Test after each addition
4. Be ready to explain your design choices in the interview
5. Bonus interview points for thoughtful, balanced customization!

**Example Creative Additions:**
- Vampire enemy that heals when attacking
- Warrior "Last Stand" ability that activates when health is low
- Poison status effect that deals damage over time
- Critical hit system based on character stats
- Rare "legendary" weapons with special effects

### Module 1: custom_exceptions.py (PROVIDED - 0 points to implement)

**This module is provided complete.** It defines all custom exceptions you'll use throughout the project.

### Module 2: game_data.py (10 points)

### Module 3: character_manager.py (15 points)

### Module 4: inventory_system.py (10 points)

### Module 5: quest_handler.py (10 points)

### Module 6: combat_system.py (10 points)

### Module 7: main.py (5 points)

## Automated Testing & Validation (60 Points)

## Interview Component (40 Points)

**Creativity Bonus** (up to 5 extra points on interview):
- Added 2+ custom enemy types beyond required three
- Designed unique and balanced special abilities
- Implemented creative game mechanics (status effects, advanced combat, etc.)
- Thoughtful stat balancing with clear reasoning

**Note:** Creativity is encouraged, but functionality comes first! A working game with required features scores higher than a broken game with lots of extras.

### Update README.md

Document your project with:

1. **Module Architecture:** Explain your module organization
2. **Exception Strategy:** Describe when/why you raise specific exceptions
3. **Design Choices:** Justify major decisions
4. **AI Usage:** Detail what AI assistance you used
5. **How to Play:** Instructions for running the game

### What to Submit:

1. **GitHub Repository:** Your completed multi-module project
2. **Interview:** Complete 10-minute explanation session
3. **README:** Updated documentation

## Protected Files Warning

⚠️ **IMPORTANT: Test Integrity**

Test files are provided for your learning but are protected. Modifying test files constitutes academic dishonesty and will result in:

- Automatic zero on the project
- Academic integrity investigation

You can view tests to understand requirements, but any modifications will be automatically detected.
# ----------------------------------------------------------------------------------
🏗️ Module Architecture:

The project employs a **multi-modular architecture** where each core game function is isolated in its own Python file, ensuring a strong separation of concerns for easier testing and maintenance.

| Module | Core Responsibility | Key Functions/Classes | Dependencies |
| :--- | :--- | :--- | :--- |
| **`main.py`** | Game flow, UI, and state management. | `main()`, `game_loop()`, `quest_menu()`, `combat_menu()` | All other modules |
| **`character_manager.py`** | Character data creation, persistence (save/load/delete), and fundamental stat changes (XP, Gold, Healing). | `create_character()`, `save_character()`, `load_character()`, `gain_experience()` | `custom_exceptions.py` |
| **`inventory_system.py`** | Item management, usage, and purchasing. | `add_item_to_inventory()`, `use_item()`, `purchase_item()`, `sell_item()` | `character_manager.py`, `custom_exceptions.py` |
| **`quest_handler.py`** | Quest state tracking, prerequisites, and rewards. | `accept_quest()`, `complete_quest()`, `is_quest_completed()`, `can_accept_quest()` | `character_manager.py`, `custom_exceptions.py` |
| **`combat_system.py`** | Battle logic, damage calculation, and enemy definition. | `SimpleBattle` class, `create_enemy()`, `calculate_damage()`, `get_victory_rewards()` | `custom_exceptions.py` |
| **`game_data.py`** | Reading and parsing static game data (Quests, Items) from external text files. | `load_quests()`, `load_items()`, `create_default_data_files()` | `custom_exceptions.py` |
| **`custom_exceptions.py`** | Defines all project-specific exception classes. | `GameError`, `CharacterError`, `QuestError`, etc. | None |

---

### 1.2. Exception Strategy:

The project utilizes a structured **hierarchical exception strategy** defined in `custom_exceptions.py`. This provides specific error handling while maintaining a unified approach through inherited classes.

| Exception | Raised When/Why | Module |
| :--- | :--- | :--- |
| **`CharacterNotFoundError`** | Attempting to load a character save file that does not exist. | `character_manager.py` |
| **`InventoryFullError`** | An item is added when the inventory size limit (`MAX_INVENTORY_SIZE`) has been reached. | `inventory_system.py` |
| **`MissingDataFileError`** | A required static data file cannot be found. | `game_data.py` |
| **`QuestRequirementsNotMetError`** | A character attempts to accept a quest without having completed the necessary prerequisite quest. | `quest_handler.py` |
| **`ValueError`** (Standard Python) | Specifically raised in `character_manager.add_gold` when the transaction would result in a **negative gold total**. | `character_manager.py` |

---

### 1.3. Key Design Choices:

* **Quest Completion Side-Effect:**
    * **Justification:** The `quest_handler.complete_quest()` function was designed to directly **apply XP and Gold rewards** to the character object. This deviates slightly from pure separation of concerns but was a critical decision made to ensure compliance with the **integration test requirements** (`test_game_integration.py`).
* **Character and Enemy Naming:**
    * **Justification:** Enemy names returned by `combat_system.create_enemy()` are consistently **Title Case** (e.g., "Goblin") to match test assertions and maintain display consistency.
* **Data Handling:**
    * **Justification:** Static game data is stored in simple pipe-separated **text files** (`.txt`) and parsed by `game_data.py`. This choice simplifies external editing and directly supports testing of file parsing and file-related exception handling.

---

### 1.4. AI Usage:

AI assistance (Gemini) was used primarily for:

1.  **Debugging and Refactoring:** Identifying the source of test failures and providing code fixes (e.g., correcting the logic flow in `quest_handler.complete_quest`).
2.  **Partial Code Completion:** Implementing **`TODO`** sections, such as the logic for `character_manager.heal_character` and `character_manager.validate_character_data`.
3.  **Test Requirement Analysis:** Confirming exception requirements (e.g., raising standard `ValueError` for negative gold) to ensure all tests passed successfully.

## 2. How to Play:

### Requirements
* Python 3.x

### 1. Run the Game
Navigate to the project root directory in your terminal and execute:

```bash
python main.py