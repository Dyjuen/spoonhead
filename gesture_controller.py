import cv2
import mediapipe as mp
import time

class HandGestureController:
    """Simplified hand gesture controller - EASIER TO USE!
    
    Controls:
    - Hand Position (Left/Right): Move character
    - Open Hand (5 fingers): SHOOT (continuous)
    - Closed Fist (0 fingers): JUMP
    - Peace Sign (2 fingers): DASH
    """

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Cooldowns
        self.jump_cooldown = 0.3
        self.dash_cooldown = 0.8
        self.shoot_cooldown = 0.15
        
        self.last_jump = 0
        self.last_dash = 0
        self.last_shoot = 0
        
        self.prev_finger_count = 0

    def count_fingers(self, hand_landmarks):
        """Count how many fingers are extended"""
        finger_tips = [
            self.mp_hands.HandLandmark.THUMB_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        
        finger_pips = [
            self.mp_hands.HandLandmark.THUMB_IP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.PINKY_PIP
        ]
        
        count = 0
        for tip, pip in zip(finger_tips, finger_pips):
            tip_y = hand_landmarks.landmark[tip].y
            pip_y = hand_landmarks.landmark[pip].y
            
            # Finger is extended if tip is above pip
            if tip_y < pip_y:
                count += 1
        
        return count

    def get_gestures(self, frame):
        """
        Process frame and return simplified actions
        """
        actions = {
            'move_x': None, 
            'shoot': False, 
            'dash': False, 
            'jump': False
        }
        
        current_time = time.time()
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # Get hand position for movement
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                actions['move_x'] = wrist.x

                # Count fingers
                finger_count = self.count_fingers(hand_landmarks)
                
                # Display finger count on screen
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # SHOOT: Open hand (4-5 fingers)
                if finger_count >= 4:
                    if current_time - self.last_shoot > self.shoot_cooldown:
                        actions['shoot'] = True
                        self.last_shoot = current_time
                        cv2.putText(frame, "SHOOT!", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # JUMP: Closed fist (0-1 fingers)
                elif finger_count <= 1:
                    if current_time - self.last_jump > self.jump_cooldown:
                        if self.prev_finger_count > 1:  # Transition detection
                            actions['jump'] = True
                            self.last_jump = current_time
                            cv2.putText(frame, "JUMP!", (10, 70), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                # DASH: Peace sign (2 fingers)
                elif finger_count == 2:
                    if current_time - self.last_dash > self.dash_cooldown:
                        if self.prev_finger_count != 2:  # Transition detection
                            actions['dash'] = True
                            self.last_dash = current_time
                            cv2.putText(frame, "DASH!", (10, 70), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                self.prev_finger_count = finger_count
        else:
            # No hand detected
            cv2.putText(frame, "No hand detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.prev_finger_count = 0

        # Draw control instructions on frame
        instructions = [
            "Controls:",
            "Open Hand (5): SHOOT",
            "Fist (0): JUMP", 
            "Peace (2): DASH",
            "Move Hand: Left/Right"
        ]
        
        y_offset = frame.shape[0] - 150
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return actions, frame