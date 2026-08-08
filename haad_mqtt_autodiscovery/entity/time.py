from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTTimePayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Time entities (Readable/Writable)."""
    command_topic: str = ""



class MQTTTime(MQTTEntity):
    def __init__(self, namespace: str, identifier: str, name: str, icon: str = None, device: MQTTDevice = None, unique_id: str = None, initial_state: str = None,
                 entity_category: EntityCategory = None):
        # Maps to HA's 'time' MQTT platform, functioning like an input_datetime with has_date=false
        super().__init__(namespace, identifier, name, "time", icon=icon, device=device, unique_id=unique_id, initial_state=initial_state, entity_category=entity_category)

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
            entity_category=self.entity_category
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a time update. Echo it to verify."""
        await self._publish_state(payload)

    def get_state(self, default: str = None) -> Optional[str]:
        state = self.state
        if state is None:
            return default
        return state
