import paho.mqtt.client as mqtt
import sqlite3
import re
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

# Connect to SQLite database
db = sqlite3.connect('SensorData.db',check_same_thread=False)  # SQLite uses a file for the database
cursor = db.cursor()

# Ensure the table exists in SQLite
cursor.execute('''
CREATE TABLE IF NOT EXISTS Data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_type TEXT,
    value REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
db.commit()

# MQTT setup
broker = "3.25.226.155"
port = 1883
topic = "sensor/data"

# Function to insert sensor data into the SQLite database
def insert_data(sensor_type, value):
    sql = "INSERT INTO Data (sensor_type, value) VALUES (?, ?)"
    cursor.execute(sql, (sensor_type, value))
    db.commit()

# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message}")

    # Extract sensor type and value from the message
    match = re.match(r'(LightSensor|Hearbeat|Heartbeat): \w+: (\d+\.?\d*)', message)
    if match:
        sensor_type = match.group(1)
        value = float(match.group(2))
        insert_data(sensor_type, value)
# Initialize the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)
client.loop_forever()


# Flask route to retrieve sensor data from SQLite
@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    cursor.execute("SELECT * FROM Data")
    rows = cursor.fetchall()
    return jsonify(rows)

# Function to run Flask app in a separate thread
def run_flask_app():
    app.run(host='0.0.0.0', port=5000,debug=True)  # Run Flask on localhost

# Function to run MQTT client loop
def run_mqtt_client():
    client.connect(broker, port, 60)
    client.loop_forever()

# Run both Flask and MQTT concurrently
if __name__ == '__main__':
    # Run Flask app in a thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    # Run MQTT client in the main thread
    run_mqtt_client()