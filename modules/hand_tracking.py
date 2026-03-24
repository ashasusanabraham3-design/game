import cv2
import mediapipe as mp
import requests
import math

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

while True:

    success, img = cap.read()
    if not success:
        continue

    # Mirror camera
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
                results.multi_handedness):

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Index finger tip
            ix = int(handLms.landmark[8].x * w)
            iy = int(handLms.landmark[8].y * h)

            # Thumb tip
            tx = int(handLms.landmark[4].x * w)
            ty = int(handLms.landmark[4].y * h)

            cv2.circle(img, (ix, iy), 10, (0,255,0), -1)
            cv2.circle(img, (tx, ty), 10, (255,0,0), -1)

            # Pinch detection
            distance = math.hypot(tx - ix, ty - iy)

            if distance < 40:
                pinch = True
                cv2.putText(img,"PINCH",(50,100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,(0,255,0),3)

            label = handedness.classification[0].label

            # Normalize X position (0 → 1)
            norm_x = handLms.landmark[8].x

            if label == "Left":
                left_x = norm_x

            if label == "Right":
                right_x = norm_x

    # Send gesture data to Flask
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

    cv2.imshow("Gesture Detection", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()