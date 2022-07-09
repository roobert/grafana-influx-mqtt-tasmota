#!/usr/bin/env python

# Updated to work with tasmota devices
# Originally stolen from: https://github.com/Nilhcem/home-monitoring-grafana

import paho.mqtt.client as mqtt
import json
import logging
import os
import datetime
import time
from influxdb import InfluxDBClient


BASE_TOPIC = "tele/"
MEASUREMENT = os.getenv("INFLUXDB_DB")
TIMEZONE = "Z"
LOGLEVEL = os.getenv("LOGLEVEL", "INFO")

logging.basicConfig(level=LOGLEVEL.upper())


def boolean_env_is_true(env):
    return os.getenv(env, "false").lower() == "true"


def tasmota_uptime_to_seconds(uptime_string):
    """
    Converts tasmota uptime time strings into seconds
    >>> tasmota_uptime_to_seconds("0T01:00:00")
    3600
    >>> tasmota_uptime_to_seconds("1T00:00:10")
    86410
    >>> tasmota_uptime_to_seconds("0T00:01:01")
    61
    """
    days, timestr = uptime_string.split("T", 1)

    t = time.strptime(timestr, "%H:%M:%S")

    return int(
        datetime.timedelta(
            days=int(days), hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec
        ).total_seconds()
    )


def parse_sensor_message_into_influxdb_point(power_socket, topic, msg):
    data = json.loads(msg.payload)

    fields = None
    measurement = None
    if topic == "SENSOR":
        fields = data["ENERGY"]
        measurement = "sensor"
    elif topic == "STATE":
        fields = {"Uptime": tasmota_uptime_to_seconds(data["Uptime"])}
        measurement = "state"
    else:
        raise "Unexpected topic " + topic

    point = {
        "time": data["Time"] + TIMEZONE,
        "measurement": measurement,
        "tags": {"power_socket": power_socket, "topic": topic},
        "fields": fields,
    }

    return point


# The callback for when the client receives a CONNACK response from the server.
# 0: Connection successful
# 1: Connection refused – incorrect protocol version
# 2: Connection refused – invalid client identifier
# 3: Connection refused – server unavailable
# 4: Connection refused – bad username or password
# 5: Connection refused – not authorised
# 6-255: Currently unused.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(BASE_TOPIC + "#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"message published to topic: {msg.topic}")
    subtopic = msg.topic.replace(BASE_TOPIC, "")
    power_socket, topic = subtopic.split("/", 1)
    influxdb_client = userdata["influxdb_client"]

    if topic in ["SENSOR", "STATE"]:
        logging.info(f"New {topic} message from {power_socket}")
        point = parse_sensor_message_into_influxdb_point(power_socket, topic, msg)
        influxdb_client.write_points([point])
    elif topic == "LWT":
        logging.info(
            f"Power socket {power_socket} reports: {msg.payload.decode('UTF-8')}"
        )
    else:
        logging.warning(f"Unexpected topic {msg.topic}: {msg.payload}")


def main():
    influxdb_client = InfluxDBClient(
        host=os.getenv("INFLUXDB_HOST", "influxdb-plugs"),
        port=int(os.getenv("INFLUXDB_PORT", "18086")),
        username=os.getenv("INFLUXDB_USER"),
        password=os.getenv("INFLUXDB_PASSWORD"),
        database=os.getenv("INFLUXDB_DB", "plugs"),
        ssl=boolean_env_is_true("INFLUXDB_SSL"),
        verify_ssl=not boolean_env_is_true("INFLUXDB_NO_VERIFY_SSL"),
    )

    mqtt_client = mqtt.Client(userdata={"influxdb_client": influxdb_client})
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    logger = logging.getLogger("mqttclient")
    mqtt_client.enable_logger(logger)

    mqtt_client.connect(
        os.getenv("MQTT_HOST", "mosquitto"), int(os.getenv("MQTT_PORT", "1883")), 60
    )

    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
