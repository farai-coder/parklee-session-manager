import paho.mqtt.client as mqtt
import requests
import threading

# MQTT Broker details
BROKER = "159.65.77.162"  # Replace with your broker IP
PORT = 1883
TOPIC_PREFIX = "innovation_hub/spot/"

# Backend API endpoints
SPOT_MAP_URL = "https://fastapi-app-ctkl.onrender.com/spots/spot-number-to-id"
CHECKIN_API_URL = "https://fastapi-app-ctkl.onrender.com/sessions/check-in"
CHECKOUT_API_URL = "https://fastapi-app-ctkl.onrender.com/sessions/check-out-by-spot"  # Use query param

def get_spot_id(spot_number):
    """Fetch spot_id from backend based on spot_number."""
    try:
        resp = requests.get(SPOT_MAP_URL)
        resp.raise_for_status()
        data = resp.json()
        #print("Spot map response:", data)
        # Try int key first, fallback to string
        spot_number_int = int(spot_number)
        return str(data.get(spot_number_int) or data.get(spot_number))
    except Exception as e:
        print(f"❌ Failed to get spot_id for spot {spot_number}: {e}")
        return None

def handle_vehicle_event(spot_number, payload):
    """Handle check-in/check-out API calls based on MQTT payload."""
    spot_id = get_spot_id(spot_number)
    if not spot_id:
        print(f"❌ Could not find spot_id for spot number {spot_number}")
        return

    if payload == "Vehicle Entered":
        try:
            resp = requests.post(CHECKIN_API_URL, json={"spot_id": spot_id}, timeout=5)
            if resp.status_code == 201:
                print(f"✅ Checked in spot {spot_number} [{spot_id}] successfully.")
            else:
                print(f"❌ Check-in failed for spot {spot_number}: {resp.text}")
        except Exception as e:
            print(f"❌ Exception during check-in for spot {spot_number}: {e}")

    elif payload == "Vehicle Left":
        try:
            # Send spot_id as query parameter
            resp = requests.post(f"{CHECKOUT_API_URL}?spot_id={spot_id}", timeout=5)
            if resp.status_code == 200:
                print(f"✅ Checked out spot {spot_number} [{spot_id}] successfully.")
            else:
                print(f"❌ Check-out failed for spot {spot_number}: {resp.text}")
        except Exception as e:
            print(f"❌ Exception during check-out for spot {spot_number}: {e}")
    else:
        print(f"ℹ️ Unrecognized payload: {payload}")

def on_connect(client, userdata, flags, rc):
    """Called when MQTT client connects to broker."""
    if rc == 0:
        print("✅ Connected to broker")
        client.subscribe(TOPIC_PREFIX + "+", qos=1)
    else:
        print("❌ Failed to connect, return code", rc)

def on_message(client, userdata, msg):
    """Called when a message is received on subscribed topic."""
    payload = msg.payload.decode().strip()
    print(f"📩 Received payload '{payload}' on topic '{msg.topic}'")
    topic_parts = msg.topic.split('/')
    if len(topic_parts) >= 3 and topic_parts[0] == "innovation_hub" and topic_parts[1] == "spot":
        spot_number = topic_parts[2].strip()
        threading.Thread(target=handle_vehicle_event, args=(spot_number, payload), daemon=True).start()

if __name__ == "__main__":
    client = mqtt.Client(client_id="python-subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

# // WiFi credentials
# const char* ssid = "Cloud";
# const char* password = "cloud2024";

# // MQTT broker settings
# const char* mqtt_server = "159.65.77.162";  // your VM IP
# const int mqtt_port = 1883;                 // non-TLS for now
# const char* topic = "innovation_hub/spot/1";

# // Ultrasonic pins
# #define TRIG_PIN 5
# #define ECHO_PIN 18

# // Parameters
# const float THRESHOLD_CM = 100.0;   // 1 meter
# const unsigned long MIN_TRACK_TIME = 100; // 10 sec

# bool vehiclePresent = false;
# unsigned long trackStartTime = 0;
# bool vehicleConfirmed = false;

# // WiFi & MQTT clients
# WiFiClient espClient;
# PubSubClient client(espClient);

# // Reliable publish with retry using QoS 2
# bool publishWithRetry(const char* topic, const char* payload) {
#   bool success = false;
#   int attempts = 0;

#   while (!success && attempts < 5) {
#     success = client.publish(topic, payload, true);  // retained true, QoS 2 handled automatically by PubSubClient
#     if (!success) {
#       Serial.println("⚠️ Publish failed, retrying...");
#       delay(500);
#       client.loop();
#     }
#     attempts++;
#   }
#   return success;
# }

# void setup_wifi() {
#   Serial.print("Connecting to WiFi: ");
#   Serial.println(ssid);
#   WiFi.begin(ssid, password);

#   while (WiFi.status() != WL_CONNECTED) {
#     delay(500);
#     Serial.print(".");
#   }
#   Serial.println("\n✅ WiFi connected!");
# }

# void reconnect() {
#   while (!client.connected()) {
#     Serial.print("Connecting to MQTT...");
#     if (client.connect("ESP32Client")) {  // no username/password needed for now
#       Serial.println("✅ Connected to broker");
#     } else {
#       Serial.print("❌ Failed, rc=");
#       Serial.print(client.state());
#       Serial.println(" retrying in 5s");
#       delay(5000);
#     }
#   }
# }

# float getDistance() {
#   digitalWrite(TRIG_PIN, LOW);
#   delayMicroseconds(2);
#   digitalWrite(TRIG_PIN, HIGH);
#   delayMicroseconds(10);
#   digitalWrite(TRIG_PIN, LOW);

#   long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout ~5m
#   if (duration == 0) return -1;
#   return (duration * 0.0343) / 2; // cm
# }

# void setup() {
#   Serial.begin(9600);
#   pinMode(TRIG_PIN, OUTPUT);
#   pinMode(ECHO_PIN, INPUT);

#   setup_wifi();

#   client.setServer(mqtt_server, mqtt_port);
#   client.setBufferSize(1024);
# }

# void loop() {
#   if (!client.connected()) {
#     reconnect();
#   }
#   client.loop();

#   float distance = getDistance();
#   unsigned long now = millis();

#   if (distance > 0) {
#     Serial.print("Distance: ");
#     Serial.print(distance);
#     Serial.println(" cm");
#   }

#   if (distance > 0 && distance <= THRESHOLD_CM) {
#     if (!vehiclePresent) {
#       vehiclePresent = true;
#       trackStartTime = now;
#     } else {
#       if (!vehicleConfirmed && (now - trackStartTime >= MIN_TRACK_TIME)) {
#         vehicleConfirmed = true;
#         Serial.println("🚗 Vehicle Entered");
#         if (publishWithRetry(topic, "Vehicle Entered")) {
#           Serial.println("✅ Vehicle Entered message sent");
#         } else {
#           Serial.println("❌ Failed to send Vehicle Entered message");
#         }
#       }
#     }
#   } else {
#     if (vehicleConfirmed) {
#       Serial.println("🚗 Vehicle Left");
#       if (publishWithRetry(topic, "Vehicle Left")) {
#         Serial.println("✅ Vehicle Left message sent");
#       } else {
#         Serial.println("❌ Failed to send Vehicle Left message");
#       }
#     }
#     vehiclePresent = false;
#     vehicleConfirmed = false;
#   }

#   delay(500);
# }

