#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define RELAY_SIGNAL_PIN (4)

/* MQTT broker cert SHA1 fingerprint, used to validate connection to right server */
const uint8_t mqttCertFingerprint[] = {0xB9, 0xA7, 0xD7, 0xDA, 0x84, 0x69, 0x86, 0x26, 0x59, 0xA3, 0xD1, 0x88, 0x7E, 0x8B, 0xE4, 0x8A, 0x9F, 0x2E, 0x7B, 0x85};
String device_id = "HENLEY_STORES";

String server_host = "192.168.1.50";
int server_port = 1883;

String wifi_ap = "Southern Medical Rescue";
String wifi_pass = "SMR999111";



X509List caCertX509(caCert);
WiFiClientSecure espClient;
PubSubClient mqttClient(espClient);
String clientId = device_id + "-";

void reconnect() {
    while (!mqttClient.connected()) {
        if (mqttClient.connect(clientId.c_str())) {
            mqttClient.subscribe("device/" + device_id);      
        } else {
            delay(5000);
        }
    }
}

void setup() 
{
    pinMode(RELAY_SIGNAL_PIN, OUTPUT);

    WiFi.mode(WIFI_STA);
    WiFi.begin( wifi_ap, wifi_pass );

    while (WiFi.status() != WL_CONNECTED){
        delay(500);
    }

    espClient.allowSelfSignedCerts();               /* Enable self-signed cert support */
    espClient.setFingerprint(mqttCertFingerprint);  /* Load SHA1 mqtt cert fingerprint for connection validation */

    mqttClient.setServer( server_host, server_port );
    mqttClient.setCallback(subCallback);

    clientId += String(random(0xffff), HEX); 
}

void loop() 
{
    if(!mqttClient.connected()) {
        reconnect();
    }
    mqttClient.loop();
}

void subCallback(char *topic, byte *payload, unsigned int length)
{
    DynamicJsonDocument doc(256);
    deserializeJson(doc, (char*)payload);  
    JsonObject root = doc.as<JsonObject>();


    if(!root["set"].isNull()) {
        if (root["command"] == "open") {
            digitalWrite(RELAY_SIGNAL_PIN, HIGH);
            delay( 500 );
            digitalWrite(RELAY_SIGNAL_PIN, LOW);
        }
    }
}