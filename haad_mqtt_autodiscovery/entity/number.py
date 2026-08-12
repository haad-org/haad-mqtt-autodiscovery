import asyncio
from dataclasses import dataclass
from typing import Optional

from haad_mqtt_autodiscovery import MQTTDiscoveryPayload, MQTTDevice, EntityCategory
from haad_mqtt_autodiscovery.entity import MQTTEntity


@dataclass
class MQTTNumberPayload(MQTTDiscoveryPayload):
    """Schema specific to MQTT Numbers (Readable/Writable)."""
    command_topic: str = ""
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    mode: Optional[str] = None  # e.g., 'auto', 'box', 'slider'
    unit_of_measurement: Optional[str] = None


class MQTTNumber(MQTTEntity):
    def __init__(
        self,
        namespace: str,
        identifier: str,
        name: str,
        device: MQTTDevice = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        step: Optional[float] = None,
        mode: Optional[str] = None,
        unit_of_measurement: Optional[str] = None,
        icon: Optional[str] = None,
        entity_picture: Optional[str] = None,
        unique_id: Optional[str] = None, area: Optional[str] = None,
        initial_state: Optional[float] = None,
        entity_category: Optional[EntityCategory] = None
    ):
        if initial_state is not None:
            if min_val is not None and initial_state < min_val:
                raise ValueError(f"initial_state {initial_state} must be >= min_val {min_val} for {identifier}")
            if max_val is not None and initial_state > max_val:
                raise ValueError(f"initial_state {initial_state} must be <= max_val {max_val} for {identifier}")
            if step is not None:
                import math
                base = min_val if min_val is not None else 0.0
                remainder = (initial_state - base) % step
                if not (math.isclose(remainder, 0, abs_tol=1e-5) or math.isclose(remainder, step, abs_tol=1e-5)):
                    raise ValueError(f"initial_state {initial_state} does not align with step {step} for {identifier}")

        initial_state_str = str(initial_state) if initial_state is not None else None
        super().__init__(
            namespace, identifier, name, component="number",
            icon=icon, entity_picture=entity_picture, device=device, unique_id=unique_id, area=area,
            initial_state=initial_state_str,
            entity_category=entity_category
        )
        self.min = min_val
        self.max = max_val
        self.step = step
        self.mode = mode
        self.unit_of_measurement = unit_of_measurement

    @property
    def command_topic(self) -> str:
        return f"{self.base_topic}/set"

    def get_discovery_payload(self) -> MQTTNumberPayload:
        return MQTTNumberPayload(
            name=self.name,
            default_entity_id=self.entity_id,
            unique_id=self.unique_id,
            state_topic=self.state_topic,
            command_topic=self.command_topic,
            json_attributes_topic=self.json_attributes_topic if self.entity_picture else None,
            device=self.device,
            icon=self.icon,
            entity_picture=self.absolute_entity_picture,
            suggested_area=self.area,
            entity_category=self.entity_category,
            min=self.min,
            max=self.max,
            step=self.step,
            mode=self.mode,
            unit_of_measurement=self.unit_of_measurement
        )

    async def handle_command(self, payload: str):
        """Fired when HA sends a number command. Echo it to verify."""
        await self._publish_state(payload)

    async def get_state(self, default: float = None) -> Optional[float]:  # type: ignore[override]
        state = self.state
        if state is None:
            return default
        return float(state)

    def _format_value(self, value: float) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def _format_payload(self, payload: str) -> str:
        try:
            return self._format_value(float(payload))
        except ValueError:
            return payload

    async def set_state(self, value: float):
        await self._publish_state(self._format_value(value))

    async def handle_state_sync(self, payload: str, retain: bool = False):
        formatted = self._format_payload(payload)

        if formatted != payload:
            payload = formatted
            if retain:
                asyncio.create_task(self._publish_state(formatted))

        await super().handle_state_sync(payload, retain)

    def _numeric_initial_state(self) -> float:
        if self.initial_state is not None:
            return float(self.initial_state)
        return self.min if self.min is not None else 0.0

    async def increment(self):
        """Increment the number by step."""
        step = self.step if self.step is not None else 1.0
        current = await self.get_state(self._numeric_initial_state())
        new_val = current + step
        if self.max is not None and new_val > self.max:
            new_val = self.max
        await self.set_state(new_val)

    async def decrement(self):
        """Decrement the number by step."""
        step = self.step if self.step is not None else 1.0
        current = await self.get_state(self._numeric_initial_state())
        new_val = current - step
        if self.min is not None and new_val < self.min:
            new_val = self.min
        await self.set_state(new_val)

    async def reset(self):
        """Reset the number to its initial state or minimum value."""
        await self.set_state(self._numeric_initial_state())
