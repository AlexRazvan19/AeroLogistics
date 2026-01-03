class IDNotFound(Exception):
    """Exception raised when an entity with a specific id can not be found"""
    def __init__(self, id_value : int,item):
        self._message = f"{item} with ID: {id_value} not found"
        super().__init__(self._message)

class DuplicateID(Exception):
    """Exception raised when an entity with a specific id already exists"""
    def __init__(self, id_value : int,item):
        self._message = f"{item} with ID: {id_value} already exists"
        super().__init__(self._message)

class WeightExceeded(Exception):
    """Exception raised when a parcel's weight exceeds drone's max payload"""
    def __init__(self, drone_payload : float, parcel_weight : float):
        self._message = f"Drone payload exceeded! Drone payload is {drone_payload} kg while the parcel require {parcel_weight} kg"
        super().__init__(self._message)

class DroneUnavailable(Exception):
    """Exception raised when a drone's status is unavailable"""
    def __init__(self, drone_id : int):
        self._message = f"Drone with ID {drone_id} is currently unavailable"
        super().__init__(self._message)

class NoDroneAvailable(Exception):
    """Exception raised when there is no drone available for a mission assignment"""
    def __init__(self,parcel_id : int):
        self._message = f"No drone available for the mission with parcel ID {parcel_id}"
        super().__init__(self._message)

class ParcelAlreadyDelivered(Exception):
    """Exception raised when a user tries to assign a mission to a parcel that has been already delivered"""
    def __init__(self,parcel_id : int):
        self._message = f"Parcel with ID {parcel_id} was already delivered"
        super().__init__(self._message)

class DroneInFlight(Exception):
    """Exception raised when a user tries to delete or update a drone while it is in flight"""
    def __init__(self, drone_id : int):
        self.message = f"Drone with ID {drone_id} is currently in flight"
        super().__init__(self.message)

class InvalidTime(Exception):
    """Exception raised when a user enters an in the past time"""
    def __init__(self, time):
        self.message = f"Introduced start time {time} is in the past"
        super().__init__(self.message)

class ParcelAlreadyAssigned(Exception):
    """Exception raised when a user tries to assign a mission to a parcel that has been already assigned"""
    def __init__(self,parcel_id : int):
        self._message = f"Parcel with ID {parcel_id} was already assigned"
        super().__init__(self._message)

class DroneFlightAssigned(Exception):
    """Exception raised when a user tries to delete or update a drone while it have an flight assigned"""
    def __init__(self, drone_id : int):
        self.message = f"Drone with ID {drone_id} have an flight assigned"
        super().__init__(self.message)

class ParcelDelivered(Exception):
    """Exception raised when a user tries to remove or update  a parcel that has been already delivered"""
    def __init__(self,parcel_id : int ):
        self._message = f"Parcel with ID {parcel_id} was already delivered"
        super().__init__(self._message)

class ParcelAssigned(Exception):
    """Exception raised when a user tries to remove or update  a parcel that has been already assigned"""
    def __init__(self,parcel_id : int):
        self._message = f"You can not modify the parcel with ID {parcel_id} as it has been assigned to a mission"
        super().__init__(self._message)

class NotEnoughBattery(Exception):
    """Exception raised when the drone does not have enough battery for the mission user tries to assign"""
    def __init__(self,drone_id : int):
        self._message = f"Drone with ID {drone_id} does not have enough battery for this mission"
        super().__init__(self._message)
