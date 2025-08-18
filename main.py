import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "e7b11161.ala.us-east-1.emqxsl.com"
PORT = 8883
TOPIC = "innovation_hub/spot/1"
USERNAME = "farai"
PASSWORD = "farairato3210"

# Callback when client connects
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to broker")
        client.subscribe(TOPIC)
        print(f"📡 Subscribed to {TOPIC}")
    else:
        print(f"❌ Connection failed, return code {rc}")

# Callback when message arrives
def on_message(client, userdata, msg):
    print(f"📩 Message from {msg.topic}: {msg.payload.decode()}")

def main():
    client = mqtt.Client(protocol=mqtt.MQTTv5)  # use v5 protocol
    client.username_pw_set(USERNAME, PASSWORD)

    # Enable TLS (secure connection)
    client.tls_set()  # uses system CA certs
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()

if __name__ == "__main__":
    main()
