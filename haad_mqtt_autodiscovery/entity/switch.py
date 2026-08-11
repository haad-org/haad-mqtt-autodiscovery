from dataclasses import dataclass
from typing import Optional

STATE_ON = 'on'
STATE_OFF = 'off'
from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity
from haad_mqtt_autodiscovery.entity.util import parse_to_mqtt_on_off_state


@dataclass
class MQTTSwitchPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Switches."""
    command_topic: str = ""  # Required for switches
    payload_on: str = "ON"
    payload_off: str = "OFF"
    optimistic: bool = False


class MQTTSwitch(MQTTEntity):
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
        initial_state: str | bool = False
    ):
        parsed_initial_state = parse_to_mqtt_on_off_state(initial_state)
        super().__init__(
            namespace, identifier, name, component="switch",
            icon=icon, entity_picture=entity_picture, device=device, unique_id=unique_id, area=area,
            entity_category=entity_category,
            initial_state=parsed_initial_state
        )

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTSwitchPayload:
        return MQTTSwitchPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            icon=self.icon,
            suggested_area=self.area,
            entity_picture=self.absolute_entity_picture,
            entity_category=self.entity_category,
            optimistic=False
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a command. We echo it to the broker to verify it."""
        await self._publish_state(payload)

    def is_on(self) -> bool:
        current_state = self.state or ""
        return current_state.upper() == STATE_ON.upper()

    async def set_state(self, state: str | bool):
        parsed_state = parse_to_mqtt_on_off_state(state)
        if parsed_state == STATE_ON.upper():
            await self.turn_on()
        else:
            await self.turn_off()

    async def turn_on(self):
        await self._publish_state(STATE_ON.upper())

    async def turn_off(self):
        await self._publish_state(STATE_OFF.upper())

    async def toggle(self):
        if self.is_on():
            await self.turn_off()
        else:
            await self.turn_on()
