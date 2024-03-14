import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

def plot(work_dir):
    fig, ax = plt.subplots(figsize=(11, 7.166666))
    data = np.load(f"{work_dir}/npy_files/occupancy_grid.npy",allow_pickle='TRUE').item()
    occupancy_grid = data["occupancy_grid"]
    origin_x = data["origin_x"]
    origin_y = data["origin_y"]
    colors = [(1, 1, 1), (0.8, 0.8, 0.8)]  # Black to light gray
    cm = LinearSegmentedColormap.from_list('custom_gray', colors, N=256)
    ax.imshow(occupancy_grid, cmap=cm, interpolation='none', origin='upper', 
              extent=[0, occupancy_grid.shape[1], 0, occupancy_grid.shape[0]])
    
    # Highlight origin
    ax.plot(origin_x, origin_y, c="red", marker="o", zorder=10, markersize=10)
    ax.annotate(f"Radar", (origin_x + 2, origin_y + 2), zorder=10, fontsize=15)
    
    display_second_occupancy_grid = True
    if display_second_occupancy_grid:
        # Load and display the second occupancy grid
        data2 = np.load(f"{work_dir}/npy_files/occupancy_grid_without_dilating.npy", allow_pickle=True).item()
        occupancy_grid2 = data2["occupancy_grid"]
        
        # Second imshow with alpha for overlap effect
        ax.imshow(occupancy_grid2, cmap="binary", interpolation='none', origin='upper', 
                extent=[0, occupancy_grid2.shape[1], 0, occupancy_grid2.shape[0]], alpha=0.2)
        
        # Create custom patches for legend
        # first_image_patch = mpatches.Patch(color='gray', label='True land')
        # second_image_patch = mpatches.Patch(color='black', alpha=0.2, label='Land after dilation')
        

        # Add legend
        # ax.legend(handles=[first_image_patch, second_image_patch], loc='upper left', fontsize=12)
        
    
    #N_min, N_max, E_min, E_max = find_track_limits(track_history)
    ax.set_xlim(origin_x-120,origin_x + 120)
    ax.set_ylim(origin_y-140, origin_y + 20)
    ax.set_aspect('equal')
    ax.set_xlabel('East [m]',fontsize=15)
    ax.set_ylabel('North [m]',fontsize=15)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.tight_layout()

    # reformating the x and y axis
    x_axis_list = np.arange(origin_x-120,origin_x+121,20)
    x_axis_list_str = []
    for x in x_axis_list:
        x_axis_list_str.append(str(int(x-origin_x)))
    plt.xticks(x_axis_list, x_axis_list_str)

    y_axis_list = np.arange(origin_y-140,origin_y+21,20)
    y_axis_list_str = []
    for y in y_axis_list:
        y_axis_list_str.append(str(int(y-origin_y)))
    plt.yticks(y_axis_list, y_axis_list_str) 

    ax.grid(True)    
    return fig, ax, origin_x, origin_y


def plot_measurements_in_background(measurement_dict,ax,origin_x=0,origin_y=0):
    for timestamp, measurements in measurement_dict.items():
        x = []
        y = []
        color = []
        for measurement in measurements:
            y.append(measurement[1] + origin_y)
            x.append(measurement[0] + origin_x)
            color.append(measurement[5])
        ax.scatter(x, y, c=color)


def plot_for_report(measurement_dict, multi_path_object, save_dir, filename, work_dir):

    fig, ax, origin_x, origin_y = plot(work_dir)
    plot_measurements_in_background(measurement_dict, ax, origin_x, origin_y)
 
    multi_path_object.plot_multi_path(ax, origin_x, origin_y)
    
    image_patch_1 = mlines.Line2D([], [], color="#1f77b4", marker='o', linestyle='None', label='Multipath parents')
    image_patch_2 = mpatches.Patch(color="#1f77b4" , label='Multipath parents cluster area', alpha=0.4)
    dashed_line = mlines.Line2D([], [], color='#1f77b4', linestyle='dashed', label='Multipath sector')
    image_patch_3 = mlines.Line2D([], [], color="#ff7f0e", marker='o', linestyle='None', label='Multipath childeren')
    ax.legend(handles=[image_patch_1, image_patch_2, dashed_line, image_patch_3], loc='upper left', fontsize=12)

    plt.savefig(f"{save_dir}/{filename[:-5]}.png",dpi=400)
    plt.close()
    print(f"Saved plot to {save_dir}/{filename[:-5]}.png")