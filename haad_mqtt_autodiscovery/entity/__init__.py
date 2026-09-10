import inspect
import json
import logging
from typing import Optional, Callable, Awaitable, List, Protocol, Any

from haad_mqtt_autodiscovery import MQTTDevice, MQTTDiscoveryPayload, EntityCategory


class MQTTManagerProtocol(Protocol):
    async def set_state(self, entity: 'MQTTEntity', state: str) -> None: ...
    async def set_attributes(self, entity: 'MQTTEntity', attributes: str) -> None: ...

class MQTTEntity:
    discovery_prefix = "homeassistant"
    DEFAULT_DEVICE = MQTTDevice(identifiers=["custom_mqtt_client"], name="MQTT Client", manufacturer="Unknown", model="v1.0")

    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        component: str,
        icon: str | None = None,
        entity_picture: str | None = None,
        device: MQTTDevice | None = None,
        unique_id: str | None = None,
        area: str | None = None,
        initial_state: str | None = None,
        entity_category: EntityCategory | None = None,
    ):
        self.logger = logging.getLogger(f"mqttentity.{namespace}.{identifier}")
        self.namespace = namespace
        self.identifier = identifier
        self.name = name
        self.icon = icon
        self.entity_picture = entity_picture
        self.component = component
        self.device = device or self.DEFAULT_DEVICE
        self._unique_id = unique_id
        self.area = area
        self.initial_state = initial_state
        self.entity_category = entity_category

        self._manager: Optional[MQTTManagerProtocol] = None
        self._ha: Any = None
        self.state: Optional[str] = None
        self.attributes: dict = {}
        self._state_listeners: List[Callable[[str, str, str], Awaitable[None]]] = []

    def get_discovery_payload(self) -> MQTTDiscoveryPayload:
        raise NotImplementedError("Subclasses must implement get_discovery_payload()")

    def __str__(self) -> str:
        state_str = f", state={self.state}" if self.state is not None else ""
        return f"{self.__class__.__name__}(entity_id={self.entity_id}{state_str})"

    @property
    def unique_id(self) -> str:
        return self._unique_id or f"{self.namespace}_{self.identifier}"

    @property
    def ha_identifier(self) -> str:
        return f"{self.namespace}_{self.identifier}"
        
    @property
    def absolute_entity_picture(self) -> Optional[str]:
        return self.entity_picture

    @property
    def entity_id(self) -> str:
        return f"{self.component}.{self.ha_identifier}"

    @property
    def base_topic(self) -> str:
        return f"{self.discovery_prefix}/{self.component}/{self.namespace}/{self.identifier}"

    @property
    def config_topic(self) -> str:
        return f"{self.base_topic}/config"

    @property
    def json_attributes_topic(self) -> str:
        return f"{self.base_topic}/attributes"

    @property
    def state_topic(self) -> str:
        return f"{self.base_topic}/state"

    def bind_manager(self, manager: MQTTManagerProtocol):
        self._manager = manager

    async def get_state(self) -> Optional[str]:
        return self.state
        
    async def get_attributes(self) -> dict:
        """
        Returns the most recently known attributes from the MQTT broker.
        """
        return self.attributes

    def listen_state(self, callback: Callable[[str, str, str], Awaitable[None]]):
        self._state_listeners.append(callback)

    async def handle_state_sync(self, payload: str, retain: bool = False):
        """Fired automatically when the MQTT Manager receives a message on the state_topic."""
        if payload in ("unknown", "unavailable"):
            return

        old_state = self.state
        new_state = payload

        if old_state == new_state:
            self.logger.debug(f"Ignoring state change for {self.unique_id}: {old_state} -> {new_state} (no change)")
            return

        self.logger.debug(f"State change for {self.unique_id}: {old_state} -> {new_state}")
        self.state = new_state

        # Suppress callbacks for retained messages (the initial broker synchronization)
        if retain:
            return

        async def _notify_mqtt_listeners():
            if self._state_listeners:
                self.logger.debug(f"Calling {len(self._state_listeners)} state listeners for {self.unique_id}")
            for callback in self._state_listeners:
                try:
                    res = callback(self.unique_id, old_state, new_state)
                    if inspect.isawaitable(res):
                        await res
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Error in listener for {self.unique_id}: {e}", exc_info=True)

        await _notify_mqtt_listeners()

    async def _publish_state(self, state: str):
        if not self._manager:
            raise RuntimeError(f"Entity '{self.identifier}' must be registered before publishing state.")
        # Only publish to the broker. Let the state_topic subscription update local state.
        if self.state != state:
            self.logger.info(f"Publishing state change for {self.unique_id}: {self.state} -> {state}")
            await self._manager.set_state(self, state)

    async def _publish_attributes(self, payload: str):
        if not self._manager:
            raise RuntimeError(f"Entity '{self.identifier}' must be registered before publishing attributes.")
        await self._manager.set_attributes(self, payload)

    async def handle_attribute_sync(self, payload: str, retain: bool = False):
        """Fired automatically when the MQTT Manager receives a message on the json_attributes_topic."""
        try:
            new_attributes = json.loads(payload)
            if isinstance(new_attributes, dict):
                self.attributes = new_attributes
                self.logger.debug(f"Attribute sync for {self.unique_id}: {self.attributes}")
        except Exception as e:
            self.logger.error(f"Failed to parse attribute sync payload for {self.unique_id}: {e}")

from .select import MQTTSelect, MQTTSelectPayload
__all__ = ["MQTTEntity", "MQTTSelect", "MQTTSelectPayload"]
