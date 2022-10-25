# Phonetic Access Control
Access control software and hardware designed to interact with @KiloSierraCharlie/Phonetic


# Requirement
- MQTT Broker (Mosquitto) configured to use TLS/.x509.
- Phonetic system with access control module configured.

*And either*
- Local hub (eg. Raspberry Pi) to communicate and control multiple ESP nodes (recommended, especially if internet access can be unstable or slow). _Example use: Office buildings with multiple doors, and one reliable WiFi/Ethernet network)_
  - Each door/access controlled system uses an ESP node, and communicates with the hub.

- Local device (eg. Raspberry Pi Zero W) to act as a controlling node. _Example use: Controlled Drugs Safe_
  - Each door/access controlled system uses a device (eg. Raspberry Pi Zero W) to store & update credentialls locally as required, and upload access event when connections are regained.
