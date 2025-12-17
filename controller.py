import pygame
import time
import math

class KeyboardController:
    """Handles keyboard input for a player."""
    def __init__(self, is_p2=False):
        self.is_p2 = is_p2
        # Different key mappings for P1 vs P2 could be added, 
        # but usually only one keyboard is used, so we'll stick to WASD/Arrows mix or standard layout.
        # Since we only support P2 on keyboard if P1 is on Controller (or vice versa), 
        # we can assume the standard layout is available.

        # Cooldowns
        self.shoot_cooldown = 0.15
        self.last_shoot = 0
        self.switch_weapon_cooldown = 0.25
        self.last_switch = 0
        self.ultimate_cooldown = 1.0
        self.last_ultimate = 0
        
        # Edge detection
        self.last_jump_state = False

    def get_actions(self):
        actions = {
            'move_x': 0.5, # 0.0=left, 0.5=neutral, 1.0=right
            'shoot': False,
            'shoot_direction': 'horizontal',
            'dash': False,
            'jump': False,
            'switch_weapon': False,
            'activate_ultimate': False,
            'join': False # Special action for joining
        }
        
        keys = pygame.key.get_pressed()
        current_time = time.time()

        # Join detection (Enter or Space)
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            actions['join'] = True

        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            actions['move_x'] = 0.0
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            actions['move_x'] = 1.0
        
        # Jump (Edge detection)
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
        if jump_pressed and not self.last_jump_state:
            actions['jump'] = True
        self.last_jump_state = jump_pressed
        
        # Shoot
        if keys[pygame.K_j] or keys[pygame.K_LCTRL]:
            if current_time - self.last_shoot > self.shoot_cooldown:
                actions['shoot'] = True
                self.last_shoot = current_time

        # Switch weapon
        if keys[pygame.K_q]:
            if current_time - self.last_switch > self.switch_weapon_cooldown:
                actions['switch_weapon'] = True
                self.last_switch = current_time
        
        # Dash
        if keys[pygame.K_LSHIFT] or keys[pygame.K_k]:
            actions['dash'] = True
        
        # Ultimate
        if keys[pygame.K_r] or keys[pygame.K_e]: # R or E for ultimate
             if current_time - self.last_ultimate > self.ultimate_cooldown:
                actions['activate_ultimate'] = True
                self.last_ultimate = current_time

        # Shoot direction with arrow keys (overrides WASD if pressed)
        if keys[pygame.K_UP]:
            actions['shoot_direction'] = 'up'
        elif keys[pygame.K_DOWN]:
            actions['shoot_direction'] = 'down'
        
        return actions

    def rumble(self, *args):
        pass # Keyboard has no rumble

    def get_status_text(self):
        return "Keyboard: WASD/Arrows=Move, Space=Jump, J/Ctrl=Shoot, Shift=Dash"


class XboxController:
    """Xbox 360 Controller handler - strictly joystick input."""
    
    def __init__(self, controller_index=0):
        pygame.joystick.init()
        self.controller_index = controller_index
        self.joystick = None
        self.connected = False
        
        if pygame.joystick.get_count() > controller_index:
            self.joystick = pygame.joystick.Joystick(controller_index)
            self.joystick.init()
            self.connected = True
            print(f"Controller {controller_index} connected: {self.joystick.get_name()}")
        
        # Button mappings (Standard Xbox Layout)
        self.BUTTON_A = 0       # Jump
        self.BUTTON_B = 1       # Shoot
        self.BUTTON_X = 2       # Dash
        self.BUTTON_Y = 3       # Switch Weapon
        self.BUTTON_LB = 4      # Ultimate
        self.BUTTON_RB = 5      # Shoot
        self.BUTTON_BACK = 6
        self.BUTTON_START = 7   # Join
        
        # Axis mappings
        self.AXIS_LEFT_X = 0    
        self.AXIS_LEFT_Y = 1    
        self.AXIS_RIGHT_X = 2   
        self.AXIS_RIGHT_Y = 3   
        
        self.deadzone = 0.15
        
        self.shoot_cooldown = 0.15
        self.last_shoot = 0
        self.switch_weapon_cooldown = 0.25
        self.last_switch = 0
        self.ultimate_cooldown = 1.0
        self.last_ultimate = 0
        
        # Edge detection
        self.last_jump_state = False

    def apply_deadzone(self, value):
        if abs(value) < self.deadzone:
            return 0
        return value
    
    def get_actions(self):
        # Update joystick state
        # pygame.event.pump() # Assuming main loop calls this, but good to ensure
        
        actions = {
            'move_x': 0.5,
            'shoot': False,
            'shoot_direction': 'horizontal',
            'dash': False,
            'jump': False,
            'switch_weapon': False,
            'activate_ultimate': False,
            'join': False
        }
        
        if not self.connected:
            return actions

        current_time = time.time()
        
        # Join detection (Start or A)
        if self.joystick.get_button(self.BUTTON_START) or self.joystick.get_button(self.BUTTON_A):
            actions['join'] = True

        # Left stick movement
        left_x = self.apply_deadzone(self.joystick.get_axis(self.AXIS_LEFT_X))
        left_y = self.apply_deadzone(self.joystick.get_axis(self.AXIS_LEFT_Y))
        
        if left_x != 0:
            actions['move_x'] = (left_x + 1.0) / 2.0
        
        # Aim direction
        if left_x != 0 or left_y != 0:
            angle = math.degrees(math.atan2(-left_y, left_x))
            if -22.5 <= angle < 22.5: actions['shoot_direction'] = 'right'
            elif 22.5 <= angle < 67.5: actions['shoot_direction'] = 'up_right'
            elif 67.5 <= angle < 112.5: actions['shoot_direction'] = 'up'
            elif 112.5 <= angle < 157.5: actions['shoot_direction'] = 'up_left'
            elif 157.5 <= angle or angle < -157.5: actions['shoot_direction'] = 'left'
            elif -157.5 <= angle < -112.5: actions['shoot_direction'] = 'down_left'
            elif -112.5 <= angle < -67.5: actions['shoot_direction'] = 'down'
            elif -67.5 <= angle < -22.5: actions['shoot_direction'] = 'down_right'
        
        # Buttons
        # Jump (Edge detection)
        jump_pressed = self.joystick.get_button(self.BUTTON_A)
        if jump_pressed and not self.last_jump_state:
            actions['jump'] = True
        self.last_jump_state = jump_pressed
        
        if self.joystick.get_button(self.BUTTON_B) or self.joystick.get_button(self.BUTTON_RB):
            if current_time - self.last_shoot > self.shoot_cooldown:
                actions['shoot'] = True
                self.last_shoot = current_time

        if self.joystick.get_button(self.BUTTON_Y): # Changed Y to switch weapon
            if current_time - self.last_switch > self.switch_weapon_cooldown:
                actions['switch_weapon'] = True
                self.last_switch = current_time
        
        if self.joystick.get_button(self.BUTTON_X):
            actions['dash'] = True
        
        if self.joystick.get_button(self.BUTTON_LB):
             if current_time - self.last_ultimate > self.ultimate_cooldown:
                actions['activate_ultimate'] = True
                self.last_ultimate = current_time

        # D-Pad overrides
        if self.joystick.get_numhats() > 0:
            hat = self.joystick.get_hat(0)
            if hat[1] == 1: actions['shoot_direction'] = 'up'
            elif hat[1] == -1: actions['shoot_direction'] = 'down'
        
        return actions
    
    def rumble(self, low_freq=0.5, high_freq=0.5, duration=100):
        if self.connected and hasattr(self.joystick, 'rumble'):
            try:
                self.joystick.rumble(low_freq, high_freq, duration)
            except:
                pass
    
    def get_status_text(self):
        if self.connected:
             return f"Controller {self.controller_index + 1}: LS=Move, A=Jump, B/RB=Shoot, X=Dash, Y=Switch, LB=Ult"
        return "Controller Disconnected"


class ControllerManager:
    """Manages input devices for 1 or 2 players."""
    
    def __init__(self):
        pygame.joystick.init()
        self.num_joysticks = pygame.joystick.get_count()
        self.p1_input = None
        self.p2_input = None
        
        self.assign_devices()
    
    def assign_devices(self):
        print(f"Detected {self.num_joysticks} controllers.")
        
        if self.num_joysticks == 0:
            # 0 Controllers: P1=Keyboard, P2=None (No 2P possible with 1 keyboard)
            self.p1_input = KeyboardController()
            self.p2_input = None
            print("P1: Keyboard, P2: None")
            
        elif self.num_joysticks == 1:
            # 1 Controller: P1=Controller, P2=Keyboard
            self.p1_input = XboxController(0)
            self.p2_input = KeyboardController()
            print("P1: Controller 0, P2: Keyboard")
            
        else: # 2+ Controllers
            # 2 Controllers: P1=Controller 0, P2=Controller 1
            self.p1_input = XboxController(0)
            self.p2_input = XboxController(1)
            print("P1: Controller 0, P2: Controller 1")
            
    def get_p1_controller(self):
        return self.p1_input
        
    def get_p2_controller(self):
        return self.p2_input
        
    def has_p2_device(self):
        return self.p2_input is not None