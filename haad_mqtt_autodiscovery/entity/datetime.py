from dataclasses import dataclass
from typing import Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTDateTimePayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Date/Time entities (Readable/Writable)."""
    command_topic: str = ""


class MQTTDateTime(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        icon: str | None = None,
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: Optional[str] = None
    ):
        # Maps to HA's 'datetime' MQTT platform, functioning like an input_datetime
        super().__init__(
            namespace, identifier, name, component="datetime",
            icon=icon,
            entity_picture=entity_picture,
            device=device, unique_id=unique_id, area=area
        )

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTDateTimePayload:
        return MQTTDateTimePayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            device=self.device
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a datetime update. Echo it to verify."""
        await self._publish_state(payload)

    async def get_state(self, default: str = None) -> Optional[str]:
        val = await super().get_state()
        if val is None:
            return default
        return val

    async def set_state(self, dt_string: str):
        """
        Expects a parseable string layout.
        Examples: '2026-07-10', '20:15:00', or '2026-07-10 20:15:00'
        """
        await self._publish_state(dt_string)
