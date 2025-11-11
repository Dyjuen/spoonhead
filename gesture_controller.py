import cv2
import mediapipe as mp
import time
import math

class HandGestureController:
    """Two-Hand Intuitive Controller
    
    LEFT HAND (Movement):
    - Index closed, Middle up = Move LEFT
    - Middle closed, Index up = Move RIGHT
    - Both up = Stand still
    - Double tap Index = Dash RIGHT
    - Double tap Middle = Dash LEFT
    - Fist = JUMP
    
    RIGHT HAND (Shooting):
    - Point index finger = SHOOT (direction follows finger)
    """

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Cooldowns
        self.jump_cooldown = 0.4
        self.shoot_cooldown = 0.15
        
        self.last_jump = 0
        self.last_shoot = 0
        
        # For double tap detection
        self.last_index_tap = []  # List of tap timestamps
        self.last_middle_tap = []
        self.tap_time_window = 0.5  # 500ms window for double tap
        
        # Previous states for transition detection
        self.prev_left_index_up = False
        self.prev_left_middle_up = False
        self.prev_left_fist = False

    def is_left_hand(self, hand_landmarks):
        """Determine if hand is left or right based on thumb position"""
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        # Mirrored camera: thumb right of wrist = left hand
        return thumb_tip.x > wrist.x

    def is_finger_up(self, hand_landmarks, finger_tip_id, finger_pip_id):
        """Check if specific finger is extended"""
        tip = hand_landmarks.landmark[finger_tip_id]
        pip = hand_landmarks.landmark[finger_pip_id]
        return tip.y < pip.y - 0.02

    def get_finger_states(self, hand_landmarks):
        """Get state of index and middle fingers"""
        index_up = self.is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP
        )
        middle_up = self.is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP
        )
        return index_up, middle_up

    def is_fist(self, hand_landmarks):
        """Check if hand is closed fist (all fingers down)"""
        fingers_up = 0
        finger_landmarks = [
            (self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.INDEX_FINGER_PIP),
            (self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            (self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.RING_FINGER_PIP),
            (self.mp_hands.HandLandmark.PINKY_TIP, self.mp_hands.HandLandmark.PINKY_PIP)
        ]
        
        for tip_id, pip_id in finger_landmarks:
            if self.is_finger_up(hand_landmarks, tip_id, pip_id):
                fingers_up += 1
        
        return fingers_up == 0

    def detect_double_tap(self, tap_list, current_time):
        """Detect if double tap occurred within time window"""
        # Clean old taps outside window
        tap_list[:] = [t for t in tap_list if current_time - t < self.tap_time_window]
        
        # Check if we have 2 taps within window
        if len(tap_list) >= 2:
            tap_list.clear()  # Reset after detection
            return True
        return False

    def calculate_shoot_direction(self, hand_landmarks, wrist):
        """Calculate shooting direction based on index finger tip"""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y
        
        angle = math.degrees(math.atan2(dy, dx))
        
        if -135 < angle < -45:  # Up
            if dx > 0.05:
                return 'up_right'
            elif dx < -0.05:
                return 'up_left'
            else:
                return 'up'
        elif 45 < angle < 135:  # Down
            return 'down'
        else:  # Horizontal
            return 'horizontal'

    def get_gestures(self, frame):
        """Process frame with two-hand intuitive controls"""
        actions = {
            'move_x': 0.5,  # 0.5 = center (no movement)
            'shoot': False,
            'shoot_direction': 'horizontal',
            'dash': False,
            'jump': False
        }
        
        current_time = time.time()
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        left_hand_data = None
        right_hand_data = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                is_left = self.is_left_hand(hand_landmarks)
                
                if is_left:
                    left_hand_data = {'landmarks': hand_landmarks, 'wrist': wrist}
                    h, w, _ = frame.shape
                    cv2.putText(frame, "LEFT (Move)", 
                               (int(wrist.x * w) - 60, int(wrist.y * h) - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    right_hand_data = {'landmarks': hand_landmarks, 'wrist': wrist}
                    h, w, _ = frame.shape
                    cv2.putText(frame, "RIGHT (Shoot)", 
                               (int(wrist.x * w) - 60, int(wrist.y * h) - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # === LEFT HAND: Movement & Actions ===
            if left_hand_data:
                index_up, middle_up = self.get_finger_states(left_hand_data['landmarks'])
                is_left_fist = self.is_fist(left_hand_data['landmarks'])
                
                # MOVEMENT
                if not index_up and middle_up:
                    # Index closed, Middle up = Move LEFT
                    actions['move_x'] = 0.2
                    cv2.putText(frame, "< MOVE LEFT", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                elif index_up and not middle_up:
                    # Middle closed, Index up = Move RIGHT
                    actions['move_x'] = 0.8
                    cv2.putText(frame, "MOVE RIGHT >", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                else:
                    # Both up or both down = Stand still
                    actions['move_x'] = 0.5
                
                # DOUBLE TAP DETECTION for DASH
                # Detect index finger tap (transition from up to down)
                if self.prev_left_index_up and not index_up:
                    self.last_index_tap.append(current_time)
                    if self.detect_double_tap(self.last_index_tap, current_time):
                        actions['dash'] = True
                        actions['move_x'] = 0.9  # Dash right
                        cv2.putText(frame, "DASH RIGHT >>", (10, 110), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # Detect middle finger tap
                if self.prev_left_middle_up and not middle_up:
                    self.last_middle_tap.append(current_time)
                    if self.detect_double_tap(self.last_middle_tap, current_time):
                        actions['dash'] = True
                        actions['move_x'] = 0.1  # Dash left
                        cv2.putText(frame, "<< DASH LEFT", (10, 110), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # JUMP with fist
                if is_left_fist and not self.prev_left_fist:
                    if current_time - self.last_jump > self.jump_cooldown:
                        actions['jump'] = True
                        self.last_jump = current_time
                        cv2.putText(frame, "JUMP!", (10, 150), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                # Update previous states
                self.prev_left_index_up = index_up
                self.prev_left_middle_up = middle_up
                self.prev_left_fist = is_left_fist
                
                # Display finger status
                status = f"L: Index={'UP' if index_up else 'DN'} Middle={'UP' if middle_up else 'DN'}"
                if is_left_fist:
                    status = "L: FIST"
                cv2.putText(frame, status, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # === RIGHT HAND: Shooting ===
            if right_hand_data:
                index_up, _ = self.get_finger_states(right_hand_data['landmarks'])
                
                # Check if pointing (index up, others relatively down)
                if index_up:
                    shoot_dir = self.calculate_shoot_direction(
                        right_hand_data['landmarks'],
                        right_hand_data['wrist']
                    )
                    actions['shoot_direction'] = shoot_dir
                    
                    if current_time - self.last_shoot > self.shoot_cooldown:
                        actions['shoot'] = True
                        self.last_shoot = current_time
                    
                    cv2.putText(frame, f"SHOOT {shoot_dir.upper()}!", (10, 190), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Draw aiming line
                    index_tip = right_hand_data['landmarks'].landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    h, w, _ = frame.shape
                    wrist_px = (int(right_hand_data['wrist'].x * w), int(right_hand_data['wrist'].y * h))
                    tip_px = (int(index_tip.x * w), int(index_tip.y * h))
                    cv2.line(frame, wrist_px, tip_px, (0, 255, 255), 3)
                    cv2.circle(frame, tip_px, 10, (0, 255, 255), -1)
        else:
            cv2.putText(frame, "Show BOTH hands!", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Instructions
        instructions = [
            "LEFT: Index closed+Middle up=Left",
            "LEFT: Middle closed+Index up=Right",
            "LEFT: Double tap Index=Dash Right",
            "LEFT: Double tap Middle=Dash Left",
            "LEFT: Fist=Jump",
            "RIGHT: Point=Shoot"
        ]
        
        y_offset = frame.shape[0] - 170
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_offset + i * 23), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        return actions, frame