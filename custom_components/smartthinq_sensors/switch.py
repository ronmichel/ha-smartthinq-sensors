import logging

from .wideq.device import (
    LABEL_BIT_OFF,
    LABEL_BIT_ON,
    DeviceType,
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
    STATE_UNAVAILABLE,
)

from .const import DOMAIN, LGE_DEVICES
from . import LGEDevice

try:
    from homeassistant.components.switch import SwitchEntity as SwitchDevice
except ImportError:
    from homeassistant.components.switch import SwitchDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_switch(hass, config_entry, async_add_entities, type_binary):
    """Set up theswitch platform."""
    lge_switches = [] 
    SWITCH_TYPES = [
        ("eco", ECOSwitch),
        ("ice", ICESwitch),
    ]
   
    entry_config = hass.data[DOMAIN]
    lge_devices = entry_config.get(LGE_DEVICES, [])
   
    refrigerator_switches = SWITCH_TYPES
   
    lge_switches.extend(
        [
            ECOSwitch(lge_device)
            for lge_device in lge_devices.get(DeviceType.REFRIGERATOR, [])
        ]
    )
    async_add_entities(lge_switches, True)
    
    
async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.info("Starting LGE ThinQ switches...")
    await async_setup_switch(hass, config_entry, async_add_entities, False)


class LGSwitch(CoordinatorEntity, SwitchDevice):


    def __init__(
            self,
            device: LGEDevice,
            switch_property,
            switch_function,
            is_binary,
    ):
        """Initialize the switch."""
        super().__init__(device.coordinator)
        self._api = device
        self._name_slug = device.name
        self._switch_property = switch_property
        self._switch_function = switch_function
        

    async def _set_switch(self, mode, **kwargs):
        _LOGGER.warning("Set the switch")
        if mode == 'ON':
            value = self._api._device.model_info.enum_value('EcoFriendly', LABEL_BIT_ON)
        elif mode == 'OFF':
            value = self._api._device.model_info.enum_value('EcoFriendly', LABEL_BIT_OFF)    
        else:
            return None
        self._api._device._set_control('REEF', value)


    @property
    def is_on(self) -> bool:
        """Return true if on."""
        return self.available and (self._api.state.eco_friendly_state == "on")

    async def async_turn_on(self, **kwargs):
        """Turn on switch."""
        await self._set_switch("ON", **kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn off switch."""
        await self._set_switch("OFF", **kwargs)

    @property
    def available(self) -> bool:
        """Return the availability of the switch."""
        return self._api.available

    @property
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return self._api.assumed_state

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._api.unique_id}-{self._switch_function}"

    @property
    def name(self) -> str:
        return f"{self._name_slug} {self._switch_function}"

    @property
    def device_class(self):
        """Return the device_class of the switch."""
        return "switch"

    @property
    def hidden(self):
        """Return whether the switch should be hidden from the UI."""
        return not self.available

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_info(self):
        """Return the device info."""
        return self._api.device_info

      
class ECOSwitch(LGSwitch):
    """Representation of a switch."""

    def __init__(self, device):
        """Initialize the Switch."""
        # Class info
        super().__init__(device, "eco", "eco", False)


class ICESwitch(LGSwitch):
    """Representation of a switch."""

    def __init__(self, client):
        """Initialize the Switch."""
        # Class info
        super().__init__(client, "ice", "ice", "ice")


