<p align="center">
  <img src="docs/image/Spoonhead%20(2).png" alt="Spoonhead Title Screen" width="800">
</p>

<h1 align="center">Spoonhead</h1>
<h3 align="center">2D Action-Platformer — Cyberpunk Run-and-Gun Chaos</h3>

<p align="center">
  <strong>Survive the Spoon-pocalypse</strong><br>
  A high-octane 2D platformer built with <em>Python (Pygame)</em> featuring 5 levels, multi-phase boss battles, local co-op, and a weapon gacha system.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Pygame-2.6-9B59B6?style=flat&logo=python" alt="Pygame">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

## Daftar Isi

- [Tentang Spoonhead](#tentang-spoonhead)
- [Fitur & Modul](#fitur--modul)
- [Screenshot](#screenshot)
- [Characters](#characters)
- [Controls](#controls)
- [Game Systems](#game-systems)
- [Arsitektur](#arsitektur)
- [Teknologi](#teknologi)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Lisensi](#lisensi)

---

## Tentang Spoonhead

**Spoonhead** adalah game 2D action-platformer bergaya cyberpunk di mana pemain bertarung melalui 5 level intens, mengalahkan boss multi-fase, dan meningkatkan arsenal senjata untuk bertahan hidup. Game ini mendukung **local co-op** untuk 2 pemain dengan sistem progresi dan kustomisasi yang dalam.

Dibangun dengan **Python** dan **Pygame**, game ini menampilkan engine state machine yang robust, sistem gacha, inventory manajemen, dan pertarungan dinamis 8 arah.

---

## Fitur & Modul

| Fitur | Deskripsi |
|---|---|
| **5 Unique Levels** | Grassy Plains, Hazard Factory, Crystal Core, Sky Fortress, Void Dimension |
| **Boss Battles** | Boss dengan multi-phase attack patterns dan rage mode |
| **Local Co-op** | 2-player local multiplayer dengan karakter berbeda |
| **3 Playable Characters** | Cyborg (Tank), Biker (Speedster), Punk (Acrobat) — masing-masing dengan passive buff unik |
| **Weapon System** | 8+ senjata dengan rarity tiers (Common, Rare, Epic, Legendary) |
| **Gacha System** | Gun Crate untuk unlock weapon skins dan variants |
| **Shop & Upgrades** | Health Up, Damage Up, Double Jump, Dash, dan weapon unlocks |
| **Inventory** | Manajemen karakter, senjata, dan equipment per player |
| **Benchmark Test** | Performance testing tool bawaan |

---

## Screenshot

### Title Screen

<p align="center">
  <img src="docs/image/Spoonhead%20(2).png" alt="Title Screen" width="700">
  <br>
  <em>Layar utama — background gurun sci-fi dengan planet besar. Tombol navigasi: Start Game, Settings, Quit Game, Benchmark Test.</em>
</p>

### Settings

<p align="center">
  <img src="docs/image/Spoonhead%20(3).png" alt="Settings" width="700">
  <br>
  <em>Menu pengaturan — kontrol volume (+/-) dan mode tampilan (Windowed / Fullscreen).</em>
</p>

### Level Selection

<p align="center">
  <img src="docs/image/Spoonhead%20(4).png" alt="Level Selection" width="700">
  <br>
  <em>Pemilihan level — 5 level dengan tema berbeda (Grassy Plains, Hazard Factory, Crystal Core, Sky Fortress, Void Dimension). Total koin, akses Shop & Inventory, dukungan P2 controller.</em>
</p>

### Shop

<p align="center">
  <img src="docs/image/Spoonhead%20(5).png" alt="Shop" width="700">
  <br>
  <em>Toko dalam game — beli senjata baru (Burst Shot), upgrade permanen (Health Upgrade, Double Jump), dan Gun Crate (500 koin) untuk sistem gacha.</em>
</p>

### Crate Drop / Gacha

<p align="center">
  <img src="docs/image/Spoonhead%20(6).png" alt="Crate Drop / Gacha" width="700">
  <br>
  <em>Sistem gacha — animasi pembukaan krate dengan confetti, menampilkan senjata "Marksman" tingkat rarity Common, status "Duplicate!" jika sudah dimiliki.</em>
</p>

### Inventory

<p align="center">
  <img src="docs/image/Spoonhead%20(7).png" alt="Inventory" width="700">
  <br>
  <em>Menu inventaris detail — pilih karakter (Cyborg, Biker, Punk) di kiri, koleksi senjata dengan rarity (Common, Rare, Epic, Legendary) di kanan. Senjata terkunci ditandai gembok. Mendukung multiplayer (P1 Cyborg, P2 Biker).</em>
</p>

### Co-op Gameplay

<p align="center">
  <img src="docs/image/Spoonhead%20(8).png" alt="Co-op Gameplay" width="700">
  <br>
  <em>Gameplay co-op — dua karakter (P1 & P2) di layar. UI menampilkan HP, senjata aktif, Ultimate meter, dan koin. Platforming dan koleksi koin.</em>
</p>

### Action Gameplay

<p align="center">
  <img src="docs/image/Spoonhead%20(10).png" alt="Action Gameplay" width="700">
  <br>
  <em>Aksi gameplay — karakter P1 dengan senjata "Spread Shot". Ultimate meter hampir penuh (4/5), HP sudah di-upgrade ke 150.</em>
</p>

### Boss Battle

<p align="center">
  <img src="docs/image/Spoonhead%20(1).png" alt="Boss Battle" width="700">
  <br>
  <em>Pertarungan Boss — bar BOSS HEALTH merah besar di atas, ULT READY! Boss terbang menembakkan proyektil ungu dengan multi-phase attack patterns.</em>
</p>

### Game Over

<p align="center">
  <img src="docs/image/Spoonhead%20(9).png" alt="Game Over" width="700">
  <br>
  <em>Layar Game Over — teks merah muda dengan opsi tekan 'R' untuk Restart level.</em>
</p>

---

## Characters

Choose your fighter! Each character has a unique passive buff and playstyle.

| Character | Class | Passive Buff | Description |
| :--- | :--- | :--- | :--- |
| **Cyborg** | *The Tank* | **Damage Boost** | Damage increase after setiap kill. Cocok untuk agresif. |
| **Biker** | *The Speedster* | **Speed Boost** | Movement speed lebih tinggi. Ideal untuk speedrun & dodge. |
| **Punk** | *The Acrobat* | **Jump Boost** | Jump height lebih tinggi. Akses area rahasia & evade. |

*Semua karakter bisa unlock **Double Jump** dan **Dash** via Shop.*

---

## Controls

The game supports both **Keyboard** and **Xbox Controller**. Inputs detected automatically.

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
- **Health Up**: Increase max HP.
- **Damage Up**: Increase bullet damage.
- **Double Jump**: Essential for later levels.
- **Weapon Unlocks**: Buy specific weapon types like **Spread Shot** or **Burst Shot**.

### Gacha System
Feeling lucky? Spend 500 coins on the **Gun Crate** to unlock new weapon skins and variants!
- **Rarity Tiers**: Common (Gray), Rare (Blue), Epic (Purple), Legendary (Gold).
- **Weighted Drops**: Common 60%, Rare 25%, Epic 10%, Legendary 5%.
- **Duplicate System**: If you pull a gun you already own, you get a 250-coin refund!
- **Visuals**: Suspenseful unboxing animation with confetti, ribbons, and flash effects.

### Inventory
- **Character Select**: Choose between 3 characters per player.
- **Weapon Collection**: View all unlocked guns with rarity tiers.
- **Equipment**: Equip weapons independently per player (P1/P2).
- **Shared Progress**: Characters, guns, and coins are shared between players.

---

## Arsitektur

```
┌─────────────────────────────────────────────────────┐
│                    Game Engine (Pygame)               │
│          State Machine | Sprite Groups | Physics       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│                  Game States                          │
│  home_screen → level_selection → platformer          │
│       ↑ ↓              ↕               ↕             │
│    settings         shop_screen ←→ boss_fight        │
│                     inventory ←→ game_over           │
│                       gacha        victory            │
└─────────────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│              Persistence (save.json)                  │
│     Coins | Upgrades | Unlocked Characters/Guns      │
└─────────────────────────────────────────────────────┘
```

- **State Machine**: Game flow melalui states terdefinisi — dari menu hingga gameplay, shop, inventory, dan boss fight.
- **Sprite Groups**: Entities (Player, Enemy, Boss, Projectile, Platform) dipisahkan dalam group untuk collision detection dan rendering efisien.
- **Multiplayer**: ControllerManager mendeteksi P1 (keyboard) dan P2 (controller) secara otomatis.
- **Persistence**: Semua data pemain (coins, upgrades, unlocked items) disimpan ke `save.json`.

---

## Teknologi

- **Python 3.9+** — Bahasa pemrograman utama
- **Pygame 2.6** — Game framework (SDL2 wrapper)
- **JSON** — Data persistence & level data

---

## Instalasi

### Prasyarat

- **Python 3.9+**
- **pip** (Python package manager)

### Langkah Instalasi

```bash
# Clone repositori
git clone https://github.com/username/spoonhead.git
cd spoonhead

# Install dependencies
pip install pygame

# Jalankan game
python main.py
```

---

## Penggunaan

1. **Main Menu** — Pilih Start Game untuk memulai, Settings untuk pengaturan, atau Benchmark Test
2. **Select Level** — Pilih level yang sudah terbuka (semakin tinggi semakin sulit)
3. **Shop** — Beli upgrade dan senjata sebelum memulai level
4. **Inventory** — Pilih karakter dan equip senjata
5. **Gameplay** — Gunakan WASD/Arrow untuk gerak, Space untuk lompat, J/Ctrl untuk tembak
6. **Boss Fight** — Kumpulkan Ultimate meter dan gunakan R untuk ultimate saat boss fight
7. **Co-op** — Hubungkan controller untuk P2, tekan START/JUMP untuk join

---

## Lisensi

Proyek ini dilisensikan di bawah **MIT License**. Lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.

---

*Project created by Dyjuen — 2025*
