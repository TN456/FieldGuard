"""
simulator.py - Livestock Health Data Simulator
"""

import json
import time
import random
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Import model components
from animal_model import Animal, Location, HealthState

class LivestockSimulator:
    """Simulates a herd of livestock and sends data to Kafka."""

    def __init__(self, num_animals = 50, kafka_broker = "localhost:9092"):
        self.num_animals = num_animals
        self.kafka_broker = kafka_broker
        self.herd = []
        self.message_count = 0

        # Create Kafka producer
        try:
            self.producer = KafkaProducer(
                bootstrap_servers = [kafka_broker],
                value_serializer = lambda v: json.dumps(v).encode("utf-8"),
                acks = "all",
                retries = 3,
            )
            print(f"Connected to Kafka broker at {kafka_broker}")
        except Exception as e:
            print(f" Kafka Connection Failed: {e}")
            print(" (Running in Console-Only Mode. Data will print but not send.)")
            self.producer = None

        self._create_herd()

    def _create_herd(self):
        """Create a herd with random species and realistic locations."""

        # 1. Define the physical locations
        pasture_a = Location("Pasture A", 35.0000, -97.0000, 500)
        pasture_b = Location("Pasture B", 35.0100, -97.0100, 500)
        barn_1    = Location("Barn 1",    35.0020, -97.0020, 50)

        available_locs = [pasture_a, pasture_b, barn_1]

        # Define Species Mix (60% Cows, 30% Sheep, 10% Goats)
        species_list = ["Cow", "Sheep", "Goat"]
        weights = [0.6, 0.3, 0.1]

        for i in range(1, self.num_animals + 1):
            # Pick random species and location 
            chosen_species = random.choices(species_list, weights = weights, k = 1)[0]
            loc = random.choice(available_locs)

            # Create Animal
            animal = Animal(
                animal_id = i, 
                species = chosen_species,
                pasture = loc
            )
            self.herd.append(animal)

        print(f" Created herd of {self.num_animals} animals")
        print(f" -Cows: {sum(1 for a in self.herd if a.species == 'Cow')}")
        print(f" -Sheep: {sum(1 for a in self.herd if a.species == 'Sheep')}")
        print(f" -Goats: {sum(1 for a in self.herd if a.species == 'Goat')}")

    def run(self, duration_seconds = None, interval_seconds = 2):
        print(f"\n Starting simulator (sending every {interval_seconds}s)....\n")
        start_time = time.time()
        iteration = 0

        try:
            while True:
                iteration += 1

                # 1. Update every animal
                for animal in self.herd:
                    animal.simulate_step()

                # 2. Calculate Herd Stats for Console
                # Note: We check against the Enum (state != HEALTHY)
                sick_count = sum(1 for a in self.herd if a.state != HealthState.HEALTHY)
                low_batt = sum(1 for a in self.herd if a.battery < 20)

                print(
                    f"[{iteration}] Sending {self.num_animals} messages"
                    f"| Sick/Incubating: {sick_count} | Low Battery: {low_batt}"
                )
                # 3. Send to Kafka 
                for animal in self.herd:
                    self._send_to_kafka(animal)

                # Check duration
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    print(f"\n Duration limit reached. Stopping.")
                    break

                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print(f"\n Simulator stopped by user,.")

    def _send_to_kafka(self, animal):
        # Generate the realistic JSON data
        data = animal.generate_sensor_reading()

        # If the animal is sick, print a specific alert to console
        if animal.state != HealthState.HEALTHY:
            print(f" ALERT: {animal.species} #{animal.animal_id} is {animal.state.value} "
                  f"(Temp: {data['metrics']['temperature']}°C)")
            
        if self.producer:
            try:
                self.producer.send("animal-health-stream", value = data)
                self.message_count += 1
            except KafkaError as e:
                print(f" Kafka error: {e}")

    def stop(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("\n Kafka connection closed")
    
if __name__ == "__main__":
    # Create simulator 
    sim = LivestockSimulator(num_animals = 50, kafka_broker = "localhost:9092")

    # Run forever (Ctrl + C to stop)
    try:
        sim.run(duration_seconds = 1200, interval_seconds = 2)
    except Exception as e:
        print(f" Error {e}")
    finally:
        sim.stop() 