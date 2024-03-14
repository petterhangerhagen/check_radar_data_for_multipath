"""
Script Title: Multi Path
Author: Petter Hangerhagen
Email: petthang@stud.ntnu.no
Date: February 27, 2024
Description: This script contains the classes and functions that are used to check for multi path in the radar tracking pipeline.
It checks for MultiPathParents in the measurements, and then checks for MultiPathChildren that are inside the sector of the MultiPathParent.
If a valid multi path is found, the MultiPath object is created, and the multi path is visulaized.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import re


class MultiPathParent:
    def __init__(self):
        self.timestamp = 0
        self.x = 0
        self.y = 0
        self.r = 0
        self.theta_min = 0
        self.theta_max = 0
        self.theta = 0
        self.cluster_area = 0
        self.error_margin_degrees = 6
        self.error_margin_radians = np.deg2rad(self.error_margin_degrees)
    
    def add_measurement(self, timestamp, measurement):
        self.timestamp = timestamp
        self.x = measurement[0]
        self.y = measurement[1]
        self.cluster_area = measurement[2]
        self.polygon_xs = measurement[3]
        self.polygon_ys = measurement[4]

        # polar coordinates
        self.r = np.sqrt(self.x**2 + self.y**2)
        self.theta = np.arctan2(self.y, self.x)
        
        self.theta_min = self.theta - self.error_margin_radians
        self.theta_max = self.theta + self.error_margin_radians

    def plot_parent(self,ax, multi_path_num, origin_x=0, origin_y=0):
        ax.plot(self.x + origin_x, self.y + origin_y, marker="o", color="#1f77b4")
        poly_x = np.array(self.polygon_xs) + origin_x
        poly_y = np.array(self.polygon_ys) + origin_y
        ploy = plt.Polygon(np.array([poly_x,poly_y]).T, closed=True, fill=True, edgecolor='#1f77b4', facecolor='#1f77b4', alpha=0.1,linewidth=3)
        ax.add_patch(ploy)
        if multi_path_num == 0:
            ax.plot([origin_x, origin_x + 130*np.cos(self.theta_min)], [origin_y, origin_y + 130 * np.sin(self.theta_min)], color="#1f77b4", linestyle="--")
        elif multi_path_num == 1:
            ax.plot([origin_x, origin_x + 130*np.cos(self.theta_max)], [origin_y, origin_y + 130 * np.sin(self.theta_max)], color="#1f77b4", linestyle="--")
            
    def __repr__(self) -> str:
        return f"MultiPathParent: x = {self.x:.2f}, y = {self.y:.2f}, r = {self.r:.2f}, theta = {self.theta:.2f}, cluster_area = {self.cluster_area:.2f}"

class MultiPathChild:
    def __init__(self, measurement):
        self.x = measurement[0]
        self.y = measurement[1]
        self.r = np.sqrt(self.x**2 + self.y**2)
        self.theta = np.arctan2(self.y, self.x)

    def plot_child(self, ax, origin_x=0, origin_y=0):
        ax.plot(self.x + origin_x, self.y + origin_y, marker="o", color="#ff7f0e")
        

    def __repr__(self) -> str:
        return f"MultiPathChild: x = {self.x:.2f}, y = {self.y:.2f}, r = {self.r:.2f}, theta = {self.theta:.2f}"

class MultiPath:
    def __init__(self):
        self.multi_path_scenarios = {}
        

    def add_multi_path(self, multi_path_parent, multi_path_child):
        if not multi_path_parent.timestamp in self.multi_path_scenarios:
            self.multi_path_scenarios[multi_path_parent.timestamp] = []
            self.multi_path_scenarios[multi_path_parent.timestamp].append(multi_path_parent)

        self.multi_path_scenarios[multi_path_parent.timestamp].append(multi_path_child)

    def get_number_of_parents(self):
        return len(self.multi_path_scenarios.keys())
    
    def get_number_of_children(self):
        number_of_children = 0
        for timestamp, multi_path_scenario in self.multi_path_scenarios.items():
            for multi_path_elm in multi_path_scenario:
                if isinstance(multi_path_elm, MultiPathChild):
                    number_of_children += 1
        return number_of_children

    def __repr__(self) -> str:
        temp_str = ""
        for timestamp, multi_path_scenario in self.multi_path_scenarios.items():
            temp_str += f"Timestamp: {timestamp:.2f}\n"
            for multi_path_elm in multi_path_scenario:
                temp_str += f"{multi_path_elm}\n"
        return temp_str
    
    def plot_multi_path(self, ax, origin_x=0, origin_y=0):
        number_of_multi_paths = len(self.multi_path_scenarios.keys())
        multi_path_num = None
        for k, (timestamp, multi_path_scenario) in enumerate(self.multi_path_scenarios.items()):
            if k == 0:
                multi_path_num = 0
            elif k == number_of_multi_paths - 1:
                multi_path_num = 1
            else:
                multi_path_num = None

            for multi_path in multi_path_scenario:
                if isinstance(multi_path, MultiPathParent):
                    multi_path.plot_parent(ax,multi_path_num, origin_x, origin_y)
                else:
                    multi_path.plot_child(ax, origin_x, origin_y)

    def valid_multi_path(self):
        if len(self.multi_path_scenarios.keys()) > 3:
            return True


def check_for_multi_path(measurements_dict):
    # Tunable parameters
    lenght_from_origin_threshold = 50
    cluster_area_threshold = 150
    
    # Find multipath parents
    potential_multi_paths = []
    for timestamp, measurements in measurements_dict.items():
        if timestamp == "Info":
            continue
    
        multi_path_parent = MultiPathParent()
        for measurement in measurements:
            lenght_from_origin = np.sqrt(measurement[0]**2 + measurement[1]**2)
            cluster_area = measurement[2]
            if lenght_from_origin < lenght_from_origin_threshold:
                
                if cluster_area > cluster_area_threshold:
                    multi_path_parent.add_measurement(timestamp, measurement)
                    potential_multi_paths.append(multi_path_parent)

    # Verify multipath parents by finding multipath children                
    multi_path = MultiPath()
    for multi_path_parent in potential_multi_paths:
        timestamp = multi_path_parent.timestamp

        measurment_inside_sector = []
        for measurements in measurements_dict[timestamp]:
            multi_path_child = MultiPathChild(measurements)


            if multi_path_parent.theta_min < multi_path_child.theta < multi_path_parent.theta_max:
                if multi_path_child.r > multi_path_parent.r:
                    measurment_inside_sector.append(multi_path_child)
                    multi_path.add_multi_path(multi_path_parent, multi_path_child)


    if multi_path.valid_multi_path():
        return multi_path
    else:
        return None
