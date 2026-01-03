import configparser
from repositories import repository
from services.fleetservice import DroneService
from services.logistics_service import LogisticService
from ui import Console
import sys
from gui import LogisticApp
from repositories.composite_repository import CompositeRepository
from services.weather_service import WeatherService
from AI.BatteryPredictionAI import BatteryPredictionAi
import api_server
import threading


if __name__ == '__main__':
    config = configparser.ConfigParser()
    try:
        with open('settings.properties', 'r') as f:
            config_string = '[settings]\n' + f.read()
        config.read_string(config_string)
    except FileNotFoundError:
        print("Error: settings.properties file not found.")
        sys.exit(1)
        
    repo_type = config['settings']['repository'].strip('"')


    if repo_type == 'text':
        d_file = config['settings']['drones_txt_path'].strip('"')
        p_file = config['settings']['parcels_txt_path'].strip('"')
        m_file = config['settings']['missions_txt_path'].strip('"')
        d_repo = repository.DroneTextFileRepository(d_file)
        p_repo = repository.ParcelTextFileRepository(p_file)
        m_repo = repository.MissionTextFileRepository(m_file)
    elif repo_type == 'binary':
        d_file = config['settings']['drones_binary_path'].strip('"')
        p_file = config['settings']['parcels_binary_path'].strip('"')
        m_file = config['settings']['missions_binary_path'].strip('"')
        d_repo = repository.BinaryFileRepository(d_file)
        p_repo = repository.BinaryFileRepository(p_file)
        m_repo = repository.BinaryFileRepository(m_file)
    elif repo_type == "db":
        db_file = config['settings']['database_path'].strip('"')
        db_string = f"sqlite:///{db_file}"
        d_repo = repository.DroneSQLRepository(db_string)
        p_repo = repository.ParcelSQLRepository(db_string)
        m_repo = repository.MissionSQLRepository(db_string)
    elif repo_type == "master":
        db_file = config['settings']['database_path'].strip('"')
        db_string = f"sqlite:///{db_file}"
        drone_sql = repository.DroneSQLRepository(db_string)
        parcel_sql = repository.ParcelSQLRepository(db_string)
        mission_sql = repository.MissionSQLRepository(db_string)
        d_file = config['settings']['drones_binary_path'].strip('"')
        p_file = config['settings']['parcels_binary_path'].strip('"')
        m_file = config['settings']['missions_binary_path'].strip('"')
        drone_binary = repository.BinaryFileRepository(d_file)
        parcel_binary = repository.BinaryFileRepository(p_file)
        mission_binary = repository.BinaryFileRepository(m_file)
        d_file = config['settings']['drones_txt_path'].strip('"')
        p_file = config['settings']['parcels_txt_path'].strip('"')
        m_file = config['settings']['missions_txt_path'].strip('"')
        drone_text = repository.DroneTextFileRepository(d_file)
        parcel_text = repository.ParcelTextFileRepository(p_file)
        mission_text = repository.MissionTextFileRepository(m_file)
        d_repo = CompositeRepository(drone_sql, [drone_binary, drone_text])
        p_repo = CompositeRepository(parcel_sql, [parcel_binary, parcel_text])
        m_repo = CompositeRepository(mission_sql, [mission_binary, mission_text])
    else:
        print("Invalid repository type in settings")
        sys.exit(1)

    api_key = config['settings']['api_key'].strip('"')
    city = config['settings']['city'].strip('"')

    weather_service = WeatherService(api_key, city)
    ai = BatteryPredictionAi()

    d_service = DroneService(d_repo)
    l_service = LogisticService(p_repo, m_repo, d_repo, weather_service, ai)

    l_service._start_background_scheduler()
    d_service._charge_drone()

    api_server.set_repo(d_service, l_service)

    api_thread = threading.Thread(target = api_server.start_server_thread, daemon=True)
    api_thread.start()

    ui_mode = config['settings']['ui'].strip('"')

    if ui_mode == 'console':
        ui = Console(d_service, l_service)
        ui.run()
    elif ui_mode == 'gui':
        app = LogisticApp(d_service, l_service)
        app.run()
