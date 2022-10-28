#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <PN532_SWHSU.h>
#include <PN532.h>

#define RELAY_SIGNAL_PIN (5)

/* MQTT broker cert SHA1 fingerprint, used to validate connection to right server */
const uint8_t mqttCertFingerprint[] ={0x54, 0x82, 0x77, 0xFD, 0x61, 0x63, 0x1C, 0xF5, 0xD4, 0x12, 0xAD, 0xB7, 0xC5, 0xC2, 0x6B, 0xC2, 0x2F, 0xE9, 0x84, 0xB0};
String device_id = "HENLEY_STORES";

IPAddress server(192, 168, 1, 50);
int server_port = 1883;

String wifi_ap = "Southern Medical Rescue";
String wifi_pass = "SMR999111";

SoftwareSerial SWSerial( 2, 4 );
PN532_SWHSU pn532swhsu( SWSerial );
PN532 nfc( pn532swhsu );

WiFiClientSecure espClient;
PubSubClient mqttClient(espClient);
String clientId = device_id + "-";
String lastScannedTag = "";
unsigned long lastTagScan = 0;

void reconnect() {
    while (!mqttClient.connected()) {
        if (mqttClient.connect(clientId.c_str())) {
            mqttClient.publish(("device/" + device_id).c_str(), "Connected");      
            mqttClient.subscribe(("device/" + device_id).c_str());
            digitalWrite(RELAY_SIGNAL_PIN, LOW); 
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

    mqttClient.setServer( server, server_port );
    mqttClient.setCallback(subCallback);

    clientId += String(random(0xffff), HEX); 

    nfc.begin();
    uint32_t versiondata = nfc.getFirmwareVersion();
    if (! versiondata) {
        while (1); // halt
    }
    nfc.SAMConfig();
}

void loop() 
{
    if(!mqttClient.connected()) {
        reconnect();
    }
    detectTag();
    mqttClient.loop();
}

void subCallback(char *topic, byte *payload, unsigned int length)
{
    DynamicJsonDocument doc(256);
    deserializeJson(doc, (char*)payload);  
    JsonObject root = doc.as<JsonObject>();

    if(!root["command"].isNull()) {
        if (root["command"] == "open") {
            digitalWrite(RELAY_SIGNAL_PIN, HIGH);
            delay( 500 );
            digitalWrite(RELAY_SIGNAL_PIN, LOW);
            mqttClient.publish(("device/" + device_id).c_str(), "Connected"); 
        }
    }
}

void detectTag(){
    uint8_t success;
    uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
    uint8_t uidLength;
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 100);

    if ( success ) {
        String curTag = tagToString( uid );
        if( curTag == lastScannedTag ){
          if( ( millis() - lastTagScan ) < 5000 ){
            return;
          }
        }
        lastScannedTag = curTag;
        lastTagScan = millis();
        String json = "";
        StaticJsonDocument<200> root;        
        root["device"] = device_id;
        root["uid"] = lastScannedTag;
        serializeJson( root, json );
        mqttClient.publish("validate", json.c_str());
    }
}

String tagToString(byte id[4]){
  String tagId = "";
  for (byte i = 0; i < 4; i++){
    if (i < 3) tagId += String(id[i]) + "";
    else tagId += String(id[i]);
  }
  return tagId;
}