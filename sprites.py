import pygame
import random
import os
import math
import time
from settings import *

class SpriteSheet:
    """Utility for loading and parsing sprite sheets."""
    def __init__(self, filename):
        try:
            self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load sprite sheet: {filename}")
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

class Player(pygame.sprite.Sprite):
    """Player character with a reliable c    def __init__(self, x, y, game, upgrades=None, character_id=None, equipped_gun_id=None):
        super().__init__()
        from settings import CHARACTER_DATA
        from gun_data import GUN_DATA
        self.game = game
TA
        self.upgrades = upgrades if upgrades else {}
        self.character_id = character_id or 'cyborg'
        self.character_data = CHARACTER_DATA[self.character_id]
        self.gun_data = GUN_DATA
        self.buff = self.character_data['buff']
        self.buff_desc = self.character_data['buff_desc']
        # Buff state
        self.buff_active = False
        self.buff_timer = 0

        # Layered rendering
        self.
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
        self.emote_cooldown = random.randint(5000, 10000)

        # Composite image
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA) # Will be overwritten by animate
        self.rect = self.image.get_rect(center=(x, y))

        self.hitbox = pygame.Rect(0, 0, 20, 45)
        self.hitbox_offset_x = 10
        self.hitbox.center = (self.rect.centerx - self.hitbox_offset_x, self.rect.centery)
        self.max_health = 100
        self.health = self.max_health 
        self.coins = 0
        self.vx = 0
        self.vy = 0
        # Buffs
        self.speed = 6
        self.jump_power = -16
        if self.buff == 'speed_boost':
            self.speed = 7
        if self.buff == 'jump_boost':
            self.jump_power = -20
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
            print(f"Warning: Could not load gun image: {gun_path}")
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
            print(f"Warning: Could not load bullet image for {gun_id}: {bullet_path}")
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
        self.double_jump_unlocked = False
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

        if self.upgrades.get('double_jump', 0) > 0:
            self.double_jump_unlocked = True

    def switch_weapon(self):
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.unlocked_weapons)
        print(f"Switched to: {self.unlocked_weapons[self.current_weapon_index]}") # For debugging

    def load_animations(self):
        player_size = (60, 60)
        hand_size = (60, 60) # Example size, may need adjustment

        # Load body animations
        self.body_animations = {'idle': [], 'run': [], 'jump': [], 'double_jump': []}
        for anim_type in ['idle', 'run', 'jump', 'double_jump']: # Only main actions have body animations
            sprite_path = self.character_data.get(anim_type)
            if sprite_path:
                try:
                    sheet = SpriteSheet(sprite_path)
                    frames = sheet.get_animation_frames(48, 48)
                    scaled_frames = [pygame.transform.scale(frame, player_size) for frame in frames]
                    self.body_animations[anim_type] = scaled_frames
                except (pygame.error, FileNotFoundError):
                    print(f"Warning: Could not load player body animation: {sprite_path}")
                    placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                    self.body_animations[anim_type] = [placeholder_frame] * 4
            else: # Fallback if action sprite path not defined
                placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                self.body_animations[anim_type] = [placeholder_frame] * 4


        # Load hand animations for each action
        self.hand_animations = {}
        if 'hand_animations' in self.character_data:
            for anim_type, hand_path in self.character_data['hand_animations'].items():
                try:
                    img = pygame.image.load(hand_path).con
                    # Match length to body anim if possible, else use a list of 1 for single images
                    target_length = len(self.body_animations.get(anim_type, [None])) if anim_type in self.body_animations else 1
                    self.hand_animations[anim_type] = [scaled_hand] * target_length
                except (pygame.error, FileNotFoundError):
                    print(f"Warning: Could not load player hand animation: {hand_path}")
                    placeholder_frame = pygame.Surface(hand_size, pygame.SRCALPHA)
                    target_length = len(self.body_animations.get(anim_type, [None])) if anim_type in self.body_animations else 1
                    self.hand_animations[anim_type] = [placeholder_frame] * target_length
        
        # Ensure all body animation actions have a corresponding hand animation, even if placeholder
        for anim_type, body_frames in self.body_animations.items():
            if anim_type not in self.hand_animations:
                placeholder_frame = pygame.Surface(hand_size, pygame.SRCALPHA)
                self.hand_animations[anim_type] = [placeholder_frame] * len(body_frames)

        # Load emote animations
        self.emote_animations = {}
        if 'emotes' in self.character_data:
            for i, emote_path in enumerate(self.character_data['emotes']):
                try:
                    img = pygame.image.load(emote_path).convert_alpha()
                    scaled_img = pygame.transform.scale(img, player_size)
                    self.emote_animations[f'emote_{i}'] = [scaled_img] # Treat as single-frame animation
                except (pygame.error, FileNotFoundError):
                    print(f"Warning: Could not load emote animation: {emote_path}")
        
        # Load hand animations for emotes
        if 'hand_animations' in self.character_data and 'emotes' in self.character_data:
            for i, emote_path in enumerate(self.character_data['emotes']):
                emote_key = f'emote_{i}'
                # Try to find a matching hand animation for the emote
                hand_emote_path = self.character_data['hand_animations'].get(emote_key)
                if hand_emote_path:
                    try:
                        img = pygame.image.load(hand_emote_path).convert_alpha()
                        scaled_hand = pygame.transform.scale(img, hand_size)
                        self.hand_animations[emote_key] = [scaled_hand]
                    except (pygame.error, FileNotFoundError):
                        print(f"Warning: Could not load hand animation for emote: {hand_emote_path}")
                        placeholder_frame = pygame.Surface(hand_size, pygame.SRCALPHA)
                        self.hand_animations[emote_key] = [placeholder_frame]
                else: # Fallback if no specific hand emote is defined
                    placeholder_frame = pygame.Surface(hand_size, pygame.SRCALPHA)
                    self.hand_animations[emote_key] = [placeholder_frame]

    def animate(self):
        now = pygame.time.get_ticks()
        
        # Determine current body animation
        is_emote_action = self.action.startswith('emote')
        if is_emote_action and self.is_emoting:
             # Simple timer for single-frame emotes
            if now - self.last_frame_update > 1000: # Show emote for 1 second
                self.is_emoting = False
                self.set_action('idle')
        elif self.action == 'double_jump' and self.frame_index >= len(self.body_animations['double_jump']) - 1:
            self.set_action('jump')
        
        # Get animation list, default to idle if action not found
        current_body_animation = self.body_animations.get(self.action)
        if not current_body_animation: # If current action is an emote, use emote animation
            current_body_animation = self.emote_animations.get(self.action, self.body_animations['idle'])

        if now - self.last_frame_update > 100:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(current_body_animation)
        
        # Get current frames for body, gun, hand
        body_frame = current_body_animation[self.frame_index]
        
        # Get hand frame - prioritize specific hand anims for action, else fallback to idle hand
        hand_animation_key = self.action
        hand_frames_list = self.hand_animations.get(hand_animation_key, self.hand_animations['idle'])
        hand_frame = hand_frames_list[self.frame_index % len(hand_frames_list)] # Ensure frame_index is within bounds for hand anim

        # Resize hand for jump/double_jump actions
        if self.action in ('jump', 'double_jump'):
            # Make the hand larger for jump/double_jump
            hand_frame = pygame.transform.scale(hand_frame, (70, 70))
        else:
            hand_frame = pygame.transform.scale(hand_frame, (60, 60))

        gun_image = self.gun_image

        if not self.facing_right:
            body_frame = pygame.transform.flip(body_frame, True, False)
            hand_frame = pygame.transform.flip(hand_frame, True, False)
            if gun_image: # Only flip if gun image exists
                gun_image = pygame.transform.flip(gun_image, True, False)
        
        # Create a new composite image, assuming player_size (60,60) for the main sprite
        composite_image = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        # These offsets are placeholders and will need to be fine-tuned for each frame/animation
        # For now, let's try to center the hand on the character, and the gun relative to the hand
        body_rect = body_frame.get_rect()
        hand_rect = hand_frame.get_rect()
        gun_rect = gun_image.get_rect() if gun_image else None

        # Position hand relative to body
        # These values will need extensive tuning
        hand_offset_x = 20
        hand_offset_y = 30
        
        # Position gun relative to hand
        # These values will need extensive tuning
        gun_offset_x = 0
        gun_offset_y = 0

        # Blit in order: body -> gun -> hand
        composite_image.blit(body_frame, (0, 0))
        if gun_image:
            composite_image.blit(gun_image, (hand_offset_x + gun_offset_x, hand_offset_y + gun_offset_y))
        composite_image.blit(hand_frame, (hand_offset_x, hand_offset_y))

        self.image = composite_image
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_action(self, new_action):
        if self.action != new_action:
            self.action = new_action
            self.frame_index = 0
            self.last_frame_update = pygame.time.get_ticks() # Reset timer on action change

    def update(self, move_input, platforms):
        sfx_events = []
        now = pygame.time.get_ticks()

        # Emote logic
        if self.action == 'idle' and not self.is_emoting:
            self.idle_timer += self.game.clock.get_time() # Use game clock for framerate independence
            if self.idle_timer > self.emote_cooldown and self.emote_animations:
                self.is_emoting = True
                self.set_action(random.choice(list(self.emote_animations.keys())))
                self.idle_timer = 0
                self.emote_cooldown = random.randint(5000, 10000) # Reset cooldown
        elif self.action != 'idle':
            self.idle_timer = 0
            if not self.action.startswith('emote'):
                self.is_emoting = False

        if not self.is_emoting:
            if not self.on_ground:
                if self.vy > 0 and self.action != 'double_jump': self.set_action('jump') # Falling
            elif move_input is not None and (move_input < 0.4 or move_input > 0.6): self.set_action('run')
            else: self.set_action('idle')

        self.vx = 0
        if move_input is not None and not self.is_emoting:
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
                    self.jumps_made = 0
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
            # Update rect juga
            self.rect.centerx = self.hitbox.centerx + (self.hitbox_offset_x if self.facing_right else -self.hitbox_offset_x)
            self.rect.centery = self.hitbox.centery
        self.rect.centery = self.hitbox.centery

        self.animate()

        if self.on_ground and not self.was_on_ground:
            sfx_events.append('landing')

        self.was_on_ground = self.on_ground
        
        # Power-up timer
        if self.damage_boost_active and pygame.time.get_ticks() - self.damage_boost_timer > self.power_up_duration:
            self.damage_boost_active = False
            print("Damage boost deactivated") # for debugging
            
        return sfx_events

    def jump(self):
        max_jumps = 2 if self.double_jump_unlocked else 1
        if self.jumps_made < max_jumps and not self.is_emoting:
            self.vy = self.jump_power
            self.on_ground = False
            self.set_action('double_jump' if self.jumps_made == 1 else 'jump')
            self.jumps_made += 1
            return 'jump'
        elif not self.double_jump_unlocked and self.jumps_made >= 1:
            print("DEBUG: Double jump not unlocked! Purchase it from the shop.")
        return None

    def dash(self):
        current_time = pygame.time.get_ticks()
        if not self.dashing and current_time - self.last_dash > self.dash_cooldown and not self.is_emoting:
            self.dashing = True; self.dash_timer = current_time; self.last_dash = current_time

    def shoot(self, shoot_direction='horizontal'):
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
            print("Damage boost activated!") # for debugging
        elif power_up_type == 'health':
            self.health += 25
            if self.health > self.max_health:
                self.health = self.max_health
            print("Health boost activated!") # for debugging

    def increase_ultimate_meter(self):
        if not self.ultimate_ready:
            self.ultimate_meter += 1
            if self.ultimate_meter >= self.ultimate_max_meter:
                self.ultimate_ready = True
                print("Ultimate ready!") # for debugging
        # Trigger buff on kill for Cyborg only
        if self.buff == 'damage_boost':
            self.apply_buff()

    def activate_ultimate(self):
        if self.ultimate_ready:
            self.ultimate_meter = 0
            self.ultimate_ready = False
            print("Ultimate activated! Massive shot fired!") # for debugging
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
        self.health, self.speed, self.direction = 30, speed, 1
        self.start_x, self.patrol_distance = x, patrol_distance
        self.shoot_cooldown, self.last_shot_time = shoot_cooldown, time.time()
        self.detection_range = 400
        # Flashing effect for damage
        self.flash_timer = 0
        self.original_image = self.image

    def load_animations(self):
        self.animations = {'walk': []}
        enemy_size = (64, 64)
        try:
            sheet = SpriteSheet(ENEMY_WALK_SPRITE)
            frames = sheet.get_animation_frames(48, 48) 
            for frame in frames:
                self.animations['walk'].append(pygame.transform.scale(frame, enemy_size))
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load enemy animation: {ENEMY_WALK_SPRITE}")
            placeholder = pygame.Surface(enemy_size); placeholder.fill(RED)
            self.animations['walk'] = [placeholder]

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 120:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.action])
            new_image = self.animations[self.action][self.frame_index]
            if self.direction == -1: new_image = pygame.transform.flip(new_image, True, False)
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

    def update(self, player, all_sprites_group, enemy_projectiles_group):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.centerx - self.start_x) > self.patrol_distance: self.direction *= -1
        self.animate()
        if abs(player.rect.centerx - self.rect.centerx) < self.detection_range and time.time() - self.last_shot_time > self.shoot_cooldown:
            self.shoot_at_player(player, all_sprites_group, enemy_projectiles_group)
            self.last_shot_time = time.time()

    def shoot_at_player(self, player, all_sprites, projectiles_group):
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
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
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA); self.image.fill(ORANGE)
        pygame.draw.circle(self.image, YELLOW, (6, 6), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy, self.lifetime = vx, vy, 180

    def update(self):
        self.rect.move_ip(self.vx, self.vy); self.lifetime -= 1
        if self.lifetime <= 0 or not self.rect.colliderect(pygame.Rect(-100,-100,10000,SCREEN_HEIGHT+200)): self.kill()

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__(); self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PINK, (8, 8), 8); pygame.draw.circle(self.image, PURPLE, (8, 8), 5)
        self.rect = self.image.get_rect(center=(x, y)); self.vx, self.vy = vx, vy

    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        if not self.rect.colliderect(pygame.Rect(-50,-50,SCREEN_WIDTH+100,SCREEN_HEIGHT+100)): self.kill()

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
            print("Warning: Player projectile images not found."); surf = pygame.Surface(bullet_size, pygame.SRCALPHA); surf.fill(YELLOW)
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
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (10, 10), 10); pygame.draw.circle(self.image, YELLOW, (10, 10), 8)
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset, self.bob_range, self.original_y = random.uniform(0, 2*math.pi), 4, y

    def update(self):
        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range); self.bob_offset += 0.1

class BossGate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(); self.image = pygame.Surface((80, 120), pygame.SRCALPHA); self.image.fill(PURPLE)
        pygame.draw.rect(self.image, GOLD, self.image.get_rect(), 5); font = pygame.font.Font(None, 30)
        self.image.blit(font.render("BOSS", True, WHITE), (15, 45)); self.rect = self.image.get_rect(center=(x, y))

class PowerUpBox(pygame.sprite.Sprite):
    def __init__(self, x, y, power_up_type='damage_boost', health=50):
        super().__init__()
        self.image = pygame.Surface((40, 40)); self.image.fill(GRAY)
        pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 3)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.power_up_type = power_up_type
        self.health = health
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            # Placeholder for spawning a PowerUp, will be handled in main.py
            return True
        return False

    def update(self):
        # A static box, so update does nothing for now
        pass

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_up_type):
        super().__init__()
        self.power_up_type = power_up_type
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        # Assign color/image based on type
        if self.power_up_type == 'damage_boost':
            self.image.fill(ORANGE)
        elif self.power_up_type == 'health':
            self.image.fill(GREEN)
        else: # Default or unknown power-up
            self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2) # Border

    def update(self):
        # Optional: Add a bobbing or floating effect
        pass

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, game, boss_type, health, speed, shoot_interval, phases):
        super().__init__()
        self.game = game
        self.boss_type = boss_type
        self.max_health = health
        self.health = health
        self.speed = speed
        self.shoot_interval = shoot_interval / 1000.0  # Convert ms to seconds for time.time()
        self.phases = phases
        self.current_phase = 1
        self.last_shot_time = time.time()
        self.pattern_counter = 0  # Used for cycling through patterns

        # Flashing effect for damage
        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 100 # milliseconds

        self.load_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.original_image = self.image.copy() # Store original for flashing

        self.direction = 1 # For simple horizontal movement

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
        # Simple horizontal movement for now
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1

        now = time.time()
        if now - self.last_shot_time > self.shoot_interval:
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
            self.kill()
            return
        self.is_flashing = True
        self.flash_timer = pygame.time.get_ticks()
        # No image change here, handled in update()
set_x + gun_offset_x, hand_offset_y + gun_offset_y))
        composite_image.blit(hand_frame, (hand_offset_x, hand_offset_y))

        self.image = composite_image
        self.rect = self.image.get_rect(center=self.rect.center) # Keep original centerern_3(self):
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
            self.kill()
            return
        self.is_flashing = True
        self.flash_timer = pygame.time.get_ticks()
        # No image change here, handled in update()
(self.pattern_counter*15 + i*180)%360
            proj = BossProjectile(self.rect.centerx, self.rect.centery, math.cos(math.radians(angle))*5, math.sin(math.radians(angle))*5)
            self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)
        self.pattern_counter+=1

    def take_damage(self, amount):
        if self.is_flashing: return # Prevent taking damage while flashing (invincibility frames)
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.kill()
            return
        self.is_flashing = True
        self.flash_timer = pygame.time.get_ticks()
        # No image change here, handled in update()ttern_3(self):
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
            self.kill()
            return
        self.is_flashing = True
        self.flash_timer = pygame.time.get_ticks()
        # No image change here, handled in update()
