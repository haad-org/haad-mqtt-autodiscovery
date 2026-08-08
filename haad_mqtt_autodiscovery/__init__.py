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
        def _factory(data):
            res = {}
            for k, v in data:
                if v is not None:
                    if isinstance(v, Enum):
                        v = v.value
                    if k == "entity_category" and v == EntityCategory.CONTROLS.value:
                        continue
                    res[k] = v
            return res

        return asdict(self, dict_factory=_factory)
