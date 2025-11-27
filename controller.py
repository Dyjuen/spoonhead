import pygame

class XboxController:
    """Xbox 360 Controller handler for game input - supports up to 2 controllers"""
    
    def __init__(self, controller_index=0):
        pygame.joystick.init()
        self.controller_index = controller_index
        self.joystick = None
        self.connected = False
        self.active = False  # For player 2, needs to press button to activate
        
        # Try to connect to controller at specified index
        if pygame.joystick.get_count() > controller_index:
            self.joystick = pygame.joystick.Joystick(controller_index)
            self.joystick.init()
            self.connected = True
            # Player 1 (index 0) is always active, Player 2 needs to join
            self.active = (controller_index == 0)
            print(f"Controller {controller_index} connected: {self.joystick.get_name()}")
            print(f"  Buttons: {self.joystick.get_numbuttons()}, Axes: {self.joystick.get_numaxes()}, Hats: {self.joystick.get_numhats()}")
            if controller_index > 0:
                print(f"  -> Press START (or any button) to join as Player {controller_index + 1}")
        else:
            if controller_index == 0:
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
        self.switch_weapon_cooldown = 0.25
        self.last_switch = 0
        self.ultimate_cooldown = 1.0 # Add ultimate cooldown
        self.last_ultimate = 0

    def check_join_input(self):
        """Check if player is trying to join (for Player 2+)"""
        if not self.connected or self.active:
            return False
            
        # Check if any button is pressed to join
        for i in range(self.joystick.get_numbuttons()):
            if self.joystick.get_button(i):
                self.active = True
                print(f"Player {self.controller_index + 1} has joined!")
                return True
        return False
        
    def apply_deadzone(self, value):
        """Apply deadzone to analog stick input"""
        if abs(value) < self.deadzone:
            return 0
        return value
    
    def get_actions(self):
        """Get controller input and return game actions"""
        import time
        import math
        
        # CRITICAL: Update joystick state!
        pygame.event.pump()
        
        current_time = time.time()
        
        actions = {
            'move_x': 0.5,  # 0.0 = left, 0.5 = neutral, 1.0 = right
            'shoot': False,
            'shoot_direction': 'horizontal',
            'dash': False,
            'jump': False,
            'switch_weapon': False,
            'activate_ultimate': False # New action for ultimate
        }
        
        # If controller is connected but not active yet, check for join input
        if self.connected and not self.active:
            self.check_join_input()
            return actions  # Return neutral actions if not active yet
        
        if not self.connected:
            # Fallback to keyboard if no controller (only for Player 1)
            if self.controller_index == 0:
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

                # Switch weapon
                if keys[pygame.K_q]: # Q for switch weapon (temporary keyboard mapping)
                    if current_time - self.last_switch > self.switch_weapon_cooldown:
                        actions['switch_weapon'] = True
                        self.last_switch = current_time
                
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

        # X button for switch weapon
        if self.joystick.get_button(self.BUTTON_Y): # Changed Y to switch weapon for consistency
            if current_time - self.last_switch > self.switch_weapon_cooldown:
                actions['switch_weapon'] = True
                self.last_switch = current_time
        
        # X button for dash
        if self.joystick.get_button(self.BUTTON_X):
            actions['dash'] = True
        
        # LB button for ultimate
        if self.joystick.get_button(self.BUTTON_LB):
            if current_time - self.last_ultimate > self.ultimate_cooldown:
                actions['activate_ultimate'] = True
                self.last_ultimate = current_time

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
            if self.controller_index == 0:
                return "Keyboard: WASD/Arrows=Move, Space=Jump, J/Ctrl=Shoot, Shift=Dash"
            return ""
        
        if not self.active:
            return f"Controller {self.controller_index + 1}: Press any button to join"
            
        return f"P{self.controller_index + 1} Xbox: Left Stick=Move+Aim, A=Jump, B=Shoot, X=Dash"
    
    @staticmethod
    def get_available_controllers():
        """Get number of available controllers"""
        pygame.joystick.init()
        return pygame.joystick.get_count()


class ControllerManager:
    """Manages multiple controllers for local multiplayer"""
    
    def __init__(self, max_players=2):
        self.max_players = max_players
        self.controllers = []
        self.initialize_controllers()
    
    def initialize_controllers(self):
        """Initialize all available controllers"""
        available = XboxController.get_available_controllers()
        num_controllers = min(available, self.max_players)
        
        print(f"\n=== Controller Setup ===")
        print(f"Available controllers: {available}")
        print(f"Initializing {num_controllers} controller(s)")
        
        for i in range(self.max_players):
            controller = XboxController(i)
            self.controllers.append(controller)
        
        print("========================\n")
    
    def get_active_controllers(self):
        """Get list of active (joined) controllers"""
        return [ctrl for ctrl in self.controllers if ctrl.active]
    
    def get_controller(self, index):
        """Get controller at specific index"""
        if 0 <= index < len(self.controllers):
            return self.controllers[index]
        return None
    
    def update(self):
        """Update all controllers - check for join inputs"""
        for controller in self.controllers:
            if controller.connected and not controller.active:
                controller.check_join_input()
    
    def get_all_actions(self):
        """Get actions from all active controllers"""
        actions_list = []
        for i, controller in enumerate(self.controllers):
            if controller.active or (controller.controller_index == 0 and not controller.connected):
                actions = controller.get_actions()
                actions['player_id'] = i
                actions_list.append(actions)
        return actions_list
    
    def get_status_texts(self):
        """Get status text for all controllers"""
        texts = []
        for controller in self.controllers:
            text = controller.get_status_text()
            if text:
                texts.append(text)
        return texts