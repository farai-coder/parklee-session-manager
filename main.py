import time
import paho.mqtt.client as mqtt

BROKER = "e7b11161.ala.us-east-1.emqxsl.com"
PORT = 8883   # secure TLS port
TOPIC = "test/topic"

# Authentication (if EMQX requires username/password)
USERNAME = "farai"
PASSWORD = "farairato3210"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to broker")
        client.subscribe(TOPIC)
    else:
        print("❌ Failed to connect, return code", rc)

def on_message(client, userdata, msg):
    print(f"📩 Received: {msg.payload.decode()} on topic {msg.topic}")

while True:
    try:
        # Use callback_api=2 to fix deprecation warning
        client = mqtt.Client(
            client_id="python-subscriber",
            protocol=mqtt.MQTTv5,
            callback_api=2
        )
        client.username_pw_set(USERNAME, PASSWORD)
        client.tls_set()  # enable TLS

        client.on_connect = on_connect
        client.on_message = on_message

        print("⏳ Connecting to broker...")
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)
