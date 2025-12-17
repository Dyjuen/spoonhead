# This file contains the data for all game levels.

LEVEL_1 = {
    "name": "Grassy Plains",
    "platforms": [
        # Ground
        (0, 550, 400, 40), (500, 550, 800, 40), (1400, 550, 500, 40), (2000, 550, 500, 40),
        # Simple platforms
        (200, 450, 150, 30),
        (600, 400, 120, 30),
        (900, 350, 150, 30),
        (1200, 300, 120, 30),
        (1600, 450, 150, 30),
        (1850, 400, 120, 30),
        # Extended part
        (2600, 550, 400, 40),
        (3100, 550, 600, 40), (3700, 550, 200, 40),
        (2800, 450, 150, 30),
        (3000, 400, 120, 30),
        (3300, 350, 150, 30),
        (3600, 300, 120, 30),
        # Even more platforms to make the level longer
        (4000, 550, 500, 40),
        (4600, 550, 500, 40),
        (5200, 550, 500, 40),
        (5800, 550, 500, 40),
        (6400, 550, 500, 40),
        (7000, 550, 500, 40),
        (4200, 450, 150, 30),
        (4400, 400, 120, 30),
        (4600, 350, 150, 30),
        (4800, 300, 120, 30),
        (5000, 250, 150, 30),
        (5300, 450, 150, 30),
        (5500, 400, 120, 30),
        (5700, 350, 150, 30),
        (6000, 300, 120, 30),
        (6200, 250, 150, 30),
        (6500, 450, 150, 30),
        (6800, 400, 120, 30),
        (7100, 350, 150, 30),
        (7400, 300, 120, 30),
    ],
    "moving_platforms": [
        (400, 500, 100, 25, 'y', 100, 1), # Gentle vertical movement
        (2500, 500, 100, 25, 'y', 100, 2),
        (5100, 500, 100, 25, 'y', 150, 2),
    ],
    "coins": [
        (250, 400), (650, 350), (950, 300), (1250, 250), (1650, 400), (1900, 350),
        (450, 400), # On the moving platform
        # Extended part
        (2850, 400), (3050, 350), (3350, 300), (3650, 250),
        # Coins for the new extended part
        (4250, 400), (4450, 350), (4650, 300), (4850, 250), (5050, 200),
        (5350, 400), (5550, 350), (5750, 300), (6050, 250), (6250, 200),
        (6550, 400), (6850, 350), (7150, 300), (7450, 250),
    ],
    "enemies": [
        # Simple patrols
        { "x": 700, "y": 500, "patrol_distance": 100, "speed": 1, "shoot_cooldown": 4.0 },
        { "x": 1500, "y": 500, "patrol_distance": 150, "speed": 1, "shoot_cooldown": 5.0 },
        # Extended part
        { "x": 2900, "y": 500, "patrol_distance": 100, "speed": 1.5, "shoot_cooldown": 3.0 },
        { "x": 3400, "y": 500, "patrol_distance": 150, "speed": 1.5, "shoot_cooldown": 4.0 },
        # Enemies for the new extended part
        { "x": 4300, "y": 500, "patrol_distance": 100, "speed": 2, "shoot_cooldown": 2.5 },
        { "x": 5400, "y": 500, "patrol_distance": 200, "speed": 1, "shoot_cooldown": 3.0 },
        { "x": 6700, "y": 500, "patrol_distance": 150, "speed": 2.5, "shoot_cooldown": 2.0 },
        { "x": 7200, "y": 500, "patrol_distance": 100, "speed": 2, "shoot_cooldown": 1.5 },
    ],
    "power_up_boxes": [
        (750, 350),
        (4500, 300),
    ],
    "boss": {
        "boss_type": 1,
        "x": 4000,
        "y": 400,
        "health": 250,
        "speed": 4,
        "shoot_interval": 100,
        "phases": 1, # Only one phase
    },
    "boss_gate_x": 7800,
}

LEVEL_2 = {
    "name": "Hazard Factory",
    "platforms": [
        (0, 550, 200, 40), (350, 550, 500, 40), (950, 550, 300, 40),
        (1500, 550, 200, 40), (1800, 550, 600, 40),
        # Trickier platforms
        (400, 450, 100, 25), (600, 350, 100, 25), (800, 250, 100, 25),
        (1200, 400, 80, 25), (1350, 320, 80, 25), (1500, 240, 80, 25),
        # Extended part
        (2500, 550, 300, 40), (2900, 550, 400, 40), (3300, 550, 800, 40),
        (2700, 450, 100, 25), (2900, 350, 100, 25), (3100, 250, 100, 25),
        # New extension
        (4200, 550, 400, 40), (4700, 550, 400, 40), (5200, 550, 400, 40),
        (5700, 550, 400, 40), (6200, 550, 400, 40), (6700, 550, 400, 40),
        (4300, 450, 100, 25), (4500, 350, 100, 25), (4700, 250, 100, 25),
        (5000, 400, 80, 25), (5150, 320, 80, 25), (5300, 240, 80, 25),
        (5500, 450, 100, 25), (5700, 350, 100, 25), (5900, 250, 100, 25),
        (6200, 400, 80, 25), (6350, 320, 80, 25), (6500, 240, 80, 25),
    ],
    "moving_platforms": [
        (250, 500, 100, 25, 'x', 200, 3), # Fast horizontal
        (1000, 450, 100, 25, 'y', 200, 2), # Wider vertical
        (1650, 500, 150, 25, 'x', 150, -3), # Fast reverse horizontal
        # Extended part
        (2600, 500, 100, 25, 'x', 200, 4),
        (3200, 450, 100, 25, 'y', 200, -3),
        # New extension
        (4400, 500, 100, 25, 'x', 200, 5),
        (5400, 450, 100, 25, 'y', 200, 3),
        (6400, 500, 150, 25, 'x', 150, -5),
        (7300, 500, 150, 25, 'x', 200, 2), # New platform before boss portal
    ],
    "coins": [
        (450, 400), (650, 300), (850, 200), (1240, 350), (1390, 270), (1540, 190),
        (300, 400), (1100, 250),
        # Extended part
        (2750, 400), (2950, 300), (3150, 200),
        # New extension
        (4350, 400), (4550, 300), (4750, 200), (5040, 350), (5190, 270), (5340, 190),
        (5550, 400), (5750, 300), (5950, 200), (6240, 350), (6390, 270), (6540, 190),
    ],
    "enemies": [
        # Fewer, slower enemies
        { "x": 400, "y": 500, "patrol_distance": 150, "speed": 1.5, "shoot_cooldown": 3.5 },
        { "x": 1000, "y": 500, "patrol_distance": 100, "speed": 2, "shoot_cooldown": 3.0 },
        { "x": 2000, "y": 500, "patrol_distance": 200, "speed": 1.5, "shoot_cooldown": 4.0 },
        { "x": 2800, "y": 500, "patrol_distance": 150, "speed": 2, "shoot_cooldown": 3.0 },
        # New extension
        { "x": 4600, "y": 500, "patrol_distance": 150, "speed": 2.5, "shoot_cooldown": 2.5 },
        { "x": 5600, "y": 500, "patrol_distance": 100, "speed": 3, "shoot_cooldown": 2.0 },
        { "x": 6600, "y": 500, "patrol_distance": 200, "speed": 2.5, "shoot_cooldown": 3.0 },
    ],
    "boss": {
        "boss_type": 2,
        "x": 4200,
        "y": 350,
        "health": 350,      # Reduced from 500
        "speed": 5,         # Reduced from 4
        "shoot_interval": 400,
        "phases": 1,        # Reduced from 2
    },
    "boss_gate_x": 7800,
}

LEVEL_3 = {
    "name": "Crystal Core",
    "gate_type": "boss",
    "platforms": [
        (0, 550, 150, 40), (250, 550, 150, 40), # Small starting ground
        (800, 500, 100, 25), (1000, 450, 100, 25), (1200, 400, 100, 25),
        (1400, 350, 100, 25), (1600, 300, 100, 25),
        (2200, 550, 400, 40),
        # Extended part
        (3000, 550, 200, 40), (3300, 550, 200, 40), (3500, 550, 1000, 40),
        (2800, 500, 100, 25), (3000, 450, 100, 25), (3200, 400, 100, 25),
        (3400, 350, 100, 25), (3600, 300, 100, 25),
        # New extension
        (4600, 550, 400, 40), (5100, 550, 400, 40), (5600, 550, 400, 40),
        (6100, 550, 400, 40), (6600, 550, 400, 40), (7100, 550, 400, 40),
        (4700, 500, 100, 25), (4900, 450, 100, 25), (5100, 400, 100, 25),
        (5300, 350, 100, 25), (5500, 300, 100, 25),
        (6000, 500, 100, 25), (6200, 450, 100, 25), (6400, 400, 100, 25),
        (6600, 350, 100, 25), (6800, 300, 100, 25),
    ],
    "moving_platforms": [
        (450, 500, 100, 25, 'y', 250, 4), # Fast vertical lift
        (650, 250, 100, 25, 'x', 300, 5), # Long, fast patrol
        (1800, 500, 80, 20, 'y', 300, -5), # Fast downward
        (1900, 200, 80, 20, 'x', 200, 4),
        # Extended part
        (2500, 400, 100, 25, 'y', 200, 6),
        (2700, 200, 100, 25, 'x', 400, -6),
        # New extension
        (4800, 400, 100, 25, 'y', 250, 7),
        (5800, 250, 100, 25, 'x', 300, -8),
        (7000, 500, 80, 20, 'y', 300, 8),
    ],
    "coins": [
        (850, 450), (1050, 400), (1250, 350), (1450, 300), (1650, 250),
        (500, 300), (700, 200),
        # Extended part
        (2850, 450), (3050, 400), (3250, 350), (3450, 300), (3650, 250),
        # New extension
        (4750, 450), (4950, 400), (5150, 350), (5350, 300), (5550, 250),
        (6050, 450), (6250, 400), (6450, 350), (6650, 300), (6850, 250),
    ],
    "enemies": [
        # Lots of very aggressive enemies
        { "x": 300, "y": 500, "patrol_distance": 50, "speed": 4.5, "shoot_cooldown": 1.2 },
        { "x": 900, "y": 450, "patrol_distance": 80, "speed": 3.5, "shoot_cooldown": 1.5 },
        { "x": 1300, "y": 300, "patrol_distance": 100, "speed": 3.5, "shoot_cooldown": 1.8 },
        { "x": 1700, "y": 250, "patrol_distance": 50, "speed": 4.5, "shoot_cooldown": 1.2 },
        { "x": 2300, "y": 500, "patrol_distance": 80, "speed": 3.5, "shoot_cooldown": 0.8 },
        { "x": 3100, "y": 500, "patrol_distance": 60, "speed": 5.5, "shoot_cooldown": 0.8 },
        { "x": 3500, "y": 450, "patrol_distance": 90, "speed": 4.5, "shoot_cooldown": 1.0 },
        { "x": 4000, "y": 500, "patrol_distance": 100, "speed": 5, "shoot_cooldown": 1.0 },
        # New extension
        { "x": 4800, "y": 500, "patrol_distance": 50, "speed": 6, "shoot_cooldown": 1.0 },
        { "x": 5400, "y": 450, "patrol_distance": 80, "speed": 5, "shoot_cooldown": 1.2 },
        { "x": 6200, "y": 300, "patrol_distance": 100, "speed": 5, "shoot_cooldown": 1.5 },
        { "x": 7200, "y": 250, "patrol_distance": 50, "speed": 6, "shoot_cooldown": 1.0 },
    ],
    "boss": {
        "boss_type": 3,
        "x": 4600,
        "y": 300,
        "health": 750,
        "speed": 7, # Very fast
        "shoot_interval": 150,
        "phases": 3, # All three phases
    },
    "boss_gate_x": 8800,
}

LEVEL_4 = {
    "name": "Sky Fortress",
    "gate_type": "next_level", # Transitions to Level 5
    "platforms": [
        (0, 550, 200, 40), # Start
        (300, 500, 100, 25), (500, 450, 100, 25), (700, 400, 100, 25),
        (900, 350, 100, 25), (1100, 300, 100, 25), (1300, 250, 100, 25),
        (1600, 550, 200, 40), # Checkpoint 1
        (1900, 450, 50, 25), (2000, 350, 50, 25), (2100, 250, 50, 25), # Tiny steps
        (2300, 200, 200, 40),
        (2600, 300, 100, 25), (2800, 400, 100, 25), (3000, 500, 100, 25),
        (3300, 550, 300, 40), # Checkpoint 2
        (3700, 450, 100, 25), (3900, 350, 100, 25), (4100, 250, 100, 25),
        (4400, 550, 500, 40), # End area
    ],
    "moving_platforms": [
        (150, 400, 80, 20, 'y', 300, 3),
        (800, 200, 80, 20, 'x', 400, 4),
        (2200, 400, 80, 20, 'y', 200, -4),
        (3200, 300, 80, 20, 'x', 300, 5),
        (4000, 200, 80, 20, 'y', 300, 6),
    ],
    "coins": [
        (350, 450), (550, 400), (750, 350), (950, 300),
        (1950, 400), (2050, 300),
        (2700, 250), (2900, 350),
        (3800, 400), (4000, 300),
    ],
    "enemies": [
        { "x": 1650, "y": 500, "patrol_distance": 50, "speed": 3, "shoot_cooldown": 1.5 },
        { "x": 2350, "y": 150, "patrol_distance": 50, "speed": 4, "shoot_cooldown": 1.0 },
        { "x": 3400, "y": 500, "patrol_distance": 100, "speed": 5, "shoot_cooldown": 0.8 },
        { "x": 4500, "y": 500, "patrol_distance": 150, "speed": 4, "shoot_cooldown": 1.2 },
    ],
    "boss": { # Placeholder, effectively skipped by gate_type logic
        "boss_type": 1,
        "x": 0, "y": 0, "health": 1, "speed": 0, "shoot_interval": 9999, "phases": 1
    },
    "boss_gate_x": 4800,
}

LEVEL_5 = {
    "name": "Void Dimension",
    "gate_type": "boss", # Transitions to Boss Fight
    "platforms": [
        (0, 550, 200, 40),
        (300, 550, 50, 25), (450, 500, 50, 25), (600, 450, 50, 25),
        (750, 400, 50, 25), (900, 350, 50, 25), (1050, 300, 50, 25),
        (1300, 550, 300, 40),
        (1700, 450, 100, 25), (1900, 350, 100, 25), (2100, 250, 100, 25),
        (2400, 550, 400, 40),
        (2900, 500, 50, 25), (3050, 450, 50, 25), (3200, 400, 50, 25),
        (3350, 350, 50, 25), (3500, 300, 50, 25), (3650, 250, 50, 25),
        (4000, 550, 500, 40), # Boss Arena Pre-chamber
    ],
    "moving_platforms": [
        (500, 200, 80, 20, 'x', 500, 6), # Very fast horizontal
        (1500, 300, 80, 20, 'y', 200, 5),
        (2500, 200, 80, 20, 'x', 400, -6),
        (3500, 500, 80, 20, 'y', 300, 7),
    ],
    "coins": [
        (325, 500), (475, 450), (625, 400),
        (1750, 400), (1950, 300),
        (2950, 450), (3100, 400), (3250, 350),
    ],
    "enemies": [
        { "x": 1400, "y": 500, "patrol_distance": 100, "speed": 5, "shoot_cooldown": 0.8 },
        { "x": 2500, "y": 500, "patrol_distance": 150, "speed": 6, "shoot_cooldown": 0.6 },
        { "x": 4100, "y": 500, "patrol_distance": 100, "speed": 7, "shoot_cooldown": 0.5 },
    ],
    "boss": {
        "boss_type": 3, # Reusing Boss 3 stats but maybe buffed in main.py logic or here
        "x": 4200,
        "y": 300,
        "health": 1000, # Harder
        "speed": 8,
        "shoot_interval": 100,
        "phases": 3,
    },
    "boss_gate_x": 4400,
}


ALL_LEVELS = {
    1: LEVEL_1,
    2: LEVEL_2,
    3: LEVEL_3,
    4: LEVEL_4,
    5: LEVEL_5
}
