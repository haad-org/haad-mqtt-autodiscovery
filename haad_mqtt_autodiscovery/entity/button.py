from dataclasses import dataclass, asdict
from typing import Dict, Any

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload
from haad_mqtt_autodiscovery.entity import MQTTEntity

@dataclass
class MQTTButtonPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Buttons."""
    command_topic: str = ""  # Required for buttons
    payload_press: str = "PRESS"

    def to_json(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

class MQTTButton(MQTTEntity):
    def __init__(self, namespace: str, identifier: str, name: str, icon: str = None, **kwargs):
        super().__init__(namespace, identifier, name, "button", icon=icon, **kwargs)

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTButtonPayload:
        return MQTTButtonPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
            entity_category=self.entity_category
        )
