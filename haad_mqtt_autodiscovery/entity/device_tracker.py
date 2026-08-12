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
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: Optional[str] = None,
        entity_category: EntityCategory | None = None,
        source_type: DeviceTrackerSourceType = DeviceTrackerSourceType.GPS,
    ):
        super().__init__(
            namespace, identifier, name, component="device_tracker",
            icon=icon, entity_picture=entity_picture, device=device, unique_id=unique_id, area=area,
            entity_category=entity_category
        )
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
            entity_picture=self.absolute_entity_picture,
            suggested_area=self.area,
            entity_category=self.entity_category,
            source_type=self.source_type.value
        )

    async def set_location(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        gps_accuracy: Optional[float] = None,
        location_name: Optional[str] = None
    ):
        # Start with the base payload
        payload = {
            "source_type": self.source_type.value,
        }

        # Only add coordinates if they are explicitly provided
        if latitude is not None:
            payload["latitude"] = latitude
        if longitude is not None:
            payload["longitude"] = longitude
        if gps_accuracy is not None:
            payload["gps_accuracy"] = gps_accuracy
        if location_name:
            payload["location_name"] = location_name

        await self._publish_attributes(json.dumps(payload))
        await self._publish_state(location_name if location_name else "not_home")

    async def is_home(self) -> bool:
        state = await self.get_state()
        return state == "home"

    async def get_last_known_location(self) -> Optional[dict]:
        # TODO: get_attributes doesn't exist yet
        attributes = await self.get_attributes()
        if not attributes:
            return None
        return {
            "latitude": float(attributes.get("latitude")),
            "longitude": float(attributes.get("longitude")),
            "gps_accuracy": float(attributes.get("gps_accuracy")) if attributes.get("gps_accuracy") is not None else None,
            "location_name": attributes.get("location_name"),
        }
