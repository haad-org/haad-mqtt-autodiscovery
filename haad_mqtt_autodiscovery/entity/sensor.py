from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTSensorPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Sensors (Read-only)."""
    device_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    state_class: Optional[str] = None
    icon: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        # Filter out None values to keep the payload clean
        return {k: v for k, v in asdict(self).items() if v is not None}


class MQTTSensor(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        device: MQTTDevice = None,
        device_class: Optional[str] = None,
        unit_of_measurement: Optional[str] = None,
        state_class: Optional[str] = None,
        icon: Optional[str] = None,
        entity_picture: Optional[str] = None,
        unique_id: str = None
    ):
        super().__init__(namespace, identifier, name, "sensor", device=device, unique_id=unique_id, icon=icon, entity_picture=entity_picture)
        self.device_class = device_class
        self.unit_of_measurement = unit_of_measurement
        self.state_class = state_class

    def get_discovery_payload(self) -> MQTTSensorPayload:
        return MQTTSensorPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            device_class=self.device_class,
            unit_of_measurement=self.unit_of_measurement,
            state_class=self.state_class,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture
        )

    def get_state(self, default: str = None) -> Optional[str]:
        state = self.state
        if state is None:
            return default
        return state

    async def set_state(self, value: Any):
        """Helper to cast values to strings before publishing."""
        await self._publish_state(str(value))
