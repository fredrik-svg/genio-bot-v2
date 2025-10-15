"""
MQTT client med förbättrad felhantering och säkerhet.
"""
import json
import time
import logging
from typing import Callable, Optional, Any, Dict
import paho.mqtt.client as mqtt
import ssl

class MqttClientError(Exception):
    """Bas exception för MQTT-relaterade fel."""
    pass

class MqttClient:
    """
    MQTT client för kommunikation mellan Raspberry Pi och n8n.
    
    Stödjer TLS, återanslutning och robust felhantering.
    """
    
    def __init__(self, host: str, port: int, username: str = "", password: str = "",
                 tls: bool = False, client_id: str = "rpi-voice", 
                 on_message: Optional[Callable[[str, Dict], None]] = None,
                 max_payload_size: int = 100000):
        """
        Initialisera MQTT-klient.
        
        Args:
            host: MQTT broker host
            port: MQTT broker port
            username: MQTT användarnamn
            password: MQTT lösenord
            tls: Använd TLS-kryptering
            client_id: Unikt client ID
            on_message: Callback för inkommande meddelanden
            max_payload_size: Max payload-storlek i bytes (säkerhet)
        """
        if not host:
            raise ValueError("MQTT host kan inte vara tom")
        if not 1 <= port <= 65535:
            raise ValueError(f"Ogiltig MQTT port: {port}")
            
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.tls = tls
        self.client_id = client_id
        self.on_message_cb = on_message
        self.max_payload_size = max_payload_size
        self._connected = False

        self._client = mqtt.Client(client_id=self.client_id, clean_session=True, 
                                   userdata=None, protocol=mqtt.MQTTv311)
        if self.username:
            self._client.username_pw_set(self.username, self.password)
        if self.tls:
            self._client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Callback när anslutning upprättas."""
        if rc == 0:
            self._connected = True
            logging.info("MQTT ansluten")
        else:
            logging.error(f"MQTT anslutning misslyckades med kod: {rc}")

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Callback när anslutning bryts."""
        self._connected = False
        if rc != 0:
            logging.warning(f"MQTT frånkopplad oväntat: rc={rc}")
        else:
            logging.info("MQTT frånkopplad")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """
        Callback för inkommande meddelanden.
        
        Validerar payload-storlek och JSON-format.
        """
        try:
            # Säkerhet: Kontrollera payload-storlek
            if len(msg.payload) > self.max_payload_size:
                logging.warning(f"MQTT payload för stor: {len(msg.payload)} bytes")
                return
                
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)
            
            # Anropa callback
            if self.on_message_cb:
                self.on_message_cb(msg.topic, data)
        except json.JSONDecodeError as e:
            logging.error(f"Ogiltig JSON i MQTT-meddelande: {e}")
        except UnicodeDecodeError as e:
            logging.error(f"Kunde inte dekoda MQTT payload: {e}")
        except Exception as e:
            logging.exception(f"Oväntat fel vid hantering av MQTT-meddelande: {e}")

    def loop_start(self) -> None:
        """Starta MQTT nätverksloop i separat tråd."""
        self._client.loop_start()

    def loop_stop(self) -> None:
        """Stoppa MQTT nätverksloop."""
        try:
            self._client.loop_stop()
        except Exception as e:
            logging.error(f"Fel vid stopp av MQTT loop: {e}")

    def connect(self, retries: int = 5, backoff: float = 2.0, timeout: int = 10) -> bool:
        """
        Anslut till MQTT broker med exponentiell backoff.
        
        Args:
            retries: Antal återförsök
            backoff: Initial väntetid mellan försök (sekunder)
            timeout: Timeout per anslutningsförsök (sekunder)
            
        Returns:
            True om anslutning lyckades, annars False
        """
        for attempt in range(1, retries + 1):
            try:
                logging.info(f"Ansluter till MQTT broker {self.host}:{self.port} (försök {attempt}/{retries})")
                self._client.connect(self.host, self.port, keepalive=60)
                
                # Vänta på anslutning
                start_time = time.time()
                while not self._connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                if self._connected:
                    logging.info("MQTT anslutning etablerad")
                    return True
                else:
                    logging.warning("MQTT anslutning timeout")
            except Exception as e:
                logging.error(f"MQTT anslutning misslyckades (försök {attempt}/{retries}): {e}")
                
            if attempt < retries:
                wait_time = backoff * (2 ** (attempt - 1))  # Exponentiell backoff
                logging.info(f"Väntar {wait_time:.1f}s innan nästa försök...")
                time.sleep(wait_time)
        
        return False

    def disconnect(self) -> None:
        """Koppla från MQTT broker på ett säkert sätt."""
        try:
            self._client.disconnect()
            logging.info("MQTT frånkopplad")
        except Exception as e:
            logging.error(f"Fel vid frånkoppling från MQTT: {e}")

    def publish_json(self, topic: str, obj: Dict, qos: int = 0, retain: bool = False) -> bool:
        """
        Publicera JSON-objekt till MQTT topic.
        
        Args:
            topic: MQTT topic
            obj: Dict att serialisera till JSON
            qos: Quality of Service (0-2)
            retain: Behåll meddelande på broker
            
        Returns:
            True om publicering lyckades
        """
        try:
            if not self._connected:
                logging.error("Kan inte publicera: MQTT ej ansluten")
                return False
                
            payload = json.dumps(obj, ensure_ascii=False)
            
            # Säkerhet: Kontrollera payload-storlek
            if len(payload) > self.max_payload_size:
                logging.error(f"Payload för stor att publicera: {len(payload)} bytes")
                return False
                
            res = self._client.publish(topic, payload=payload, qos=qos, retain=retain)
            
            if res.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.debug(f"MQTT publicerad till {topic}")
                return True
            else:
                logging.error(f"MQTT publicering misslyckades: rc={res.rc}")
                return False
        except Exception as e:
            logging.exception(f"Fel vid MQTT publicering: {e}")
            return False

    def subscribe(self, topic: str, qos: int = 0) -> bool:
        """
        Prenumerera på MQTT topic.
        
        Args:
            topic: MQTT topic att prenumerera på
            qos: Quality of Service (0-2)
            
        Returns:
            True om prenumeration lyckades
        """
        try:
            result, mid = self._client.subscribe(topic, qos=qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Prenumererar på MQTT topic: {topic}")
                return True
            else:
                logging.error(f"MQTT prenumeration misslyckades: rc={result}")
                return False
        except Exception as e:
            logging.exception(f"Fel vid MQTT prenumeration: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Returnera om klienten är ansluten."""
        return self._connected
