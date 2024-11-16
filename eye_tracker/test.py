import cv2

# Try each index and see which ones work
for i in range(10):  # Test indices 0 through 9
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera found at index {i}")
        cap.release()
    else:
        print(f"No camera found at index {i}")
