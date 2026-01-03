from exceptions import IDNotFound, DuplicateID, WeightExceeded, DroneUnavailable, NoDroneAvailable,ParcelAlreadyDelivered, InvalidTime
from models.parcel import Parcel
from models.mission import Mission
from faker import Faker
import random
from datetime import datetime
import threading
import time
from exceptions import ParcelAlreadyAssigned, ParcelAssigned, ParcelDelivered, NotEnoughBattery

class LogisticService:
    def __init__(self, parcels_repo, missions_repo, drone_repo, weather_service, ai):
        self._parcels_repo = parcels_repo
        self._missions_repo = missions_repo
        self._drone_repo = drone_repo
        self._weather_service = weather_service
        self._ai = ai
        if len(self._parcels_repo.get_data()) == 0:
            self.__generate_parcels()

    def __generate_parcels(self):
        possible_priority = ["HIGH", "STANDARD"]
        possible_status = ["DELIVERED", "PENDING"]
        fake = Faker()
        for i in range(1, 21):
            parcel_recipient_name = fake.name().replace(',', ' ')
            parcel_delivery_address = fake.address().replace('\n', '-').replace(',', ';')
            weight = round(random.uniform(0.5, 10.0), 2)  
            distance = random.randint(10,100)
            priority = random.choice(possible_priority)
            status = random.choice(possible_status)
            parcel = Parcel(i, parcel_recipient_name, parcel_delivery_address, weight, priority,status, distance)
            self._parcels_repo.add_item(parcel)

    def _start_background_scheduler(self):
        thread = threading.Thread(target = self._scheduled_missions_deploy, daemon=True)
        thread.start()

    def _scheduled_missions_deploy(self):
        while True:
            try:
                missions = self._missions_repo.get_data()
                filtered_missions = [mission for mission in missions if mission.get_status() == "SCHEDULED"]
                for mission in filtered_missions:
                    mission_start_time = datetime.strptime(mission.get_start_time(), "%Y-%m-%d %H:%M:%S")
                    if mission_start_time <= datetime.now():
                        mission.set_status("EN_ROUTE")
                        self._missions_repo.update(mission)
                        drone = self._drone_repo.search_by_id(mission.get_drone_id())
                        if drone:
                            drone.set_status("IN_FLIGHT")
                            self._drone_repo.update(drone)
            except Exception as e:
                print(f"SCHEDULER ERROR {e}")
            time.sleep(10)

                
    def search_by_id(self, parcel_id : int):
        return self._parcels_repo.search_by_id(parcel_id)
     
    def add_parcel(self, parcel_id : int, recipient_name : str, delivery_address : str, weight : float, 
                   priority : str,distance : float):
        duplicate_parcel = self._parcels_repo.search_by_id(parcel_id)
        if duplicate_parcel:
            raise DuplicateID(parcel_id, "Parcel")
        
        if weight <= 0:
            raise ValueError("Parcel Weight must be positive")
        
        status = "PENDING"
        if distance <= 0:
            raise ValueError("Parcel distance must be greater than 0")
        
        parcel = Parcel(parcel_id, recipient_name, delivery_address, weight, priority,status, distance)
        self._parcels_repo.add_item(parcel)

    def remove_parcel(self, parcel_id : int):
        exist_parcel = self._parcels_repo.search_by_id(parcel_id)
        if not exist_parcel:
            raise IDNotFound(parcel_id,"Parcel")
        
        if exist_parcel.get_status() == "DELIVERED":
            raise ParcelDelivered(parcel_id)
        
        if exist_parcel.get_status() == "ASSIGNED":
            raise ParcelAssigned(parcel_id)
        
        self._parcels_repo.remove_item(parcel_id)

    def update_parcel(self, parcel_id : int, recipient_name : str, delivery_address : str, 
                      weight : float, priority : str,status : str, distance : float):
        exist_parcel = self._parcels_repo.search_by_id(parcel_id)
        if not exist_parcel:
            raise IDNotFound(parcel_id,"Parcel")
        
        if exist_parcel.get_status() == "DELIVERED":
            raise ParcelDelivered(parcel_id)
        
        if exist_parcel.get_status() == "ASSIGNED":
            raise ParcelAssigned(parcel_id)
        
        if weight <= 0:
            raise ValueError("Parcel Weight must be positive")
        
        if distance <= 0:
            raise ValueError("Parcel distance must be greater than 0")
        
        new_parcel = Parcel(parcel_id, recipient_name, delivery_address, weight, priority,status, distance)
        self._parcels_repo.update(new_parcel)

    def get_parcels(self) -> list:
        return self._parcels_repo.get_data()
    
    def get_delivered_parcels(self) -> list:
        parcels = self._parcels_repo.get_data()
        delivered_parcels = [parcel for parcel in parcels if parcel.get_status() == "DELIVERED"]
        return delivered_parcels
    
    def search_parcels(self, query) -> list:
        parcels = self._parcels_repo.get_data()
        filtered_drones = [parcel for parcel in parcels if parcel.fuzzy_match(query)]
        return filtered_drones
    
    def assign_a_mission_manually(self, mission_id : int,drone_id : int, parcel_id : int, start_time : str):
        drone = self._drone_repo.search_by_id(drone_id)
        if not drone:
            raise IDNotFound(drone_id, "Drone")
        parcel = self._parcels_repo.search_by_id(parcel_id)
        if not parcel:
            raise IDNotFound(parcel_id, "Parcel")
        if parcel.get_status() == "DELIVERED":
            raise ParcelAlreadyDelivered(parcel.get_id())
        if parcel.get_status() == "ASSIGNED":
            raise ParcelAlreadyAssigned(parcel.get_id())
        if parcel.get_weight() > drone.get_max_payload():
            raise WeightExceeded(drone.get_max_payload(), parcel.get_weight())
        if drone.get_status() != "IDLE":
            raise DroneUnavailable(drone.get_id())
        
        scheduled_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if scheduled_dt > datetime.now():
            status = "SCHEDULED"
            new_drone_status = "FLIGHT SCHEDULED"
        elif scheduled_dt == datetime.now():
            status = "EN_ROUTE"
            new_drone_status = "IN_FLIGHT"
        else:
            raise InvalidTime(start_time)
        
        required_battery = self._calculate_necessary_battery_level(parcel.get_distance(), scheduled_dt, parcel.get_weight(), 
                                                                   drone.get_max_payload())
        if  required_battery > drone.get_battery_level():
            raise NotEnoughBattery(drone.get_id())
        mission = Mission(mission_id, drone_id, parcel_id, start_time, status)
        parcel.set_status("ASSIGNED")
        self._parcels_repo.update(parcel)
        self._missions_repo.add_item(mission)
        drone.set_status(new_drone_status)
        self._drone_repo.update(drone)

    def _generate_mission_id(self) -> int:
        missions = self._missions_repo.get_data()
        existing_ids = {mission.get_id() for mission in missions}
        id = 1
        while id in existing_ids:
            id += 1
        return id
    
    def assign_a_mission_automatically(self, parcel_id : int, start_time : str) -> int:
        parcel = self._parcels_repo.search_by_id(parcel_id)
        if not parcel:
            raise IDNotFound(parcel_id, "Parcel")
        if parcel.get_status() == "DELIVERED":
            raise ParcelAlreadyDelivered(parcel.get_id())
        if parcel.get_status() == "ASSIGNED":
            raise ParcelAlreadyAssigned(parcel.get_id())
        scheduled_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if scheduled_dt > datetime.now():
            status = "SCHEDULED"
            new_drone_status = "FLIGHT SCHEDULED"
        elif scheduled_dt == datetime.now():
            status = "EN_ROUTE"
            new_drone_status = "IN_FLIGHT"
        else:
            raise InvalidTime(start_time)
        best_drone = self._find_best_drone(parcel, scheduled_dt)
        if not best_drone:
            raise NoDroneAvailable(parcel_id)
        mission_id = self._generate_mission_id()
        parcel.set_status("ASSIGNED")
        self._parcels_repo.update(parcel)
        mission = Mission(mission_id, best_drone._id, parcel_id, start_time, status)
        self._missions_repo.add_item(mission)
        best_drone.set_status(new_drone_status)
        self._drone_repo.update(best_drone)
        return best_drone.get_id()

    def modify_mission_status(self, mission_id : int, status : str):
        mission = self._missions_repo.search_by_id(mission_id)
        if not mission:
            raise IDNotFound(mission_id, "Mission")
        mission.set_status(status)
        self._missions_repo.update(mission)
        drone = self._drone_repo.search_by_id(mission.get_drone_id())
        parcel = self._parcels_repo.search_by_id(mission.get_parcel_id())
        if status == "FAILED":
            drone_status = "MAINTENANCE"
            parcel_status = "PENDING"
        else:
            drone_status = "IDLE"
            parcel_status = "DELIVERED"
        start_time = mission.get_start_time()
        scheduled_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        battery_consumed = self._calculate_necessary_battery_level(parcel.get_distance(), scheduled_dt, parcel.get_weight())
        parcel.set_status(parcel_status)
        drone.update_battery(battery_consumed)
        drone.set_status(drone_status)
        self._drone_repo.update(drone)

    def get_missions(self) -> list:
        return self._missions_repo.get_data()
    
    def _calculate_necessary_battery_level(self, parcel_distance : float, scheduled_dt, 
                                           parcel_weight : float, drone_max_payload : float) -> int:
        weather = self._weather_service.get_current_weather(scheduled_dt)
        drainage = self._ai.predict_drain_multiplier(weather['wind_speed'], weather['temperature'], weather['is_raining'])
        distance_in_meters = parcel_distance * 1000
        load_factor = drone_max_payload / parcel_weight
        required_battery_to_comeback = distance_in_meters / 600
        required_battery_to_deliver = required_battery_to_comeback * (1 + load_factor)
        required_battery = (required_battery_to_comeback + required_battery_to_deliver) * drainage + 5
        return required_battery
    
    def _find_best_drone(self, parcel : Parcel, scheduled_dt : str):
        mini = float('inf')
        best_drone = None
        drones = self._drone_repo.get_data()
        for drone in drones:
            required_battery = self._calculate_necessary_battery_level(parcel.get_distance(), scheduled_dt, parcel.get_weight(),
                                                                       drone.get_max_payload())
            if drone.get_max_payload() >= parcel.get_weight() and drone.get_max_payload() - parcel.get_weight() < mini \
            and drone.get_status() == "IDLE" and drone.get_battery_level() >= required_battery:
                mini = drone.get_max_payload() - parcel.get_weight()
                best_drone = drone
        return best_drone
        


