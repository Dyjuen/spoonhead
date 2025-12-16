import pygame
import random
import os
import math
import time
from settings import *
from level_data import ALL_LEVELS

class SpriteSheet:
    """Utility for loading and parsing sprite sheets."""
    def __init__(self, filename):
        try:
            self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            raise e

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def get_animation_frames(self, frame_width, frame_height):
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        for x in range(0, sheet_width, frame_width):
            frame = self.get_image(x, 0, frame_width, self.sprite_sheet.get_height())
            frames.append(frame)
        return frames

    def get_frames_from_grid(self, rows, cols, frame_width, frame_height):
        frames = []
        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frame = self.get_image(x, y, frame_width, frame_height)
                frames.append(frame)
        return frames

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game, upgrades=None, character_id=None, equipped_gun_id=None, upgrades_data=None):
        super().__init__()
        from settings import CHARACTER_DATA
        from gun_data import GUN_DATA
        self.game = game
        self.upgrades = upgrades if upgrades else {}
        self.character_id = character_id or 'cyborg'
        self.character_data = CHARACTER_DATA[self.character_id]
        self.gun_data = GUN_DATA
        self.buff = self.character_data['buff']
        self.buff_desc = self.character_data['buff_desc']
        # Buff state
        self.buff_active = False
        self.buff_timer = 0

        if upgrades_data is None:
            upgrades_data = {}
        self.upgrades_data = upgrades_data # Store for later if needed

        # Layered rendering
        self.gun_animations = {} # Not used for now, as guns are single image
        self.hand_animations = {}
        self.emote_animations = {}
        self.gun_image = None
        self.hand_image = None # This will be set by animate
        
        self.load_animations()
        self.equipped_gun_id = equipped_gun_id or 'pistol_1'
        self.equip_gun(self.equipped_gun_id)

        self.action = 'idle'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.idle_timer = 0
        self.is_emoting = False
        self.is_emote_playing = False # New line
        self.emote_cooldown = random.randint(5000, 10000)

        # Emote & Double Jump Specifics
        self.idle_timer_start = pygame.time.get_ticks()
        self.idle_duration_threshold = random.randint(5000, 10000) # 5 to 10 seconds
        self.current_emote_frames = []
        self.current_emote_frame_index = 0
        self.emote_start_time = 0
        self.emote_animation_speed = 150 # milliseconds per frame

        self.double_jump_enabled = False
        self.jumps_left = 1 # Default

        # Composite image
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA) # Will be overwritten by animate
        self.rect = self.image.get_rect(center=(x, y))

        self.hitbox = pygame.Rect(0, 0, 20, 45)
        self.hitbox_offset_x = 10
        self.hitbox.center = (self.rect.centerx - self.hitbox_offset_x, self.rect.centery)
        self.max_health = 100
        self.health = self.max_health 
        self.coins_collected_in_level = 0 # Reintroduced for level-specific count
        self.vx = 0
        self.vy = 0
        # Buffs
        self.speed = 6
        self.jump_power = -16
        if self.buff == 'speed_boost':
            self.speed = 7
        if self.buff == 'jump_boost':
            self.jump_power = -20

        # Apply upgrades after max_health is set
        if self.upgrades_data.get("health_up", 0) > 0: # Check if level > 0
            self.max_health = int(self.max_health * 1.5) # Example: 50% more health
            self.health = self.max_health # Update current health to new max

        if self.upgrades_data.get("double_jump", 0) > 0: # Check if level > 0
            self.double_jump_enabled = True
            self.jumps_left = 2 # Allow two jumps
        else:
            self.jumps_left = 1 # Default to single jump

        self.update_buff() # Initialize physics attributes

    def equip_gun(self, gun_id):
        self.equipped_gun_id = gun_id
        gun_info = self.gun_data[gun_id]
        gun_path = gun_info['image_path']
        try:
            # For non-animated guns, just load a single image
            self.gun_image = pygame.image.load(gun_path).convert_alpha()
            self.gun_image = pygame.transform.scale(self.gun_image, (15, 15)) # Example scale
        except pygame.error:
            self.gun_image = pygame.Surface((15, 15), pygame.SRCALPHA)
            self.gun_image.fill(GRAY)
        
        # Load bullet image for the gun
        bullet_path = gun_info['bullet_path']
        try:
            bullet_img = pygame.image.load(bullet_path).convert_alpha()
            scaled_bullet = pygame.transform.scale(bullet_img, (20, 10))
            Projectile.animation_frames_right = [scaled_bullet]
            Projectile.animation_frames_left = [pygame.transform.flip(scaled_bullet, True, False)]
        except pygame.error:
            surf = pygame.Surface((20, 10), pygame.SRCALPHA); surf.fill(YELLOW)
            Projectile.animation_frames_right = [surf]
            Projectile.animation_frames_left = [surf]

    def apply_buff(self):
        # Cyborg: damage boost after kill (5s)
        if self.buff == 'damage_boost':
            self.damage_boost_active = True
            self.damage_boost_timer = pygame.time.get_ticks()
            self.buff_active = True
            self.buff_timer = pygame.time.get_ticks()
        # Biker: speed boost (5s)
        elif self.buff == 'speed_boost':
            self.speed = 10
            self.buff_active = True
            self.buff_timer = pygame.time.get_ticks()
        # Punk: jump boost (5s)
        elif self.buff == 'jump_boost':
            self.jump_power = -28
            self.buff_active = True
            self.buff_timer = pygame.time.get_ticks()

    def update_buff(self):
        # Buff duration: 5 seconds
        if self.buff_active and pygame.time.get_ticks() - self.buff_timer > 5000:
            if self.buff == 'damage_boost':
                self.damage_boost_active = False
            elif self.buff == 'speed_boost':
                self.speed = 7
            elif self.buff == 'jump_boost':
                self.jump_power = -20
            self.buff_active = False
        self.gravity = 0.8
        self.on_ground = False
        self.jumps_made = 0
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 200
        self.dash_speed = 15
        self.dash_cooldown = 500
        self.last_dash = 0
        self.can_shoot = True
        self.shoot_cooldown = 250
        self.last_shot = 0
        self.facing_right = True
        self.shot_damage = 10
        self.unlocked_weapons = ['default']
        self.current_weapon_index = 0
        self.was_on_ground = False
        self.damage_boost_active = False
        self.damage_boost_timer = 0
        self.power_up_duration = 10000
        self.ultimate_meter = 0
        self.ultimate_max_meter = 5
        self.ultimate_ready = False
        self.apply_upgrades()

    def apply_upgrades(self):
        self.max_health += 25 * self.upgrades.get('health_up', 0)
        self.shot_damage += 5 * self.upgrades.get('damage_up', 0)

        if self.upgrades.get('spread_shot', 0) > 0 and 'spread_shot' not in self.unlocked_weapons:
            self.unlocked_weapons.append('spread_shot')

        if self.upgrades.get('burst_shot', 0) > 0 and 'burst_shot' not in self.unlocked_weapons:
            self.unlocked_weapons.append('burst_shot')



    def switch_weapon(self):
        if self.is_emote_playing: return
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.unlocked_weapons)

    def load_animations(self):
        player_size = (62, 62)
        hand_size = (62, 62) # Example size

        # Load body animations
        self.body_animations = {'idle': [], 'run': [], 'jump': [], 'double_jump': []}
        for anim_type in ['idle', 'run', 'jump', 'double_jump']: # Only main actions have body animations
            sprite_path = self.character_data.get(anim_type)
            if sprite_path:
                loaded_frames = []
                if isinstance(sprite_path, list): # Handle list of image paths
                    for path in sprite_path:
                        try:
                            img = pygame.image.load(path).convert_alpha()
                            scaled_img = pygame.transform.scale(img, player_size)
                            loaded_frames.append(scaled_img)
                        except (pygame.error, FileNotFoundError):
                            loaded_frames.append(pygame.Surface(player_size, pygame.SRCALPHA)) # Placeholder
                    self.body_animations[anim_type] = loaded_frames
                else: # Handle single sprite sheet path
                    try:
                        sheet = SpriteSheet(sprite_path)
                        frames = sheet.get_animation_frames(48, 48)
                        scaled_frames = [pygame.transform.scale(frame, player_size) for frame in frames]
                        self.body_animations[anim_type] = scaled_frames
                    except (pygame.error, FileNotFoundError):
                        placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                        self.body_animations[anim_type] = [placeholder_frame] * 4
            else: # Fallback if action sprite path not defined
                placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                self.body_animations[anim_type] = [placeholder_frame] * 4


        # Load hand animations for each action
        self.hand_animations = {}
        if 'hand_animations' in self.character_data:
            for anim_type, hand_path_val in self.character_data['hand_animations'].items():
                loaded_frames = []
                if isinstance(hand_path_val, list):
                    for path in hand_path_val:
                        try:
                            img = pygame.image.load(path).convert_alpha()
                            scaled_img = pygame.transform.scale(img, hand_size)
                            loaded_frames.append(scaled_img)
                        except (pygame.error, FileNotFoundError):
                            loaded_frames.append(pygame.Surface(hand_size, pygame.SRCALPHA)) # Placeholder
                else: # Assume it's a single string path
                    try:
                        img = pygame.image.load(hand_path_val).convert_alpha()
                        scaled_img = pygame.transform.scale(img, hand_size)
                        loaded_frames.append(scaled_img)
                    except (pygame.error, FileNotFoundError):
                        loaded_frames.append(pygame.Surface(hand_size, pygame.SRCALPHA)) # Placeholder
                
                # Match length to body anim if possible, else use a list of 1 for single images
                target_length = len(self.body_animations.get(anim_type, [None])) if anim_type in self.body_animations else 1
                
                # If loaded_frames is empty (e.g., all paths failed to load)
                if not loaded_frames:
                    loaded_frames.append(pygame.Surface(hand_size, pygame.SRCALPHA)) # Ensure at least one placeholder

                # If only one frame is loaded but target_length > 1, repeat the frame
                if len(loaded_frames) == 1 and target_length > 1:
                    self.hand_animations[anim_type] = loaded_frames * target_length
                else:
                    self.hand_animations[anim_type] = loaded_frames
        
        # Ensure all body animation actions have a corresponding hand animation, even if placeholder
        for anim_type, body_frames in self.body_animations.items():
            if anim_type not in self.hand_animations:
                placeholder_frame = pygame.Surface(hand_size, pygame.SRCALPHA)
                self.hand_animations[anim_type] = [placeholder_frame] * len(body_frames)

        # Load emote animations
        self.emote_animations = {}
        if 'emotes' in self.character_data:
            for emote_path in self.character_data['emotes']:
                emote_name = os.path.splitext(os.path.basename(emote_path))[0].lower() # Extract name from path
                try:
                    img = pygame.image.load(emote_path).convert_alpha()
                    scaled_img = pygame.transform.scale(img, player_size)
                    self.emote_animations[emote_name] = [scaled_img] # Use name as key
                except (pygame.error, FileNotFoundError):
                    pass

    def animate(self):
        now = pygame.time.get_ticks()
        
        body_frame = None
        hand_frame = None

        if self.is_emoting:
            # Emote animation
            # self.action holds the key for the current emote (e.g., 'emote_angry')
            current_emote_animation = self.emote_animations.get(self.action, [pygame.Surface((60, 60), pygame.SRCALPHA)])
            
            if now - self.emote_start_time > self.emote_animation_speed:
                self.emote_start_time = now
                self.current_emote_frame_index = (self.current_emote_frame_index + 1) % len(current_emote_animation)
            
            body_frame = current_emote_animation[self.current_emote_frame_index]
            # No hand or gun when emoting, so hand_frame remains None
            
        else: # Regular animation logic
            if self.action == 'double_jump' and self.frame_index >= len(self.body_animations['double_jump']) - 1:
                self.set_action('jump')
            
            current_body_animation = self.body_animations.get(self.action)
            if not current_body_animation:
                current_body_animation = self.body_animations['idle'] # Fallback
            
            if now - self.last_frame_update > 100:
                self.last_frame_update = now
                self.frame_index = (self.frame_index + 1) % len(current_body_animation)
            
            body_frame = current_body_animation[self.frame_index]
            hand_frames_list = self.hand_animations.get(self.action, self.hand_animations['idle'])
            hand_frame = hand_frames_list[self.frame_index % len(hand_frames_list)]
        
        # Handle flipping and composite image creation
        if not self.facing_right:
            body_frame = pygame.transform.flip(body_frame, True, False)
            if hand_frame:
                hand_frame = pygame.transform.flip(hand_frame, True, False)
        
        # Create a new composite image
        composite_image = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        # Blit body frame
        composite_image.blit(body_frame, (0, 0))

        if not self.is_emoting and self.action not in ('jump', 'double_jump'): # Only draw hand and gun if not emoting AND not jumping
            # Position hand relative to body
            current_hand_offset_x = 20
            current_hand_offset_y = 30
            
            # Adjust offsets for jump/double_jump
            if self.action in ('jump', 'double_jump'):
                current_hand_offset_x = 10 # Example adjustment
                current_hand_offset_y = 15 # Example adjustment

            # Position gun relative to hand
            gun_offset_x = 0
            gun_offset_y = 0

            # Blit gun and hand
            if self.gun_image:
                flipped_gun_image = pygame.transform.flip(self.gun_image, True, False) if not self.facing_right else self.gun_image
                composite_image.blit(flipped_gun_image, (current_hand_offset_x + gun_offset_x, current_hand_offset_y + gun_offset_y))
            if hand_frame:
                composite_image.blit(hand_frame, (current_hand_offset_x, current_hand_offset_y))

        self.image = composite_image
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_action(self, new_action):
        if self.action != new_action:
            self.action = new_action
            self.frame_index = 0
            self.last_frame_update = pygame.time.get_ticks() # Reset timer on action change
            if self.action.startswith('emote'):
                self.is_emoting = True # Keep this for idle timer logic
            else:
                self.is_emoting = False # Reset this if not emoting

    def update(self, move_input, platforms):
        sfx_events = []
        now = pygame.time.get_ticks()

        # Emote logic
        if self.action == 'idle' and not self.is_emoting and self.on_ground and (move_input is None or (move_input >= 0.4 and move_input <= 0.6)): # Only trigger emotes when truly idle
            if now - self.idle_timer_start > self.idle_duration_threshold:
                if self.emote_animations:
                    self.is_emoting = True
                    # Randomly select an emote from the dictionary keys
                    selected_emote_key = random.choice(list(self.emote_animations.keys()))
                    self.set_action(selected_emote_key)
                    self.current_emote_frames = self.emote_animations[selected_emote_key]
                    self.current_emote_frame_index = 0
                    self.emote_start_time = now
                    # Reset idle timer for next potential emote
                    self.idle_timer_start = now
                    self.idle_duration_threshold = random.randint(5000, 10000)
        # If player moves, jumps, or shoots, stop emoting
        elif self.is_emoting and (
            (move_input is not None and (move_input < 0.4 or move_input > 0.6)) # Movement
            or self.vy < 0 # Jumping
            or (hasattr(self.game, 'shooting') and self.game.shooting and pygame.time.get_ticks() - self.last_shot < self.shoot_cooldown) # Shooting
        ):
            self.is_emoting = False
            self.set_action('idle') # Return to idle animation
            self.idle_timer_start = now # Reset timer
            self.idle_duration_threshold = random.randint(5000, 10000)
        # Reset idle timer if not idle or emoting has stopped naturally
        if not self.is_emoting and (self.action != 'idle' or not self.on_ground or (move_input is not None and (move_input < 0.4 or move_input > 0.6))):
            self.idle_timer_start = now
            self.idle_duration_threshold = random.randint(5000, 10000)

        if self.is_emote_playing:
            self.vx = 0 # No horizontal movement during emote
            # No action change based on movement during emote
        else: # Only process movement and action changes if not emoting
            if not self.on_ground:
                if self.vy > 0 and self.action != 'double_jump': self.set_action('jump') # Falling
            elif move_input is not None and (move_input < 0.4 or move_input > 0.6): self.set_action('run')
            else: self.set_action('idle')

            self.vx = 0
            if move_input is not None:
                if self.dashing:
                    if pygame.time.get_ticks() - self.dash_timer > self.dash_duration: self.dashing = False
                    self.vx = self.dash_speed * (1 if self.facing_right else -1)
                else:
                    if move_input < 0.4: self.vx = -self.speed; self.facing_right = False
                    elif move_input > 0.6: self.vx = self.speed; self.facing_right = True
        
        self.hitbox.x += self.vx
        for platform in platforms:
            if platform.rect.colliderect(self.hitbox):
                if self.vx > 0: self.hitbox.right = platform.rect.left
                elif self.vx < 0: self.hitbox.left = platform.rect.right
        # Apply offset yang dinamis berdasarkan arah hadap
        offset = self.hitbox_offset_x if self.facing_right else -self.hitbox_offset_x
        self.rect.centerx = self.hitbox.centerx + offset

        # Vertical movement (gravity)
        self.vy += self.gravity
        if self.vy > 15: self.vy = 15
        self.hitbox.y += self.vy
        self.on_ground = False
        
        # Track the moving platform the player is standing on
        self.standing_on_moving = None
        for platform in platforms:
            if platform.rect.colliderect(self.hitbox):
                if self.vy > 0:
                    self.hitbox.bottom = platform.rect.top
                    self.vy = 0
                    self.on_ground = True
                    # Reset jumps_left when landing
                    self.jumps_left = 2 if self.double_jump_enabled else 1
                    # Cek apakah platform adalah MovingPlatform
                    if hasattr(platform, 'direction') and hasattr(platform, 'speed') and hasattr(platform, 'move_axis'):
                        self.standing_on_moving = platform
                elif self.vy < 0:
                    self.hitbox.top = platform.rect.bottom
                    self.vy = 0

        # Jika berdiri di atas moving platform, ikutkan pergerakan platform
        if self.on_ground and self.standing_on_moving is not None:
            # Hitung delta gerak platform
            plat = self.standing_on_moving
            if plat.move_axis == 'x':
                self.hitbox.x += plat.speed * plat.direction
            else:
                self.hitbox.y += plat.speed * plat.direction
        
        self.rect.bottom = self.hitbox.bottom
        # Re-center X after potential moving platform adjustments
        self.rect.centerx = self.hitbox.centerx + (self.hitbox_offset_x if self.facing_right else -self.hitbox_offset_x)

        self.animate()

        if self.on_ground and not self.was_on_ground:
            sfx_events.append('landing')

        self.was_on_ground = self.on_ground
        
        # Power-up timer
        if self.damage_boost_active and pygame.time.get_ticks() - self.damage_boost_timer > self.power_up_duration:
            self.damage_boost_active = False
            
        return sfx_events

    def jump(self):
        if self.is_emote_playing: return None
        if self.jumps_left > 0 and not self.is_emoting:
            self.vy = self.jump_power
            self.on_ground = False
            if self.double_jump_enabled and self.jumps_left == 2: # First jump
                self.set_action('jump')
            elif self.double_jump_enabled and self.jumps_left == 1: # Second jump
                self.set_action('double_jump')
            elif not self.double_jump_enabled and self.jumps_left == 1: # Single jump
                self.set_action('jump')
            self.jumps_left -= 1
            return 'jump'
        elif not self.double_jump_enabled and self.jumps_left == 0:
            pass
        return None

    def dash(self):
        if self.is_emote_playing: return
        current_time = pygame.time.get_ticks()
        if not self.dashing and current_time - self.last_dash > self.dash_cooldown and not self.is_emoting:
            self.dashing = True; self.dash_timer = current_time; self.last_dash = current_time

    def shoot(self, shoot_direction='horizontal'):
        if self.is_emote_playing: return None, None
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown and not self.is_emoting:
            self.last_shot = current_time
            projectiles = pygame.sprite.Group()
            sfx_name = 'default_shot' # Default sound
            
            damage = self.shot_damage * 2 if self.damage_boost_active else self.shot_damage
            
            direction = 1 if self.facing_right else -1
            current_weapon = self.unlocked_weapons[self.current_weapon_index]

            if current_weapon == 'burst_shot':
                sfx_name = 'burst_shot'
                for i in range(3):
                    proj = Projectile(self.rect.centerx + (i * 15 * direction), self.rect.centery, 12 * direction, 0, damage=damage)
                    projectiles.add(proj)
                return projectiles, sfx_name

            if current_weapon == 'spread_shot':
                sfx_name = 'spread_shot'
                angles = [-15, 0, 15] # Degrees
                for angle in angles:
                    rad_angle = math.radians(angle)
                    # Adjust for facing direction
                    if not self.facing_right:
                        rad_angle = math.pi - rad_angle
                    
                    vx = 12 * math.cos(rad_angle)
                    vy = 12 * math.sin(rad_angle)
                    projectiles.add(Projectile(self.rect.centerx, self.rect.centery, vx, vy, damage=damage))
                return projectiles, sfx_name

            # Default shot
            speed = 12
            sqrt2_half = 0.7071 # Approximation of sin(45) and cos(45)

            if shoot_direction == 'up':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, 0, -speed, damage=damage))
            elif shoot_direction == 'down':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, 0, speed, damage=damage))
            elif shoot_direction == 'up_right':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed * sqrt2_half, -speed * sqrt2_half, damage=damage))
            elif shoot_direction == 'up_left':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, -speed * sqrt2_half, -speed * sqrt2_half, damage=damage))
            elif shoot_direction == 'down_right':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed * sqrt2_half, speed * sqrt2_half, damage=damage))
            elif shoot_direction == 'down_left':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, -speed * sqrt2_half, speed * sqrt2_half, damage=damage))
            elif shoot_direction == 'left':
                 projectiles.add(Projectile(self.rect.centerx, self.rect.centery, -speed, 0, damage=damage))
            elif shoot_direction == 'right':
                 projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed, 0, damage=damage))
            else: # horizontal
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed * direction, 0, damage=damage))
            
            return projectiles, sfx_name
        return None, None

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0: self.health = 0

    def activate_power_up(self, power_up_type):
        if power_up_type == 'damage_boost':
            self.damage_boost_active = True
            self.damage_boost_timer = pygame.time.get_ticks()
        elif power_up_type == 'health':
            self.health += 25
            if self.health > self.max_health:
                self.health = self.max_health

    def increase_ultimate_meter(self):
        if not self.ultimate_ready:
            self.ultimate_meter += 1
            if self.ultimate_meter >= self.ultimate_max_meter:
                self.ultimate_ready = True
        # Trigger buff on kill for Cyborg only
        if self.buff == 'damage_boost':
            self.apply_buff()

    def activate_ultimate(self):
        if self.is_emote_playing: return None
        if self.ultimate_ready:
            self.ultimate_meter = 0
            self.ultimate_ready = False
            # Create a massive projectile
            # For simplicity, let's make it deal a fixed high damage and be larger
            massive_damage = 50
            massive_speed = 15
            direction = 1 if self.facing_right else -1
            # Adjust projectile's appearance or properties for massive shot if needed
            # There is no special animation for the ultimate, the projectile is just scaled up.
            proj = Projectile(self.rect.centerx, self.rect.centery, massive_speed * direction, 0, damage=massive_damage)
            # You might want to make this projectile visually different (e.g., larger sprite, different color)
            # This would require modifying the Projectile class or creating a new UltimateProjectile class.
            # For now, we'll just use the regular Projectile class with higher damage.
            proj.image = pygame.transform.scale(proj.image, (40, 20)) # Example: make it bigger
            return proj
        return None


class Enemy(pygame.sprite.Sprite):
    """Enemy that patrols and shoots, with flashing effect only when taking damage."""
    def __init__(self, x, y, player, patrol_distance=100, speed=2, shoot_cooldown=2.0):
        super().__init__()
        self.player = player
        self.load_animations()
        self.action = 'walk'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.copy()
        self.health, self.speed, self.direction = 30, speed, 1
        self.start_x, self.patrol_distance = x, patrol_distance
        self.shoot_cooldown, self.last_shot_time = shoot_cooldown, time.time()
        self.detection_range = 400
        # Flashing effect for damage
        self.flash_timer = 0
        self.original_image = self.image
        self.vy = 0
        self.gravity = 0.8
        self.on_ground = False

    def load_animations(self):
        self.animations = {}
        enemy_size = (106, 106) # Increased size by 10 pixels
        
        animation_types = ['walk', 'idle', 'attack1', 'attack2', 'attack3', 'attack4', 'death', 'hurt', 'special']
        
        for anim_type in animation_types:
            path = f"assets/orangjahat/{anim_type.capitalize()}.png"
            try:
                sheet = SpriteSheet(path)
                frames = sheet.get_animation_frames(96, 96)
                self.animations[anim_type] = [pygame.transform.scale(frame, enemy_size) for frame in frames]
            except Exception as e:
                # If a specific animation is missing, create a placeholder
                placeholder_surface = pygame.Surface(enemy_size, pygame.SRCALPHA)
                placeholder_surface.fill((255, 0, 255, 128)) # Pink placeholder
                self.animations[anim_type] = [placeholder_surface] * 6

    def animate(self):
        now = pygame.time.get_ticks()
        
        # Ensure self.action is valid, otherwise default to 'idle'
        if self.action not in self.animations:
            self.action = 'idle'
            
        current_animation = self.animations[self.action]
        
        if now - self.last_frame_update > 120:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(current_animation)
            new_image = current_animation[self.frame_index]
            if self.direction == -1:
                new_image = pygame.transform.flip(new_image, True, False)
            center = self.rect.center
            self.image, self.rect = new_image, new_image.get_rect(center=center)
            self.original_image = self.image
        
        # Apply flashing effect if taking damage
        if self.flash_timer > 0:
            self.flash_timer -= 1
            # Flash every 100ms (alternating visible/invisible)
            if (self.flash_timer // 5) % 2 == 0:
                flash_image = self.original_image.copy()
                flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                self.image = flash_image

    def update(self, player, all_sprites_group, enemy_projectiles_group, platforms):
        # State logic
        if self.speed > 0:
            self.action = 'walk'
        else:
            self.action = 'idle'
            
        # Horizontal movement
        self.hitbox.x += self.speed * self.direction
        if abs(self.hitbox.centerx - self.start_x) > self.patrol_distance:
            self.direction *= -1

        # Vertical movement (gravity)
        self.vy += self.gravity
        if self.vy > 15: self.vy = 15
        self.hitbox.y += self.vy
        self.on_ground = False

        # Vertical collision with platforms
        for platform in platforms:
            if platform.rect.colliderect(self.hitbox) and self.vy > 0:
                self.hitbox.bottom = platform.rect.top
                self.vy = 0
                self.on_ground = True
        
        self.rect.bottom = self.hitbox.bottom
        self.rect.centerx = self.hitbox.centerx

        self.animate()
        
        # Shooting logic
        if abs(player.rect.centerx - self.rect.centerx) < self.detection_range and time.time() - self.last_shot_time > self.shoot_cooldown:
            self.shoot_at_player(player, all_sprites_group, enemy_projectiles_group)
            self.last_shot_time = time.time()

    def shoot_at_player(self, player, all_sprites, projectiles_group):
        dx = player.rect.centerx - self.rect.centerx
        # Aim for the player's lower body instead of their center
        dy = (player.rect.bottom - 10) - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance == 0: return
        vx, vy = (dx / distance) * 6, (dy / distance) * 6
        proj = EnemyProjectile(self.rect.centerx, self.rect.centery, vx, vy)
        all_sprites.add(proj); projectiles_group.add(proj)

    def take_damage(self, amount):
        self.health -= amount
        # Trigger flash effect for 300ms
        self.flash_timer = 30
        if self.health <= 0:
            self.kill()
            self.player.increase_ultimate_meter()

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA); self.image.fill(RED)
        pygame.draw.circle(self.image, RED, (6, 6), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy, self.lifetime = vx, vy, 180

    def update(self, platforms):
        self.rect.move_ip(self.vx, self.vy); self.lifetime -= 1
        if self.lifetime <= 0 or not self.rect.colliderect(pygame.Rect(-100,-100,10000,SCREEN_HEIGHT+200)): self.kill()
        if pygame.sprite.spritecollide(self, platforms, False):
            self.kill()

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__(); self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PINK, (8, 8), 8); pygame.draw.circle(self.image, PURPLE, (8, 8), 5)
        self.rect = self.image.get_rect(center=(x, y)); self.vx, self.vy = vx, vy

    def update(self, platforms):
        self.rect.move_ip(self.vx, self.vy)
        if not self.rect.colliderect(pygame.Rect(-50,-50,SCREEN_WIDTH+100,SCREEN_HEIGHT+100)): self.kill()
        if pygame.sprite.spritecollide(self, platforms, False):
            self.kill()

class Projectile(pygame.sprite.Sprite):
    animation_frames_right, animation_frames_left = [], []
    @staticmethod
    def load_images():
        if Projectile.animation_frames_right: return
        bullet_size, sprite_paths = (20, 10), [os.path.join("assets", "Guns", "Pistols", "5 Bullets", f"7_{i}.png") for i in "12"]
        try:
            for path in sprite_paths:
                img = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(img, bullet_size)
                Projectile.animation_frames_right.append(scaled)
                Projectile.animation_frames_left.append(pygame.transform.flip(scaled, True, False))
        except pygame.error:
            surf = pygame.Surface(bullet_size, pygame.SRCALPHA); surf.fill(YELLOW)
            Projectile.animation_frames_right = [surf]*2; Projectile.animation_frames_left = [surf]*2

    def __init__(self, x, y, vx, vy, damage=10):
        super().__init__()
        direction = 1 if vx >= 0 else -1
        self.anim_frames = Projectile.animation_frames_right if direction == 1 else Projectile.animation_frames_left
        self.frame_index, self.last_frame_update = 0, pygame.time.get_ticks()
        self.image = self.anim_frames[self.frame_index]; self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy
        self.damage = damage

    def update(self):
        if pygame.time.get_ticks() - self.last_frame_update > 100:
            self.last_frame_update = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(self.anim_frames); self.image = self.anim_frames[self.frame_index]
        self.rect.move_ip(self.vx, self.vy)
        if not self.rect.colliderect(pygame.Rect(-100,-100,10000,SCREEN_HEIGHT+200)): self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height)); self.image.fill(BROWN)
        pygame.draw.rect(self.image, DARK_BROWN, (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, move_axis='x', move_range=100, speed=2):
        super().__init__(x, y, width, height)
        self.start_pos = pygame.math.Vector2(x, y)
        self.move_axis, self.move_range, self.speed, self.direction = move_axis, move_range, speed, 1

    def update(self):
        if self.move_axis == 'x': self.rect.x += self.speed * self.direction
        else: self.rect.y += self.speed * self.direction
        if abs((self.rect.x if self.move_axis == 'x' else self.rect.y) - (self.start_pos.x if self.move_axis == 'x' else self.start_pos.y)) >= self.move_range:
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations = {}
        self.load_animations()
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()

        self.image = self.animations['idle'][self.frame_index] # Set initial image
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset, self.bob_range, self.original_y = random.uniform(0, 2*math.pi), 4, y

    def load_animations(self):
        self.animations['idle'] = []
        coin_size = (32, 32) # Increased size for better visibility
        try:
            sheet = SpriteSheet(COIN_SPRITE_PATH)
            frames = sheet.get_animation_frames(16, 16) # Use provided frame dimensions
            self.animations['idle'] = [pygame.transform.scale(frame, coin_size) for frame in frames]
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(coin_size, pygame.SRCALPHA); placeholder_frame.fill(GOLD)
            self.animations['idle'] = [placeholder_frame] * 15 # Use number of frames provided

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 100: # Adjust animation speed as needed
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations['idle'])
            self.image = self.animations['idle'][self.frame_index]

        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range); self.bob_offset += 0.1

class BossGate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations = {}
        self.load_animations()
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

    def load_animations(self):
        self.animations['idle'] = []
        portal_size = (128, 128) # Scaled up size for better visibility
        try:
            for i in range(1, 8): # Load portal1_frame_1.png to portal1_frame_7.png
                path = os.path.join(PORTAL_IMAGES_DIR, f"portal1_frame_{i}.png")
                img = pygame.image.load(path).convert_alpha()
                self.animations['idle'].append(pygame.transform.scale(img, portal_size))
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(portal_size, pygame.SRCALPHA)
            placeholder_frame.fill(PURPLE)
            self.animations['idle'] = [placeholder_frame] * 7

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 100: # Animation speed
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations['idle'])
            self.image = self.animations['idle'][self.frame_index]

class PowerUpBox(pygame.sprite.Sprite):
    def __init__(self, x, y, power_up_type='damage_boost', health=50):
        super().__init__()
        self.animations = {}
        self.load_animations()
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()

        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.power_up_type = power_up_type
        self.health = health
        self.bob_offset = random.uniform(0, 2*math.pi)
        self.bob_range = 4
        self.original_y = y

    def load_animations(self):
        self.animations['idle'] = []
        crate_size = (80, 80)
        try:
            sheet = SpriteSheet(CRATE_SPRITE_PATH)
            frames = sheet.get_animation_frames(48, 48)
            self.animations['idle'] = [pygame.transform.scale(frame, crate_size) for frame in frames]
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(crate_size, pygame.SRCALPHA); placeholder_frame.fill(GRAY)
            self.animations['idle'] = [placeholder_frame] * 6

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return self.power_up_type
        return None

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 100:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations['idle'])
            self.image = self.animations['idle'][self.frame_index]

        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range); self.bob_offset += 0.1

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_up_type):
        super().__init__()
        self.power_up_type = power_up_type
        
        power_up_size = (32, 32)
        if self.power_up_type == 'damage_boost':
            try:
                self.image = pygame.image.load(DAMAGE_POWERUP_PATH).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.image = pygame.Surface(power_up_size, pygame.SRCALPHA); self.image.fill(ORANGE)
        elif self.power_up_type == 'health':
            try:
                self.image = pygame.image.load(HEALTH_POWERUP_PATH).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.image = pygame.Surface(power_up_size, pygame.SRCALPHA); self.image.fill(GREEN)
        else: # Default or unknown power-up
            self.image = pygame.Surface(power_up_size, pygame.SRCALPHA); self.image.fill(WHITE)

        self.image = pygame.transform.scale(self.image, power_up_size)
        self.rect = self.image.get_rect(center=(x, y))

        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2) # Border

        # Add bobbing attributes
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.bob_range = 8  # More pronounced bob
        self.original_y = y  # Store original Y for bobbing
        self.bob_speed = 0.1 # Speed of bobbing

    def update(self):
        # Implement bobbing effect
        self.bob_offset += self.bob_speed
        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range)

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, game, boss_type, health, speed, shoot_interval, phases):
        super().__init__()
        self.game = game
        self.boss_type = boss_type
        self.max_health = health
        self.health = health
        self.speed = speed
        self.shoot_interval = shoot_interval  # Now assumed to be in milliseconds
        self.phases = phases
        self.current_phase = 1
        self.last_shot_time = pygame.time.get_ticks() # Use pygame.time.get_ticks() for consistency with shoot_interval
        self.pattern_counter = 0  # Used for cycling through patterns

        # Flashing effect for damage
        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 100 # milliseconds

        self.animations = {} # Initialize animations dictionary
        self.load_animations() # Load animations
        self.action = 'idle'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()

        self.dying_state = None # 'falling', 'exploding', None
        self.vy = 0 # Vertical velocity for falling
        self.gravity = 0.5 # Gravity for falling
        self.explosion_start_time = 0 # To track explosion duration

        self.image = self.animations[self.action][self.frame_index] # Set initial image
        self.rect = self.image.get_rect(center=(x, y))
        self.original_image = self.image.copy() # Store original for flashing

        self.direction = 1 # For simple horizontal movement

    def load_animations(self):
        self.animations = {'idle': [], 'walk': [], 'death': []}
        boss_size = (96, 96) # Adjust size to exact frame dimensions

        # Load Idle animation
        try:
            sheet = SpriteSheet(BOSS_IDLE_SPRITE_PATH)
            frames = sheet.get_animation_frames(72, 72) # Use provided frame dimensions
            self.animations['idle'] = [pygame.transform.scale(frame, boss_size) for frame in frames]
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(boss_size, pygame.SRCALPHA); placeholder_frame.fill(PURPLE)
            self.animations['idle'] = [placeholder_frame] * 4

        # Load Walk animation
        try:
            sheet = SpriteSheet(BOSS_WALK_SPRITE_PATH)
            frames = sheet.get_animation_frames(72, 72) # Use provided frame dimensions
            self.animations['walk'] = [pygame.transform.scale(frame, boss_size) for frame in frames]
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(boss_size, pygame.SRCALPHA); placeholder_frame.fill(DARK_PURPLE)
            self.animations['walk'] = [placeholder_frame] * 4
        
        # Load Death animation
        try:
            sheet = SpriteSheet(BOSS_DEATH_SPRITE_PATH)
            frames = sheet.get_animation_frames(72, 72) # Use provided frame dimensions
            self.animations['death'] = [pygame.transform.scale(frame, boss_size) for frame in frames]
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(boss_size, pygame.SRCALPHA); placeholder_frame.fill(RED)
            self.animations['death'] = [placeholder_frame] * 4
        
        # Load Explosion animation
        explosion_size = (128, 128) # Larger size for explosion effect
        try:
            sheet = SpriteSheet(BOSS_EXPLOSION_SPRITE_PATH)
            frames = sheet.get_animation_frames(64, 52) # Use provided frame dimensions for explosion
            self.animations['explosion'] = [pygame.transform.scale(frame, explosion_size) for frame in frames]
        except (pygame.error, FileNotFoundError):
            placeholder_frame = pygame.Surface(explosion_size, pygame.SRCALPHA); placeholder_frame.fill(ORANGE)
            self.animations['explosion'] = [placeholder_frame] * 32 # Use number of frames provided

    def animate(self):
        now = pygame.time.get_ticks()
        current_animation = self.animations.get(self.action)
        if not current_animation:
            current_animation = self.animations['idle'] # Fallback

        animation_speed = 150 # Default speed
        is_looping_animation = True

        if self.action == 'death':
            animation_speed = 200 # Slower death animation
            is_looping_animation = False
        elif self.action == 'explosion':
            animation_speed = 30 # Faster explosion animation
            is_looping_animation = False

        if now - self.last_frame_update > animation_speed:
            self.last_frame_update = now
            
            if is_looping_animation or self.frame_index < len(current_animation) - 1:
                self.frame_index = (self.frame_index + 1) % len(current_animation)
            # If it's a non-looping animation and we're at the last frame, keep it there.

            new_image = current_animation[self.frame_index]
            if self.direction == -1: # Assuming Boss also flips based on direction
                new_image = pygame.transform.flip(new_image, True, False)
            
            center = self.rect.center
            self.image, self.rect = new_image, new_image.get_rect(center=center)
            self.original_image = self.image.copy() # Update original_image for flashing

    def load_image(self):
        # Placeholder image for the boss
        # In a real game, this would load actual boss spritesheets/animations
        boss_size = (100, 100)
        self.image = pygame.Surface(boss_size, pygame.SRCALPHA)
        self.image.fill(PURPLE)
        pygame.draw.circle(self.image, DARK_PURPLE, (boss_size[0]//2, boss_size[1]//2), boss_size[0]//2 - 5)
        # You can add different visuals based on boss_type here
        if self.boss_type == 1:
            self.image.fill(BLUE)
        elif self.boss_type == 2:
            self.image.fill(GREEN)
        elif self.boss_type == 3:
            self.image.fill(RED)

    def update(self):
        if self.dying_state == 'falling':
            self.vy += self.gravity
            self.rect.y += self.vy

            # Collision with platforms for falling
            # Assuming self.game.platforms is accessible and contains all platforms
            for platform in self.game.platforms:
                if platform.rect.colliderect(self.rect) and self.vy > 0: # Only check if falling
                    self.rect.bottom = platform.rect.top
                    self.vy = 0
                    self.dying_state = 'exploding'
                    self.explosion_start_time = pygame.time.get_ticks()
                    self.game.start_screen_shake(duration=500, intensity=5) # 0.5s shake, medium intensity
                    self.game._play_sfx('explosion') # Play explosion sound
                    break # Stop checking for platforms once landed

            # Continue death animation while falling
            self.animate()
            return # Stop other updates if boss is in dying state

        elif self.dying_state == 'exploding':
            # Set action to explosion and animate
            self.action = 'explosion'
            self.animate() # This will ensure the explosion frames are played

            # After explosion animation, kill the boss and transition to victory
            # Check if explosion animation has finished playing
            if self.frame_index >= len(self.animations['explosion']) - 1:
                self.kill()
                self.game.game_state = 'victory' 
                
                # Unlock next level logic
                if self.game.current_level == self.game.unlocked_levels and self.game.unlocked_levels < len(ALL_LEVELS):
                    self.game.unlocked_levels += 1
                
                self.game.total_coins += self.game.player.coins_collected_in_level
                self.game.save_game_data()
                
                self.game._play_sfx('victory') 
            return # Stop other updates during explosion
        # If not dying, proceed with normal boss behavior
        # Simple horizontal movement for now
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1

        # Always use idle animation if not dying
        self.action = 'idle'
        
        self.animate() # Update boss animation

        now = pygame.time.get_ticks() # Use pygame.time.get_ticks() for consistency
        if now - self.last_shot_time > self.shoot_interval and self.shoot_interval != float('inf'): # Check if boss is still attacking
            self.last_shot_time = now
            if self.boss_type == 1:
                self.shoot_pattern_boss1()
            elif self.boss_type == 2:
                self.shoot_pattern_boss2()
            elif self.boss_type == 3:
                self.shoot_pattern_boss3()
        
        # Handle flashing
        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_timer > self.flash_duration:
                self.is_flashing = False
                self.image = self.original_image.copy() # Revert to original
            else:
                # Simple flash: make it brighter
                flash_image = self.original_image.copy()
                flash_image.fill((100, 100, 100, 0), special_flags=pygame.BLEND_ADD) # Brighten
                self.image = flash_image


    def shoot_pattern_boss1(self):
        # Boss 1 only has one simple pattern.
        self.shoot_pattern_1()

    def shoot_pattern_boss2(self):
        # Boss 2 uses pattern 2 in phase 1, and pattern 3 in phase 2.
        if self.current_phase == 1:
            self.shoot_pattern_2()
        else:
            self.shoot_pattern_3()

    def shoot_pattern_boss3(self):
        # Boss 3 cycles through all patterns based on its phase.
        if self.current_phase == 1:
            self.shoot_pattern_1()
        elif self.current_phase == 2:
            self.shoot_pattern_2()
        else:
            self.shoot_pattern_3()

    def shoot_pattern_1(self):
        proj = BossProjectile(self.rect.centerx, self.rect.bottom, 0, 5)
        self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)

    def shoot_pattern_2(self):
        for angle in range(0, 360, 45):
            proj = BossProjectile(self.rect.centerx, self.rect.centery, math.cos(math.radians(angle))*4, math.sin(math.radians(angle))*4)
            self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)

    def shoot_pattern_3(self):
        for i in range(2):
            angle = (self.pattern_counter*15 + i*180)%360
            proj = BossProjectile(self.rect.centerx, self.rect.centery, math.cos(math.radians(angle))*5, math.sin(math.radians(angle))*5)
            self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)
        self.pattern_counter+=1

    def take_damage(self, amount):
        if self.is_flashing: return # Prevent taking damage while flashing (invincibility frames)
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            if not self.dying_state: # First time entering dying state
                self.dying_state = 'falling'
                self.action = 'death' # Show death animation while falling
                self.frame_index = 0 # Start death animation from beginning
                self.game._play_sfx('explosion') # Play explosion sound (was death)
                # Disable boss movement and attacks immediately
                self.speed = 0
                self.shoot_interval = float('inf') # Stop attacking
                self.death_fall_start_time = pygame.time.get_ticks()
            return
        self.is_flashing = True
        self.flash_timer = pygame.time.get_ticks()
        # No image change here, handled in update()