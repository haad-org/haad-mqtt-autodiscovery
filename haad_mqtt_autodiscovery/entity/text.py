from dataclasses import dataclass
from typing import Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTTextPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Text entities (Readable/Writable)."""
    command_topic: str = ""  # Required for HA to send text updates
    mode: str = "text"  # 'text' or 'password'
    min: Optional[int] = None
    max: Optional[int] = None
    pattern: Optional[str] = None


class MQTTText(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        icon: str | None = None,
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: Optional[str] = None,
        entity_category: EntityCategory | None = None,
        mode: str = "text"
    ):
        super().__init__(
            namespace, identifier, name, component="text",
            icon=icon, entity_picture=entity_picture,
            device=device, unique_id=unique_id, area=area,
            entity_category=entity_category
        )
        self.mode = mode

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTTextPayload:
        return MQTTTextPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            device=self.device,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
            suggested_area=self.area,
            entity_category=self.entity_category,
            mode=self.mode
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a text input command. Echo it to verify."""
        await self._publish_state(payload)

    def get_state(self, default: str = None) -> Optional[str]:
        state = self.state
        if state is None:
            return default
        return state

    async def set_state(self, text: str):
        await self._publish_state(text)

    async def clear(self):
        await self._publish_state("")
