from dataclasses import dataclass

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTButtonPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Buttons."""
    command_topic: str = ""  # Required for buttons
    payload_press: str = "PRESS"


class MQTTButton(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        icon: str | None = None,
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: str | None = None,
        initial_state: str | None = None,
        entity_category: EntityCategory | None = None,
    ):
        super().__init__(
            namespace, identifier, name, "button",
            icon=icon, entity_picture=entity_picture, device=device,
            unique_id=unique_id, area=area, initial_state=initial_state, entity_category=entity_category
        )

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
            suggested_area=self.area,
            entity_category=self.entity_category
        )
