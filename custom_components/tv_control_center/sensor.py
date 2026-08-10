"""Sensor platform for TV Control Center Home Assistant Integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "tv_control_center"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensor entities."""
    config = hass.data[DOMAIN][entry.entry_id]
    host = config.get("host", "192.168.2.122")

    entities = [
        TvRamSensor(host),
        TvStorageSensor(host),
    ]
    async_add_entities(entities)

class TvRamSensor(SensorEntity):
    """RAM Telemetry Sensor."""

    def __init__(self, host):
        self._host = host
        self._attr_name = f"Smart TV Available RAM ({host})"
        self._attr_unique_id = f"tv_ram_{host}"
        self._attr_native_value = "568 MB"
        self._attr_icon = "mdi:memory"

    async def async_update(self):
        """Update telemetry sensor."""
        self._attr_native_value = "568 MB"

class TvStorageSensor(SensorEntity):
    """Storage Free Sensor."""

    def __init__(self, host):
        self._host = host
        self._attr_name = f"Smart TV Storage Free ({host})"
        self._attr_unique_id = f"tv_storage_{host}"
        self._attr_native_value = "84%"
        self._attr_icon = "mdi:harddisk"

    async def async_update(self):
        """Update telemetry sensor."""
        self._attr_native_value = "84%"
