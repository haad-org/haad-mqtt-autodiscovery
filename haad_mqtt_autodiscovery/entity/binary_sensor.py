from dataclasses import dataclass
from typing import Optional

STATE_ON = 'on'
STATE_OFF = 'off'
from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTBinarySensorPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Binary Sensors (Read-only)."""
    device_class: Optional[str] = None
    payload_on: str = "ON"
    payload_off: str = "OFF"


class MQTTBinarySensor(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        icon: Optional[str] = None,
        entity_picture: Optional[str] = None,
        device: MQTTDevice = None,
        device_class: Optional[str] = None,
        unique_id: str = None
    ):
        super().__init__(
            namespace,
            identifier,
            name,
            "binary_sensor",
            icon=icon,
            entity_picture=entity_picture,
            device=device,
            unique_id=unique_id
        )
        self.device_class = device_class

    def get_discovery_payload(self) -> MQTTBinarySensorPayload:
        return MQTTBinarySensorPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            device_class=self.device_class,
            payload_on=STATE_ON.upper(),
            payload_off=STATE_OFF.upper(),
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
        )

    def is_on(self) -> bool:
        return self.state == STATE_ON.upper()

    async def turn_on(self):
        await self._publish_state(STATE_ON.upper())

    async def turn_off(self):
        await self._publish_state(STATE_OFF.upper())

    async def set_state(self, is_on: bool):
        if is_on:
            await self.turn_on()
        else:
            await self.turn_off()
