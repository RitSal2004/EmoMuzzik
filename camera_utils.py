import cv2
import numpy as np
from threading import Thread, Lock

class CameraFeed:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
        
        # Optimized camera settings
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Threading for smooth performance
        self.lock = Lock()
        self.frame = None
        self.stopped = False
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
    
    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                break
            with self.lock:
                self.frame = frame
    
    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def release(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()
        cv2.destroyAllWindows()

def display_frame(frame, emotion=None, confidence=None):
    if frame is None:
        return None
    
    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Add face detection rectangle and emotion text
    if emotion and confidence:
        # Draw rectangle around face
        h, w = frame.shape[:2]
        cv2.rectangle(frame_rgb, (0, 0), (w-1, h-1), (0, 255, 0), 2)
        
        # Add emotion text
        text = f"{emotion} ({confidence:.2f})"
        cv2.putText(frame_rgb, text, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return frame_rgb