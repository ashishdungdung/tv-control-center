"""Media Player platform for TV Control Center Home Assistant Integration."""
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "tv_control_center"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up media player entity."""
    config = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TvMediaPlayer(config)])

class TvMediaPlayer(MediaPlayerEntity):
    """TV Control Center Media Player Entity."""

    def __init__(self, config):
        self._host = config.get("host", "192.168.2.122")
        self._name = config.get("name", f"Smart TV ({self._host})")
        self._attr_unique_id = f"tv_media_player_{self._host}"
        self._state = MediaPlayerState.ON
        self._attr_supported_features = (
            MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_turn_on(self):
        """Turn the TV on."""
        self._state = MediaPlayerState.ON

    async def async_turn_off(self):
        """Turn the TV off."""
        self._state = MediaPlayerState.OFF
