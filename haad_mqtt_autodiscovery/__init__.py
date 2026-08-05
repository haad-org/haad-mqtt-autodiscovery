import re
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional, Dict, Any


def slugify(text: str) -> str:
    """Mimics Home Assistant's internal string slugification."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\s\-]+', '_', text)
    return re.sub(r'[^a-z0-9_]', '', text)


@dataclass
class MQTTDevice:
    """Represents the physical/logical device grouping entities in HA."""
    identifiers: list[str] = field(default_factory=lambda: ["custom_mqtt_client"])
    name: str = "MQTT Client"
    manufacturer: str = "Unknown"
    model: str = "v1.0"
    suggested_area: Optional[str] = None


class EntityCategory(str, Enum):
    CONTROLS = "controls"
    CONFIG = "config"
    DIAGNOSTIC = "diagnostic"


@dataclass
class MQTTDiscoveryPayload:
    """Base schema for ALL Home Assistant MQTT entities."""
    name: str
    unique_id: str
    state_topic: str
    device: MQTTDevice
    default_entity_id: Optional[str] = None

    # Easily expanded later for advanced HA features:
    # device_class: Optional[str] = None
    icon: Optional[str] = None
    entity_picture: Optional[str] = None
    entity_category: Optional[EntityCategory] = None
    json_attributes_topic: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        data = {}
        for k, v in asdict(self).items():
            if v is not None:
                val = v.value if isinstance(v, Enum) else v
                # If the category is CONTROLS, we omit it from the payload
                # because HA defaults to "Controls" when no category is specified.
                if k == "entity_category" and val == EntityCategory.CONTROLS.value:
                    continue
                data[k] = val
        return data
