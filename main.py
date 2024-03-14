
"""
Author: Petter Hangerhagen
Email: petthang@stud.ntnu.no
Date: February 27, 2024
Description: 
"""
import glob
import os
import import_data_from_json
import multi_path
import plotting
import utilities

"""
IMPORTANT: Need to change the radar_data_path and wokring_directory to the correct paths!!
"""
work_dir = "/home/aflaptop/Desktop/multi_path"
radar_data_path = "/home/aflaptop/Documents/radar_data"


def main():
    # root = f"{radar_data_path}/data_aug_15-18"
    # root = f"{radar_data_path}/data_aug_18-19"
    # root = f"{radar_data_path}/data_aug_22-23"
    # root = f"{radar_data_path}/data_aug_25-26-27"
    # root = f"{radar_data_path}/data_aug_28-29-30-31"
    # root = f"{radar_data_path}/data_sep_1-2-3-4-5-6-7"
    # root = f"{radar_data_path}/data_sep_8-9-11-14"
    # root = f"{radar_data_path}/data_sep_17-18-19-24"
    # path_list = glob.glob(os.path.join(root, '*.json'))
    # path_list = glob.glob(os.path.join(radar_data_path,'**' ,'*.json'))


    txt_filename = f"{work_dir}/multi_path_scenarios.txt"
    path_list = utilities.find_files(radar_data_path,txt_filename)

    path_list = [f"{radar_data_path}/data_aug_18-19/rosbag_2023-08-18-18-32-57.json"]
    
    for i, file_path in enumerate(path_list):
        if True:
            print(f"Processing file {i+1} of {len(path_list)}")
            filename = os.path.basename(file_path)
            print(f"File: {filename}")
            measurement_dict = import_data_from_json.import_data_from_json(file_path)
            measurement_dict.pop('Timestamp')
            
            multi_paths = multi_path.check_for_multi_path(measurement_dict)
            if multi_paths is not None:
                print("Multi path scenario")
                utilities.write_filenames_to_txt(file_path, txt_filename)

                save_dir = utilities.make_new_directory(filename, work_dir)
                measurement_dict = utilities.add_color_scaling(measurement_dict)
                tracks = utilities.nearest_neighbor(measurement_dict)
                tracks = utilities.filter_tracks(tracks)
                new_measurement_dict = utilities.convert_tracks_to_measurement_dict(tracks, measurement_dict)
                plotting.plot_for_report(new_measurement_dict, multi_paths, save_dir, filename)
               
            else:
                print("No multi path scenario")
            
        


if __name__ == "__main__":
    main()