class Parcel:
    def __init__(self, id : int, recipient_name : str, delivery_address : str, weight_kg : float, 
                 priority : str, status : str, distance : float):
        self._id = id
        self._recipient_name = recipient_name
        self._delivery_address = delivery_address
        self._weight = weight_kg
        self._distance = distance
        self._priority = priority
        self._status = status


    def get_id(self):
        return self._id
    
    def get_recipient_name(self):
        return self._recipient_name
    
    def get_delivery_address(self):
        return self._delivery_address
    
    def get_weight(self):
        return self._weight
    
    def get_priority(self):
        return self._priority
    
    def get_status(self):
        return self._status
    
    def get_distance(self):
        return self._distance
    
    def set_status(self, new_status):
        self._status = new_status
    
    def fuzzy_match(self, query):
        query = str(query)
        query = query.lower().strip()
        if query in self._recipient_name.lower(): return True
        if query in self._delivery_address.lower(): return True
        if query in self._priority: return True
        if query in str(self._weight): return True
        return False

    def __str__(self):
        return f"""ID : {self._id} | Recipient Name : {self._recipient_name} | Delivery Adress : {self._delivery_address} |
                Weight : {self._weight} kg | Distance {self._distance} km | Priority : {self._priority} | Status : {self._status}"""