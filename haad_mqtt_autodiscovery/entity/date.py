from dataclasses import dataclass
from typing import Optional
from datetime import date

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTDatePayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Date entities (Readable/Writable)."""
    command_topic: str = ""


class MQTTDate(MQTTEntity):
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
        # Maps to HA's 'date' MQTT platform
        super().__init__(
            namespace, identifier, name, component="date",
            icon=icon,
            entity_picture=entity_picture,
            device=device, unique_id=unique_id, area=area
        )

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTDatePayload:
        return MQTTDatePayload(
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
        """Fired when HA sends a date update. Echo it to verify."""
        await self._publish_state(payload)

    async def get_state(self, default: date = None) -> Optional[date]:
        val = await super().get_state()
        if val is None:
            return default
        try:
            return date.fromisoformat(val)
        except ValueError:
            return default

    async def set_state(self, dt: date | str):
        """
        Expects a date object or a parseable ISO 8601 string layout.
        Examples: '2026-07-10'
        """
        if isinstance(dt, date):
            dt = dt.isoformat()
        await self._publish_state(dt)
