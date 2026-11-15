import asyncio
import json

import pytest

from haad_mqtt_autodiscovery import MQTTDevice
from haad_mqtt_autodiscovery.entity import MQTTEntity
from haad_mqtt_autodiscovery.entity.event import MQTTEvent


class RecordingManager:
    def __init__(self):
        self.published: list[tuple[str, str, bool]] = []

    async def set_state(self, entity: MQTTEntity, state: str) -> None:
        self.published.append((entity.state_topic, state, entity.retain_state))

    async def set_attributes(self, entity: MQTTEntity, attributes: str) -> None:
        pass


def make_event() -> MQTTEvent:
    return MQTTEvent(
        "xtouch", "strip_1_buttons", "Strip 1 buttons", ["mute_pressed", "mute_released"],
        device_class="button", device=MQTTDevice(identifiers=["xtouch"], name="X-Touch"),
    )


def test_discovery_payload_lists_the_event_types():
    payload = make_event().get_discovery_payload().to_json()

    assert payload["event_types"] == ["mute_pressed", "mute_released"]
    assert payload["device_class"] == "button"
    assert payload["state_topic"] == "homeassistant/event/xtouch/strip_1_buttons/state"
    assert "command_topic" not in payload


def test_an_event_needs_event_types():
    with pytest.raises(ValueError):
        MQTTEvent("xtouch", "x", "x", [])


def test_every_trigger_is_published_not_retained():
    event = make_event()
    manager = RecordingManager()
    event.bind_manager(manager)

    asyncio.run(event.trigger("mute_pressed"))
    asyncio.run(event.trigger("mute_pressed", strip=1))

    assert [(topic, json.loads(state), retain) for topic, state, retain in manager.published] == [
        ("homeassistant/event/xtouch/strip_1_buttons/state", {"event_type": "mute_pressed"}, False),
        ("homeassistant/event/xtouch/strip_1_buttons/state", {"event_type": "mute_pressed", "strip": 1}, False),
    ]


def test_unknown_event_types_and_unregistered_events_raise():
    event = make_event()
    with pytest.raises(RuntimeError):
        asyncio.run(event.trigger("mute_pressed"))
    event.bind_manager(RecordingManager())
    with pytest.raises(ValueError):
        asyncio.run(event.trigger("select_pressed"))


def test_an_event_coming_back_from_the_broker_is_no_state():
    event = make_event()
    asyncio.run(event.handle_state_sync('{"event_type": "mute_pressed"}'))
    assert event.state is None


def test_other_entities_are_retained():
    assert MQTTEntity.retain_state
