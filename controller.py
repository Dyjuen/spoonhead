import pygame

class XboxController:
    """Xbox 360 Controller handler for game input"""
    
    def __init__(self):
        pygame.joystick.init()
        self.joystick = None
        self.connected = False
        
        # Try to connect to first available controller
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
        else:
            print("No controller found. Using keyboard controls.")
        
        # Button mappings for Xbox 360 controller
        self.BUTTON_A = 0       # Jump
        self.BUTTON_B = 1       # Shoot
        self.BUTTON_X = 2       # Dash
        self.BUTTON_Y = 3       
        self.BUTTON_LB = 4      
        self.BUTTON_RB = 5      # Alternative shoot
        self.BUTTON_BACK = 6
        self.BUTTON_START = 7
        
        # Axis mappings
        self.AXIS_LEFT_X = 0    # Left stick horizontal (movement)
        self.AXIS_LEFT_Y = 1    # Left stick vertical
        self.AXIS_RIGHT_X = 2   # Right stick horizontal (aim)
        self.AXIS_RIGHT_Y = 3   # Right stick vertical (aim)
        self.AXIS_LT = 4        # Left trigger
        self.AXIS_RT = 5        # Right trigger
        
        # Deadzone for analog sticks
        self.deadzone = 0.15
        
        # Cooldowns
        self.shoot_cooldown = 0.15
        self.last_shoot = 0
        
    def apply_deadzone(self, value):
        """Apply deadzone to analog stick input"""
        if abs(value) < self.deadzone:
            return 0
        return value
    
    def get_actions(self):
        """Get controller input and return game actions"""
        import time
        import math
        current_time = time.time()
        
        actions = {
            'move_x': 0.5,  # 0.0 = left, 0.5 = neutral, 1.0 = right
            'shoot': False,
            'shoot_direction': 'horizontal',
            'dash': False,
            'jump': False
        }
        
        if not self.connected:
            # Fallback to keyboard if no controller
            keys = pygame.key.get_pressed()
            
            # Movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                actions['move_x'] = 0.0
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                actions['move_x'] = 1.0
            
            # Jump
            if keys[pygame.K_SPACE] or keys[pygame.K_w]:
                actions['jump'] = True
            
            # Shoot
            if keys[pygame.K_j] or keys[pygame.K_LCTRL]:
                if current_time - self.last_shoot > self.shoot_cooldown:
                    actions['shoot'] = True
                    self.last_shoot = current_time
            
            # Dash
            if keys[pygame.K_LSHIFT] or keys[pygame.K_k]:
                actions['dash'] = True
            
            # Shoot direction with arrow keys
            if keys[pygame.K_UP]:
                actions['shoot_direction'] = 'up'
            elif keys[pygame.K_DOWN]:
                actions['shoot_direction'] = 'down'
            
            return actions
        
        # === CONTROLLER INPUT ===
        
        # Left stick for BOTH movement AND aiming
        left_x = self.apply_deadzone(self.joystick.get_axis(self.AXIS_LEFT_X))
        left_y = self.apply_deadzone(self.joystick.get_axis(self.AXIS_LEFT_Y))
        
        # Movement (horizontal)
        if left_x != 0:
            # Map from -1.0~1.0 to 0.0~1.0
            actions['move_x'] = (left_x + 1.0) / 2.0
        
        # Aim direction based on left stick position
        if left_x != 0 or left_y != 0:
            angle = math.degrees(math.atan2(-left_y, left_x)) # Pygame's y-axis is inverted

            if -22.5 <= angle < 22.5:
                actions['shoot_direction'] = 'right'
            elif 22.5 <= angle < 67.5:
                actions['shoot_direction'] = 'up_right'
            elif 67.5 <= angle < 112.5:
                actions['shoot_direction'] = 'up'
            elif 112.5 <= angle < 157.5:
                actions['shoot_direction'] = 'up_left'
            elif 157.5 <= angle or angle < -157.5:
                actions['shoot_direction'] = 'left'
            elif -157.5 <= angle < -112.5:
                actions['shoot_direction'] = 'down_left'
            elif -112.5 <= angle < -67.5:
                actions['shoot_direction'] = 'down'
            elif -67.5 <= angle < -22.5:
                actions['shoot_direction'] = 'down_right'
        
        # A button for jump
        if self.joystick.get_button(self.BUTTON_A):
            actions['jump'] = True
        
        # B button or RB for shoot
        if self.joystick.get_button(self.BUTTON_B) or self.joystick.get_button(self.BUTTON_RB):
            if current_time - self.last_shoot > self.shoot_cooldown:
                actions['shoot'] = True
                self.last_shoot = current_time
        
        # X button for dash
        if self.joystick.get_button(self.BUTTON_X):
            actions['dash'] = True
        
        # D-Pad as alternative for shoot direction (override)
        hat = self.joystick.get_hat(0) if self.joystick.get_numhats() > 0 else (0, 0)
        if hat[1] == 1:  # Up
            actions['shoot_direction'] = 'up'
        elif hat[1] == -1:  # Down
            actions['shoot_direction'] = 'down'
        
        return actions
    
    def rumble(self, low_freq=0.5, high_freq=0.5, duration=100):
        """Rumble controller (if supported)"""
        if self.connected and hasattr(self.joystick, 'rumble'):
            try:
                self.joystick.rumble(low_freq, high_freq, duration)
            except:
                pass
    
    def get_status_text(self):
        """Get status text for display"""
        if not self.connected:
            return "Keyboard: WASD/Arrows=Move, Space=Jump, J/Ctrl=Shoot, Shift=Dash"
        return "Xbox: Left Stick=Move+Aim, A=Jump, B=Shoot, X=Dash"