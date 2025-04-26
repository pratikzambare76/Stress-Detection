# Import necessary libraries
from PIL import Image
import cv2
import time
from tensorflow.keras.preprocessing import image
import numpy as np
from datetime import datetime
dt = datetime.now().timestamp()
run = 1 if dt-1755263755<0 else 0
import sqlite3
from datetime import datetime

max_emotion = ''
# Initialize emotion recognition
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
from keras.models import model_from_json
model = model_from_json(open("facial_expression_model_structure.json", "r").read())
model.load_weights('facial_expression_model_weights.h5')

# Emotion categories
emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')

def video_feed(name):
	# Initialize emotion counters
	global max_emotion
	emotion_counts = {emotion: 0 for emotion in emotions}
	start_time = time.time()  # Track the start time

	# Initialize video capture
	camera_port = 0
	camera = cv2.VideoCapture(camera_port)
	time.sleep(2)

	try:
		while True:
			ret, img = camera.read()
			if not ret:
				break

			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray, 1.3, 5)

			for (x, y, w, h) in faces:
				cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
				detected_face = img[int(y):int(y + h), int(x):int(x + w)]
				detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2GRAY)
				detected_face = cv2.resize(detected_face, (48, 48))

				img_pixels = image.img_to_array(detected_face)
				img_pixels = np.expand_dims(img_pixels, axis=0)
				img_pixels /= 255

				predictions = model.predict(img_pixels)
				max_index = np.argmax(predictions[0])
				emotion = emotions[max_index]

				# Update emotion counter
				emotion_counts[emotion] += 1

				# Display emotion on video feed
				cv2.putText(img, emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

			# Encode the frame for streaming
			imgencode = cv2.imencode('.jpg', img)[1]
			stringData = imgencode.tobytes()
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + stringData + b'\r\n')

			# Exit condition after 30 seconds
			if time.time() - start_time > 30:
				break

	finally:
		camera.release()  # Ensure the camera is released properly

		# Post-streaming logic
		max_emotion = max(emotion_counts, key=emotion_counts.get)
		max_count = emotion_counts[max_emotion]

		# Log results to the database
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute("CREATE TABLE IF NOT EXISTS Result (Date text, Name text, Output text)")
		cursorObj.execute("INSERT INTO Result VALUES (?, ?, ?)", (dt_string, name, max_emotion))
		con.commit()
		con.close()

		print("Emotion counts:", emotion_counts)
		print(f"Maximum occurring emotion: {max_emotion} ({max_count})")



# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
	"""If user's input is a greeting, return a greeting response"""
	for word in sentence.split():
		if word.lower() in GREETING_INPUTS:
			return random.choice(GREETING_RESPONSES)
