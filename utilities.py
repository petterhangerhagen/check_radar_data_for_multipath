import numpy as np
import os
import glob
from matplotlib.cm import get_cmap
from shapely.geometry import Point

class Track:
    def __init__(self, track_id):
        self.track_id = track_id
        self.measurements = []

    def add_measurement(self, timestamp, x, y):
        self.measurements.append({'timestamp': timestamp, 'x': x, 'y': y})

    def sort_by_timestamp(self):
        self.measurements = sorted(self.measurements, key=lambda k: k['timestamp'])

    def calculate_distance(self):
        if len(self.measurements) < 2:
            return 0.0  # Distance is zero if there's only one measurement

        start_point = (self.measurements[0]['x'], self.measurements[0]['y'])
        end_point = (self.measurements[-1]['x'], self.measurements[-1]['y'])
        return euclidean_distance(start_point, end_point)
    
    def total_distance(self):
        total_distance = 0
        for i in range(len(self.measurements)-1):
            total_distance += euclidean_distance((self.measurements[i]['x'], self.measurements[i]['y']), (self.measurements[i+1]['x'], self.measurements[i+1]['y']))
        return total_distance

    def __repr__(self) -> str:
        temp_str = f"Track {self.track_id} with {len(self.measurements)} measurements\n"
        for measurement in self.measurements:
            temp_str += f"Timestamp: {measurement['timestamp']:.2f}, x: {measurement['x']:.2f}, y: {measurement['y']:.2f}\n"
        return temp_str  

def euclidean_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def nearest_neighbor(measurement_dict):
    measurement_distance_threshold = 10
    tracks = []
    track_counter = 0

    data = measurement_dict
    for timestamp in data:
        measurements = data[timestamp]

        if not tracks:
            for measurement in measurements:
                track = Track(track_counter)
                y = measurement[0]
                x = measurement[1]
                track.add_measurement(timestamp, x, y)
                tracks.append(track)
                track_counter += 1
            continue

        for measurement in measurements:
            distances = []
            y = measurement[0]
            x = measurement[1]
            for track in tracks:
                distances.append(euclidean_distance((track.measurements[-1]['x'], track.measurements[-1]['y']), (x, y)))
     
            if min(distances) < measurement_distance_threshold:
                tracks[distances.index(min(distances))].add_measurement(timestamp, x, y)
            else:
                track = Track(track_counter)
                track.add_measurement(timestamp, x, y)
                tracks.append(track)
                track_counter += 1

    return tracks

def filter_tracks(tracks):
    new_tracks = []
    not_stationary_objects = []
    track_ids = []
    for i, track in enumerate(tracks):
        track_ids.append(track.track_id)

    for i, track in enumerate(tracks):
        # want to draw a circle around the first track point, and if some other track point is outside of the circle, remove the track
        if len(track.measurements) < 2:
            continue
        start_point = (track.measurements[0]['x'], track.measurements[0]['y'])
        circle = Point(start_point[0], start_point[1]).buffer(30)
        for measurement in track.measurements:
            if not circle.contains(Point(measurement['x'], measurement['y'])):
                not_stationary_objects.append(track.track_id)
                break

    for track in tracks:
        if track.track_id in not_stationary_objects:
            new_tracks.append(track)
    return new_tracks

def convert_tracks_to_measurement_dict(tracks, old_measurement_dict):
    measurement_dict = {}
    # measurement_dict['Timestamp'] = ["x","y","area","polygon_xs","polygon_ys"]

    for i, track in enumerate(tracks):
        for measurement in track.measurements:
            timestamp = measurement['timestamp']
            if not timestamp in measurement_dict:
                measurement_dict[timestamp] = []
            # Need to find the corresponding measurement in the old measurement dict
            for old_measurement in old_measurement_dict[timestamp]:
                if (old_measurement[1], old_measurement[0]) == (measurement['x'], measurement['y']):
                    measurement_dict[timestamp].append(old_measurement)
                    break


    measurement_dict = dict(sorted(measurement_dict.items()))
    np.save("measurement_dict.npy", measurement_dict)   
    return measurement_dict

def add_color_scaling(measurement_dict):
    data = measurement_dict
    cmap = get_cmap('Greys')
    timestamps = []
    for timestamp, measurements in data.items():
        timestamps.append(timestamp)
    timestamps = np.asarray(timestamps)
    interval = (timestamps-timestamps[0]+timestamps[-1]/5)/(timestamps[-1]-timestamps[0]+timestamps[-1]/5)

    for timestamp, measurements in data.items():
        # Iterate over each measurement and assign a color based on position
        for index, measurement in enumerate(measurements):
            measurement_color = cmap(interval[timestamps == timestamp])

            # Append the color value to the measurement
            measurement.append(measurement_color.squeeze())
           

    return data

def write_filenames_to_txt(filename, txt_filename):
    """
    Writes the filename to the txt file, if the filename is not already written
    """
    with open(txt_filename, 'r') as f:
        lines = f.readlines()
    files = []
    for line in lines:
        files.append(line[:-1])

    already_written = False
    if os.path.basename(filename) in files:
        already_written = True
        print(f"File {os.path.basename(filename)} already written to txt file")

    if not already_written:
        with open(txt_filename, 'a') as f:
            f.write(os.path.basename(filename) + "\n")

def find_files(root,txt_filename):
    """
    Finds the files in the root directory that are given in the txt file
    """
    with open(txt_filename, 'r') as f:
        lines = f.readlines()
    files = []
    for line in lines:
        files.append(line[:-1])

    path_list = []
    for item in os.listdir(root):
        list_of_files = glob.glob(os.path.join(root, item, '*.json'))
        for file in list_of_files:
            if  os.path.basename(file) in files:
                path_list.append(file)

    return path_list

def make_new_directory(filename, work_dir):
    plotting_dir = f"{work_dir}/multi_path_plots"
    filename = filename[:-5]
    save_dir = os.path.join(plotting_dir,filename)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    return save_dir