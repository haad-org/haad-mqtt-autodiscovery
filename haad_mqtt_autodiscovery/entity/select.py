from dataclasses import dataclass
from typing import Optional, List

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity

@dataclass
class MQTTSelectPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Selects."""
    options: List[str] = None
    command_topic: str = ""  # Required for selects

class MQTTSelect(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        options: List[str],
        icon: str | None = None,
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: Optional[str] = None,
        entity_category: EntityCategory | None = None,
        initial_state: str | None = None
    ):
        self._options = options
        super().__init__(
            namespace, identifier, name, component="select",
            icon=icon, entity_picture=entity_picture, device=device, unique_id=unique_id, area=area,
            entity_category=entity_category,
            initial_state=initial_state if initial_state is not None else options[0] if options else ""
        )

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTSelectPayload:
        return MQTTSelectPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            options=self._options,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            icon=self.icon,
            suggested_area=self.area,
            entity_picture=self.absolute_entity_picture,
            entity_category=self.entity_category
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a command. We echo it to the broker to verify it."""
        if payload in self._options:
            await self._publish_state(payload)

    async def set_state(self, state: str):
        if state in self._options:
            await self._publish_state(state)
        else:
            self.logger.warning(f"Attempted to set invalid option '{state}' on MQTTSelect {self.entity_id}. Valid options: {self._options}")

    @property
    def options(self) -> List[str]:
        return self._options
