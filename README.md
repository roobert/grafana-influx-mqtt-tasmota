# Grafana InfluxDB MQTT Tasmota

Data store for tasmota plugs on the local network.

## Usage

Start the services:
```
docker-compose up
```

Finally, configure the plug to send data to the machine IP, port 1883, using MQTT protocol.
