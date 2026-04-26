
import cv2
import numpy as np
from keras.models import load_model
import requests
import time

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

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
emotion_model = load_model('emotion_model.h5', compile=False)

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

        # Send to Telegram 
        current_time = time.time()
        if emotion != last_emotion or (current_time - last_sent_time) > cooldown_seconds:
            send_telegram_message(f"{emoji} {emotion}")
            last_emotion = emotion
            last_sent_time = current_time

    # Show webcam window
    cv2.imshow('Face + Emoji Detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
