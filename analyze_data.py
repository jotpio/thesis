from scipy import signal
from util import rolling_mean_data, get_successful_runs, get_challenge_runs, get_fish_pos_per_run, get_fish_dir_per_run
from iterator_functions import forward_rolling_window_apply
from scipy.ndimage import uniform_filter1d
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
        return v
    return v / norm

def get_magnitude_of_diff_dir_to_target_and_dir_robot(robot_positions, target_positions, robot_directions, rolling_mean=False):
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

def get_run_turns_towards_target(fish1_pos_this_run, robot_pos_run, robot_dir_run, run_target_dists, plot=False):
    turning_points = []

    assert len(fish1_pos_this_run) == len(robot_pos_run), print(f"fish:{len(fish1_pos_this_run)}; robot:{len(robot_pos_run)}")

    # flatten plateaus before finding peaks in metric robot direction - dir towards target
    metric_dir_robot_dir_tow_target = get_magnitude_of_diff_dir_to_target_and_dir_robot(robot_pos_run, fish1_pos_this_run, robot_dir_run, rolling_mean=True)
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
    
    return turning_points


def calculate_tortuosity(dates_dict, only_successful=True, plot=False):
    all_dates_fish1_tortuosity_straightness_index = []
    all_dates_robot_tortuosity_straightness_index = []
    all_dates_fish1_sinuosity = []
    all_dates_robot_sinuosity = []

    for date_key in dates_dict:
        date_dict = dates_dict[date_key]
        fish_instance = date_dict["fish"]
        runs = date_dict["runs"]
        # filter runs
        if only_successful:
            runs, ids_runs = get_successful_runs(runs,date_dict["successful"])
        elif challenges:
            runs, ids_runs = get_challenge_runs(runs,date_dict["challenges"])
        else:
            runs = date_dict["runs"]
            ids_runs = list(range(len(runs)))

        # get pos for all fish for all timesteps
        if len(runs) > 0:
            fish_pos_runs = get_fish_pos_per_run(fish_instance,runs)
            fish_dir_runs = get_fish_dir_per_run(fish_instance,runs)
        else:
            print(f"No runs in {date_key}")
            continue

        # iterate runs
        date_fish1_tortuosity_straightness_index = []
        date_robot_tortuosity_straightness_index = []
        date_fish1_sinuosity = []
        date_robot_sinuosity = []

        for id_run, run in enumerate(runs):
            # get data
            all_fish_pos_this_run = fish_pos_runs[id_run]
            all_fish_dir_this_run = fish_dir_runs[id_run]
            fish1_pos_this_run = np.array([fish[0] for fish in all_fish_pos_this_run])
            fish1_dir_run = np.array([fish[0] for fish in all_fish_dir_this_run])
            robot_pos_run = np.array(date_dict['positions'][run[0]:run[1]+1])
            robot_dir_run = np.array(date_dict['orientation'][run[0]:run[1]+1])

            '''
            straightness index

            (distance_start_end_point / distance_traveled)
            '''
            # get dist to next pos per timestep
            fish1_dists_per_step = np.abs(np.linalg.norm(np.diff(fish1_pos_this_run),axis=1))
            robot_dists_per_step = np.abs(np.linalg.norm(np.diff(robot_pos_run),axis=1))
            # get distance traveled
            fish1_dist_traveled = np.sum(fish1_dists_per_step)
            robot_dist_traveled = np.sum(robot_dists_per_step)
            # get dist between start end end
            fish1_dist_start_end = np.abs(np.linalg.norm(fish1_pos_this_run[0]-fish1_pos_this_run[-1]))
            robot_dist_start_end = np.abs(np.linalg.norm(robot_pos_run[0]-robot_pos_run[-1]))
            # get tortuosity (track length / distance between start and end points)
            fish1_tortuosity_straightness_index = fish1_dist_start_end / fish1_dist_traveled if fish1_dist_traveled != 0 else 0
            robot_tortuosity_straightness_index = robot_dist_start_end / robot_dist_traveled if robot_dist_traveled !=0 else 0
            #
            date_fish1_tortuosity_straightness_index.append(fish1_tortuosity_straightness_index)
            date_robot_tortuosity_straightness_index.append(robot_tortuosity_straightness_index)

            '''
            sinuosity

            S = 2[p(((1 + c)/(1 - c)) + b^2)]^-0.5
            c is the mean cosine of turning angles
            b is the coefficient of variation of the step length
            p is the mean step length
            '''
            robot_calc_turn_angle = lambda x : np.arctan2(x[1][1], x[1][0]) - np.arctan2(x[0][1], x[0][0]) #difference between vec1 angle to x axis and vec2 angle to x axis

            #robot
            robot_turning_angles = forward_rolling_window_apply(robot_dir_run, window_size=2, function=robot_calc_turn_angle)
            for id_angle, angle in enumerate(robot_turning_angles): #normalize angles in to [-PI,PI]
                if angle > np.pi:
                    angle -= 2 * np.pi
                    robot_turning_angles[id_angle] = angle

                elif angle <= -np.pi:
                    angle += 2 * np.pi
                    robot_turning_angles[id_angle] = angle

            robot_cosines_of_turning_angles = np.cos(robot_turning_angles)
            robot_mean_cosine_of_turning_angles = np.mean(robot_cosines_of_turning_angles)
            robot_mean_step_length = np.mean(robot_dists_per_step)
            robot_coefficient_of_variation_of_step_length = np.std(robot_dists_per_step) / robot_mean_step_length

            c = robot_mean_cosine_of_turning_angles
            b = robot_coefficient_of_variation_of_step_length
            p = robot_mean_step_length
            robot_sinuosity = 2 * np.power(( p*( ((1+c)/(1-c)) + np.power(b,2) )),-0.5)

            #fish1
            fish1_dir_run = [np.radians(angle+180) for angle in fish1_dir_run]
            for id_angle, angle in enumerate(fish1_dir_run): #normalize angles in to [-PI,PI]
                if angle > np.pi:
                    angle -= 2 * np.pi
                    fish1_dir_run[id_angle] = angle

                elif angle <= -np.pi:
                    angle += 2 * np.pi
                    fish1_dir_run[id_angle] = angle
            fish1_calc_turning_angle = lambda x : x[1] - x[0]
            fish1_turning_angles = forward_rolling_window_apply(fish1_dir_run, window_size=2, function=fish1_calc_turning_angle)
            for id_angle, angle in enumerate(fish1_turning_angles): #normalize angles in to [-PI,PI]
                if angle > np.pi:
                    angle -= 2 * np.pi
                    fish1_turning_angles[id_angle] = angle

                elif angle <= -np.pi:
                    angle += 2 * np.pi
                    fish1_turning_angles[id_angle] = angle

            fish1_cosines_of_turning_angles = np.cos(fish1_turning_angles)
            fish1_mean_cosine_of_turning_angles = np.mean(fish1_cosines_of_turning_angles)
            fish1_mean_step_length = np.mean(fish1_dists_per_step)
            fish1_coefficient_of_variation_of_step_length = np.std(fish1_dists_per_step) / fish1_mean_step_length

            c = fish1_mean_cosine_of_turning_angles
            b = fish1_coefficient_of_variation_of_step_length
            p = fish1_mean_step_length
            fish1_sinuosity = 2 * np.power(( p*( ((1+c)/(1-c)) + np.power(b,2) )),-0.5)

            #
            date_fish1_sinuosity.append(fish1_sinuosity)
            date_robot_sinuosity.append(robot_sinuosity)

        all_dates_fish1_tortuosity_straightness_index.extend(date_fish1_tortuosity_straightness_index)
        all_dates_robot_tortuosity_straightness_index.extend(date_robot_tortuosity_straightness_index)
        all_dates_fish1_sinuosity.extend(date_fish1_sinuosity)
        all_dates_robot_sinuosity.extend(date_robot_sinuosity)
    if plot:
        # plot straightness index
        fig = plt.figure(figsize=(16,9))
        bins = np.linspace(0, 0.2, 100)
        plt.title("straightness index of robot and target fish path (distance_start_end_point / distance_traveled)")
        plt.hist(all_dates_fish1_tortuosity_straightness_index, bins=bins, color="b", alpha=0.5, label="fish1 straightness index")
        plt.hist(all_dates_robot_tortuosity_straightness_index, bins=bins, color="g", alpha=0.5, label="robot straightness index")
        plt.xlabel("straightness index (distance_start_end_point / distance_traveled)")
        plt.ylabel("number of runs")
        plt.legend()
        plt.show()

        # plot sinuosity
        fig = plt.figure(figsize=(16,9))
        bins = np.linspace(0, 0.1, 100)
        plt.title("sinuosity of robot and target fish path")
        plt.hist(all_dates_fish1_tortuosity_straightness_index, bins=bins, color="b", alpha=0.5, label="fish1 sinuosity")
        plt.hist(all_dates_robot_sinuosity, bins=bins, color="g", alpha=0.5, label="robot sinuosity")
        plt.xlabel("sinuosity")
        plt.ylabel("number of runs")
        plt.legend()
        plt.show()
    
    return all_dates_fish1_tortuosity_straightness_index, all_dates_robot_tortuosity_straightness_index, all_dates_fish1_sinuosity, all_dates_robot_sinuosity


def get_run_turns_curvature(timestamps_run, robot_pos_run, plot=False):
    # curvature: κ = |v_x a_y − v_y a_x| /(v_x^2 + v_y^2 )^(3/2)
    dt_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in timestamps_run]
    timedeltas_run = [delta.total_seconds() for delta in np.diff(dt_timestamps)]

    posxdeltas_run = np.diff(robot_pos_run[:,0])
    posydeltas_run = np.diff(robot_pos_run[:,1])

    velocity_x_run = posxdeltas_run / timedeltas_run
    velocity_y_run = posydeltas_run / timedeltas_run
    velocity_vectors_run = list(zip(velocity_x_run, velocity_y_run))
    
    speed_run = np.linalg.norm(velocity_vectors_run, axis=1) # magnitude of velocity vector is speed
    
    acceleration_x_run = np.diff(velocity_x_run) / timedeltas_run[0:-1]
    acceleration_y_run = np.diff(velocity_y_run) / timedeltas_run[0:-1]
    acceleration_vectors_run = list(zip(acceleration_x_run, acceleration_y_run))
    K1 = np.abs(velocity_x_run[0:-1] * acceleration_y_run - velocity_y_run[0:-1] * acceleration_x_run)
    K2 = np.power((np.power(velocity_x_run[0:-1],2)+np.power(velocity_y_run[0:-1],2)),(3/2))
    K = np.empty_like(K1)
    K[:] = np.nan
    K = np.divide(K1,K2, out=K, where=K2!=0)
    #print(np.isfinite(K).all())
    #print(K)
    #print(K1)
    #print(K2)
    # threshold: κth,robo = 0.02κ_mean + 0.98κ_min
    if not np.isnan(K).all():
        threshold = 0.02*np.nanmean(K) + 0.98*np.nanmin(K)
        peaks, peak_properties = signal.find_peaks(np.asarray(K), height=threshold, prominence=0.01)
    else:
        peaks, peak_properties = [], {}

    if plot:
        plt.figure(figsize=(16,5))
        plt.plot(K)
        plt.scatter(peaks, K[peaks],s=30,c='r')
        plt.axhline(threshold)
        plt.yscale("log")
        plt.show()
        
        plt.figure(figsize=(16,5))
        plt.plot(speed_run)
        plt.scatter(peaks, speed_run[peaks],s=30,c='r')
        #plt.axhline(threshold)
        #plt.yscale("log")
        plt.show()
        
        plt.figure(figsize=(10,10))
        plt.plot(robot_pos_run[:,0], robot_pos_run[:,1])
        plt.scatter(robot_pos_run[:,0][peaks],robot_pos_run[:,1][peaks], marker='o', color='r')
        plt.show()
    
    return peaks, peak_properties