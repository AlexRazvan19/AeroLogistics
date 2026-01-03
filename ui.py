from exceptions import DuplicateID,IDNotFound, DroneUnavailable, WeightExceeded, NoDroneAvailable, ParcelAlreadyDelivered,DroneInFlight
from rich.table import Table
from rich.console import Console as RichConsole
from exceptions import InvalidTime, ParcelAlreadyAssigned, DroneFlightAssigned, ParcelAssigned, ParcelDelivered, NotEnoughBattery

class Console:
    def __init__(self, drone_service, logistic_service):
        self._rc = RichConsole()
        self._drone_service = drone_service
        self._logistic_service = logistic_service

    def print_main_menu(self):
        print("===Select an option from the list below===")
        print("1. Manage Drones")
        print("2. Manage Parcels")
        print("3. Manage Missions")
        print("0. Exit the program")

    def print_drone_menu(self):
        print("===Select an option from the list below===")
        print("1. Add a drone")
        print("2. Remove a drone")
        print("3. Update a drone")
        print("4. List the drones")
        print("5. Search for drones")
        print("0. Exit the program")
    
    def print_parcel_menu(self):
        print("===Select an option from the list below===")
        print("1. Add a parcel")
        print("2. Remove a parcel")
        print("3. Update a parcel")
        print("4. List the parcels")
        print("5. Search for parcels")
        print("6. Show History")
        print("0. Exit the program")

    def print_mission_menu(self):
        print("===Select an option from the list below===")
        print("1. Automatically assign a mission")
        print("2. Manually assign a mission")
        print("3. Mark a mission as finished")
        print("4. List the missions")
        print("0. Exit the program")

    def run(self):
        while True:
            self.print_main_menu()
            try:
                option = int(input(">>> Enter an option: "))
            except ValueError:
                print(">>>ERROR: Option must be an integer")
            if option == 1:
                self.print_drone_menu()
                try:
                    option = int(input(">>> Enter an option: "))
                except ValueError:
                    print("Option must be an integer")
                if option == 1:
                    try:
                        drone_id = int(input(">>>Enter the ID: "))
                        serial_number = input(">>>Enter the serial number: ")
                        model_type = input(">>>Enter the model type: ")
                        max_payload = float(input(">>>Enter the maximum payload (kg): "))
                        battery_level = int(input(">>>Enter the battery level: "))
                        status = input(">>>Enter the status (IDLE, IN_FLIGHT, MAINTENANCE): ")
                        status = status.upper()
                        if status != "IDLE" and status != "IN_FLIGHT" and status != "MAINTENANCE":
                            print(">>>ERROR: Invalid Status")
                            continue
                        if max_payload <= 0:
                            print(">>>ERROR: Drone PayLoad must be positive")
                            continue
                        if battery_level < 0:
                            print(">>>ERROR: Drone Battery Level must be positive")
                            continue
                        if battery_level > 100:
                            print(">>>ERROR: Maximum battery level is 100")
                            continue
                        self._drone_service.add_drone(drone_id, serial_number, model_type, max_payload, status, battery_level)
                        print(">>>Succesfully added the drone")
                    except ValueError as v:
                        print(f">>>ERROR: {v}")
                        print("Please try again with valid inputs")
                    except DuplicateID as e:
                        print(f">>>ERROR: {e}")
                        print("Please try again with a unique iD")
                elif option == 2:
                    try:
                        drone_id = int(input(">>>Enter the id of the drone you want to remove: "))
                        self._drone_service.remove_drone(drone_id)
                        print("Succesfully removed the drone")
                    except ValueError as v:
                        print("Drone ID must be an integer")
                    except IDNotFound as e:
                        print(e)
                        print("Please try again with an valid ID")
                    except DroneInFlight as dif:
                        print(dif)
                    except DroneFlightAssigned as dfa:
                        print(dfa)
                elif option == 3:
                    try:
                        drone_id = int(input(">>>Enter the ID of the drone you want to update: "))
                        serial_number = input(">>>Enter the new serial number of the drone: ")
                        model_type = input(">>>Enter the new model type of drone: ")
                        max_payload = float(input(">>>Enter the new maximum payload (kg): "))
                        battery_level = int(input(">>>Enter the battery level: "))
                        status = input(">>>Enter the new status of the drone (IDLE, IN_FLIGHT, MEINTENANCE): ")
                        status = status.upper()
                        if status != "IDLE" and status != "IN_FLIGHT" and status != "MEINTENANCE":
                            print(">>>ERROR: Invalid Status")
                            continue
                        if max_payload <= 0:
                            print(">>>ERROR: Drone PayLoad must be positive")
                            continue
                        if battery_level < 0:
                            print(">>>ERROR: Drone Battery Level must be positive")
                            continue
                        if battery_level > 100:
                            print(">>>ERROR: Maximum battery level is 100")
                            continue
                        self._drone_service.update_drone(drone_id, serial_number, model_type, max_payload, status, battery_level)
                        print("Succesfully updated the drone")
                    except ValueError as v:
                        print(f">>>ERROR: {v}")
                        print("Please try again with valid inputs")
                    except IDNotFound as e:
                        print(e)
                        print("Please try again with an valid ID")
                    except DroneInFlight as dif:
                        print(dif)
                    except DroneFlightAssigned as dfa:
                        print(dfa)
                elif option == 4:
                    table = Table(title="Drone Fleet Status")

                    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                    table.add_column("Model", style="magenta")
                    table.add_column("Payload", justify="right", style="green")
                    table.add_column("Battery Level", justify="right")
                    table.add_column("Status", justify="center")
                    drones = self._drone_service.list_the_drones()
                    for drone in drones:
                        status_style = "green" if drone.get_status() == "IDLE" else "red"
                        if drone.get_battery_level() >= 70:
                            battery_style = "green"
                        elif drone.get_battery_level() >= 30:
                            battery_style = "yellow"
                        else:
                            battery_style = "red"
                        table.add_row(
                            str(drone.get_id()), 
                            drone.get_model_type(), 
                            f"{drone.get_max_payload()} kg", 
                            f"[{battery_style}]{drone.get_battery_level()}%[/{battery_style}]",
                            f"[{status_style}]{drone.get_status()}[/{status_style}]"
                        )
                    self._rc.print(table)
                elif option == 5:
                    query = input(">>>Enter the query (drone_id, status, model_type, max_payload): ")
                    drones = self._drone_service.search_drone(query)
                    if not drones:
                        print("No drones found based on the query")
                        continue
                    table = Table(title="Drone Search")

                    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                    table.add_column("Model", style="magenta")
                    table.add_column("Payload", justify="right", style="green")
                    table.add_column("Battery Level", justify="right")
                    table.add_column("Status", justify="center")
                    for drone in drones:
                        status_style = "green" if drone.get_status() == "IDLE" else "red"
                        if drone.get_battery_level() >= 70:
                            battery_style = "green"
                        elif drone.get_battery_level() >= 30:
                            battery_style = "yellow"
                        else:
                            battery_style = "red"
                        table.add_row(
                            str(drone.get_id()), 
                            drone.get_model_type(), 
                            f"{drone.get_max_payload()} kg",
                            f"[{battery_style}]{drone.get_battery_level()}%[/{battery_style}]",
                            f"[{status_style}]{drone.get_status()}[/{status_style}]"
                        )
                    self._rc.print(table)
                elif option == 0:
                    print(">>> Exiting the program...")
                    break
                else:
                    print(">>>ERROR: Invalid Input")
            elif option == 2:
                self.print_parcel_menu()
                try:
                    option = int(input(">>> Enter an option: "))
                except ValueError:
                    print(">>>ERROR: Option must be an integer")
                if option == 1:
                        try:
                            parcel_id = int(input(">>>Enter the ID: "))
                            recipient_name = input(">>>Enter the recipient name: ")
                            delivery_adress = input(">>>Enter the delivery adress: ")
                            weight = float(input(">>>Enter the weight (kg): "))
                            distance = float(input(">>>Enter the distance (km):"))
                            priority = input(">>>Enter the priority of the parcel (HIGH, STANDARD): ")
                            priority = priority.upper()
                            if priority != "HIGH" and priority != "STANDARD":
                                print(">>>ERROR: Invalid priority")
                                continue
                            if weight <= 0:
                                print(">>>ERROR: Parcel weight must be greater than 0")
                                continue
                            if distance <= 0:
                                print(">>>ERROR: Parcel distance must be greater than 0")
                                continue
                            self._logistic_service.add_parcel(parcel_id, recipient_name, delivery_adress, weight, priority)
                            print("Succesfully added the parcel")
                        except ValueError as v:
                            print(f">>>ERROR: {v}")
                            print("Please try again with valid inputs")
                        except IDNotFound as e:
                            print(e)
                            print("Please try again with an valid ID")
                elif option == 2:
                        try:
                            parcel_id = int(input(">>>Enter the ID of the parcel you want to remove: "))
                            self._logistic_service.remove_parcel(parcel_id)
                            print("Succesfully removed the parcel")
                        except ValueError as v:
                            print("Parcel ID must be an integer")
                        except IDNotFound as e:
                            print(e)
                            print("Please try again with an valid ID")
                        except ParcelAssigned as pa:
                            print(pa)
                        except ParcelDelivered as pd:
                            print(pd)
                elif option == 3:
                        try:
                            parcel_id = int(input(">>>Enter the ID of the parcel you want to update: "))
                            recipient_name = input(">>>Enter the new recipient name: ")
                            delivery_adress = input(">>>Enter the new delivery adress: ")
                            weight = float(input(">>>Enter the new weight (kg): "))
                            distance = float(input(">>>Enter the new distance (km): "))
                            priority = input(">>>Enter the new priority  (HIGH, STANDARD): ")
                            status = input(">>>Enter the new status (DELIVERED, PENDING, ASSIGNED)")
                            priority = priority.upper()
                            if priority != "HIGH" and priority != "STANDARD":
                                print(">>>ERROR: Invalid priority")
                                continue
                            status = status.upper()
                            if status != "DELIVERED" and status != "PENDING" and status != "ASSIGNED":
                                print(">>>ERROR: Invalid status")
                                continue
                            if weight <= 0:
                                print(">>>ERROR: Parcel weight must be greater than 0")
                                continue
                            if distance <= 0:
                                print(">>>ERROR: Parcel distance must be greater than 0")
                                continue
                            self._logistic_service.update_parcel(parcel_id, recipient_name, delivery_adress, weight, priority,status)
                            print("Succesfully updated the parcel")
                        except ValueError as v:
                            print(f">>>ERROR: {v}")
                            print("Please try again with valid inputs")
                        except IDNotFound as e:
                            print(e)
                            print("Please try again with an valid ID")
                        except ParcelDelivered as pd:
                            print(pd)
                        except ParcelAssigned as pa:
                            print(pa)
                elif option == 4:
                        parcels = self._logistic_service.get_parcels()
                        table = Table(title="Parcels")

                        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                        table.add_column("Recipient Name", style="magenta")
                        table.add_column("Delivery Address", justify="right")
                        table.add_column("Weight", justify="center",  style="green")
                        table.add_column("Distance", justify="center", style="#6098BE")
                        table.add_column("Priority", justify="center")
                        table.add_column("Status", justify="center")
                        for parcel in parcels:
                            if parcel.get_status() != "DELIVERED":
                                priority_style = "red" if parcel.get_priority() == "HIGH" else "yellow"
                                if parcel.get_status() == "ASSIGNED":
                                    status_style = "blue"
                                elif parcel.get_status() == "PENDING":
                                    status_style = "orange" 
                                table.add_row(
                                    str(parcel._id), 
                                    parcel.get_recipient_name(), parcel.get_delivery_address(),
                                    f"{parcel.get_weight()} kg", f"{parcel.get_distance()}",
                                    f"[{priority_style}]{parcel.get_priority()}[/{priority_style}]",
                                    f"[{status_style}]{parcel.get_status()}[/{status_style}]"
                                )
                        self._rc.print(table)
                elif option == 5:
                        query = input(">>>Enter the query (recipient_name, delivery_address, weight, priority): ")
                        filtered_parcels = self._logistic_service.search_parcels(query)
                        if len(filtered_parcels) == 0:
                            print("No parcels found based on the query")
                            continue
                        table = Table(title="Parcels Search")

                        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                        table.add_column("Recipient Name", style="magenta")
                        table.add_column("Delivery Address", justify="right")
                        table.add_column("weight", justify="center",  style="green")
                        table.add_column("Distance", justify="center", style="#6098BE")
                        table.add_column("priority", justify="center")
                        table.add_column("status", justify="center")
                        for parcel in filtered_parcels:
                            if parcel.get_status() != "DELIVERED":
                                priority_style = "red" if parcel.get_priority() == "HIGH" else "yellow"
                                if parcel.get_status() == "ASSIGNED":
                                    status_style = "blue"
                                elif parcel.get_status() == "PENDING":
                                    status_style = "orange"
                                table.add_row(
                                    str(parcel.get_id()), 
                                    parcel.get_recipient_name(), parcel.get_delivery_address(),
                                    f"{parcel.get_weight()} kg", f"{parcel.get_distance()}",
                                    f"[{priority_style}]{parcel.get_priority()}[/{priority_style}]",
                                    f"[{status_style}]{parcel.get_status()}[/{status_style}]"
                                )
                        self._rc.print(table)
                elif option == 6:
                    delivered_parcels = self._logistic_service.get_delivered_parcels()
                    if len(delivered_parcels) == 0:
                        print("No parcels delivered")
                        continue
                    table = Table(title="Parcels Search")

                    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                    table.add_column("Recipient Name", style="magenta")
                    table.add_column("Delivery Address", justify="right")
                    table.add_column("Weight", justify="center",  style="green")
                    table.add_column("Distance", justify="center", style="#6098BE")
                    table.add_column("Priority", justify="center")
                    table.add_column("Status", justify="center")
                    for parcel in delivered_parcels:
                            priority_style = "red" if parcel.get_priority() == "HIGH" else "yellow"
                            status_style = "green"
                            table.add_row(
                                str(parcel.get_id()), 
                                parcel.get_recipient_name(), parcel.get_delivery_address(),
                                f"{parcel.get_weight()} kg", f"{parcel.get_distance()}",
                                f"[{priority_style}]{parcel.get_priority()}[/{priority_style}]",
                                f"[{status_style}]{parcel.get_status()}[/{status_style}]"
                            )
                    self._rc.print(table)
                elif option == 0:
                        print(">>> Exiting the program...")
                        break
                else:
                        print(">>>ERROR: Invalid Input")
            elif option == 3:
                self.print_mission_menu()
                try:
                    option = int(input(">>> Enter an option: "))
                except ValueError:
                    print(">>>ERROR: Option must be an integer")
                if option == 1:
                    try:
                        parcel_id = int(input(">>>Enter the ID of the parcel: "))
                        start_time = input(">>>Enter the start time (YYYY-MM-DD HH-MM-SS): ")
                        drone_id = self._logistic_service.assign_a_mission_automatically(parcel_id, start_time)
                        print(f"Succesfully assigned the mission to the drone with ID {drone_id}")
                    except ValueError as v:
                        print(f">>>ERROR: {v}")
                        print("Please try again with valid inputs")
                    except IDNotFound as e:
                        print(e)
                        print("Please try again with an valid ID")
                    except NoDroneAvailable as nde:
                        print(nde)
                    except ParcelAlreadyDelivered as pad:
                        print(pad)
                    except InvalidTime as it:
                        print(it)
                    except ParcelAlreadyAssigned as paa:
                        print(paa)
                elif option == 2:
                    try:
                        mission_id = int(input(">>>Enter the ID of the mission: "))
                        drone_id = int(input(">>>Enter the ID of the drone: "))
                        parcel_id = int(input(">>>Enter the ID of the parcel: "))
                        start_time = input(">>>Enter the start time (YYYY-MM-DD HH-MM-SS): ")
                        self._logistic_service.assign_a_mission_manually(mission_id, drone_id, parcel_id, start_time)
                        print("Succesfully assigned the mission")
                    except ValueError as v:
                        print(f">>>ERROR: {v}")
                        print("Please try again with valid inputs")
                    except IDNotFound as e:
                            print(e)
                            print("Please try again with an valid ID")
                    except DroneUnavailable as du:
                        print(du)
                    except WeightExceeded as we:
                        print(we)
                    except ParcelAlreadyDelivered as pad:
                        print(pad)
                    except InvalidTime as it:
                        print(it)
                    except ParcelAlreadyDelivered as paa:
                        print(paa)
                    except NotEnoughBattery as neb:
                        print(neb)
                elif option == 3:
                    try:
                        mission_id = int(input(">>>Enter the ID of the mission: "))
                        status = input(">>>Enter the status of the mission (FAILED, DELIVERED): ")
                        status = status.upper()
                        if status != "FAILED" and status != "DELIVERED":
                            print(">>>ERROR: Invalid status")
                            continue
                        self._logistic_service.modify_mission_status(mission_id, status)
                        print("Succesfully changed the mission status")
                    except ValueError as v:
                        print(f">>>ERROR: {v}")
                        print("Please try again with valid inputs")
                    except IDNotFound:
                        print(e)
                        print("Please try again with an valid ID")
                elif option == 4:
                    missions = self._logistic_service.get_missions()
                    table = Table(title="Missions")

                    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                    table.add_column("Drone_ID", style="magenta")
                    table.add_column("Parcel_ID", justify="right", style = "Yellow")
                    table.add_column("Start_Time", justify="center")
                    table.add_column("Status", justify="center")
                    for mission in missions:
                        status_style = "red" if mission.get_status() == "FAILED" else "green"
                        table.add_row(
                                str(mission.get_id()), 
                                str(mission.get_drone_id()), str(mission.get_parcel_id()),
                                mission.get_start_time(), 
                                f"[{status_style}]{mission.get_status()}[/{status_style}]"
                        )
                    self._rc.print(table)
                elif option == 0:
                    print(">>> Exiting the program...")
                    break
                else:
                    print(">>>ERROR: Invalid Input")
            elif option == 0:
                print(">>> Exiting the program...")
                break
            else:
                print(">>>ERROR: Invalid Input")

