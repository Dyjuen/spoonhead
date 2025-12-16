# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
PURPLE = (147, 51, 234)
DARK_PURPLE = (87, 30, 140)
PINK = (255, 192, 203)
BROWN = (139, 90, 43)
DARK_BROWN = (101, 67, 33)
GOLD = (255, 215, 0)
SKY_BLUE = (135, 206, 235)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Font
PIXEL_FONT = "assets/font/PressStart2P.ttf"

# --- Asset Placeholders ---
# Replace these with paths to your own assets
# Example: PLAYER_IMAGE = "assets/images/player.png"

# Character sprite paths and buffs
CHARACTER_DATA = {
	'cyborg': {
		'name': 'Cyborg',
		'default': True,
		'idle': "assets/Character/3 Cyborg/Idle1.png",
		'run': "assets/Character/3 Cyborg/Run1.png",
		'jump': "assets/Character/3 Cyborg/Jump1.png",
		'double_jump': "assets/Character/3 Cyborg/Jump2.png",
		'death': "assets/Character/3 Cyborg/Cyborg_death.png",
		'buff': 'damage_boost',  # Example: double damage for 5s after kill
		'buff_desc': 'Damage boost after each kill',
        'emotes': [
            "assets/Character/Emotes/Cyborg/Angry.png",
            "assets/Character/Emotes/Cyborg/Happy.png",
            "assets/Character/Emotes/Cyborg/Idle2.png",
            "assets/Character/Emotes/Cyborg/Sitdown.png",
            "assets/Character/Emotes/Cyborg/Talk.png",
            "assets/Character/Emotes/Cyborg/Use.png",
        ],
        'hand_animations': {
            'idle': "assets/Character/Hands/3 Cyborg/1.png",
            'run': "assets/Character/Hands/3 Cyborg/6.png",
            'jump': ["assets/Character/Hands/3 Cyborg/4.png", "assets/Character/Hands/3 Cyborg/5.png"],
            'double_jump': ["assets/Character/Hands/3 Cyborg/4.png", "assets/Character/Hands/3 Cyborg/5.png"], 
            'emote_angry': "assets/Character/Emotes/Cyborg/Angry.png",
            'emote_happy': "assets/Character/Emotes/Cyborg/Happy.png",
            'emote_talk': "assets/Character/Emotes/Cyborg/Talk.png",
            'emote_use': "assets/Character/Emotes/Cyborg/Use.png",
        }
	},
	'biker': {
		'name': 'Biker',
		'default': False,
		'idle': "assets/Character/1 Biker/Idle1.png",
		'run': "assets/Character/1 Biker/Run1.png",
		'jump': "assets/Character/1 Biker/Jump1.png", # Corrected path
		'double_jump': "assets/Character/1 Biker/Jump2.png", # Corrected path
		'death': "assets/Character/1 Biker/Death.png",
		'buff': 'speed_boost',  # Example: faster run speed
		'buff_desc': 'Increased movement speed',
        'emotes': [
            "assets/Character/Emotes/Biker/Angry.png",
            "assets/Character/Emotes/Biker/Happy.png",
            "assets/Character/Emotes/Biker/Idle2.png",
            "assets/Character/Emotes/Biker/Sitdown.png",
            "assets/Character/Emotes/Biker/Talk.png",
            "assets/Character/Emotes/Biker/Use.png",
        ],
        'hand_animations': {
            'idle': "assets/Character/Hands/1 Biker/1.png",
            'run': "assets/Character/Hands/1 Biker/6.png",
            'jump': ["assets/Character/Hands/1 Biker/4.png", "assets/Character/Hands/1 Biker/5.png"],
            'double_jump': ["assets/Character/Hands/1 Biker/4.png", "assets/Character/Hands/1 Biker/5.png"],
            'emote_angry': "assets/Character/Emotes/Biker/Angry.png",
            'emote_happy': "assets/Character/Emotes/Biker/Happy.png",
            'emote_talk': "assets/Character/Emotes/Biker/Talk.png",
            'emote_use': "assets/Character/Emotes/Biker/Use.png",
        }
	},
	'punk': {
		'name': 'Punk',
		'default': False,
		'idle': "assets/Character/2 Punk/Idle1.png",
		'run': "assets/Character/2 Punk/Run1.png",
		'jump': "assets/Character/2 Punk/Jump1.png", # Corrected path
		'double_jump': "assets/Character/2 Punk/Jump2.png", # Corrected path
		'death': "assets/Character/2 Punk/Death.png",
		'buff': 'jump_boost',  # Example: higher jump
		'buff_desc': 'Higher jump height',
        'emotes': [
            "assets/Character/Emotes/Punk/Angry.png",
            "assets/Character/Emotes/Punk/Happy.png",
            "assets/Character/Emotes/Punk/Idle2.png",
            "assets/Character/Emotes/Punk/Sitdown.png",
            "assets/Character/Emotes/Punk/Talk.png",
            "assets/Character/Emotes/Punk/Use.png",
        ],
        'hand_animations': {
            'idle': "assets/Character/Hands/2 Punk/1.png",
            'run': "assets/Character/Hands/2 Punk/6.png",
            'jump': ["assets/Character/Hands/2 Punk/4.png", "assets/Character/Hands/2 Punk/5.png"],
            'double_jump': ["assets/Character/Hands/2 Punk/4.png", "assets/Character/Hands/2 Punk/5.png"],
            'emote_angry': "assets/Character/Emotes/Punk/Angry.png",
            'emote_happy': "assets/Character/Emotes/Punk/Happy.png",
            'emote_talk': "assets/Character/Emotes/Punk/Talk.png",
            'emote_use': "assets/Character/Emotes/Punk/Use.png",
        }
	},
}

BULLET_SPRITE = "assets/Bullets/1.png"

ENEMY_IDLE_SPRITE = "assets/orangjahat/Idle.png"
ENEMY_WALK_SPRITE = "assets/orangjahat/Walk.png"

PLAYER_IMAGE = None
PROJECTILE_IMAGE = None
BOSS_IMAGE = "assets/orangjahat/Idle.png"
ENEMY_IMAGE = ENEMY_IDLE_SPRITE # Default to idle sprite

# Sound effects
SHOOT_SOUND_PATH = None
SHOOT_SOUND = None
HIT_SOUND = None
COIN_SOUND = None
JUMP_SOUND = None
DASH_SOUND = None
GAMEOVER_SOUND = None
VICTORY_SOUND = None

# Music
THEME_MUSIC = "assets/audio/theme.mp3"
LEVEL_MUSIC = "assets/audio/stage.mp3"
BOSS_THEME = "assets/audio/boss.mp3"

# Game Constants
BOSS_COLLISION_DAMAGE = 10
PLAYER_INVINCIBILITY_TIME = 1000 # milliseconds

# Boss Assets
BOSS_IDLE_SPRITE = "assets/orangjahat/Idle.png"
BOSS_WALK_SPRITE = "assets/orangjahat/Walk.png"
BOSS_DEATH_SPRITE = "assets/orangjahat/Death.png"
BOSS_ATTACK1_SPRITE = "assets/orangjahat/Attack1.png"
BOSS_ATTACK2_SPRITE = "assets/orangjahat/Attack2.png"
BOSS_ATTACK3_SPRITE = "assets/orangjahat/Attack3.png"
BOSS_ATTACK4_SPRITE = "assets/orangjahat/Attack4.png"
BOSS_HURT_SPRITE = "assets/orangjahat/Hurt.png"

# Actual Boss Sprites
BOSS_IDLE_SPRITE_PATH = "assets/boss/Idle.png"
BOSS_WALK_SPRITE_PATH = "assets/boss/Walk.png"
BOSS_DEATH_SPRITE_PATH = "assets/boss/Death.png"

# Sound Effects
DEATH_SOUND = "assets/audio/mati.mp3"
DEFAULT_SHOT_SOUND = "assets/audio/tembak1.mp3"
SPREAD_SHOT_SOUND = "assets/audio/3tembak.mp3"
BURST_SHOT_SOUND = "assets/audio/burst.mp3"
WALK_SOUND = "assets/audio/jalan.mp3"
JUMP_SOUND = "assets/audio/lompat.mp3"
LANDING_SOUND = "assets/audio/landing.mp3"
COIN_SOUND = "assets/audio/coin.mp3"
VICTORY_SOUND = "assets/audio/win.mp3"