import pytest
from haad_mqtt_autodiscovery import (
    MQTTDiscoveryPayload, 
    MQTTDevice, 
    EntityCategory
)

def test_discovery_payload_strips_nested_none_values():
    device = MQTTDevice(
        identifiers=["device_1"],
        name="Test Device",
        suggested_area=None
    )
    
    payload = MQTTDiscoveryPayload(
        name="Test Entity",
        unique_id="test_entity_1",
        state_topic="test/state",
        device=device,
        default_entity_id=None
    )
    
    result = payload.to_json()
    
    assert "default_entity_id" not in result
    assert "suggested_area" not in result["device"]
    assert result["device"]["name"] == "Test Device"


def test_discovery_payload_omits_controls_category():
    device = MQTTDevice(
        identifiers=["device_1"],
        name="Test Device"
    )
    
    payload = MQTTDiscoveryPayload(
        name="Test Entity",
        unique_id="test_entity_1",
        state_topic="test/state",
        device=device,
        entity_category=EntityCategory.CONTROLS
    )
    
    result = payload.to_json()
    
    assert "entity_category" not in result


def test_discovery_payload_includes_other_categories():
    device = MQTTDevice(
        identifiers=["device_1"],
        name="Test Device"
    )
    
    payload = MQTTDiscoveryPayload(
        name="Test Entity",
        unique_id="test_entity_1",
        state_topic="test/state",
        device=device,
        entity_category=EntityCategory.CONFIG
    )
    
    result = payload.to_json()
    
    assert "entity_category" in result
    assert result["entity_category"] == "config"

from haad_mqtt_autodiscovery.entity.number import MQTTNumberPayload

def test_number_discovery_payload_strips_nested_none_values():
    device = MQTTDevice(
        identifiers=["device_1"],
        name="Test Device",
        suggested_area=None
    )
    
    payload = MQTTNumberPayload(
        name="Test Number",
        unique_id="test_number_1",
        state_topic="test/state",
        device=device,
        command_topic="test/set",
        min=None,
        max=100.0,
        step=1.0,
        mode=None
    )
    
    result = payload.to_json()
    
    assert "suggested_area" not in result["device"]
    assert "min" not in result
    assert "mode" not in result
    assert result["max"] == 100.0
    assert result["device"]["name"] == "Test Device"
    assert result["command_topic"] == "test/set"
