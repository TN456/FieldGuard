"""
animal_model.py - Virtual Livestock Animal with Realistic Health Metrics & GPS

Simulates:
- Heart Rate (beats per minute)
- Body Temperature (Celsius)
- Rumination (minutes spent chewing per hour)
- Location (GPS coordinates with circular geofencing)
- Battery Level (IoT collar battery %)
"""

import random 
import math
from datetime import datetime, timezone
from enum import Enum

# ===============================================
# CONFIGURATION & BIOLOGICAL BASELINES
# ===============================================

# 1 degree lat/lon is approx 111,000 meters
METERS_PER_DEGREE = 111000

# Baseline health metrics for different species
SPECIES_CONFIG = {
    "Cow"   : {"base_hr" : 65, "base_temp" : 38.5, "base_rum": 50},
    "Sheep" : {"base_hr" : 80, "base_temp" : 39.0, "base_rum": 45},
    "Goat"  : {"base_hr" : 85, "base_temp" : 39.5, "base_rum": 45},
}

class HealthState(Enum):
    HEALTHY = "HEALTHY"
    INCUBATING = "INCUBATING"  # Early Signs
    FEVER = "FEVER"            # Full Sickness
    RECOVERING = "RECOVERING"  # Returning to normal

class Location: 
    """
    Represents a circular geofenced pasture. 
    Uses basic trigonometry to constrain movement within a radius. 
    """
    def __init__(self, name, center_lat, center_lon, radius_meters):
        self.name = name
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_deg = radius_meters / METERS_PER_DEGREE

        # Start animal at the center
        self.current_lat = center_lat
        self.current_lon = center_lon 

    def move(self, mobility_factor = 1.0):
        """
        Simulate movement with circular boundary checks.
        Args:
            mobility_factor (float): 0.0 (immobile) to 1.0 (full speed)
        """
        if mobility_factor <= 0.05: return # Too sick to move

        # Random walk step (approx 2-5 meters)
        step_size = random.uniform(0.00002, 0.00005) * mobility_factor
        angle = random.uniform(0, 2 * math.pi)

        new_lat = self.current_lat + (step_size * math.cos(angle))
        new_lon = self.current_lon + (step_size * math.sin(angle))

        # Circular Geofence Check 
        # Calculate distance from center
        dist = math.sqrt((new_lat - self.center_lat) ** 2 + (new_lon - self.center_lon) ** 2)

        if dist > self.radius_deg:
            # If outisde, nudge them back towards the center
            angle_to_center = math.atan2(self.center_lon - new_lon, self.center_lat - new_lat)
            self.current_lat += step_size * math.cos(angle_to_center)
            self.current_lon += step_size * math.sin(angle_to_center)
        else:
            self.current_lat = new_lat
            self.current_lon = new_lon

    def get_coords(self):
        return round(self.current_lat, 6), round(self.current_lon, 6)
    
class Animal:
    def __init__(self, animal_id, species = "Cow", pasture = None):
        self.animal_id = animal_id
        self.species = species
        self.location = pasture or Location("Default", 35.0, -97.0, 500)

        # 1. Load Config
        # If species is not found, default to Cow
        self.config = SPECIES_CONFIG.get(species, SPECIES_CONFIG["Cow"])

        # 2. Set Initial Biological State
        self.state = HealthState.HEALTHY
        self.true_temp = self.config["base_temp"]
        self.true_hr = self.config["base_hr"]
        self.true_rumination = self.config["base_rum"]

        # IoT Device State
        self.battery = 100.0
        self.start_timer = 0

    def simulate_step(self):
        """
        Run one simulation cycle (e.g., represents 5 minutes of real time)
        """

        # 1. State Machine Logic
        self._update_biological_state()

        # 2. Update Metrics based on State
        self._update_metrics()

        # 3. Move Animal (Sick animals don't move)
        mobility = 1.0 if self.state == HealthState.HEALTHY else 0.1
        self.location.move(mobility)

        # 4. Drain Battery (Realistically slow drain)
        self.battery = max(0, self.battery - random.uniform(0.001, 0.005))

    def _update_biological_state(self):
        """
        Transitions between health states.
        """
        self.start_timer += 1

        if self.state == HealthState.HEALTHY:
            # Low chance to get sick
            if random.random() < 0.001:
                self.state = HealthState.INCUBATING
                self.start_timer = 0
            
        elif self.state == HealthState.INCUBATING:
            if self.start_timer > 20:
                # 50/50 chance to get worse or better
                if random.random() < 0.5:
                    self.state = HealthState.FEVER
                else:
                    self.state = HealthState.HEALTHY
                self.start_timer = 0
        
        elif self.state == HealthState.FEVER:
            if self.start_timer > 50:
                self.state = HealthState.RECOVERING
                self.start_timer = 0

        elif self.state == HealthState.RECOVERING:
            if self.start_timer > 30:
                self.state = HealthState.HEALTHY
                self.start_timer = 0

    def _update_metrics(self):
        """
        Adjusts metrics based on state and SPECIES CONFIG.
        Uses 'drift' so values change gradually
        """

        # Start with the species baseline
        target_temp = self.config["base_temp"]
        target_hr = self.config["base_hr"]
        target_rum = self.config["base_rum"]

        # Apply Sickness Modifiers (Relative Deltas)
        if self.state == HealthState.INCUBATING:
            target_rum -= 20 # Rumination drops first
            target_hr += 10 # HR goes up slightly

        elif self.state == HealthState.FEVER:
            target_temp += 2.0 # Fever spike 
            target_hr += 30 # HR spikes 
            target_rum = 5 # Stops eating almost entirely

        elif self.state == HealthState.RECOVERING:
            target_temp += 0.5
            target_hr += 5
            target_rum -= 15

        # Move "True" values towards Target values (Drifting)
        self.true_temp += (target_temp - self.true_temp) * 0.1 + random.uniform(-0.05, 0.05)
        self.true_hr += (target_hr - self.true_hr) * 0.1 + random.uniform(-1, 1)
        self.true_rumination += (target_rum - self.true_rumination) * 0.1 + random.uniform(-2, 2)

    def generate_sensor_reading(self):
        """
        Returns the data packet 
        """

        lat, lon = self.location.get_coords()

        # Sensor Noise: The device
        sensor_temp = self.true_temp + random.uniform(-0.1, 0.1)
        sensor_hr = int(self.true_hr + random.uniform(-2, 2))

        return {
            "animal_id": self.animal_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": {"lat" : lat, "lon" : lon},
            "metrics": {
                "temperature": round(sensor_temp, 2),
                "heart_rate": sensor_hr,
                "rumination_index": int(max(0, self.true_rumination)),
                "battery_level": round(self.battery, 2)
            }, 
            "_debug_state": self.state.value
        }
