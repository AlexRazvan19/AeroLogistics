import customtkinter as ctk
from tkinter import messagebox
from exceptions import IDNotFound, DuplicateID, DroneUnavailable, WeightExceeded, NoDroneAvailable, DroneInFlight, InvalidTime
from exceptions import ParcelAlreadyDelivered, ParcelAlreadyAssigned, NotEnoughBattery

class LogisticApp(ctk.CTk):
    def __init__(self, drone_service, logistic_service):
        super().__init__()
        self._drone_service = drone_service
        self._logistic_service = logistic_service
        self.title("Drone Fleet Manager")
        self.geometry("800x600")
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(pady = 20, padx = 20,fill = "both", expand = True)
        self.tab_drones = self.tab_view.add("Manage Drones")
        self.tab_parcels = self.tab_view.add("Manage Parcels")
        self.tab_missions = self.tab_view.add("Manage Missions")
        self._setup_drone_tab()
        self._setup_parcel_tab()
        self._setup_mission_tab()

    def _setup_drone_tab(self):
        label1 = ctk.CTkLabel(self.tab_drones, text="Add a Drone", font=("Arial", 12))
        label1.pack(pady = 20)

        self.drone_id = ctk.CTkEntry(self.tab_drones, placeholder_text="ID")
        self.drone_id.pack(pady = 5)

        self.drone_serial_number = ctk.CTkEntry(self.tab_drones, placeholder_text="SERIAL NUMBER")
        self.drone_serial_number.pack(pady = 5)

        self.drone_model_type = ctk.CTkEntry(self.tab_drones, placeholder_text="MODEL TYPE")
        self.drone_model_type.pack(pady = 5)

        self.drone_max_payload = ctk.CTkEntry(self.tab_drones, placeholder_text="MAX PAYLOAD (KG)")
        self.drone_max_payload.pack(pady = 5)

        self.drone_battery = ctk.CTkEntry(self.tab_drones, placeholder_text= "BATTERY LEVEL")
        self.drone_battery.pack(pady = 5)

        self.drone_status = ctk.CTkComboBox(self.tab_drones, values=["IDLE", "MAINTENANCE", "IN_FLIGHT"])
        self.drone_status.pack(pady = 5)

        btn_add = ctk.CTkButton(self.tab_drones, text="Add drone", command=self._handle_add_drone)
        btn_add.pack(pady=20)

        self.drone_list_frame  = ctk.CTkScrollableFrame(self.tab_drones, height = 200)
        self.drone_list_frame.pack(fill="x", padx = 10)
        self._refresh_drone_list()

    def _setup_parcel_tab(self):
        label1 = ctk.CTkLabel(self.tab_parcels, text="Add a Parcel", font=("Arial", 12))
        label1.pack(pady = 20)

        self.parcel_id = ctk.CTkEntry(self.tab_parcels, placeholder_text="ID")
        self.parcel_id.pack(pady = 5)

        self.parcel_recipient_name = ctk.CTkEntry(self.tab_parcels, placeholder_text="RECIPIENT NAME")
        self.parcel_recipient_name.pack(pady = 5)

        self.parcel_delivery_address = ctk.CTkEntry(self.tab_parcels, placeholder_text="DELIVERY ADDRESS")
        self.parcel_delivery_address.pack(pady = 5)

        self.parcel_weight = ctk.CTkEntry(self.tab_parcels, placeholder_text="WEIGHT (KG)")
        self.parcel_weight.pack(pady = 5)

        self.parcel_distance = ctk.CTkEntry(self.tab_parcels, placeholder_text="DISTANCE (KM)")
        self.parcel_distance.pack(pady = 5)

        self.parcel_priority = ctk.CTkComboBox(self.tab_parcels, values=["HIGH", "STANDARD"])
        self.parcel_priority.pack(pady = 5)

        btn_add = ctk.CTkButton(self.tab_parcels, text="Add Parcel", command=self._handle_add_parcel)
        btn_add.pack(pady=20)

        btn_see_history = ctk.CTkButton(self.tab_parcels, text = "See History", command=self._handle_see_history)
        btn_see_history.pack(side = "right" , pady = 20)

        self.parcel_list_frame  = ctk.CTkScrollableFrame(self.tab_parcels, height = 200)
        self.parcel_list_frame.pack(fill="x", padx = 10)
        self._refresh_parcel_list()

    def _setup_mission_tab(self):
        manually_label =  ctk.CTkLabel(self.tab_missions, text = "Assign a mission manually", font=("Arial", 12))
        manually_label.pack(pady=20)
        
        self.mission_id = ctk.CTkEntry(self.tab_missions, placeholder_text="ID")
        self.mission_id.pack(pady = 5)

        self.mission_drone_id = ctk.CTkEntry(self.tab_missions, placeholder_text="DRONE ID")
        self.mission_drone_id.pack(pady = 5)

        self.mission_parcel_id = ctk.CTkEntry(self.tab_missions, placeholder_text="PARCEL ID")
        self.mission_parcel_id.pack(pady = 5)

        self.mission_start_time = ctk.CTkEntry(self.tab_missions, placeholder_text="START TIME (YYYY-MM-DD HH-MM-SS)")
        self.mission_start_time.pack(pady = 5)

        btn_add = ctk.CTkButton(self.tab_missions, text="Assign Mission", command=self._handle_assign_mission)
        btn_add.pack(pady = 20)
        self.mission_list_frame = ctk.CTkScrollableFrame(self.tab_missions, height = 200)
        self.mission_list_frame.pack(fill="x", padx = 10)
        self._refresh_mission_list()

    def _handle_assign_mission(self):
        try:
            id = int(self.mission_id.get())
            drone_id = int(self.mission_drone_id.get())
            parcel_id = int(self.mission_parcel_id.get())
            start_time = self.mission_start_time.get()
            self._logistic_service.assign_a_mission_manually(id, drone_id, parcel_id, start_time)
            messagebox.showinfo(title="Success", message="Succesfully assigned the mission")
            self._refresh_mission_list()
        except IDNotFound as idnf:
            messagebox.showerror("ERROR", str(idnf))
        except DroneUnavailable as du:
            messagebox.showerror("ERROR", str(du))
        except ValueError as ve:
            messagebox.showerror("ERROR", f"Invalid Inputs {ve}")
        except WeightExceeded as we:
            messagebox.showerror("ERROR", str(we))
        except ParcelAlreadyDelivered as pad:
            messagebox.showerror("ERROR", str(pad))
        except InvalidTime as it:
            messagebox.showerror("ERROR", str(it))
        except ParcelAlreadyAssigned as paa:
            messagebox.showerror("ERROR", str(paa))
        except NotEnoughBattery as neb:
            messagebox.showerror("ERROR", str(neb))
                
    def _handle_add_drone(self):
        try:
            id = int(self.drone_id.get())
            serial_number = self.drone_serial_number.get()
            model_type = self.drone_model_type.get()
            max_payload = float(self.drone_max_payload.get())
            status = self.drone_status.get()
            battery_level = int(self.drone_battery.get())
            status = status.upper()
            if status != "IDLE" and status != "IN_FLIGHT" and status != "MAINTENANCE":
                messagebox.showwarning(title="Incorrect Status", message="Status of Drone is incorrect, please try again")
                return
            if max_payload <= 0:
                messagebox.showwarning(title="Value Error", message="Drone Max Payload must be greater than 0")
                return
            if battery_level < 0:
                messagebox.showwarning(title="Value Error", message="Drone Battery Level must be positive")
                return
            if battery_level > 100:
                messagebox.showwarning(title="Value Error", message="Maximum battery level is 100")
                return
            self._drone_service.add_drone(id, serial_number, model_type, max_payload, status, battery_level)
            messagebox.showinfo(title="Success", message="Succesfully added the drone")
            self._refresh_drone_list()
        except DuplicateID as e:
            messagebox.showerror("ERROR", str(e))
        except ValueError as ve:
            messagebox.showerror("ERROR", f"Invalid Inputs {ve}")

    def _handle_add_parcel(self):
        try:
            id = int(self.parcel_id.get())
            recipient_name = self.parcel_recipient_name.get()
            delivery_address = self.parcel_delivery_address.get()
            weight = float(self.parcel_weight.get())  
            distance = float(self.parcel_distance.get())
            priority = self.parcel_priority.get()
            if priority != "HIGH" and priority != "STANDARD":
                messagebox.showwarning(title="Incorrect Priority", message="Priority of parcel is incorrect, please try again")
                return
            if weight <= 0:
                messagebox.showwarning(title="Value Error", message="Parcel weight must be greater than 0")
                return
            if distance <= 0:
                messagebox.showwarning(title="Value Error", message="Parcel distance must be greater than 0")
                return
            self._logistic_service.add_parcel(id, recipient_name, delivery_address, weight, priority, distance)
            messagebox.showinfo(title="Success", message="Succesfully added the parcel")
            self._refresh_parcel_list()
        except DuplicateID as e:
            messagebox.showerror("ERROR", str(e))
        except ValueError as ve:
            messagebox.showerror("ERROR", f"Invalid Inputs {ve}")
    
    def _refresh_drone_list(self):
        for widget in self.drone_list_frame.winfo_children():
            widget.destroy()

        drones = self._drone_service.list_the_drones()
        for drone in drones:

            row_frame = ctk.CTkFrame(self.drone_list_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady = 2)

            row_text = f"""ID : {drone.get_id()} | Serial Number : {drone.get_serial_number()} | Model Type : {drone.get_model_type()} | 
                    Max Payload : {drone.get_max_payload()}kg | Status : {drone.get_status()} | Battery Level : {drone.get_battery_level()}% \n"""
            label = ctk.CTkLabel(row_frame, text = row_text)
            label.pack(side = "left", padx = 10)   

            is_locked = drone.get_status() not in ["IDLE", "MAINTENANCE"]
            btn_update = ctk.CTkButton(row_frame, text = "Update", fg_color="gray" if is_locked else "purple", width=50, 
                                       state="disabled" if is_locked else "normal",
                                       command=lambda d_id = drone.get_id(): self._open_drone_edit_window(d_id))
            btn_update.pack(side = "right", padx = 2)

            btn_del = ctk.CTkButton(row_frame, text = "Delete", fg_color="gray" if is_locked else "red", width=50,
                                    state="disabled" if is_locked else "normal",
                                    command=lambda d_id = drone.get_id(): self._handle_drone_delete_by_id(d_id))
            btn_del.pack(side = "right", padx = 2)

            if drone.get_status() == "IDLE" and drone.get_battery_level() > 0:
                btn_assign_mission = ctk.CTkButton(row_frame, text="Assign Mission", fg_color="blue", width=50, 
                                                    command=lambda d_id = drone.get_id():self._open_drone_assign_mission(d_id))
                btn_assign_mission.pack(side="right", padx=2)

    def _refresh_parcel_list(self):
        for widget in self.parcel_list_frame.winfo_children():
            widget.destroy()

        parcels = self._logistic_service.get_parcels()
        for parcel in parcels:
            if parcel.get_status() != "DELIVERED":
                row_frame = ctk.CTkFrame(self.parcel_list_frame, fg_color="transparent")
                row_frame.pack(fill = "x", pady = 2)

                is_locked = True if parcel.get_status() != "PENDING" else False
                btn_del = ctk.CTkButton(row_frame, text = "Delete", fg_color="grey" if is_locked else "red", width=50, 
                                        state = "disabled" if is_locked else "normal",
                                        command=lambda p_id = parcel.get_id(): self._handle_parcel_delete_by_id(p_id))
                btn_del.pack(side = "right", padx = 2)

                btn_update = ctk.CTkButton(row_frame, text = "Update", fg_color="grey" if is_locked else "purple", width=50,
                                           state = "disabled" if is_locked else "normal",
                                           command=lambda p_id = parcel.get_id(): self._open_parcel_edit_window(p_id))
                btn_update.pack(side="right", padx=2)

                if parcel.get_status() == "PENDING":
                    btn_start_mission = ctk.CTkButton(row_frame, text="Start Mission", fg_color="blue", width=50, 
                                                        command=lambda p_id = parcel.get_id():self._open_parcel_assign_mission(p_id))
                    btn_start_mission.pack(side="right", padx=2)

                row_text = f"""ID : {parcel.get_id()} | Recipient Name : {parcel.get_recipient_name()} | Delivery Adress : {parcel.get_delivery_address()} |
                    Weight : {parcel.get_weight()}kg | Distance : {parcel.get_distance()} km | Priority : {parcel.get_priority()} | Status : {parcel.get_status()}"""
                label = ctk.CTkLabel(row_frame, text = row_text)
                label.pack(side = "left", padx = 10)

    def _refresh_mission_list(self):
        for widget in self.mission_list_frame.winfo_children():
            widget.destroy()

        missions = self._logistic_service.get_missions()
        for mission in missions:
            row_frame = ctk.CTkFrame(self.mission_list_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady = 2)

            btn_change_status = ctk.CTkButton(row_frame, text="Update Status", fg_color="green", width=50, command=lambda m_id = mission.get_id(): self._open_mission_edit_window(m_id))
            btn_change_status.pack(side = "right", padx = 2)

            row_text = f"""ID : {mission.get_id()} | Drone ID : {mission.get_drone_id()} | Parcel ID : {mission.get_parcel_id()} |
                Start Time : {mission.get_start_time()} | Status : {mission.get_status()}"""
            label = ctk.CTkLabel(row_frame, text = row_text)
            label.pack(side = "left", padx = 10)

    def _open_drone_edit_window(self, drone_id : int):
        if hasattr(self, 'edit_window') and self.edit_window.winfo_exists():
            self.edit_window.focus()
            return
        self.edit_window = EditDroneWindow(self, drone_id, self._drone_service, self._refresh_drone_list)

    def _open_parcel_edit_window(self, parcel_id : int):
        if hasattr(self, "edit_window") and self.edit_window.winfo_exists():
            self.edit_window.focus()
            return
        self.edit_window = EditParcelWindow(self, parcel_id,  self._logistic_service, self._refresh_parcel_list)

    def _open_mission_edit_window(self,mission_id : int):
        if hasattr(self, 'edit_window') and self.edit_window.winfo_exists():
            self.edit_window.focus()
            return
        self.edit_window = EditMissionStatusWindow(self, mission_id, self._logistic_service, self._refresh_mission_list)

    def _open_drone_assign_mission(self, drone_id : int):
        if hasattr(self, "assign_drone_mission") and self.assign_drone_mission.winfo_exists():
            self.assign_drone_mission.focus()
            return
        self.assign_drone_mission = AssignDroneMissionWindow(self, drone_id, self._drone_service, self._logistic_service, 
                                                             self._refresh_drone_list, self._refresh_mission_list, self._refresh_parcel_list)
        
    def _open_parcel_assign_mission(self, parcel_id : int):
        if hasattr(self, "assign_parcel_mission") and self.assign_drone_mission.winfo_exists():
            self.assign_parcel_mission.focus()
            return
        
        self.assign_drone_mission = AssignParcelMissionWindow(self, parcel_id, self._drone_service, self._logistic_service, 
                                                             self._refresh_drone_list, self._refresh_mission_list, self._refresh_parcel_list)

    def _handle_drone_delete_by_id(self, drone_id : int):
        if messagebox.askyesno(title="Confirm", message=f"Are you sure you want to delete drone with id {drone_id}?"):
            try:
                self._drone_service.remove_drone(drone_id)
                messagebox.showinfo(title="Success", message="Drone removed succesfully")
                self._refresh_drone_list()
            except IDNotFound as idnf:
                messagebox.showerror(title="ERROR", message=f"{idnf}")
            except Exception as e:
                messagebox.showerror(title="ERROR", message=f"{e}")
            except DroneInFlight as din:
                messagebox.showerror(title="ERROR", message=f"{din}")

    def _handle_parcel_delete_by_id(self, parcel_id : int):
        if messagebox.askyesno(title="Confirm", message=f"Are you sure you want to delete parcel with id {parcel_id}?"):
            try:
                self._logistic_service.remove_parcel(parcel_id)
                messagebox.showinfo(title="Success", message="Parcel removed succesfully")
                self._refresh_parcel_list()
            except IDNotFound as idnf:
                messagebox.showerror(title="ERROR", message=f"{idnf}")
            except Exception as e:
                messagebox.showerror(title="ERROR", message=f"{e}")

    def _handle_see_history(self):
        if hasattr(self, "history_window") and self.history_window.winfo_exists():
            self.history_window.focus()
            return
        
        self.history_window = HistoryWindow(self, self._logistic_service)

    def run(self):
        self.mainloop()

class EditDroneWindow(ctk.CTkToplevel):
    def __init__(self, parent, drone_id, drone_service, on_close_callback):
        super().__init__(parent)
        self._drone_service = drone_service
        self._drone_id = drone_id
        self._on_close_callback = on_close_callback
        
        self.title(f"Update Drone with ID {drone_id}")
        self.geometry("400x400")
        
        self._current_drone = self._drone_service.search_by_id(drone_id)
        
        self._label = ctk.CTkLabel(self, text = f"Editing Drone {drone_id}", font=("Arial", 12, "bold"))
        self._label.pack(pady=10)

        self._new_serial_number = ctk.CTkEntry(self, placeholder_text="Serial Number")
        self._new_serial_number.insert(0, self._current_drone.get_serial_number())
        self._new_serial_number.pack(pady=5)

        self._new_model_type = ctk.CTkEntry(self, placeholder_text="Model Type")
        self._new_model_type.insert(0, self._current_drone.get_model_type())
        self._new_model_type.pack(pady=5)

        self._new_max_payload = ctk.CTkEntry(self, placeholder_text="Max Payload")
        self._new_max_payload.insert(0, self._current_drone.get_max_payload())
        self._new_max_payload.pack(pady=5)

        self._new_battery_level = ctk.CTkEntry(self, placeholder_text="Battery Level")
        self._new_battery_level.insert(0, self._current_drone.get_battery_level())
        self._new_battery_level.pack(pady = 5)

        self._new_status = ctk.CTkEntry(self, placeholder_text="Status")
        self._new_status.insert(0, self._current_drone.get_status())
        self._new_status.pack(pady=5)

        self._save_button = ctk.CTkButton(self, text="Save Changes", fg_color="Green", command=self._save_edit_changes)
        self._save_button.pack(pady=20)

    def _save_edit_changes(self):
        try:
            serial_number = self._new_serial_number.get()
            model_type = self._new_model_type.get()
            max_payload = float(self._new_max_payload.get())
            status = self._new_status.get()
            battery_level = int(self._new_battery_level.get())
            status = status.upper()
            if status != "IDLE" and status != "IN_FLIGHT" and status != "MAINTENANCE":
                messagebox.showwarning(title="Incorrect Status", message="Status of Drone is incorrect, please try again")
                return
            if max_payload <= 0:
                messagebox.showwarning(title="Value Error", message="Drone Max Payload must be greater than 0")
                return
            if battery_level < 0:
                messagebox.showwarning(title="Value Error", message="Drone Battery Level must be positive")
                return
            if battery_level > 100:
                messagebox.showwarning(title="Value Error", message="Maximum battery level is 100")
                return
            self._drone_service.update_drone(self._drone_id, serial_number, model_type, max_payload, status, battery_level)
            messagebox.showinfo("Success", "Succesfully updated the drone")
            self.destroy()
            self._on_close_callback()
            self.destroy()
        except IDNotFound as idnf:
            messagebox.showerror("ERROR", str(idnf))
        except ValueError as ve:
            messagebox.showerror("ERROR", f"Invalid Inputs {ve}")
        except DroneInFlight as dif:
            messagebox.showerror("ERROR", str(dif))

class EditParcelWindow(ctk.CTkToplevel):
    def __init__(self, parent, parcel_id, logistic_service, on_close_callback):
        super().__init__(parent)
        self._logistic_service = logistic_service
        self._parcel_id = parcel_id
        self._on_close_callback = on_close_callback
        
        self.title(f"Update Parcel with ID {parcel_id}")
        self.geometry("400x400")
        
        self._current_parcel = self._logistic_service.search_by_id(parcel_id)
        
        self._label = ctk.CTkLabel(self, text = f"Editing Parcel {parcel_id}", font=("Arial", 12, "bold"))
        self._label.pack(pady=10)

        self._new_recipient_name = ctk.CTkEntry(self, placeholder_text="Recipient Name")
        self._new_recipient_name.insert(0, self._current_parcel.get_recipient_name())
        self._new_recipient_name.pack(pady=5)

        self._new_delivery_address = ctk.CTkEntry(self, placeholder_text="Delivery Address")
        self._new_delivery_address.insert(0, self._current_parcel.get_delivery_address())
        self._new_delivery_address.pack(pady=5)

        self._new_weight = ctk.CTkEntry(self, placeholder_text="Weight (kg)")
        self._new_weight.insert(0, self._current_parcel.get_weight())
        self._new_weight.pack(pady=5)

        self._new_distance = ctk.CTkEntry(self, placeholder_text="Distance (km)")
        self._new_distance.insert(0, self._current_parcel.get_distance())
        self._new_distance.pack(pady=5)

        self._new_priority = ctk.CTkEntry(self, placeholder_text="Priority")
        self._new_priority.insert(0, self._current_parcel.get_priority())
        self._new_priority.pack(pady=5)

        self._new_status = ctk.CTkEntry(self, placeholder_text="Status")
        self._new_status.insert(0, self._current_parcel.get_status())
        self._new_status.pack(pady=5)

        self._save_button = ctk.CTkButton(self, text="Save Changes", fg_color="Green", command=self._save_edit_changes)
        self._save_button.pack(pady=20)

    def _save_edit_changes(self):
        try:
            recipient_name = self._new_recipient_name.get()
            delivery_address = self._new_delivery_address.get()
            weight = float(self._new_weight.get())
            distance = float(self._new_distance.get())
            priority = self._new_priority.get()
            status = self._new_status.get()
            priority = priority.upper()
            if priority != "HIGH" and priority != "STANDARD":
                messagebox.showwarning(title="Incorrect Priority", message="Priority of Parcel is incorrect, please try again (HIGH, STANDARD)")
                return
            status = status.upper()
            if status != "DELIVERED" and status != "PENDING" and status != "ASSIGNED":
                messagebox.showwarning(title="Incorrect Status", message="Status of Parcel is incorrect, please try again (DELIVERED, ASSIGNED, PENDING)")
                return
            if weight <= 0:
                messagebox.showwarning(title="Value Error", message="Parcel weight must be greater than 0")
                return
            if distance <= 0:
                messagebox.showwarning(title="Value Error", message="Parcel distance must be greater than 0")
                return
            self._logistic_service.update_parcel(self._parcel_id, recipient_name, delivery_address, weight, priority,status,distance)
            messagebox.showinfo("Success", "Succesfully updated the parcel")
            self.destroy()
            self._on_close_callback()
            self.destroy()
        except IDNotFound as idnf:
            messagebox.showerror("ERROR", str(idnf))
        except ValueError as ve:
            messagebox.showerror("ERROR", f"Invalid Inputs {ve}")

class EditMissionStatusWindow(ctk.CTkToplevel):
    def __init__(self, parent, mission_id, logistic_service, on_close_callback):
        super().__init__(parent)
        self._mission_id = mission_id
        self._logistic_service = logistic_service
        self._on_close_callback = on_close_callback

        self.title(f"Editing Mission {mission_id} Status")
        self.geometry("400x400")

        label = ctk.CTkLabel(self, text="Select the new status of the mission")
        label.pack(pady=10)

        self._new_status = ctk.CTkComboBox(self, values=["FAILED", "DELIVERED"])
        self._new_status.pack(pady = 5)

        self._save_button = ctk.CTkButton(self, text = "Save Changes", fg_color="green", command=self._save_status_change)
        self._save_button.pack(pady=20)

    def _save_status_change(self):
        try:
            new_status = self._new_status.get()
            if new_status != "FAILED" and new_status != "DELIVERED":
                messagebox.showerror("ERROR", "Status of mission is invalid, please try again")
                return
            self._logistic_service.modify_mission_status(self._mission_id, new_status)
            messagebox.showinfo("Success", "Succesfully updated the mission status")
            self.destroy()
            self._on_close_callback()
            self.destroy()
        except IDNotFound as idnf:
            messagebox.showerror("ERROR", str(idnf))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

class AssignDroneMissionWindow(ctk.CTkToplevel):
    def __init__(self, parent, drone_id, drone_service, logistic_service, drone_callback, mission_callback, parcel_callback):
        super().__init__(parent)
        self._drone_id = drone_id
        self._drone_service = drone_service
        self._logistic_service = logistic_service
        self._drone_callback = drone_callback
        self._mission_callback = mission_callback
        self._parcel_callback = parcel_callback

        self._drone = self._drone_service.search_by_id(drone_id)

        self.title(f"Assign Mission")
        self.geometry("400x400")
        self._setup_assign_mission()

    def _setup_assign_mission(self):
        self._label = ctk.CTkLabel(self, text=f"Assign a Mission to drone {self._drone_id}")
        self._label.pack(pady = 10)

        self._mission_id = ctk.CTkEntry(self, placeholder_text="MISSION ID")
        self._mission_id.pack(pady = 5)

        self._start_time = ctk.CTkEntry(self, placeholder_text="START TIME (YYYY-MM-DD HH-MM-SS")
        self._start_time.pack(pady = 5)

        self._parcel_list_frame = ctk.CTkScrollableFrame(self, height = 200)
        self._parcel_list_frame.pack(fill="x", padx = 10)
        self._refresh_parcel_list()

    def _refresh_parcel_list(self):
        for widget in self._parcel_list_frame.winfo_children():
            widget.destroy()

        parcels = self._logistic_service.get_parcels()
        ok = False
        for parcel in parcels:
            if parcel.get_weight() < self._drone.get_max_payload() and parcel.get_status() == "PENDING":
                ok = True
                row_frame = ctk.CTkFrame(self._parcel_list_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady = 2)

                btn_select = ctk.CTkButton(row_frame, width=50, fg_color="green", text="Select", 
                                           command=lambda p_id = parcel.get_id(): self._handle_assign_mission(p_id))
                btn_select.pack(side = "right", padx = 2)
                row_text = f"""ID : {parcel.get_id()} | Recipient Name : {parcel.get_recipient_name()} | Delivery Adress : {parcel.get_delivery_address()} |
                Weight : {parcel.get_weight()}kg | Distance : {parcel.get_distance()} | Priority : {parcel.get_priority()} | Status : {parcel.get_status()}"""
                label = ctk.CTkLabel(row_frame, text = row_text)
                label.pack(side = "left", padx = 10)
        if not ok:
            messagebox.showinfo(title="No Parcels Found", message=f"No pending parcels meet the payload capacity requirements of Drone with id{self._drone_id}")

    def _handle_assign_mission(self, parcel_id):
        if messagebox.askyesno(title="Confirm", message=f"Are you sure you want to assign parcel with id {parcel_id} to drone {self._drone_id}?"):
            try:
                id = int(self._mission_id.get())
                start_time = self._start_time.get()
                self._logistic_service.assign_a_mission_manually(id, self._drone_id, parcel_id, start_time)
                messagebox.showinfo(title="Success", message="Succesfully assigned the mission")
                self.destroy()
                self._mission_callback()
                self._drone_callback()
                self._parcel_callback()
            except IDNotFound as idnf:
                messagebox.showerror("ERROR", str(idnf))
            except DroneUnavailable as du:
                messagebox.showerror("ERROR", str(du))
            except ValueError as ve:
                messagebox.showerror("ERROR", f"Invalid Inputs {ve}")
            except WeightExceeded as we:
                messagebox.showerror("ERROR", str(we))
            except InvalidTime as it:
                messagebox.showerror("ERROR", str(it))
            except NotEnoughBattery as neb:
                messagebox.showerror("ERROR", str(neb))

class AssignParcelMissionWindow(ctk.CTkToplevel):
    def __init__(self, parent, parcel_id, drone_service, logistic_service, drone_callback, mission_callback,parcel_callback):
        super().__init__(parent)
        self._parcel_id = parcel_id
        self._drone_service = drone_service
        self._logistic_service = logistic_service
        self._drone_callback = drone_callback
        self._mission_callback = mission_callback
        self._parcel_callback = parcel_callback

        self._parcel = self._logistic_service.search_by_id(parcel_id)

        self.title(f"Assign Mission")
        self.geometry("400x400")
        self._setup_assign_mission()

    def _setup_assign_mission(self):
        self._label = ctk.CTkLabel(self, text=f"Assign a Mission to parcel {self._parcel_id}")
        self._label.pack(pady = 10)

        self._start_time = ctk.CTkEntry(self, placeholder_text="START TIME (YYYY-MM-DD HH-MM-SS)")
        self._start_time.pack(pady = 5)

        btn_complete = ctk.CTkButton(self, width=100, fg_color="green", text="Confirm", command=self._handle_assign_mission)
        btn_complete.pack(pady=(10,20))


    def _handle_assign_mission(self):
        try:
            start_time = self._start_time.get()
            drone_id = self._logistic_service.assign_a_mission_automatically(self._parcel_id, start_time)
            messagebox.showinfo(title="Success", message=f"Succesfully assigned the mission to drone {drone_id}")
            self.destroy()
            self._mission_callback()
            self._drone_callback()
            self._parcel_callback()
        except IDNotFound as idnf:
            messagebox.showerror("ERROR", str(idnf))
        except NoDroneAvailable as nda:
            messagebox.showerror("ERROR", str(nda))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))
        except InvalidTime as it:
            messagebox.showerror("ERROR", str(it))

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, logistic_service):
        super().__init__(parent)
        self._logistic_service = logistic_service
        self.title("Parcel History")
        self.geometry("400x400")
        self._parcel_history_frame = ctk.CTkScrollableFrame(self, height = 400)
        self._parcel_history_frame.pack(fill="x", padx = 10)
        self._show_parcel_history()

    def _show_parcel_history(self):
        for widget in self._parcel_history_frame.winfo_children():
            widget.destroy()

        parcels = self._logistic_service.get_delivered_parcels()
        for parcel in parcels:
            row_frame = ctk.CTkFrame(self._parcel_history_frame, fg_color="transparent")
            row_frame.pack(fill = "x", pady = 2)

            row_text = f"""ID : {parcel.get_id()} | Recipient Name : {parcel.get_recipient_name()} | Delivery Adress : {parcel.get_delivery_address()} |
            Weight : {parcel.get_weight()}kg | Priority : {parcel.get_priority()} | Status : {parcel.get_status()}"""
            label = ctk.CTkLabel(row_frame, text = row_text)
            label.pack(side = "left", padx = 10)
        
    






















