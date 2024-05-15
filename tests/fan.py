import pytest
from unittest.mock import AsyncMock, patch
from custom_components.comfoconnect import ComfoConnectFan
from custom_components.comfoconnect.const import DOMAIN, SIGNAL_COMFOCONNECT_UPDATE_RECEIVED
from aiocomfoconnect.const import VentilationMode, VentilationSpeed
from custom_components.comfoconnect.sensors import SENSOR_FAN_SPEED_MODE, SENSOR_OPERATING_MODE

# Fixtures and test setup

@pytest.fixture
def comfoconnect_bridge():
    """Generate a mock ComfoConnectBridge."""
    ccb = AsyncMock()
    ccb.uuid = 'mock-uuid'
    return ccb

@pytest.fixture
def fan(comfoconnect_bridge, hass):
    """Create a mock ComfoConnectFan entity."""
    fan = ComfoConnectFan(ccb=comfoconnect_bridge, config_entry=AsyncMock())
    fan.hass = hass
    return fan

# Test cases

@pytest.mark.asyncio
async def test_initialization(fan):
     """Test initialization of the fan entity."""
     assert fan.unique_id == 'mock-uuid'
     assert isinstance(fan, ComfoConnectFan)

@pytest.mark.asyncio
async def test_fan_turn_on_defaults(hass, fan):
    """Test turning on the fan with default values."""
    with patch.object(fan, 'async_set_percentage') as mock_set_percentage:
        await fan.async_turn_on()
        mock_set_percentage.assert_called_once_with(1)  # Default turn on to low

@pytest.mark.asyncio
async def test_fan_turn_on_with_percentage(hass, fan):
    """Test turning on the fan with a specific percentage."""
    test_percentage = 50
    with patch.object(fan, 'async_set_percentage') as mock_set_percentage:
        await fan.async_turn_on(percentage=test_percentage)
        mock_set_percentage.assert_called_once_with(test_percentage)

@pytest.mark.asyncio
async def test_fan_turn_off(hass, fan):
    """Test turning off the fan."""
    with patch.object(fan, 'async_set_percentage') as mock_set_percentage:
        await fan.async_turn_off()
        mock_set_percentage.assert_called_once_with(0)  # Off should set to away

@pytest.mark.asyncio
async def test_preset_mode(hass, fan):
    """Test setting preset modes on the fan."""
    with patch.object(fan, 'async_set_preset_mode') as mock_set_preset_mode:
        await fan.async_turn_on(preset_mode=VentilationMode.AUTO)
        mock_set_preset_mode.assert_called_once_with(VentilationMode.AUTO)

@pytest.mark.asyncio
async def test_invalid_preset_mode(hass, fan):
    """Test setting invalid preset mode on the fan."""
    with pytest.raises(ValueError):
        await fan.async_set_preset_mode("InvalidPresetMode")

@pytest.mark.asyncio
async def test_set_valid_percentage(hass, fan):
    """Test setting a valid percentage for the fan speed."""
    valid_percentage = 50  # Assuming 50% is a valid speed
    with patch.object(fan._ccb, 'set_speed') as mock_set_speed:
        await fan.async_set_percentage(valid_percentage)
        mock_set_speed.assert_called_once()

@pytest.mark.asyncio
async def test_set_invalid_percentage(hass, fan):
    """Test setting an invalid percentage for the fan speed."""
    invalid_percentage = 999  # Assuming 999% is invalid
    with pytest.raises(ValueError):
        await fan.async_set_percentage(invalid_percentage)

@pytest.mark.asyncio
async def test_handle_speed_update(hass, fan):
    """Test handling updates for the fan speed."""
    # Simulate a speed update signal for medium speed
    fan._handle_speed_update(FAN_SPEED_MAPPING[2])  # Medium speed
    await hass.async_block_till_done()
    assert fan.percentage == 67  # Or the concrete percentage for medium speed (2 out of 3)

@pytest.mark.asyncio
async def test_handle_mode_update(hass, fan):
    """Test handling updates for the operating mode."""
    # Test updating to AUTO mode
    fan._handle_mode_update(-1)  # AUTO mode
    await hass.async_block_till_done()
    assert fan.preset_mode == VentilationMode.AUTO
    
    # Test updating to MANUAL mode
    fan._handle_mode_update(0)  # MANUAL mode
    await hass.async_block_till_done()
    assert fan.preset_mode == VentilationMode.MANUAL
