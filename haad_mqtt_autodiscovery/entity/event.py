import json
from dataclasses import dataclass, field
from typing import Optional, List, Any

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTEventPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Events (read-only, stateless: e.g. button presses)."""
    event_types: List[str] = field(default_factory=list)
    device_class: Optional[str] = None  # 'button', 'doorbell' or 'motion'


class MQTTEvent(MQTTEntity):
    """
    Something that happens, like a button press: Home Assistant shows the last one and lets automations trigger on
    every one. Unlike other entities it has no state to sync: every `trigger()` is sent, even the same event type
    twice in a row, and it is not retained (a reconnect must not repeat an old press).
    """

    retain_state = False

    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        event_types: List[str],
        device_class: Optional[str] = None,
        icon: str | None = None,
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: Optional[str] = None,
        entity_category: EntityCategory | None = None,
    ):
        if not event_types:
            raise ValueError(f"MQTTEvent {identifier} needs at least one event type")
        super().__init__(
            namespace, identifier, name, component="event",
            icon=icon, entity_picture=entity_picture, device=device, unique_id=unique_id, area=area,
            entity_category=entity_category
        )
        self.event_types = list(event_types)
        self.device_class = device_class

    def get_discovery_payload(self) -> MQTTEventPayload:
        return MQTTEventPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
            suggested_area=self.area,
            entity_category=self.entity_category,
            event_types=self.event_types,
            device_class=self.device_class,
        )

    async def trigger(self, event_type: str, **attributes: Any):
        """Sends an event; `attributes` become attributes of the event entity in Home Assistant."""
        if event_type not in self.event_types:
            raise ValueError(f"Unknown event type '{event_type}' for {self.entity_id}, valid: {self.event_types}")
        if not self._manager:
            raise RuntimeError(f"Entity '{self.identifier}' must be registered before triggering events.")
        await self._manager.set_state(self, json.dumps({"event_type": event_type, **attributes}))

    async def handle_state_sync(self, payload: str, retain: bool = False):
        """Events are not states: what comes back from the broker changes nothing."""
