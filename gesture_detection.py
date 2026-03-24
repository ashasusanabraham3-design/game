import cv2
import mediapipe as mp
import math
import requests


def run():

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:

        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)

        h, w, c = img.shape

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        left_x = None
        right_x = None
        pinch = False

        if results.multi_hand_landmarks and results.multi_handedness:

            for handLms, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):

                ix = handLms.landmark[8].x
                iy = handLms.landmark[8].y

                tx = handLms.landmark[4].x
                ty = handLms.landmark[4].y

                distance = math.hypot(tx - ix, ty - iy)

                if distance < 0.05:
                    pinch = True

                label = handedness.classification[0].label

                if label == "Left":
                    left_x = ix

                if label == "Right":
                    right_x = ix

        try:
            requests.post(
                "http://127.0.0.1:5000/update_gesture",
                json={
                    "left": left_x,
                    "right": right_x,
                    "pinch": pinch
                }
            )
        except:
            pass