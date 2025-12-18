# Spoonhead 

**Spoonhead** is a high-octane, 2D action-platformer where Cyberpunk aesthetics meet run-and-gun chaos. Battle through 5 intense levels, defeat multi-phase bosses, and upgrade your arsenal to survive the spoon-pocalypse.

Built with Python and Pygame, this game features a robust engine with state management, layered animations, and a dynamic combat system.

## 📖 Table of Contents
- [Game Overview](#-game-overview)
- [Characters](#-characters)
- [Controls](#-controls)
- [Game Systems](#-game-systems)
    - [Shop & Upgrades](#shop--upgrades)
    - [Gacha System](#gacha-system)
- [Installation](#-installation)
- [Credits](#-credits)

---

## Game Overview

In **Spoonhead**, you play as one of three rebels fighting against the system. The game combines precise platforming with 8-directional shooting.
- **5 Unique Levels**: Traverse through distinct biomes, each with its own platforming challenges and enemy types.
- **Boss Battles**: Face off against powerful bosses with unique attack patterns and "rage" phases.
- **Local Co-op**: Team up with a friend in 2-player local multiplayer mode!

---

## Characters

Choose your fighter! Each character has a unique passive buff and playstyle.

| Character | Class | Passive Buff | Description |
| :--- | :--- | :--- | :--- |
| **Cyborg** | *The Tank* | **Damage Boost** | Gains a temporary damage increase after every kill. Perfect for aggressive players. |
| **Biker** | *The Speedster* | **Speed Boost** | Moves faster than other characters. Ideal for speedrunning and dodging projectiles. |
| **Punk** | *The Acrobat* | **Jump Boost** | Has a higher jump height. Great for reaching secret areas and evading ground attacks. |

*All characters can unlock **Double Jump** and **Dash** abilities via the Shop.*

---

## Controls

The game supports both **Keyboard** and **Xbox Controllers**. Inputs are detected automatically.

| Action | Keyboard | Xbox Controller |
| :--- | :--- | :--- |
| **Move** | `W`, `A`, `S`, `D` / Arrows | Left Stick |
| **Jump** | `Space` | `A` Button |
| **Shoot** | `J` or `Ctrl` | `B` or `RB` |
| **Dash** | `Shift` | `X` Button |
| **Switch Weapon** | `Q` | `Y` Button |
| **Ultimate** | `R` | `LB` Button |
| **Pause** | `P` | `Start` |
| **Interact / Select** | `Space` | `A` Button |

---

## Game Systems

### Shop & Upgrades 
Visit the shop between levels to spend your hard-earned coins. Progress is saved automatically!
- **Health Up**: Increase your max HP.
- **Damage Up**: Increase bullet damage.
- **Double Jump**: Essential for later levels.
- **Weapon Unlocks**: Buy specific weapon types like **Spread Shot** or **Burst Shot**.

### Gacha System 
Feeling lucky? Spend coins on the **Gacha Box** to unlock new weapon skins and variants!
- **Rarity Tiers**: Common (Gray), Rare (Blue), Epic (Purple), Legendary (Gold).
- **Duplicate System**: If you pull a gun you already own, you'll be notified!
- **Visuals**: Enjoy a suspenseful unboxing animation with confetti and ribbons.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### Setup
1.  **Clone the repository** (or download the source code):
    ```bash
    git clone https://github.com/yourusername/spoonhead.git
    cd spoonhead
    ```

2.  **Install dependencies**:
    ```bash
    pip install pygame
    ```

3.  **Run the game**:
    ```bash
    python main.py
    ```

---

## Technical Details for Developers

This project serves as a reference for advanced Pygame architecture:
- **ECS-Lite Structure**: Entities (Sprites) are decoupled from logic where possible.
- **State Machine**: The game flows through distinct states (`MENU`, `GAME`, `SHOP`, `GACHA`, `PAUSE`).
- **Asset Management**: A centralized `settings.py` manages all asset paths and constants.
- **Persistence**: Player data (coins, upgrades) is saved to a local JSON file.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

*Project created by Dyjuen - 2025*