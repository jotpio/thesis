from scipy import signal
from util import rolling_mean_data
from scipy.ndimage import uniform_filter1d
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
        return v
    return v / norm

def find_turning_points(robot_positions, target_positions, robot_directions, rolling_mean=False):
    # calcalate direction towards target
    directions_to_target = [normalize(tpos - rpos) for (rpos, tpos) in zip(robot_positions, target_positions)]
    # get magnitude of diff of direction to target and direction of robot
    magnitude_of_diff_dir_to_target_and_dir_robot = [np.linalg.norm(dirtotar-rdir, axis=0) for (rdir,dirtotar) in zip(robot_directions, directions_to_target)]
    
    # rolling mean to smooth data and find more meaningful peaks -> better turning points
    if rolling_mean:
        #magnitude_of_diff_dir_to_target_and_dir_robot = rolling_mean_data(magnitude_of_diff_dir_to_target_and_dir_robot, window_size=3)
        magnitude_of_diff_dir_to_target_and_dir_robot = uniform_filter1d(magnitude_of_diff_dir_to_target_and_dir_robot, size=5)
    
    return magnitude_of_diff_dir_to_target_and_dir_robot

def flatten_plateau_rolling_window(array, window_size, threshold):
    '''
        Flatten parts of data where it does not change much
    '''
    flattened_array = list(array)
    if window_size <= 1:
        return flattened_array
    #print(flattened_array, window_size, threshold)
    # iterate over array, find plateaus and average all values in plateau
    for id_point, point in enumerate(flattened_array):
        if id_point+window_size < len(flattened_array):
            window_array = flattened_array[id_point:id_point+window_size]
            if np.std(window_array) < threshold:
                flattened_array[id_point:id_point+window_size] = [np.mean(window_array)] * window_size
        else:
            last_window = flatten_plateau_rolling_window(flattened_array[id_point:len(array)], window_size-1, threshold)
            try:
                array[id_point:len(flattened_array)-1] = last_window
            except Exception:
                print(flattened_array[id_point:len(flattened_array)-1], last_window)
            break
            
                
    return flattened_array


def flatten_plateaus(array, threshold):
    flattened_array = list(array)
    #iterate though data, find plateaus and level them
    current_plateau = []
    current_plateau_ids = []
    for id_point, point in enumerate(flattened_array):
        if not current_plateau:
            current_plateau.append(point)
            current_plateau_ids = [id_point, id_point] #[start id, end id]
            continue
        else:
            current_plateau.append(point)
            if np.std(current_plateau) > threshold:
                # add old pleateau
                current_plateau = current_plateau[:-1]
                flattened_array[current_plateau_ids[0]:current_plateau_ids[1]+1] = [np.mean(current_plateau)] * len(current_plateau)
                
                # new plateau
                current_plateau = [point]
                current_plateau_ids = [id_point, id_point]
            else:
                current_plateau_ids[1] = id_point
                
            # check if at end and if so add current plateau to flattened array
            if id_point == len(flattened_array)-1:
                flattened_array[current_plateau_ids[0]:current_plateau_ids[1]+1] = [np.mean(current_plateau)] * len(current_plateau)
                continue
            
    return flattened_array

def get_run_turns(all_fish_pos_this_run, fish1_pos_this_run, robot_pos_run, robot_dir_run, plot=False):
    turning_points = []
    dists_at_turning_points = []

    assert len(fish1_pos_this_run) == len(robot_pos_run), print(f"fish:{len(fish1_pos_this_run)}; robot:{len(robot_pos_run)}")
    run_target_dists = np.linalg.norm(np.array(fish1_pos_this_run)-np.array(robot_pos_run), axis=1)

    # flatten plateaus before finding peaks in metric robot direction - dir towards target
    metric_dir_robot_dir_tow_target = find_turning_points(robot_pos_run, fish1_pos_this_run, robot_dir_run, rolling_mean=True)
    flat_metric_dir_robot_dir_tow_target = np.array(flatten_plateaus(metric_dir_robot_dir_tow_target, threshold=0.1))
    # get valley points towards target
    metric_peaks, metric_peaks_properties = signal.find_peaks(np.asarray(flat_metric_dir_robot_dir_tow_target), distance=3, prominence=0.1, plateau_size=1)
    #print(metric_peaks_properties)
    #number_of_turning_points.append(len(metric_peaks))

    # flatten plateaus before finding peaks in dist to target
    #flat_run_target_dists = np.array(flatten_plateaus(run_target_dists, window_size=5, threshold=50))
    flat_run_target_dists = np.array(flatten_plateaus(run_target_dists, threshold=30))
    target_dist_peaks, peaks_properties = signal.find_peaks(np.asarray(flat_run_target_dists), distance=3, prominence=10)

    # for each peak in target distance, find peak in metric_dir_robot_dir_tow_target shortly before that
    for id_peak, dist_peak in enumerate(target_dist_peaks):
        for peak_prop_zip in zip(metric_peaks, metric_peaks_properties['right_edges']):
            if np.abs(dist_peak - peak_prop_zip[0]) < 20 or np.abs(dist_peak - peak_prop_zip[1]) < 20:
                # found turn in metric
                turning_points.append(dist_peak)
                dists_at_turning_points.append(run_target_dists[dist_peak])
                break
    if plot:
        #plot
        fig = plt.figure(figsize=(10,5))
        ax1 = fig.add_subplot()
        ax2 = ax1.twinx()
        ax1.plot(metric_dir_robot_dir_tow_target, 'g-')
        ax1.plot(flat_metric_dir_robot_dir_tow_target, 'b-')
        ax1.scatter(metric_peaks,np.asarray(flat_metric_dir_robot_dir_tow_target)[metric_peaks],color='b')

        ax2.plot(run_target_dists, 'r-')
        ax2.plot(flat_run_target_dists, 'm-')
        #print(target_dist_peaks)
        ax2.scatter(target_dist_peaks, flat_run_target_dists[target_dist_peaks], color='m')
        ax2.scatter(turning_points, flat_run_target_dists[turning_points], color='r', s=100)

        ax1.set_xlabel('X timesteps (frames)')
        ax1.set_ylabel('Y1 magnitude of diff of dir robot and dir towards target', color='g')
        ax2.set_ylabel('Y2 distance robot target', color='m')
        plt.show()
        '''
        fig = plt.figure(num=date_key, figsize=(16,9))
        plt.xlim(0,2000)
        plt.ylim(0,2000)
        plt.scatter(robot_pos_run[0:20,0],robot_pos_ru[0:20,1], label="robot", s=2)
        plt.scatter(fish1_pos_this_run[0:20,0],fish1_pos_this_run[0:20,1], label="target", s=2)
        plt.quiver(robot_pos_run[0:20,0],robot_pos_run[0:20,1], robot_dir_run[0:20,0],robot_dir_run[0:20,1], width=0.001)
        plt.quiver(robot_pos_run[0:20,0],robot_pos_run[0:20,1], directions_to_target[0:20,0],directions_to_target[0:20,1], width=0.001, color="red")
        plt.legend()
        '''
    
    return turning_points, dists_at_turning_points