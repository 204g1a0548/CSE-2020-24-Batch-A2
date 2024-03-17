import cv2
import numpy as np
import RPi.GPIO as IO
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.imagenet_utils import decode_predictions
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from pushbullet import Pushbullet

# Load the pre-trained MobileNetV2 model
model = MobileNetV2(weights='imagenet')

# Replace 'YOUR_PUSHBULLET_API_KEY' with your actual API key
API_KEY = 'o.AEKiQmSN5q1MaxajyXas0LdWX39iO2f2'

BUZZER_PIN_1 = 6

IO.setmode(IO.BCM)
IO.setwarnings(False)

#GPIO.setup(SERVO_PIN, GPIO.OUT)
IO.setup(BUZZER_PIN_1, IO.OUT)

def preprocess_image(image):
    image = cv2.resize(image, (224, 224))  
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
    image = preprocess_input(image)  
    image = np.expand_dims(image, axis=0)  
    return image

def predict_frame(frame):
    processed_frame = preprocess_image(frame)
    predictions = model.predict(processed_frame)
    decoded_predictions = decode_predictions(predictions, top=3)
   
    '''thresholds={
        'dog':0.5,
        'cat':0.5,
        'Quaker_Parrot':0.5
    }
    detected_objects=[]
    for pred in decoded_predictions[0]:
        label=pred[1]
        probability=pred[2]
        if label.lower() in thresholds:
            if probability>=thresholds[label.lower()]:
                detected_objects.append((label, probability))'''
   
    return decoded_predictions[0]
    #return detected_objects

def send_notification(title, body):
    try:
        pb = Pushbullet(API_KEY)
        push = pb.push_note(title, body)
        print("Notification sent successfully!")
    except Exception as e:
        print(f"Error sending notification: {e}")

def real_time_recognition():
    cap = cv2.VideoCapture(0)  
   
    if not cap.isOpened():
        print("Cannot open USB camera")
        return
   
    object_detected = {}  # Dictionary to track detected objects and notifications

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
               
            predictions = predict_frame(frame)
            label = predictions[0][1]  
            print(label)  
           
            # Check for specific objects and send notification (once per object)
            specific_objects = ['dog', 'cat', 'bird', 'elephant', 'german_shepherd', 'granny_smith', 'golden_retriever', 'persian_cat', 'alexandrine_parakeet', 'quaker_parrot']
            for obj in specific_objects:
                IO.output(BUZZER_PIN_1, IO.HIGH)
                if obj in label.lower() and obj not in object_detected:
                    notification_title = "Object Detected"
                    notification_body = f"{obj.capitalize()} is in view!"
                    send_notification(notification_title, notification_body)
                    object_detected[obj] = True  # Mark object as detected
            else:
                 IO.output(BUZZER_PIN_1, IO.LOW)
            #cv2.imshow('USB Camera', frame)  
           
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
# Start real-time recognition
real_time_recognition()
