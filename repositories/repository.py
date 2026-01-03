import os
from models import drone
from models.drone import Drone
from models.parcel import Parcel
from models.mission import Mission
import pickle
from sqlalchemy import create_engine, Float,String,Integer, Column
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class Repository:
    def __init__(self):
        self._data = []

    def add_item(self, item):
        self._data.append(item)
    
    def remove_item(self, item_id):
        new_data = [item for item in self._data if item._id != item_id]
        self._data = new_data[:]
    
    def search_by_id(self, item_id):
        for item in self._data:
            if item._id == item_id:
                return item
        return None
    
    def get_data(self):
        return self._data
    
    def update(self, new_item):
        for index, item in enumerate(self._data):
            if item._id == new_item._id:
                self._data[index] = new_item
        
    
class TextFileRepository(Repository):
    def __init__(self, file):
        super().__init__()
        self._file = file
        self._load_from_file()

    def _save_in_file(self):
        with open(self._file, "w") as f:
            for item in self._data:
                f.write(self._object_to_line(item) + "\n")

    def _load_from_file(self):
        if not os.path.exists(self._file):
            return
        with open(self._file, "r") as f:
            for line in f:
                super().add_item(self._line_to_object(line.strip()))

    def add_item(self, item):
        super().add_item(item)
        self._save_in_file()

    def remove_item(self, item_id):
        super().remove_item(item_id)
        self._save_in_file()
    
    def update(self, new_item):
        super().update(new_item)
        self._save_in_file()

class BinaryFileRepository(Repository):
    def __init__(self,binary_file):
        super().__init__()
        self._file = binary_file
        self._load_from_file()

    def _load_from_file(self):
        if not os.path.exists(self._file):
            return
        try:
            with open(self._file, "rb") as f:
                self._data = pickle.load(f)
        except EOFError:
            self._data = []
    
    def _save_in_file(self):
        with open(self._file, "wb") as f:
            pickle.dump(self._data, f)
    
    def add_item(self, item):
        super().add_item(item)
        self._save_in_file()

    def remove_item(self,item_id):
        super().remove_item(item_id)
        self._save_in_file()

    def update(self, new_item):
        super().update(new_item)
        self._save_in_file()

class DroneTextFileRepository(TextFileRepository):
    def _object_to_line(self, item):
        return f"{item._id},{item._serial_number},{item._model_type},{item._max_payload},{item._status},{item._battery_level}"
    
    def _line_to_object(self, line):
        parts = line.split(',')
        return Drone(int(parts[0]),  parts[1], parts[2], float(parts[3]), parts[4], parts[5])
    
class ParcelTextFileRepository(TextFileRepository):
    def _object_to_line(self, item):
        return f"{item._id},{item._recipient_name},{item._delivery_address},{item._weight},{item._priority},{item._status}, {item._distance}"
    
    def _line_to_object(self, line):
        parts = line.split(',')
        return Parcel(int(parts[0]),parts[1], parts[2], float(parts[3]), parts[4], parts[5], parts[6])
    
class MissionTextFileRepository(TextFileRepository):
    def _object_to_line(self, item):
        return f"{item._id},{item._drone_id},{item._parcel_id},{item._start_time},{item._status}"

    def _line_to_object(self, line):
        parts = line.split(',')
        return Mission(int(parts[0]),int(parts[1]), int(parts[2]), parts[3], parts[4])

class DroneModel(Base):
    __tablename__ = "Drones"
    id = Column(Integer, primary_key = True)
    serial_number = Column(String)
    model_type = Column(String)
    max_payload = Column(Float)
    battery_level = Column(Integer)
    status = Column(String)

class DroneSQLRepository:
    def __init__(self, connection_string = "sqlite:///logistics.db"):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind = self.engine)

    def add_item(self, drone):
        session = self.session()
        d_model = DroneModel(
            id = drone.get_id(),
            serial_number = drone.get_serial_number(),
            model_type = drone.get_model_type(),
            max_payload = drone.get_max_payload(),
            battery_level = drone.get_battery_level(),
            status = drone.get_status()
        )
        try:
            session.add(d_model)
            session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def get_data(self):
        session = self.session()
        db_Drones = session.query(DroneModel).all()
        drones = [Drone(d.id, d.serial_number, d.model_type, d.max_payload, d.status, d.battery_level) for d in db_Drones]
        session.close()
        return drones
    
    def search_by_id(self, drone_id):
        session = self.session()
        db_drone =  session.query(DroneModel).filter_by(id=drone_id).first()
        session.close()

        if db_drone is None:
            return None
        
        drone = Drone(db_drone.id, db_drone.serial_number,db_drone.model_type, db_drone.max_payload, db_drone.status,
                      db_drone.battery_level)
        return drone
        
    def update(self, new_drone):
        session =  self.session()
        try:
            db_drone = session.query(DroneModel).filter_by(id=new_drone.get_id()).first()
            if db_drone:
                db_drone.max_payload = new_drone.get_max_payload()
                db_drone.model_type = new_drone.get_model_type()
                db_drone.serial_number = new_drone.get_serial_number()
                db_drone.battery_level = new_drone.get_battery_level()
                db_drone.status = new_drone.get_status()
                session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def remove_item(self, item_id):
        session = self.session()
        try:
            db_drone = session.query(DroneModel).filter_by(id=item_id).first()
            if db_drone:
                session.delete(db_drone)
                session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def __len__(self):
        session = self.session()
        count = session.query(DroneModel).count()
        session.close()
        return count

class ParcelModel(Base):
    __tablename__ = "Parcels"
    id = Column(Integer, primary_key = True)
    recipient_name = Column(String)
    delivery_address = Column(String)
    weight = Column(Float)
    distance = Column(Float)
    priority = Column(String)
    status = Column(String)

class ParcelSQLRepository:
    def __init__(self, connection_string = "sqlite:///logistics.db"):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind = self.engine)

    def add_item(self, parcel):
        session  = self.session()
        p_model = ParcelModel(
            id = parcel.get_id(),
            recipient_name = parcel.get_recipient_name(),
            delivery_address = parcel.get_delivery_address(),
            weight = parcel.get_weight(),
            distance = parcel.get_distance(),
            priority = parcel.get_priority(),
            status = parcel.get_status()
        )
        try:
            session.add(p_model)
            session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def get_data(self):
        session = self.session()
        db_parcels = session.query(ParcelModel).all()
        session.close()
        parcels = [Parcel(p.id, p.recipient_name, p.delivery_address, p.weight, p.priority, p.status, p.distance) for p in db_parcels]
        return parcels
    
    def search_by_id(self, parcel_id):
        session = self.session()
        db_parcel = session.query(ParcelModel).filter_by(id = parcel_id).first()
        session.close()

        if db_parcel is None:
            return None
        
        parcel = Parcel(db_parcel.id, db_parcel.recipient_name, db_parcel.delivery_address, db_parcel.weight, db_parcel.priority, db_parcel.status,
                        db_parcel.distance)
        return parcel

    def update(self, new_parcel):
        session = self.session()
        try:
            db_parcel = session.query(ParcelModel).filter_by(id = new_parcel.get_id()).first()
            if db_parcel:
                db_parcel.recipient_name = new_parcel.get_recipient_name()
                db_parcel.delivery_address = new_parcel.get_delivery_address()
                db_parcel.weight = new_parcel.get_weight()
                db_parcel.distance = new_parcel.get_distance()
                db_parcel.priority = new_parcel.get_priority()
                db_parcel.status = new_parcel.get_status()
                session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def remove_item(self, parcel_id):
        session = self.session()
        try:
            db_parcel = session.query(ParcelModel).filter_by(id = parcel_id).first()
            if db_parcel:
                session.delete(db_parcel)
                session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def __len__(self):
        session = self.session()
        count = session.query(ParcelModel).count()
        session.close()
        return count

class MissionModel(Base):
    __tablename__ = "Missions"
    id = Column(Integer, primary_key = True)
    drone_id = Column(Integer)
    parcel_id = Column(Integer)
    start_time = Column(String)
    status = Column(String)

class MissionSQLRepository:
    def __init__(self, connection_string = "sqlite:///logistics.db"):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind = self.engine)

    def add_item(self, mission):
        session  = self.session()
        m_model = MissionModel(
            id = mission.get_id(),
            drone_id = mission.get_drone_id(),
            parcel_id = mission.get_parcel_id(),
            start_time = mission.get_start_time(),
            status = mission.get_status()
        )
        try:
            session.add(m_model)
            session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def get_data(self):
        session = self.session()
        db_missions = session.query(MissionModel).all()
        session.close()
        missions = [Mission(m.id, m.drone_id, m.parcel_id, m.start_time, m.status) for m in db_missions]
        return missions
    
    def search_by_id(self, mission_id):
        session = self.session()
        db_mission = session.query(MissionModel).filter_by(id = mission_id).first()
        session.close()

        if db_mission is None:
            return None
        
        mission = Mission(db_mission.id, db_mission.drone_id, db_mission.parcel_id, db_mission.start_time, db_mission.status)
        return mission

    def update(self, new_mission):
        session = self.session()
        try:
            db_mission = session.query(MissionModel).filter_by(id = new_mission.get_id()).first()
            if db_mission:
                db_mission.drone_id = new_mission.get_drone_id()
                db_mission.parcel_id = new_mission.get_parcel_id()
                db_mission.start_time = new_mission.get_start_time()
                db_mission.status = new_mission.get_status()
                session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def remove_item(self, mission_id):
        session = self.session()
        try:
            db_mission = session.query(MissionModel).filter_by(id = mission_id).first()
            if db_mission:
                session.delete(db_mission)
                session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

    def __len__(self):
        session = self.session()
        count = session.query(MissionModel).count()
        session.close()
        return count
        


        



        

    
    
