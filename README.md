# Spoonhead 🥄

**Spoonhead** is a modular 2D action-platformer built with Python and Pygame. It demonstrates advanced game development concepts including layered sprite animation, state machine architecture, persistent data systems, and multi-phase boss battles.

## 🎮 Key Features

*   **Advanced Platforming**: Smooth movement with Double Jump, Dash, and Moving Platforms.
*   **Combat System**: 8-directional shooting with multiple weapon types (Pistol, Spread Shot, Burst Shot).
*   **Dynamic Boss Fights**: Multi-phase bosses that change patterns based on health thresholds.
*   **RPG Elements**:
    *   **Shop System**: Purchase permanent upgrades (Health, Damage, Abilities).
    *   **Gacha System**: Unlock new weapons with a rarity-based loot box mechanic.
    *   **Character Selection**: Choose from 3 characters (Cyborg, Biker, Punk) with unique passive buffs.
*   **Dual Input Support**: Seamlessly switch between **Keyboard** and **Xbox Controller**.
*   **Save/Load System**: JSON-based persistence for all progress (Coins, Upgrades, Unlocks).

## 🛠️ Installation

1.  **Prerequisites**: Ensure you have Python 3.x installed.
2.  **Install Dependencies**:
    ```bash
    pip install pygame
    ```
3.  **Run the Game**:
    ```bash
    python main.py
    ```

## 🕹️ Controls

The game supports automatic switching between Keyboard and Controller.

| Action | Keyboard | Xbox Controller |
| :--- | :--- | :--- |
| **Move** | `WASD` or `Arrow Keys` | Left Stick |
| **Jump** | `Space` or `W` | Button `A` |
| **Shoot** | `J` or `Ctrl` | Button `B` / `RB` |
| **Dash** | `Shift` or `K` | Button `X` |
| **Switch Weapon** | `Q` | Button `Y` |
| **Pause** | `P` | `Start` |

## 📂 Project Structure

Spoonhead utilizes a modular architecture to ensure scalability and maintainability.

```text
spoonhead/
├── main.py           # Entry point: Game Loop & State Manager
├── sprites.py        # ECS-Lite: Player, Enemy, Boss, Physics
├── controller.py     # Input Wrapper (Xbox/Keyboard)
├── shop.py           # Shop Interface & Logic
├── level_data.py     # Level Configuration (Data-driven)
├── shop_data.py      # Item & Upgrade Definitions
├── settings.py       # Global Constants & Configuration
└── assets/           # Game Resources (Sprites, Audio, Fonts)
```

## 🧠 Technical Highlights

*   **Layered Animation System**: Characters are rendered by compositing body, hand, and weapon sprites in real-time.
*   **Two-Pass Collision**: Prevents tunneling and ensures precise platforming physics.
*   **State Machine AI**: Enemies and Bosses utilize FSMs for behavior logic (Patrol -> Detect -> Attack).

## 📝 License

This project is for educational and research purposes.

---
*Developed as part of a Research & Development study on Python Game Architecture.*
