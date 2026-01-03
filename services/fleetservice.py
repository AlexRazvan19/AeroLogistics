from models.drone import Drone
from exceptions import IDNotFound
from exceptions import DuplicateID, DroneInFlight, DroneFlightAssigned
from faker import Faker
import random
import threading
import time

class DroneService:
    def __init__(self, repository):
        self._repository = repository
        if len(self._repository.get_data()) == 0:
            self.__generate_drones()

    def __generate_drones(self):
        statuses = ['IDLE', 'MAINTENANCE']
        models = ['Swift-X1', 'HeavyLift-V2', 'Interceptor-9']
        fake = Faker()
        for i in range(1, 21):
            drone_serial = fake.bothify(text='DRN-####-????') 
            drone_model = random.choice(models)
            drone_status = random.choice(statuses)
            drone_battery = random.randint(0,100)
            payload = round(random.uniform(0.5, 10.0), 2)
            drone = Drone(i, drone_serial, drone_model, payload, drone_status, drone_battery)
            self._repository.add_item(drone)

    def _charge_drone(self):
        charge = threading.Thread(target = self._drone_charger, daemon=True)
        charge.start()

    def _drone_charger(self):
        while True:
            try:
                drones = self._repository.get_data()
                for drone in drones:
                    if drone.get_status() == "IDLE":
                        if drone.get_battery_level() < 80:
                            drone.charge_battery(3)
                        elif drone.get_battery_level() < 100:
                            drone.charge_battery(1)
                    self._repository.update(drone)
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error trying to charge the drones {e}")
            time.sleep(10)


    def search_by_id(self, drone_id : int):
        return self._repository.search_by_id(drone_id)

    def add_drone(self, id : int, serial_number : str, model_type : str, payload : float, status : str, battery_level : int):
        drone = self._repository.search_by_id(id)
        if drone:
            raise DuplicateID(id, "Drone")
        if payload <= 0:
            raise ValueError("Drone PayLoad must be greater than 0")
        if battery_level < 0:
            raise ValueError("Drone Battery Level must be positive")
        if battery_level > 100:
            raise ValueError("Maximum battery level is 100")
        drone = Drone(id, serial_number, model_type, payload, status, battery_level)
        self._repository.add_item(drone)

    def remove_drone(self, id : int):
        drone = self._repository.search_by_id(id)
        if not drone:
            raise IDNotFound(id, "Drone")
        if drone.get_status() == "IN_FLIGHT":
            raise DroneInFlight(id)
        if drone.get_status() == "ASSIGNED":
            raise DroneFlightAssigned(id)
        self._repository.remove_item(id)

    def update_drone(self, id : int, new_serial_number : str, new_model_type : str, new_payload : float, 
                     new_status : str, battery_level : int):
        drone = self._repository.search_by_id(id)
        if not drone:
            raise IDNotFound(id, "Drone")
        if drone.get_status() == "IN_FLIGHT":
            raise DroneInFlight(id)
        if drone.get_status() == "ASSIGNED":
            raise DroneFlightAssigned(id)
        if new_payload <= 0:
            raise ValueError("Drone PayLoad must be greater than 0")
        if battery_level < 0:
            raise ValueError("Drone Battery Level must be positive")
        if battery_level > 100:
            raise ValueError("Maximum battery level is 100")
        new_drone = Drone(id, new_serial_number, new_model_type, new_payload, new_status, battery_level)
        self._repository.update(new_drone)

    def list_the_drones(self) -> list:
        return self._repository.get_data()
    
    def search_drone(self, query) -> list:
        drones = self._repository.get_data()
        filtered_drones = [drone for drone in drones if drone.fuzzy_match(query)]
        return filtered_drones

    
