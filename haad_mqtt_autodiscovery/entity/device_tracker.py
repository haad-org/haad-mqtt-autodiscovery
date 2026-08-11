import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTDeviceTrackerPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Device Trackers."""
    source_type: str = "gps"


class DeviceTrackerSourceType(StrEnum):
    """Enumeration of valid source types for device trackers."""
    BLUETOOTH = "bluetooth"
    BLE = "bluetooth_le"
    GPS = "gps"
    ROUTER = "router"


class MQTTDeviceTracker(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        icon: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: Optional[str] = None,
        entity_category: EntityCategory | None = None,
        source_type: DeviceTrackerSourceType = DeviceTrackerSourceType.GPS,
    ):
        super().__init__(namespace, identifier, name, "device_tracker", icon=icon, device=device, unique_id=unique_id, area=area, entity_category=entity_category)
        self.source_type = source_type

    def get_discovery_payload(self) -> MQTTDeviceTrackerPayload:
        return MQTTDeviceTrackerPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            json_attributes_topic=self.json_attributes_topic,
            device=self.device,
            icon=self.icon,
            suggested_area=self.area,
            entity_category=self.entity_category,
            source_type=self.source_type.value
        )

    async def set_location(self, latitude: float, longitude: float, gps_accuracy: float = 10, location_name: Optional[str] = None):
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": gps_accuracy,
            "source_type": self.source_type.value,
        }
        if location_name:
            payload["location_name"] = location_name

        await self._publish_attributes(json.dumps(payload))
        await self._publish_state(location_name if location_name else "not_home")

    async def is_home(self) -> bool:
        state = self.get_state()
        return state == "home"