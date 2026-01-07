"""Sensor platform for Smart Meter Burgenland integration."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smart Meter Burgenland sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        SmartMeterSensor(
            coordinator,
            entry,
            "consumption_today",
            "Verbrauch Heute",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
            "mdi:flash",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "consumption_yesterday",
            "Verbrauch Gestern",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL,
            "mdi:flash",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "consumption_month",
            "Verbrauch Dieser Monat",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
            "mdi:calendar-month",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "consumption_last_month",
            "Verbrauch Letzter Monat",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL,
            "mdi:calendar-month-outline",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "avg_daily",
            "Durchschnitt pro Tag",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.MEASUREMENT,
            "mdi:chart-line",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "cost_today",
            "Kosten Heute",
            CURRENCY_EURO,
            SensorDeviceClass.MONETARY,
            SensorStateClass.TOTAL_INCREASING,
            "mdi:currency-eur",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "cost_yesterday",
            "Kosten Gestern",
            CURRENCY_EURO,
            SensorDeviceClass.MONETARY,
            SensorStateClass.TOTAL,
            "mdi:currency-eur",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "cost_month",
            "Kosten Dieser Monat",
            CURRENCY_EURO,
            SensorDeviceClass.MONETARY,
            SensorStateClass.TOTAL_INCREASING,
            "mdi:cash",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "cost_last_month",
            "Kosten Letzter Monat",
            CURRENCY_EURO,
            SensorDeviceClass.MONETARY,
            SensorStateClass.TOTAL,
            "mdi:cash",
        ),
        SmartMeterSensor(
            coordinator,
            entry,
            "last_reading",
            "Letzter Messwert",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.MEASUREMENT,
            "mdi:gauge",
        ),
    ]

    async_add_entities(sensors)


class SmartMeterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Smart Meter Burgenland sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        name: str,
        unit: str,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Smart Meter {name}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Smart Meter Burgenland",
            "manufacturer": "Netz Burgenland",
            "model": "Smart Meter",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self.coordinator.data is None:
            return {}
        
        attrs = {}
        
        # Füge Zeitstempel der letzten Messung hinzu
        if self._sensor_type == "last_reading" and "last_reading_time" in self.coordinator.data:
            attrs["last_reading_time"] = self.coordinator.data["last_reading_time"]
        
        # Füge Preis pro kWh zu Verbrauchssensoren hinzu
        if "consumption" in self._sensor_type:
            attrs["price_per_kwh"] = self.coordinator.data.get("price_per_kwh", 0.15)
        
        # Füge Update-Zeit hinzu
        attrs["last_update"] = datetime.now().isoformat()
        
        return attrs
