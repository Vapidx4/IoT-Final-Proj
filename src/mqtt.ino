#include <SPI.h>
#include <MFRC522.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define SS_PIN D8
#define RST_PIN D0
#define pResistorPin A0

const char* ssid = "Ishi";
const char* password = "tvnq0987";
const char* mqtt_server = "192.168.7.48";

WiFiClient espClient;
PubSubClient client(espClient);

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

MFRC522::MIFARE_Key key;

// Init array that will store new NUID
byte nuidPICC[4];

void setup_wifi();
void callback(char* topic, byte* message, unsigned int length);
void reconnect();
void publishRFIDValue();

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  SPI.begin();         // Init SPI bus
  rfid.PCD_Init();      // Init MFRC522

  Serial.println();
  Serial.print(F("Reader :"));
  rfid.PCD_DumpVersionToSerial();

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  Serial.println();
  Serial.println(F("This code scans the MIFARE Classic NUID."));
  Serial.print(F("Using the following key:"));
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();
  publishRFIDValue();
  publishSensorValue();
  delay(5000);
}

void setup_wifi() {
  Serial.println("Connecting to " + String(ssid));
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected - ESP-8266 IP address: " + WiFi.localIP().toString());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: " + String(topic) + ". Message: ");

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
  }

  Serial.println("\n");
}

void reconnect() {
  Serial.print("Attempting MQTT connection...");

  if (client.connect("vapid")) {
    Serial.println("connected");
    client.subscribe("Home/LIGHT");
    client.subscribe("Home/USER");
  } else {
    Serial.println("failed, rc=" + String(client.state()) + " try again in 3 seconds");
    delay(3000);
  }
}

void publishRFIDValue() {
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  if (rfid.uid.uidByte[0] != nuidPICC[0] ||
      rfid.uid.uidByte[1] != nuidPICC[1] ||
      rfid.uid.uidByte[2] != nuidPICC[2] ||
      rfid.uid.uidByte[3] != nuidPICC[3]) {

    Serial.println(F("A new card has been detected."));

    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }

    Serial.println(F("The NUID tag is:"));
    printHex(rfid.uid.uidByte, rfid.uid.size);
    Serial.println();
    client.publish("Home/USER", rfid.uid.uidByte, rfid.uid.size);
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

void publishSensorValue() {
  int sensorValue = analogRead(pResistorPin);
  client.publish("Home/LIGHT", String(sensorValue).c_str());
}

void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}
