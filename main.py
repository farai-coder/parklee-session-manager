import time
import ssl
import logging
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG)

BROKER = "e7b11161.ala.us-east-1.emqxsl.com"
PORT = 8883
TOPIC = "test/topic"
USERNAME = "farai"
PASSWORD = "farairato3210"

def on_connect(client, userdata, flags, rc, properties=None):
    print("on_connect", rc)
    if rc == 0:
        print("✅ Connected to broker")
        client.subscribe(TOPIC)
    else:
        print("❌ Failed to connect, return code", rc)

def on_message(client, userdata, msg):
    print(f"📩 Received: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client(client_id="python-subscriber", protocol=mqtt.MQTTv5)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)  # less strict, for testing; use default in production!

client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        print("⏳ Connecting to broker...")
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)
