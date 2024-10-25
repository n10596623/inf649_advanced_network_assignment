import paho.mqtt.client as mqtt
import serial
import time

# Set up serial communication for Bluetooth modules
ser1 = serial.Serial('/dev/rfcomm0', 9600)  # Change to the correct port
ser2 = serial.Serial('/dev/rfcomm1', 9600)  # Change to the correct port

# MQTT setup
broker = "3.25.226.155"
port = 1883
topic = "sensor/data"

# Create an MQTT client instance
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client.on_connect = on_connect
client.connect(broker, port, 60)

# Function to read data from sensors
def read_sensors():
    if ser1.in_waiting:
        light_data = ser1.readline().decode('utf-8').strip()
        client.publish(topic, f"LightSensor: {light_data}")
    
    if ser2.in_waiting:
        heartbeat_data = ser2.readline().decode('utf-8').strip()
        client.publish(topic, f"Heartbeat: {heartbeat_data}")
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if message == "reduce_light_high_count":
        global light_high_count
        light_high_count -= 1
        print(f"Light High Count reduced to: {light_high_count}")

client.subscribe("sensor/control")
client.on_message = on_message
# Continuously read and publish sensor data
while True:
    read_sensors()
    time.sleep(1)
    
