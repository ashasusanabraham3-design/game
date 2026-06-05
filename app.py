from flask import Flask, render_template, request, jsonify
import sqlite3
import threading
import cv2
import mediapipe as mp
import math

app = Flask(__name__)

DATABASE = "database/game.db"

# -------------------------
# GLOBAL GESTURE STATE
# -------------------------

gesture_data = {
    "left": None,
    "leftY": None,
    "right": None,
    "rightY": None,
    "pinch": False
}

def camera_loop():

    global gesture_data

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(0)

    while True:

        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        left_x = None
        left_y = None
        right_x = None
        right_y = None
        pinch = False

        if results.multi_hand_landmarks:

            for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness):

                ix = hand_landmarks.landmark[8].x
                iy = hand_landmarks.landmark[8].y

                tx = hand_landmarks.landmark[4].x
                ty = hand_landmarks.landmark[4].y

                distance = math.hypot(tx - ix, ty - iy)

                if distance < 0.05:
                    pinch = True

                label = handedness.classification[0].label

                if label == "Left":
                    left_x = ix
                    left_y = iy

                if label == "Right":
                    right_x = ix
                    right_y = iy

        gesture_data = {
            "left": left_x,
            "leftY": left_y,
            "right": right_x,
            "rightY": right_y,
            "pinch": pinch
        }

        print("GESTURE:", gesture_data)

        cv2.imshow("Gesture Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT,
            score INTEGER,
            level INTEGER,
            mode TEXT
        )
    """)

    conn.commit()
    conn.close()


# -------------------------
# PAGE ROUTES
# -------------------------

@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/camera")
def camera():
    return render_template("camera.html")

# -------------------------
# SAVE SCORE
# -------------------------

@app.route("/save_score", methods=["POST"])
def save_score():

    data = request.json

    player = data["player_name"]
    score = data["score"]
    level = data["level"]
    mode = data["mode"]

    print("Saving:", player, score, level, mode)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO score (player, score, level, mode)
        VALUES (?, ?, ?, ?)
    """, (player, score, level, mode))

    conn.commit()

    print("SAVED SUCCESSFULLY")

    conn.close()

    return jsonify({"status":"score saved"})

# -------------------------
# GET LEADERBOARD
# -------------------------

@app.route("/get_scores")
def get_scores():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT player, score, level, mode FROM score ORDER BY score DESC LIMIT 10"
    )

    scores = cursor.fetchall()
    conn.close()

    result = []

    for s in scores:
        result.append({
            "player": s["player"],
            "score": s["score"],
            "level": s["level"],
            "mode": s["mode"]
        })

    return jsonify(result)

# -------------------------
# GET CURRENT GESTURE
# -------------------------

@app.route("/gesture")
def gesture():
    global gesture_data
    return jsonify(gesture_data)

# -------------------------
# START CAMERA THREAD
# -------------------------

camera_thread = threading.Thread(target=camera_loop)
camera_thread.daemon = True
camera_thread.start()

# -------------------------
# RUN SERVER
# -------------------------
init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)