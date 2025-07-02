'''import cv2
import numpy as np
from keras.models import load_model

# Load face detection model
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load the emotion detection model
emotion_model = load_model('emotion_model.h5', compile=False)

# Emotion labels and their corresponding emojis
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
emoji_map = {
    'Angry': '😠',
    'Disgust': '🤢',
    'Fear': '😱',
    'Happy': '😊',
    'Sad': '😢',
    'Surprise': '😲',
    'Neutral': '😐'
}

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi_gray, (64, 64))

        roi = roi.astype('float32') / 255.0
        roi = np.expand_dims(roi, axis=-1)
        roi = np.expand_dims(roi, axis=0)

        prediction = emotion_model.predict(roi)
        label_idx = np.argmax(prediction)
        emotion = emotion_labels[label_idx]
        emoji = emoji_map.get(emotion, '')

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{emotion} {emoji}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Emoji Generator', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() '''

'''import cv2
import numpy as np
from keras.models import load_model
import time

# Load the model and Haar Cascade
model = load_model('emotion_model.h5')
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Emotion labels
emotion_dict = {
    0: "😠",
    1: "🤢",
    2: "😨",
    3: "😀",
    4: "😢",
    5: "😲",
    6: "😐"
}

# Constants
FONT = cv2.FONT_HERSHEY_SIMPLEX
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Start webcam
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

last_emotion = "😀"
last_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display_frame = np.ones((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8) * 0  # black background

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    emotion = last_emotion  # Default

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        face = cv2.resize(roi_gray, (48, 48))
        face = face.reshape(1, 48, 48, 1) / 255.0
        prediction = model.predict(face)
        label_idx = np.argmax(prediction)
        emotion = emotion_dict[label_idx]
        last_emotion = emotion
        last_time = time.time()

    # Fill screen with emojis (spacing = 50px)
    for i in range(0, FRAME_HEIGHT, 50):
        for j in range(0, FRAME_WIDTH, 50):
            cv2.putText(display_frame, emotion, (j, i + 30), FONT, 1.5, (255, 255, 255), 2)

    cv2.imshow("Emoji Explosion", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

'''

import cv2
import numpy as np
from keras.models import load_model
import requests
import time

# ========== Telegram Bot Configuration ==========
BOT_TOKEN = '8197469820:AAHYn2uFtlG3cxeJzRK_ECGIrEFNriYZW-4'
CHAT_ID = '6840597467'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

# ========== Load Face & Emotion Model ==========
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
emotion_model = load_model('emotion_model.h5', compile=False)

# ========== Labels and Emoji Map ==========
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
emoji_map = {
    'Angry': '😠',
    'Disgust': '🤢',
    'Fear': '😱',
    'Happy': '😊',
    'Sad': '😢',
    'Surprise': '😲',
    'Neutral': '😐'
}

# ========== Start Webcam ==========
cap = cv2.VideoCapture(0)

last_emotion = None
last_sent_time = 0
cooldown_seconds = 5  # To avoid spamming

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi_gray, (64, 64))
        roi = roi.astype('float32') / 255.0
        roi = np.expand_dims(roi, axis=-1)
        roi = np.expand_dims(roi, axis=0)

        prediction = emotion_model.predict(roi)
        label_idx = np.argmax(prediction)
        emotion = emotion_labels[label_idx]
        emoji = emoji_map.get(emotion, '')

        # Draw bounding box and label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{emotion} {emoji}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Send to Telegram if changed or after cooldown
        current_time = time.time()
        if emotion != last_emotion or (current_time - last_sent_time) > cooldown_seconds:
            send_telegram_message(f"{emoji} {emotion}")
            last_emotion = emotion
            last_sent_time = current_time

    # Show webcam window
    cv2.imshow('Face + Emoji Detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ========== Cleanup ==========
cap.release()
cv2.destroyAllWindows()
