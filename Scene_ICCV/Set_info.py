"""
This module records driving-related signals (driver inputs, vehicle state,
take-over flags, collision info, …) into a CSV file at a fixed rate.

Core classes / functions
------------------------
• `Info`      – collects data continuously in a background thread.
• `dict_0`    – the main in-memory store before dumping to CSV.
"""

from vehicle_method import *       # utility helpers (get_speed, …)
import threading
import csv
import time
import math

# --------------------------------------------------------------------- #
# In-memory data container – every key maps to a growing list.
# --------------------------------------------------------------------- #
dict_0 = {
    "time": [],              # timestamp (s)
    "steering": [],          # steering-wheel angle
    "accelerator": [],       # accelerator pedal position
    "brake": [],             # brake pedal position
    # "main_car_dev": [],    # lane deviation if you need it
    "TOR_flag": [],          # 0 = no take-over, 1 = take-over request issued
    "Handchange_flag": [],   # driver switched to manual control?
    "Collision_flag": [],    # 0 = no collision, otherwise collider ID
}

# --------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------- #
def get_vehicle_yaw(vehicle):
    """Return vehicle yaw in radians within [0, 2π)."""
    yaw_deg = vehicle.get_transform().rotation.yaw
    return math.radians(yaw_deg % 360)


def get_lane_deviation(vehicle):
    """Distance between vehicle location and lane center (m)."""
    vehicle_location = vehicle.get_location()
    waypoint = world.get_map().get_waypoint(vehicle_location)
    lane_center = waypoint.transform.location
    return vehicle_location.distance(lane_center)


# --------------------------------------------------------------------- #
# Data-logging class
# --------------------------------------------------------------------- #
class Info:
    """
    Collects information from a list of CARLA vehicles and driver input
    devices, then dumps everything to CSV when `save_info()` is called.

    Parameters
    ----------
    dict_index : list[str]
        Short identifiers for each vehicle (e.g. ['ego', 'npc1', …]).
    dict_0 : dict[str, list]
        The master dictionary that stores column → list.
    file_name : str
        CSV file path to write when finished.
    fps : int, optional
        Target logging frequency in Hz (default 60).  The actual sleep
        interval is slightly offset (`+70` trick) to fine-tune overhead.
    """

    def __init__(self, dict_index, dict_0, file_name, fps: int = 60):
        self.car_list = []              # list[carla.Vehicle]
        self.flag = True                # controls the background loop
        self.dict_index = dict_index
        self.dict_0 = dict_0
        self.fps = fps
        self.file_name = file_name

        # flags updated by the main program
        self.TOR_flag = 0
        self.Handchange_flag = 0
        self.Collision_flag = 0

    # ----------------------------------------------------------------- #
    # Start background thread
    # ----------------------------------------------------------------- #
    def get_info(self):
        """Launch a thread that samples data until `self.flag` is False."""

        def _loop():
            while self.flag:
                # --- driver inputs ------------------------------------ #
                self.dict_0["time"].append(round(time.time(), 3))
                steering, accelerator, brake = get_sensor_data()
                self.dict_0["steering"].append(steering)
                self.dict_0["accelerator"].append(accelerator)
                self.dict_0["brake"].append(brake)

                # --- global flags ------------------------------------- #
                self.dict_0["TOR_flag"].append(self.TOR_flag)
                self.dict_0["Collision_flag"].append(self.Collision_flag)
                self.dict_0["Handchange_flag"].append(self.Handchange_flag)

                # --- per-vehicle data --------------------------------- #
                for idx, car in enumerate(self.car_list):
                    tag = self.dict_index[idx]          # e.g. 'ego'
                    loc = car.get_location()
                    acc = car.get_acceleration()
                    rot = car.get_transform().rotation

                    # initialise column lists the first time we see them
                    if self.dict_0.get(f"{tag}_id") is None:
                        self.dict_0[f"{tag}_id"] = [car.id]
                        self.dict_0[f"{tag}_x"] = [loc.x]
                        self.dict_0[f"{tag}_y"] = [loc.y]
                        self.dict_0[f"{tag}_z"] = [loc.z]
                        self.dict_0[f"{tag}_speed(km/h)"] = [get_speed(car)]
                        self.dict_0[f"{tag}_accx"] = [acc.x]
                        self.dict_0[f"{tag}_accy"] = [acc.y]
                        self.dict_0[f"{tag}_pitch"] = [rot.pitch]
                        self.dict_0[f"{tag}_yaw"] = [rot.yaw]
                        self.dict_0[f"{tag}_roll"] = [rot.roll]
                    else:
                        self.dict_0[f"{tag}_id"].append(car.id)
                        self.dict_0[f"{tag}_x"].append(loc.x)
                        self.dict_0[f"{tag}_y"].append(loc.y)
                        self.dict_0[f"{tag}_z"].append(loc.z)
                        self.dict_0[f"{tag}_speed(km/h)"].append(get_speed(car))
                        self.dict_0[f"{tag}_accx"].append(acc.x)
                        self.dict_0[f"{tag}_accy"].append(acc.y)
                        self.dict_0[f"{tag}_pitch"].append(rot.pitch)
                        self.dict_0[f"{tag}_yaw"].append(rot.yaw)
                        self.dict_0[f"{tag}_roll"].append(rot.roll)

                # control sampling frequency
                time.sleep(round(1 / (self.fps + 70), 12))

        threading.Thread(target=_loop, daemon=True).start()

    # ----------------------------------------------------------------- #
    # Dump to CSV
    # ----------------------------------------------------------------- #
    def save_info(self):
        """Stop logging and write the entire dictionary to a CSV file."""
        self.flag = False

        # pad shorter columns with None so every list has equal length
        max_len = max(len(v) for v in self.dict_0.values())
        for key, lst in self.dict_0.items():
            self.dict_0[key] = [None] * (max_len - len(lst)) + lst

        with open(self.file_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.dict_0.keys())           # header row
            writer.writerows(zip(*self.dict_0.values()))  # data rows
