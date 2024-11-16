import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import threading
import requests
import time
import json
import os
import pygame  # For playing sound

# Initialize face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize Pygame mixer for sound
pygame.mixer.init()
ALARM_SOUND = "alarm_sound.mp3"

# Function to calculate the Eye Aspect Ratio (EAR)
def calculate_EAR(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Function to play alarm sound in a separate thread
def play_alarm():
    print("Playing alarm sound...")
    pygame.mixer.music.load(ALARM_SOUND)
    pygame.mixer.music.play()

# Function to load or set EAR threshold
def load_calibration():
    if os.path.exists("calibration.json"):
        with open("calibration.json", "r") as f:
            return json.load(f).get("EYE_AR_THRESHOLD", None)
    return None

def save_calibration(threshold):
    with open("calibration.json", "w") as f:
        json.dump({"EYE_AR_THRESHOLD": threshold}, f)

# Function to notify the server of drowsiness in a separate thread
def notify_server():
    print("Notifying server of drowsiness...")
    try:
        requests.post("http://localhost:5000/drowsiness")  # Send as POST request
        print("Server notified successfully.")
    except requests.exceptions.RequestException as e:
        print("Could not connect to server:", e)

# Check if driving session is active (only once)
def is_session_active():
    try:
        response = requests.get("http://localhost:5000/session_status", timeout=2)  # 2-second timeout
        data = response.json()
        return data.get("session_active", False)
    except requests.exceptions.RequestException:
        print("Could not connect to the server.")
        return False

# Start only if the session is active
if not is_session_active():
    print("No active driving session. Exiting...")
    exit()

# Initialize webcam and EAR threshold
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

EYE_AR_THRESHOLD = load_calibration()
if EYE_AR_THRESHOLD is None:
    # Calibration process
    print("Calibrating. Please keep your eyes open.")
    calibration_frames = 30
    ear_sum = 0
    for _ in range(calibration_frames):
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            landmarks = predictor(gray, face)
            left_eye = [landmarks.part(i) for i in range(36, 42)]
            right_eye = [landmarks.part(i) for i in range(42, 48)]
            left_EAR = calculate_EAR([(p.x, p.y) for p in left_eye])
            right_EAR = calculate_EAR([(p.x, p.y) for p in right_eye])
            avg_EAR = (left_EAR + right_EAR) / 2.0
            ear_sum += avg_EAR
    EYE_AR_THRESHOLD = 0.70 * (ear_sum / calibration_frames)
    save_calibration(EYE_AR_THRESHOLD)
    print(f"Calibration complete. Threshold set to: {EYE_AR_THRESHOLD}")

# Main loop for drowsiness detection
CLOSED_EYES_FRAMES = 0
ALARM_TRIGGER_FRAMES = 75  # Adjust for about 5 seconds at 15 FPS
drowsiness_alert_sent = False  # New flag to control alert notification

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        left_eye = [landmarks.part(i) for i in range(36, 42)]
        right_eye = [landmarks.part(i) for i in range(42, 48)]
        left_EAR = calculate_EAR([(p.x, p.y) for p in left_eye])
        right_EAR = calculate_EAR([(p.x, p.y) for p in right_eye])
        avg_EAR = (left_EAR + right_EAR) / 2.0

        # Draw contours around the eyes
        left_eye_hull = cv2.convexHull(np.array([(p.x, p.y) for p in left_eye]))
        right_eye_hull = cv2.convexHull(np.array([(p.x, p.y) for p in right_eye]))
        cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)

        # Detect drowsiness
        if avg_EAR < EYE_AR_THRESHOLD:
            CLOSED_EYES_FRAMES += 1
            cv2.putText(frame, "Eyes Closed", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if CLOSED_EYES_FRAMES >= ALARM_TRIGGER_FRAMES:
                if not drowsiness_alert_sent:  # Send alert only once per drowsiness event
                    threading.Thread(target=play_alarm).start()  # Play alarm in a separate thread
                    threading.Thread(target=notify_server).start()  # Notify server in a separate thread
                    drowsiness_alert_sent = True  # Prevent further alerts until eyes open
                CLOSED_EYES_FRAMES = 0  # Reset frame count
        else:
            CLOSED_EYES_FRAMES = 0  # Reset counter if eyes are open
            drowsiness_alert_sent = False  # Reset alert flag so it can alert again next time
            cv2.putText(frame, "Eyes Open", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Eye Tracker", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()  # Clean up pygame mixer



#python eyetracker.py to start