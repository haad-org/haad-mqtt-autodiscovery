from dataclasses import dataclass
from typing import Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTTimePayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Time entities (Readable/Writable)."""
    command_topic: str = ""


class MQTTTime(MQTTEntity):
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
        entity_category: EntityCategory | None = None
    ):
        # Maps to HA's 'time' MQTT platform, functioning like an input_datetime with has_date=false
        super().__init__(
            namespace, identifier, name, component="time",
            icon=icon, entity_picture=entity_picture,
            device=device, unique_id=unique_id, area=area, initial_state=initial_state,
            entity_category=entity_category
        )

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTTimePayload:
        return MQTTTimePayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            device=self.device,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
            suggested_area=self.area,
            entity_category=self.entity_category
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a time update. Echo it to verify."""
        await self._publish_state(payload)

    
    async def set_state(self, time_string: str):
        """Update the time state directly from the backend."""
        await self._publish_state(time_string)

    async def get_state(self, default: str = None) -> Optional[str]:
        val = await super().get_state()
        if val is None:
            return default
        return val
