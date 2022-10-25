from time import sleep
from json import loads
from paho.mqtt import client as mqtt_client
from random import randint

class MQTTHelper:
    def __init__( self, brokerAddress, brokerPort, tokenHelper ):
        self.brokerAddr = brokerAddress
        self.brokerPort = brokerPort
        self.tokenHelper = tokenHelper
        
        self.client = None

    def connect( self ):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("[MQTT] Connected.")
            else:
                print(f"[MQTT] Failed to connect, return code {rc}.")

        self.client = mqtt_client.Client( f'phonetic-{randint( 1, 10000 )}' )
        self.client.on_connect = on_connect
        self.client.connect( self.brokerAddr, self.brokerPort )

        self.subscribe( "validate" )

    def onMessageRecieve( self, client, userdata, message ):
        try:
            data = loads( message.payload.decode() )
            validationResult = self.tokenHelper.retrieveToken( data["device"], data["uid"] )
            if( self.tokenHelper.lastLoadWeb ):
                self.tokenHelper.storeTokenResult( data["device"], data["uid"], validationResult )
            if( validationResult ):
                print( "[MQTT] Validation success." )
                self.sendAuthorization( data["device"] )
            else:
                print( "[MQTT] Validation failed." )
        except ValueError:
            print( "[MQTT] JSON data error." )

    def subscribe(self, topic):            
        self.client.subscribe( topic )
        self.client.on_message = self.onMessageRecieve

    def sendAuthorization( self, device_id ):
        while True:
            sleep(1)
            result = self.client.publish(f"device/{device_id}", "AUTH-OPEN", qos=2)
            self.client.loop()
            if result[0] == 0:
                print(f"[MQTT] Send authorization to topic `device/{device_id}`")
                return
            else:
                print(f"[MQTT] Failed to send message to topic `device/{device_id}`")
                return