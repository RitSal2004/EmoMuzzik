import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load model and labels
model = load_model("model/emotion_model.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_emotion(image_path=None, frame=None):
    try:
        if image_path:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            return None, None
        
        # Detect faces with optimized parameters
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(120, 120),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) == 0:
            return None, None
        
        # Process largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2]*f[3])
        face_roi = gray[y:y+h, x:x+w]
        
        # Preprocess for model
        face = cv2.resize(face_roi, (48, 48)) / 255.0
        face = np.reshape(face, (1, 48, 48, 1))
        
        # Predict emotion
        prediction = model.predict(face, verbose=0)
        emotion = emotion_labels[np.argmax(prediction)]
        confidence = np.max(prediction)
        
        return emotion, confidence
    
    except Exception as e:
        print(f"Detection error: {str(e)}")
        return None, None