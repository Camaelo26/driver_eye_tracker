# Drowsiness Detection System

## Goal of the Project
This project aims to monitor and detect drowsiness in drivers, providing timely alerts to help prevent accidents caused by driver fatigue. It is a full-stack application that combines machine learning for eye-tracking, a backend server for communication, and a front-end application for user interaction.

---

## Files in the Project

1. **`server.py`**  
   Backend server that handles requests and integrates with the drowsiness detection logic.

2. **`eyetracker.py`**  
   Implements the machine learning logic for eye-tracking and drowsiness detection.

3. **`App.js`**  
   Front-end React Native application for user interaction, allowing users to start/stop driving sessions and receive alerts.

---

## How to Run the Project

### Step 1: Start the Backend Server
- Open a terminal.
- Navigate to the directory containing `server.py`.
- Run the backend server with:
  ```bash
  python server.py
The server will start and listen on http://localhost:5000.

### Step 2: Start the Front-End Application
Open a second terminal.
Navigate to the directory containing App.js.
Ensure you have Node.js, npm, and Expo CLI installed.
Run the application with:
bash
Copy code
expo start
Follow the on-screen instructions to launch the app on a mobile device or emulator.
### Step 3: Start the Drowsiness Detection Script
Open a third terminal.
Navigate to the directory containing eyetracker.py.
Run the detection logic with:
bash
Copy code
python eyetracker.py
This script processes the camera feed and sends real-time data to the backend server.
Application Workflow
Starting a Session
Users can start a driving session through the front-end app. This sends a request to the backend to initialize monitoring.

### Real-Time Monitoring
The eyetracker.py script continuously monitors the driver's eyes for signs of drowsiness and sends updates to the backend.

### Drowsiness Alerts
If drowsiness is detected, the backend notifies the front-end app, which alerts the driver with a visual and audio cue.

### Ending a Session
Users can stop the session via the app, which halts all monitoring.

### Notes
Ensure all dependencies for Python scripts (server.py and eyetracker.py) are installed:
bash
Copy code
pip install -r requirements.txt
For App.js, make sure to install the required npm packages:
bash
Copy code
npm install
The eyetracker.py script requires a working camera for eye-tracking.
Future Improvements
Extend compatibility to other platforms beyond local environments.
Add support for cloud deployment.
Enhance the accuracy of the drowsiness detection algorithm.
Enjoy using the Drowsiness Detection System! 🚗✨
