from haad.util import serialization as json
from dataclasses import dataclass
from typing import Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTDeviceTrackerPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Device Trackers."""
    source_type: str = "gps"


class MQTTDeviceTracker(MQTTEntity):
    def __init__(self, namespace: str, identifier: str, name: str, icon: str = None, device: MQTTDevice = None, unique_id: str = None, entity_category: EntityCategory = None):
        super().__init__(namespace, identifier, name, "device_tracker", icon=icon, device=device, unique_id=unique_id, entity_category=entity_category)

    def get_discovery_payload(self) -> MQTTDeviceTrackerPayload:
        return MQTTDeviceTrackerPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            json_attributes_topic=self.json_attributes_topic,
            device=self.device,
            icon=self.icon,
            entity_category=self.entity_category,
            source_type="gps"
        )

    async def set_location(self, latitude: float, longitude: float, gps_accuracy: float = 10, location_name: Optional[str] = None):
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": gps_accuracy,
            "source_type": "gps"
        }
        if location_name:
            payload["location_name"] = location_name

        await self._publish_attributes(json.dumps(payload))
        await self._publish_state(location_name if location_name else "not_home")
