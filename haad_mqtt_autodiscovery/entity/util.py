STATE_ON = 'on'
STATE_OFF = 'off'


def parse_to_mqtt_on_off_state(value: str | bool) -> str:
    """Parse a value to MQTT ON/OFF state."""
    if isinstance(value, bool):
        return STATE_ON.upper() if value else STATE_OFF.upper()
    elif isinstance(value, str):
        value_upper = value.strip().upper()
        if value_upper in [STATE_ON.upper(), "TRUE", "1"]:
            return STATE_ON.upper()
        elif value_upper in [STATE_OFF.upper(), "FALSE", "0"]:
            return STATE_OFF.upper()
    return STATE_OFF.upper()  # Default to OFF if unrecognized
