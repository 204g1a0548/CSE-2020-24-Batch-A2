import Adafruit_ADS1x15
import Adafruit_DHT
import requests
import time
import RPi.GPIO as GPIO
from pushbullet import Pushbullet


# Replace 'YOUR_PUSHBULLET_API_KEY' with your actual API key
API_KEY = 'o.AEKiQmSN5q1MaxajyXas0LdWX39iO2f2'
# Create an ADS1115 instance
adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain (1 for +/-4.096V, 2 for +/-2.048V, etc.)
GAIN = 1

# Define the ADC channel (0-3)
ADC_CHANNEL = 0
# ThingSpeak parameters
channel_id = "2392052"  # Replace with your Channel ID
write_api_key = "BQIWVTISH96T7S7F"  # Replace with your Write API Key

# Configure DHT sensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 24  # GPIO pin connected to the DHT sensor

# Servo and buzzer setup
SERVO_PIN = 8  # GPIO pin connected to the servo
BUZZER_PIN = 26  # GPIO pin connected to the buzzer

# Set GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)  # PWM frequency

servo.start(0)

dry_adc_value = 27887
wet_adc_value = 60

def read_temperature(percentage):
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print(f'Humidity :{int(humidity)}')
        print(f'Temperature :{int(temperature)}')
        # Create the ThingSpeak update URL
        url = f"https://api.thingspeak.com/update?api_key={write_api_key}&field1={temperature}&field2={humidity}&field3={percentage}"
       
        # Send data to ThingSpeak
        response = requests.get(url)
       
        if response.status_code == 200:
            print("Data sent to Pushbutton")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
        time.sleep(10)  # Delay for 20 seconds before sending next data
    else:
        print("Failed to read sensor data")
       
    return temperature

def calculate_moisture_percentage(raw_value, dry_value, wet_value):
    # Calculate the range between dry and wet values
    value_range = dry_value - wet_value
   
    # Calculate the percentage
    moisture_percentage = 100 - ((raw_value - wet_value) / value_range) * 100
   
    # Ensure the percentage is within 0-100% bounds
    moisture_percentage = max(0, min(100, moisture_percentage))
   
    return moisture_percentage

def read_channel_0():
    # Read the analog sensor value from channel 0
    channel_0_value = adc.read_adc(ADC_CHANNEL, gain=GAIN)

    return channel_0_value

def activate_servo_and_buzzer():
    servo.ChangeDutyCycle(7.5)  # Rotate servo to 180 degrees
    #GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer

def deactivate_servo_and_buzzer():
    servo.ChangeDutyCycle(0)  # Set servo back to 0 degrees
    #GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off the buzzer

def send_notification(title, body):
    try:
        pb = Pushbullet(API_KEY)
        push = pb.push_note(title, body)
        print("Notification sent successfully!")
    except Exception as e:
        print(f"Error sending notification: {e}")
motor_on_flag = True
motor_off_flag = True
try:
    while True:
       
        raw_adc_value = adc.read_adc(ADC_CHANNEL, gain=GAIN)
        moisture_percentage = int(calculate_moisture_percentage(raw_adc_value, dry_adc_value, wet_adc_value))
        print(f"Moisture percentage: {moisture_percentage}%")
       
        # Read from DHT11 sensor
        temperature = read_temperature(moisture_percentage)
        if temperature is not None and temperature >= 35:
            print(f"Temperature: {temperature}°C - Threshold Reached")
            activate_servo_and_buzzer()  # Activate servo and buzzer
            notification_title = "Temperature is high!!"
            notification_body = "Temperature is high!!"
            send_notification(notification_title, notification_body)
        else:
            deactivate_servo_and_buzzer()  # Deactivate servo and buzzer
       
        if moisture_percentage >= 95  and motor_on_flag == True:
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            motor_on_flag=False
            motor_off_flag=True
            #print(f"T: {temperature}°C - Threshold Reached")
            #activate_servo_and_buzzer()  # Activate servo and buzzer
            notification_title = "Motor is off!!"
            notification_body = "Motor is off!!"
            send_notification(notification_title, notification_body)
           
        elif moisture_percentage <= 20 and motor_off_flag == True:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            motor_on_flag=True
            motor_off_flag=False
            notification_title = "Motor is on!!"
            notification_body = "Motor is on!!"
            send_notification(notification_title, notification_body)
           
        time.sleep(1)
       
except KeyboardInterrupt:
    servo.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO pins
