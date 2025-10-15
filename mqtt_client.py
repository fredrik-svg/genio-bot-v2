import json
import time
import logging
from typing import Callable, Optional
import paho.mqtt.client as mqtt
import ssl

class MqttClient:
    def __init__(self, host: str, port: int, username: str = "", password: str = "",
                 tls: bool = False, client_id: str = "rpi-voice", on_message: Optional[Callable]=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.tls = tls
        self.client_id = client_id
        self.on_message_cb = on_message

        self._client = mqtt.Client(client_id=self.client_id, clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
        if self.username:
            self._client.username_pw_set(self.username, self.password)
        if self.tls:
            self._client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        logging.info(f"MQTT connected rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        logging.warning(f"MQTT disconnected rc={rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)
        except Exception:
            logging.exception("Failed to parse MQTT message")
            data = {"raw": msg.payload}
        if self.on_message_cb:
            self.on_message_cb(msg.topic, data)

    def loop_start(self):
        self._client.loop_start()

    def loop_stop(self):
        self._client.loop_stop()

    def connect(self, retries: int = 100, backoff: float = 2.0):
        for attempt in range(retries):
            try:
                self._client.connect(self.host, self.port, keepalive=60)
                return True
            except Exception as e:
                logging.error(f"MQTT connect failed (try {attempt+1}/{retries}): {e}")
                time.sleep(backoff)
        return False

    def publish_json(self, topic: str, obj: dict, qos: int = 0, retain: bool = False):
        payload = json.dumps(obj, ensure_ascii=False)
        res = self._client.publish(topic, payload=payload, qos=qos, retain=retain)
        if res.rc != mqtt.MQTT_ERR_SUCCESS:
            logging.error(f"MQTT publish failed: rc={res.rc}")

    def subscribe(self, topic: str, qos: int = 0):
        self._client.subscribe(topic, qos=qos)
