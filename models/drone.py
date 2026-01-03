class Drone:
    def __init__(self, id : int, serial_number : str, model_type : str, max_payload_kg : float, status : float, battery_level : int):
        self._id = id
        self._serial_number = serial_number
        self._model_type = model_type
        self._max_payload = max_payload_kg
        self._status = status
        self._battery_level = battery_level


    def get_id(self):
        return self._id
    
    def get_serial_number(self):
        return self._serial_number
    
    def get_model_type(self):
        return self._model_type
    
    def get_max_payload(self):
        return self._max_payload
    
    def get_status(self):
        return self._status
    
    def set_status(self, new_status):
        self._status = new_status

    def get_battery_level(self):
        return self._battery_level
    
    def update_battery(self, battery_consumed : int):
        self._battery_level = self._battery_level - battery_consumed

    def charge_battery(self, procentage : int):
        self._battery_level = self._battery_level + procentage
    
    def fuzzy_match(self, query):
        query = str(query)
        q = query.lower().strip()
        if q in str(self._id).lower(): return True
        if q in self._model_type.lower(): return True
        if q in self._status.lower(): return True
        if q in str(self._max_payload).lower(): return True
        return False

    def __str__(self):
        return f"""ID : {self._id} | Serial Number : {self._serial_number} | Model Type : {self._model_type} | 
                    Max Payload : {self._max_payload} | Status : {self._status} | Battery Level : {self._battery_level}% \n"""     