from flask import Flask, jsonify, request
import threading
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# State variables for the drowsiness alert and driving session
drowsiness_status = {"alert": False}
driving_session_active = False
alert_reset_timer = None  # Timer to reset alert

# Function to reset drowsiness alert
def reset_alert():
    global drowsiness_status
    drowsiness_status["alert"] = False
    print("Drowsiness alert status reset to False")

# Endpoint to start driving session
@app.route("/start_session", methods=["POST"])
def start_session():
    global driving_session_active
    driving_session_active = True
    print("Driving session started.")
    return jsonify({"session_active": driving_session_active})

# Endpoint to stop driving session
@app.route("/stop_session", methods=["POST"])
def stop_session():
    global driving_session_active, drowsiness_status, alert_reset_timer
    driving_session_active = False
    drowsiness_status["alert"] = False  # Reset any alert
    if alert_reset_timer:  # Cancel any pending alert reset
        alert_reset_timer.cancel()
    print("Driving session stopped.")
    return jsonify({"session_active": driving_session_active})

# Endpoint to receive drowsiness alert from eyetracker.py (POST)
@app.route("/drowsiness", methods=["POST"])
def drowsiness_alert():
    global drowsiness_status, alert_reset_timer
    if driving_session_active:  # Only process alert if session is active
        drowsiness_status["alert"] = True
        print(f"Drowsiness alert status: {drowsiness_status['alert']}")

        # Reset the alert after 10 seconds if no new alert is received
        if alert_reset_timer:
            alert_reset_timer.cancel()  # Cancel previous timer if still running
        alert_reset_timer = threading.Timer(10.0, reset_alert)
        alert_reset_timer.start()
    else:
        print("Alert ignored. Driving session is inactive.")

    return jsonify({"alert": drowsiness_status["alert"]})

# New endpoint to check drowsiness status without setting it (GET)
@app.route("/check_drowsiness", methods=["GET"])
def check_drowsiness():
    # Only returns the current alert status without modifying it
    return jsonify({"alert": drowsiness_status["alert"]})

# Endpoint to check if driving session is active
@app.route("/session_status", methods=["GET"])
def session_status():
    return jsonify({"session_active": driving_session_active})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
