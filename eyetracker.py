import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from playsound import playsound
import threading
import time

# Initialize face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to calculate the Eye Aspect Ratio (EAR)
def calculate_EAR(eye):
    A = dist.euclidean(eye[1], eye[5])  # Vertical distance
    B = dist.euclidean(eye[2], eye[4])  # Vertical distance
    C = dist.euclidean(eye[0], eye[3])  # Horizontal distance
    ear = (A + B) / (2.0 * C)
    return ear

# Function to play alarm sound in a separate thread
def play_alarm():
    playsound('alarm_sound.mp3')

# Start webcam feed
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Calculate FPS
start_time = time.time()
num_frames = 100
for i in range(num_frames):
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break
end_time = time.time()
seconds = end_time - start_time
fps = num_frames / seconds
print(f"Calculated FPS: {fps}")

# Set alarm trigger frames for a 5-second duration
ALARM_TRIGGER_FRAMES = int(fps * 3)  # Adjust for 5 seconds
print(f"Alarm will trigger after {ALARM_TRIGGER_FRAMES} continuous closed-eye frames.")

# Calibration: Capture the EAR when eyes are fully open
print("Keep your eyes open for calibration...")
EYE_AR_THRESHOLD = None
calibration_frames = 30
ear_sum = 0
frames_counter = 0

# To track closed eye time and alarm status
CLOSED_EYES_FRAMES = 0
alarm_triggered = False

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
        left_eye_points = [(p.x, p.y) for p in left_eye]
        right_eye_points = [(p.x, p.y) for p in right_eye]

        # Calculate EAR for both eyes
        left_EAR = calculate_EAR(left_eye_points)
        right_EAR = calculate_EAR(right_eye_points)
        avg_EAR = (left_EAR + right_EAR) / 2.0

        if EYE_AR_THRESHOLD is None:
            # During calibration, average the EAR values when eyes are open
            ear_sum += avg_EAR
            frames_counter += 1
            if frames_counter >= calibration_frames:
                # Set the threshold to a percentage (e.g., 80%) of the average open-eye EAR
                EYE_AR_THRESHOLD = 0.80 * (ear_sum / calibration_frames)
                print(f"Calibration completed. Threshold set to: {EYE_AR_THRESHOLD}")
        else:
            # Draw rectangles around the eyes
            left_eye_hull = cv2.convexHull(np.array(left_eye_points))
            right_eye_hull = cv2.convexHull(np.array(right_eye_points))
            cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)

            # Check if eyes are closed
            if avg_EAR < EYE_AR_THRESHOLD:
                CLOSED_EYES_FRAMES += 1
                cv2.putText(frame, "Eyes Closed", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Trigger alarm if eyes have been closed for the defined duration
                if CLOSED_EYES_FRAMES >= ALARM_TRIGGER_FRAMES:
                    # Start the alarm sound in a new thread
                    threading.Thread(target=play_alarm).start()
                    alarm_triggered = True  # Mark alarm as triggered
                    CLOSED_EYES_FRAMES = 0  # Reset frames counter to allow retrigger after 5 seconds
            else:
                CLOSED_EYES_FRAMES = 0  # Reset counter if eyes are open
                alarm_triggered = False  # Reset the alarm trigger flag
                cv2.putText(frame, "Eyes Open", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display the frame with EAR and eye status
    cv2.imshow("Eye Tracker", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#python eyetracker.py to start