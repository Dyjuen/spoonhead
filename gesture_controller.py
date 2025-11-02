import cv2
import mediapipe as mp
import time

class HandGestureController:
    """Hand gesture controller using MediaPipe"""

    def __init__(self, cooldown=0.5, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.cooldown = cooldown
        self.last_action_time = {
            'shoot': 0,
            'dash': 0,
            'jump': 0,
        }

        self.prev_finger_states = {
            'index': False,
            'middle': False,
            'ring': False,
        }

    def get_gestures(self, frame):
        """
        Process a single frame for hand gestures and return actions.
        """
        actions = {'move_x': None, 'shoot': False, 'dash': False, 'jump': False}
        
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        current_states = {'index': False, 'middle': False, 'ring': False}

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                actions['move_x'] = wrist.x

                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                
                current_states['index'] = index_tip.y < thumb_tip.y
                current_states['middle'] = middle_tip.y < thumb_tip.y
                current_states['ring'] = ring_tip.y < thumb_tip.y

                if current_states['index']:
                    if time.time() - self.last_action_time['shoot'] > self.cooldown:
                        actions['shoot'] = True
                        self.last_action_time['shoot'] = time.time()

                if current_states['middle'] and not self.prev_finger_states['middle']:
                    if time.time() - self.last_action_time['dash'] > self.cooldown:
                        actions['dash'] = True
                        self.last_action_time['dash'] = time.time()

                if current_states['ring'] and not self.prev_finger_states['ring']:
                    if time.time() - self.last_action_time['jump'] > self.cooldown:
                        actions['jump'] = True
                        self.last_action_time['jump'] = time.time()

        self.prev_finger_states = current_states
        return actions, frame
