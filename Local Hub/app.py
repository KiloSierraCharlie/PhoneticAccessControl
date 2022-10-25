from MQTTHelper import MQTTHelper
from TokenHelper import TokenHelper

locallyStoredDevices = (
    "HENLEY_STORES", "HENLEY_GARAGE", "HENLEY_OFFICE", 
    "HENLEY_LOCKER_1", "HENLEY_LOCKER_2", "HENLEY_LOCKER_3", 
    "HENLEY_LOCKER_4"
)

def run():
    th = TokenHelper( "smr", locallyStoredDevices )
    mqtt = MQTTHelper( "broker.emqx.io", 1883, th )
    mqtt.connect()
    mqtt.client.loop_forever()

if __name__ == '__main__':
    run()