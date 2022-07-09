FROM python:3.10-alpine

LABEL maintainer="roobert" \
  description="MQTT to InfluxDB Bridge"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "-u", "main.py"]
