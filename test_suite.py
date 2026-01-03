import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from services.logistics_service import LogisticService
from services.fleetservice import DroneService
from models.drone import Drone
from models.parcel import Parcel
from exceptions import NoDroneAvailable, ParcelAlreadyAssigned , ParcelAlreadyDelivered, WeightExceeded, DroneUnavailable, InvalidTime

class TestDroneSystem(unittest.TestCase):

    def setUp(self):
        """
        Runs BEFORE every single test.
        Sets up fresh Mocks (fake databases) so tests don't mess up real data.
        """
        self.mock_drone_repo = MagicMock()
        self.mock_parcel_repo = MagicMock()
        self.mock_mission_repo = MagicMock()
        
        self.mock_parcel_repo.get_data.return_value = []
        self.mock_drone_repo.get_data.return_value = []
        self.mock_mission_repo.get_data.return_value = []

        self.mock_weather_service = MagicMock()
        self.mock_ai = MagicMock()

        self.logistic_service = LogisticService(
            self.mock_parcel_repo,
            self.mock_mission_repo,
            self.mock_drone_repo,
            self.mock_weather_service,
            self.mock_ai
        )


        self.drone_service = DroneService(self.mock_drone_repo)
        self.mock_drone_repo.add_item.reset_mock()
        self.mock_parcel_repo.add_item.reset_mock()

        self.good_drone = Drone(1, "SN-123", "Swift-X1", 10.0, "IDLE", 100)
        self.standard_parcel = Parcel(10, "John Doe", "123 St", 2.0, "STANDARD", "PENDING", 5)

    def test_assign_mission_success(self):
        """
        Verifies that a drone is successfully assigned when conditions are perfect.
        """
        print("Test: Successful Mission Assignment")

        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        self.mock_parcel_repo.search_by_id.return_value = self.standard_parcel
        self.mock_drone_repo.get_data.return_value = [self.good_drone]
        
        self.mock_weather_service.get_current_weather.return_value = {
            "wind_speed": 5, "temperature": 20, "is_raining": 0
        }
        self.mock_ai.predict_drain_multiplier.return_value = 1.0 

        assigned_drone_id = self.logistic_service.assign_a_mission_automatically(10, start_time)

        self.assertEqual(assigned_drone_id, 1, "Should have selected Drone #1")
        self.assertEqual(self.standard_parcel.get_status(), "ASSIGNED", "Parcel status should update")
        self.assertEqual(self.good_drone.get_status(), "FLIGHT SCHEDULED", "Drone status should update")
        
        self.mock_mission_repo.add_item.assert_called_once()
        print("Mission assigned successfully.")

    def test_assign_mission_rejection_long_distance(self):
        """
        Verifies that the 66km London trip is rejected due to battery physics.
        """
        print("Test: Long Distance Rejection (Physics Check)")

        london_parcel = Parcel(99, "London User", "UK", 3.91, "HIGH", "PENDING", 66)
        weak_drone = Drone(2, "Weak-Drone", "Mini", 4.29, "IDLE", 100)

        start_time = "2026-01-05 12:00:00"
        self.mock_parcel_repo.search_by_id.return_value = london_parcel
        self.mock_drone_repo.get_data.return_value = [weak_drone]
        
        self.mock_weather_service.get_current_weather.return_value = {
            "wind_speed": 0, "temperature": 20, "is_raining": 0
        }
        self.mock_ai.predict_drain_multiplier.return_value = 1.0
        with self.assertRaises(NoDroneAvailable):
            self.logistic_service.assign_a_mission_automatically(99, start_time)
        
        print("66km Mission correctly rejected (Not enough battery).")

    def test_weather_impact_on_battery(self):
        """
        Directly tests the _calculate_necessary_battery_level function 
        to prove that Bad Weather increases battery cost.
        """
        print("Test: AI Weather Penalty Calculation")

        dt = datetime.now()
        
        # --- Scenario A: Sunny Day ---
        self.mock_weather_service.get_current_weather.return_value = {"wind_speed": 0, "temperature": 20, "is_raining": 0}
        self.mock_ai.predict_drain_multiplier.return_value = 1.0
        
        cost_sunny = self.logistic_service._calculate_necessary_battery_level(
            parcel_distance=5.0, scheduled_dt=dt, parcel_weight=2.0, drone_max_payload=10.0
        )

        # --- Scenario B: Stormy Day ---
        self.mock_weather_service.get_current_weather.return_value = {"wind_speed": 50, "temperature": 5, "is_raining": 1}
        self.mock_ai.predict_drain_multiplier.return_value = 1.5 # 50% more drain
        
        cost_stormy = self.logistic_service._calculate_necessary_battery_level(
            parcel_distance=5.0, scheduled_dt=dt, parcel_weight=2.0, drone_max_payload=10.0
        )

        print(f"Sunny Cost: {cost_sunny:.2f}%")
        print(f"Storm Cost: {cost_stormy:.2f}%")

        self.assertTrue(cost_stormy > cost_sunny, "Storm cost should be higher")
        print("AI Penalty Logic verified.")

    def test_add_drone_valid(self):
        print("Test: Add Valid Drone")
        self.mock_drone_repo.search_by_id.return_value = None
        
        self.drone_service.add_drone(5, "SN-55", "ModelX", 5.0, "IDLE", 100)
        
        self.mock_drone_repo.add_item.assert_called_once()
        print("Drone added.")

    def test_add_drone_invalid_battery(self):
        print("Test: Add Drone Invalid Battery")
        self.mock_drone_repo.search_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            self.drone_service.add_drone(6, "SN-66", "ModelX", 5.0, "IDLE", 150)
        print("Caught invalid battery error.")

    def test_add_parcel_valid(self):
        print("Test: Add Valid Parcel")
        self.mock_parcel_repo.search_by_id.return_value = None
        
        self.logistic_service.add_parcel(100, "Alice", "Wonderland", 5.0, "HIGH", 15.0)
        
        self.mock_parcel_repo.add_item.assert_called_once()
        print("Parcel added successfully.")

    def test_add_parcel_invalid(self):
        print("Test: Add Invalid Parcel (Weight/Distance)")
        self.mock_parcel_repo.search_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            self.logistic_service.add_parcel(101, "Bob", "BuildSt", -5.0, "STANDARD", 10.0)
            
        with self.assertRaises(ValueError):
            self.logistic_service.add_parcel(102, "Bob", "BuildSt", 5.0, "STANDARD", -10.0)
            
        print("Caught invalid weight/distance errors.")

    def test_assign_mission_manually_success(self):
        print("Test: Manual Mission Assignment (Success)")
        
        drone = Drone(1, "SN1", "X1", 10.0, "IDLE", 100)
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "PENDING", 5.0)
        
        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel
        self.mock_mission_repo.get_data.return_value = [] 
        
        self.mock_weather_service.get_current_weather.return_value = {"wind_speed":0, "temperature":20, "is_raining":0}
        self.mock_ai.predict_drain_multiplier.return_value = 1.0

        self.logistic_service.assign_a_mission_manually(1, 1, 50, start_time)

        self.assertEqual(parcel.get_status(), "ASSIGNED")
        self.assertEqual(drone.get_status(), "FLIGHT SCHEDULED")
        self.mock_mission_repo.add_item.assert_called_once()
        print("Manual assignment successful.")

    def test_assign_mission_drone_maintenance(self):
        print("Test: Assign to Drone in MAINTENANCE")
        
        drone = Drone(1, "SN1", "X1", 10.0, "MAINTENANCE", 100)
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "PENDING", 5.0)
        
        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel
        
        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        with self.assertRaises(DroneUnavailable): 
             self.logistic_service.assign_a_mission_manually(1, 1, 50, start_time)
        print("Correctly rejected maintenance drone.")

    def test_assign_mission_drone_in_flight(self):
        print("Test: Assign to Drone IN_FLIGHT")
        
        drone = Drone(1, "SN1", "X1", 10.0, "IN_FLIGHT", 100)
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "PENDING", 5.0)
        
        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel

        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        with self.assertRaises(DroneUnavailable):
             self.logistic_service.assign_a_mission_manually(1, 1, 50, start_time)
        print("Correctly rejected busy drone.")

    def test_assign_mission_parcel_assigned(self):
        print("Test: Assign Parcel already ASSIGNED")
        
        drone = Drone(1, "SN1", "X1", 10.0, "IDLE", 100)
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "ASSIGNED", 5.0)
        
        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel

        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        with self.assertRaises(ParcelAlreadyAssigned):
             self.logistic_service.assign_a_mission_manually(1, 1, 50, start_time)
        print("Correctly rejected assigned parcel.")

    def test_assign_mission_parcel_delivered(self):
        print("Test: Assign Parcel already DELIVERED")
        
        drone = Drone(1, "SN1", "X1", 10.0, "IDLE", 100)
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "DELIVERED", 5.0)
        
        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel
        
        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        with self.assertRaises(ParcelAlreadyDelivered):
             self.logistic_service.assign_a_mission_manually(1, 1, 50, start_time)
        print("Correctly rejected delivered parcel.")

    def test_assign_mission_weight_exceeded(self):
        print("Test: Assign Heavy Parcel (Weight Exceeded)")
        
        
        drone = Drone(1, "SN1", "Mini", 5.0, "IDLE", 100)
        parcel = Parcel(50, "User", "Addr", 10.0, "STD", "PENDING", 5.0)
        
        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel

        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        with self.assertRaises(WeightExceeded):
             self.logistic_service.assign_a_mission_manually(1, 1, 50, start_time)
        print("Correctly rejected heavy parcel.")
        
    def test_assign_mission_automatic_no_drones_exist(self):
        print("Test: Automatic Assignment (No Drones Available)")
        
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "PENDING", 5.0)
        self.mock_parcel_repo.search_by_id.return_value = parcel
        self.mock_drone_repo.get_data.return_value = []
        
        start_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        with self.assertRaises(NoDroneAvailable):
            self.logistic_service.assign_a_mission_automatically(50, start_time)
            
        print("Correctly handled zero available drones.")

    def test_assign_mission_in_past(self):
        print("Test: Assign Mission in the Past")
        
        drone = Drone(1, "SN1", "X1", 10.0, "IDLE", 100)
        parcel = Parcel(50, "User", "Addr", 2.0, "STD", "PENDING", 5.0)
        
        self.mock_drone_repo.search_by_id.return_value = drone
        self.mock_parcel_repo.search_by_id.return_value = parcel
        
        past_time = "2000-01-01 12:00:00"
        
        with self.assertRaises(InvalidTime):
             self.logistic_service.assign_a_mission_manually(1, 1, 50, past_time)
             
        print("Correctly rejected past time.")

if __name__ == '__main__':
    unittest.main()