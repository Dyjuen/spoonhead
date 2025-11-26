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
    ],
    "moving_platforms": [
        (400, 500, 100, 25, 'y', 100, 1), # Gentle vertical movement
    ],
    "coins": [
        (250, 400), (650, 350), (950, 300), (1250, 250), (1650, 400), (1900, 350),
        (450, 400) # On the moving platform
    ],
    "enemies": [
        # Simple patrols
        { "x": 700, "y": 500, "patrol_distance": 100, "speed": 1, "shoot_cooldown": 4.0 },
        { "x": 1500, "y": 500, "patrol_distance": 150, "speed": 1, "shoot_cooldown": 5.0 },
    ],
    "boss": {
        "boss_type": 1,
        "x": 2400,
        "y": 400,
        "health": 250,
        "speed": 2,
        "shoot_interval": 80, # Slower shooting
        "phases": 1, # Only one phase
    },
    "boss_gate_x": 2100,
}

LEVEL_2 = {
    "name": "Hazard Factory",
    "platforms": [
        (0, 550, 200, 40), (350, 550, 500, 40), (950, 550, 300, 40),
        (1500, 550, 200, 40), (1800, 550, 600, 40),
        # Trickier platforms
        (400, 450, 100, 25), (600, 350, 100, 25), (800, 250, 100, 25),
        (1200, 400, 80, 25), (1350, 320, 80, 25), (1500, 240, 80, 25),
    ],
    "moving_platforms": [
        (250, 500, 100, 25, 'x', 200, 3), # Fast horizontal
        (1000, 450, 100, 25, 'y', 200, 2), # Wider vertical
        (1650, 500, 150, 25, 'x', 150, -3), # Fast reverse horizontal
    ],
    "coins": [
        (450, 400), (650, 300), (850, 200), (1240, 350), (1390, 270), (1540, 190),
        (300, 400), (1100, 250)
    ],
    "enemies": [
        # More enemies, faster shooting
        { "x": 400, "y": 500, "patrol_distance": 150, "speed": 2, "shoot_cooldown": 2.5 },
        { "x": 1000, "y": 500, "patrol_distance": 100, "speed": 3, "shoot_cooldown": 2.0 },
        { "x": 1300, "y": 200, "patrol_distance": 50, "speed": 2, "shoot_cooldown": 3.0 },
        { "x": 2000, "y": 500, "patrol_distance": 200, "speed": 2, "shoot_cooldown": 2.0 },
    ],
    "boss": {
        "boss_type": 2,
        "x": 2400,
        "y": 350,
        "health": 500,
        "speed": 4, # Faster movement
        "shoot_interval": 40, # Faster shooting
        "phases": 2, # Two phases
    },
    "boss_gate_x": 2300,
}

LEVEL_3 = {
    "name": "Crystal Core",
    "platforms": [
        (0, 550, 150, 40), (250, 550, 150, 40), # Small starting ground
        (800, 500, 100, 25), (1000, 450, 100, 25), (1200, 400, 100, 25),
        (1400, 350, 100, 25), (1600, 300, 100, 25),
        (2200, 550, 400, 40),
    ],
    "moving_platforms": [
        (450, 500, 100, 25, 'y', 250, 4), # Fast vertical lift
        (650, 250, 100, 25, 'x', 300, 5), # Long, fast patrol
        (1800, 500, 80, 20, 'y', 300, -5), # Fast downward
        (1900, 200, 80, 20, 'x', 200, 4),
    ],
    "coins": [
        (850, 450), (1050, 400), (1250, 350), (1450, 300), (1650, 250),
        (500, 300), (700, 200)
    ],
    "enemies": [
        # Lots of aggressive enemies
        { "x": 300, "y": 500, "patrol_distance": 50, "speed": 4, "shoot_cooldown": 1.5 },
        { "x": 900, "y": 450, "patrol_distance": 80, "speed": 3, "shoot_cooldown": 1.8 },
        { "x": 1300, "y": 300, "patrol_distance": 100, "speed": 3, "shoot_cooldown": 2.0 },
        { "x": 1700, "y": 250, "patrol_distance": 50, "speed": 4, "shoot_cooldown": 1.5 },
        { "x": 2300, "y": 500, "patrol_distance": 80, "speed": 3, "shoot_cooldown": 1.0 },
    ],
    "boss": {
        "boss_type": 3,
        "x": 2600,
        "y": 300,
        "health": 750,
        "speed": 5, # Very fast
        "shoot_interval": 20, # Very frequent shooting
        "phases": 3, # All three phases
    },
    "boss_gate_x": 2500,
}


ALL_LEVELS = {
    1: LEVEL_1,
    2: LEVEL_2,
    3: LEVEL_3
}
