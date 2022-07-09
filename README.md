# Grafana InfluxDB MQTT Tasmota

Data store for Tasmota plugs on the local network.

I use plugs from https://www.mylocalbytes.com

## Usage

```
# Build the docker image for mqtt-bridge
make rebuild

# Create a docker network
make create-network

# Start the services:
docker-compose up -d

# Create a database
make create-db
```


Finally, configure the plug to send data to the machine IP, port 1883, using MQTT protocol.
