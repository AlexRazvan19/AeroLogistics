class Mission:
    def __init__(self, id : int, drone_id : int, parcel_id : int, start_time : str, status : str):
        self._id = id
        self._drone_id = drone_id
        self._parcel_id = parcel_id
        self._start_time = start_time
        self._status = status

    def get_id(self):
        return self._id
    
    def get_drone_id(self):
        return self._drone_id
    
    def get_parcel_id(self):
        return self._parcel_id
    
    def get_start_time(self):
        return self._start_time
    
    def get_status(self):
        return self._status
    
    def set_status(self, new_status):
        self._status = new_status
        
    def __str__(self):
         return f"""ID : {self._id} | Drone ID : {self._drone_id} | Parcel ID : {self._parcel_id} |
                Start Time : {self._start_time} | Status : {self._status}"""