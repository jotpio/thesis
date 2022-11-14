import os, re
import numpy as np
from datetime import datetime 
import glob
from deta import Deta

from datetime import date

def parse_number_array_from_string(string):
    pattern = r"([-+]?\d*\.\d*)" # match unsigned or signed floating point numbers
    string_numbers = re.findall(pattern, string)
    numbers = [float(number) for number in string_numbers]
    return numbers

def distance(pos1, pos2):
    return np.linalg.norm(np.array(pos1)-np.array(pos2))

def get_all_positions(dates_dict, challenges=False, successful=False):
    all_positions = []
    
    dates_keys = dates_dict.keys()
    
    for date_key in dates_keys:    
        date_dict = dates_dict[date_key]
        if successful:
            runs, _ = get_challenge_runs(date_dict["runs"], date_dict["successful"])
        elif challenges:
            runs, _ = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
        else:
            runs = date_dict["runs"]
        # combine positions
        for run in runs:
            run_positions = date_dict["positions"][run[0]:run[1]+1]
            all_positions.extend(run_positions)
            
    return all_positions


def find_corresponding_timestamp(timestamps, timestamp, current_lineid, timedelta=0.19, checkrange=30, checkall=False):    
    compare_ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
    #print(timestamp, current_lineid, timestamps[current_lineid])
    # check full timestamp array; start at current_lineid
    if checkall:
        for i in range(current_lineid, len(timestamps)):
            ts = datetime.strptime(timestamps[i], '%Y-%m-%d %H:%M:%S,%f')
            delta = np.abs((compare_ts - ts).total_seconds())
            #print(f"{timestamps[i]}")
            #print(delta, timedelta)
            if delta < timedelta:
                return i
            
        return -1 # not found
    
    # check only timestamp at current_lineid and next one
    else:
        return_id = -1
        for i in range(checkrange):
            if np.abs((compare_ts - datetime.strptime(timestamps[current_lineid+i], '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) < timedelta:
                return_id = current_lineid+i
                # print(f"Found timestamp ({current_lineid+i}) after {i} skipped timestamps!")
                break
        return return_id
    
    
    
    # time_differences = [np.abs((compare_ts - datetime.strptime(ts, '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) for ts in timestamps]
    # id_min = np.argmin(time_differences)
    # print(id_min)
    
def get_fish_pos_per_run(all_fish_pos, runs):
    fish_pos_all_runs = []
    if len(all_fish_pos) == 0:
        return []
    for id_run, run in enumerate(runs):
        fish_pos_run = []
        run_fish = all_fish_pos[run[0]:run[1]+1]
        
        for all_fish_in_ts in run_fish:
            fish_pos_ts = []
            for fish in all_fish_in_ts:
                if fish['id'] != 0:
                    fish_pos_ts.append(fish["position"])
                    
            # print(fish_pos_ts[0])
            fish_pos_run.append(fish_pos_ts)

        fish_pos_all_runs.append(fish_pos_run)

    return fish_pos_all_runs

def get_fish_following_per_run(all_fish, runs):
    fish_following_all_runs = []
    if len(all_fish) == 0:
        return []
    for id_run, run in enumerate(runs):
        fish_following_run = []
        run_fish = all_fish[run[0]:run[1]+1]
        
        for all_fish_in_ts in run_fish:
            fish_following_ts = []
            for fish in all_fish_in_ts:
                if fish['id'] != 0:
                    fish_following_ts.append(fish["following"])
                    
            # print(fish_pos_ts[0])
            fish_following_run.append(fish_following_ts)

        fish_following_all_runs.append(fish_following_run)

    return fish_following_all_runs

def get_challenge_runs(runs, challenges):
    '''
    both need to be same length
    '''
    if len(runs) >0 and len(challenges)>0 and len(runs) == len(challenges):
        challenge_runs = np.array(runs)[np.array(challenges)]
        ids_challenge_runs = np.argwhere(challenges).ravel()
        return challenge_runs, ids_challenge_runs
    else:
        return [], []
    
def get_successful_runs(runs, successful):
    '''
    both need to be same length
    '''
    if len(runs) >0 and len(successful)>0 and len(runs) == len(successful):
        successful_runs = np.array(runs)[np.array(successful)]
        ids_successful_runs = np.argwhere(successful).ravel()
        return successful_runs, ids_successful_runs
    else:
        print(f"No runs ({len(runs)}) or no successful runs  ({len(successful)}) or different size")
        return [], []

# https://stackoverflow.com/questions/5254838/calculating-distance-between-a-point-and-a-rectangular-box-nearest-point
def get_distance_to_goal(pos):
    # goal (x<750; y>1250)
    goal_min_x = 0
    goal_max_x = 750
    goal_min_y = 1250
    goal_max_y = 2000
    pos = np.array(pos)
    if pos.ndim == 1:
        dx = np.fmax(np.fmax(goal_min_x - pos[0], 0), pos[0] - goal_max_x)
        dy = np.fmax(np.fmax(goal_min_y - pos[1], 0), pos[1] - goal_max_y)
    elif pos.ndim == 2:
        dx = np.fmax(np.fmax(goal_min_x - pos[:,0], 0), pos[:,0] - goal_max_x)
        dy = np.fmax(np.fmax(goal_min_y - pos[:,1], 0), pos[:,1] - goal_max_y)
    else:
        assert False, "Dimensions of pos are wrong! not one or two dimensional"
    return np.sqrt(dx*dx + dy*dy)


def save_dates_to_npz(dates_dict, only_challenges=True):
    if only_challenges:
        filter_dates_dict_for_challenge_runs(dates_dict)
    
    # save day by day into npy files
    for key in dates_dict.keys():
        date = dates_dict[key]
        if only_challenges:
            file_name = f".\loaded_data\challenges_dates_dict_{key}.npy"
        else:
            file_name = f".\loaded_data\dates_dict_{key}.npy"
        print(f"Saving {key} to {file_name}")
        np.save(file_name, date, allow_pickle=True)
        
def load_dates_from_npz(start_date, end_date, only_challenges=True, local=True, remote_files=None, drive=None):
    # load dates from npy files
    print("Loading data from npz files.....")
    if local:
        current_working_dir = os.getcwd()
        current_dirname = os.path.basename(current_working_dir)
        if current_dirname == 'streamlit':
            if only_challenges:
                date_files = glob.glob(f".\..\loaded_data\challenges_dates_dict_*.npy")
            else:
                date_files = glob.glob(f".\..\loaded_data\dates_dict_*.npy")
        elif current_dirname == 'thesis':
            if only_challenges:
                date_files = glob.glob(f".\loaded_data\challenges_dates_dict_*.npy")
            else:
                date_files = glob.glob(f".\loaded_data\dates_dict_*.npy")
        else:
            print("Could not find loaded data in current working directory!")
            return None
        print(f"Date files {date_files}")
        dates_dict = dict()
        for date_file in date_files:
            date_key = date_file.split('\\')[-1].split('_')[-1].split('.')[0]

            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
            date_key_dt = datetime.strptime(date_key, "%Y-%m-%d")
            if start_date_dt <= date_key_dt and end_date_dt >= date_key_dt:
                print(f"Loading {date_key}")
                dates_dict[date_key] = np.load(date_file,allow_pickle=True).item()

        print(f"Loading done!")

        return dates_dict
    else:
        if remote_files is None:
            assert False
        dates_dict = dict()
        for remote_file in remote_files:
            date_key = remote_file.split('_')[-1].split('.')[0]

            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
            date_key_dt = datetime.strptime(date_key, "%Y-%m-%d")
            if start_date_dt <= date_key_dt and end_date_dt >= date_key_dt:
                print(f"Loading {date_key}")
                date_file = drive.get(remote_file)
                dates_dict[date_key] = np.load(date_file,allow_pickle=True).item()
        return dates_dict
        print(f"Loading done!")

def ignore_standing_pos(positions, date_key):
    # ignore robot standing still
            
    old_pos = [0,0]
    skipped = 0
    adjusted_positions = []

    # compare each pos to previous pos and skip if basically unchanged
    for pos in positions:
        if distance(pos, old_pos) < 0.1:
            skipped += 1
        else:
            adjusted_positions.append(pos)
        old_pos = pos
    print(f"{date_key}: {skipped} unchanged positions skipped! ({(skipped/len(positions))*100:.2f}% of all positions)")
    
    return adjusted_positions

def calculate_velocity_speed_acceleration(date_dict):
    # calculate velocities, speeds. run_length
    runs = date_dict["runs"]
    timestamps = date_dict["timestamps"]
    dt_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in timestamps]
    
    runs_velocities = []
    runs_speeds = []
    runs_accelerations = []
    for id_run, run in enumerate(runs):
        if run is None or len(run) != 2:
            continue
        # calc valocity, speed and acceleration for this run
        velocity_vectors_run, speed_run, acceleration_run = calculate_run_velocity_speed_acceleration(date_dict, run, dt_timestamps)
        
        # add results
        runs_velocities.append(velocity_vectors_run)
        runs_speeds.append(speed_run)
        runs_accelerations.append(acceleration_run)
        
    return runs_velocities, runs_speeds, runs_accelerations

def calculate_run_velocity_speed_acceleration(date_dict, run, dt_timestamps):
    # timestamp deltas for velocity and speed
    timestamps_run = dt_timestamps[run[0]:run[1]+1]
    timedeltas_run = [delta.total_seconds() for delta in np.diff(timestamps_run)]

    posxdeltas_run = np.diff(np.array(date_dict["positions"])[run[0]:run[1]+1,0])
    posydeltas_run = np.diff(np.array(date_dict["positions"])[run[0]:run[1]+1,1])

    velocity_x_run = posxdeltas_run / timedeltas_run
    velocity_y_run = posydeltas_run / timedeltas_run

    velocity_vectors_run = list(zip(velocity_x_run, velocity_y_run))
    speed_run = np.linalg.norm(velocity_vectors_run, axis=1) # magnitude of velocity vector is speed

    acceleration_run = np.diff(speed_run)
    
    return velocity_vectors_run, speed_run, acceleration_run


def get_hours_minutes_seconds_from_decimal_hours(dec_hours):
    hours = int(dec_hours)
    minutes = int((dec_hours*60) % 60)
    seconds = int((dec_hours*3600) % 60)
    return hours, minutes, seconds

def get_number_of_days(start_date, end_date):
    '''
        Returns total number of days in selected timeframe 
    '''
    # print(start_date, end_date)
    d0 = datetime.strptime(start_date, '%Y-%m-%d')
    d1 = datetime.strptime(end_date, '%Y-%m-%d')
    delta = d1 - d0
    return delta.days + 1

def get_number_of_runs(dates_dict, start_date, end_date, successful=False, challenges=False):
    '''
        Returns total number of runs in selected timeframe 
    '''
    number_of_runs = 0
    
    dates_keys = dates_dict.keys()
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        
        if successful:
            runs, _ = get_challenge_runs(date_dict["runs"], date_dict["successful"])
        elif challenges:
            runs, _ = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
        else:
            runs = date_dict["runs"]
            
        number_of_runs += len(runs)
        
    return number_of_runs

def get_date_run_tuples(dates_dict, successful, challenges):
    '''
        Returns list of date-run tuples for each run in selected timeframe 
    '''
    date_run_tuples = []
    
    dates_keys = dates_dict.keys()
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        
        if successful:
            runs, ids_runs = get_challenge_runs(date_dict["runs"], date_dict["successful"])
        elif challenges:
            runs, ids_runs = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
        else:
            runs = date_dict["runs"]
            ids_runs = list(range(len(runs)))
        #combine date and run id to tuples and add to list
        for id_run in ids_runs:
            date_run_tuples.append((date_key, id_run))
    
    return date_run_tuples
        

def get_use_time(dates_dict,start_date, end_date):
    '''
        Returns total use time in selected timeframe 
    '''
    total_use_time = 0
    
    dates_keys = dates_dict.keys()
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        date_run_lengths = date_dict["run_lengths"]
        total_use_time += np.sum(date_run_lengths)/60/60
        
    return total_use_time
    
    
def get_number_of_frames(dates_dict, start_date, end_date):
    '''
        Returns total number of frames in selected timeframe 
    '''
    total_number_of_frames = 0
    
    dates_keys = dates_dict.keys()
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        date_number_of_timestamps = len(date_dict["timestamps"])
        total_number_of_frames += date_number_of_timestamps
        
    return total_number_of_frames

def flatten_2d_list(input_list):
    flat_list = []
    for i in input_list:
        for e in i:
            flat_list.append(e)
    return flat_list

def tolerant_mean(arrs):
    lens = [len(i) for i in arrs]
    arr = np.ma.empty((np.max(lens),len(arrs)))
    arr.mask = True
    for idx, l in enumerate(arrs):
        arr[:len(l),idx] = l
    return arr.mean(axis = -1), arr.std(axis=-1)

def equalize_arrays(arrs, fillvalue):
    max_len = max([len(i) for i in arrs])
    print(max_len)
    
    for arr in arrs:
        arr.extend([fillvalue for i in range(max_len-len(arr))])
    return arrs


def filter_date_dict_for_challenge_runs(date_dict, challenge_runs, ids_challenge_runs):
    filtered_date_dict = dict()
    filtered_date_dict['timestamps'] = []
    filtered_date_dict['positions'] = []
    filtered_date_dict['orientation'] = []
    filtered_date_dict['rotation'] = []
    filtered_date_dict['runs'] = []
    filtered_date_dict['day_length'] = date_dict['day_length']
    filtered_date_dict['run_lengths'] = []
    filtered_date_dict['difficulties'] = []
    filtered_date_dict['fish'] = []
    filtered_date_dict['challenges'] = []
    filtered_date_dict['successful'] = []
    
    run_pointer = 0
    for challenge_tuple in zip(challenge_runs, ids_challenge_runs):
        #print(challenge_tuple)
        filtered_date_dict['timestamps'].extend(date_dict['timestamps'][challenge_tuple[0][0]:challenge_tuple[0][1]+1])
        filtered_date_dict['positions'].extend(date_dict['positions'][challenge_tuple[0][0]:challenge_tuple[0][1]+1])
        filtered_date_dict['orientation'].extend(date_dict['orientation'][challenge_tuple[0][0]:challenge_tuple[0][1]+1])
        filtered_date_dict['rotation'].extend(date_dict['rotation'][challenge_tuple[0][0]:challenge_tuple[0][1]+1])
        filtered_date_dict['runs'].append([run_pointer, run_pointer + (date_dict['runs'][challenge_tuple[1]][1] - date_dict['runs'][challenge_tuple[1]][0])])
        run_pointer = run_pointer + date_dict['runs'][challenge_tuple[1]][1] - date_dict['runs'][challenge_tuple[1]][0] + 1
        filtered_date_dict['run_lengths'].append(date_dict['run_lengths'][challenge_tuple[1]])
        filtered_date_dict['difficulties'].append(date_dict['difficulties'][challenge_tuple[1]])
        filtered_date_dict['fish'].extend(date_dict['fish'][challenge_tuple[0][0]:challenge_tuple[0][1]+1])
        filtered_date_dict['challenges'].append(date_dict['challenges'][challenge_tuple[1]])
        filtered_date_dict['successful'].append(date_dict['successful'][challenge_tuple[1]])
        
        
        # sanity check filtered data
        
        # all timeseries data array should be the same length
        og_len_ts = len(date_dict['timestamps'])
        len_ts = len(filtered_date_dict['timestamps'])
        assert len_ts == len(filtered_date_dict['positions']) == len(filtered_date_dict['orientation']) == len(filtered_date_dict['rotation']) == len(filtered_date_dict['fish'])
        
        # overall length of runs must be the same as timeseries length
        overall_run_length = filtered_date_dict['runs'][-1][1] - filtered_date_dict['runs'][0][0] + 1
        assert len_ts == overall_run_length, f"timestamp length ({len_ts}) not equal to overall run length ({overall_run_length})"

    
    return filtered_date_dict

def filter_dates_dict_for_challenge_runs(dates_dict):
    for date_dict_key in dates_dict:
        date_dict = dates_dict[date_dict_key]
        runs = date_dict['runs']
        challenges = date_dict['challenges']
        challenge_runs, ids_challenge_runs = get_challenge_runs(runs, challenges)

        filtered_date_dict = filter_date_dict_for_challenge_runs(date_dict, challenge_runs, ids_challenge_runs)
        #print(date_dict['successful'][0:10], filtered_date_dict['successful'][0:10])
        dates_dict[date_dict_key] = filtered_date_dict
        
        print(f"Filtered challenge runs out of {date_dict_key}")
        
def check_if_date_in_range(date, start, end):
    if (start is not None and date < start) or (end is not None and date > end):
        return False
    return True

def dates_string_to_datetime(date):
    # date to datetime
    if date is not None:
        date_dt = datetime.strptime(date, '%Y-%m-%d')
    return date

def clean_line(line, id_line, file_path, rest_cut_off):
    # remove \n
    line = line.replace("\n", "")
    # remove \x00
    line = line.replace("\x00", "")
    # split line at white spaces
    split_line = line.split(" ")

    # get prefixed time stamp
    ts_date = split_line[0].replace("\t","")
    if ts_date.startswith("\x00"):
        print(file_path, id_line, line)
    # print(ts_date)
    timestamp = f"{split_line[0]} {split_line[1]}".replace("\t","")

    rest = line[rest_cut_off:]
    
    return line, split_line, timestamp, rest

def check_line(split_line, id_line, file_path):
    # check if line is irregular
    if len(split_line) == 1: #no whitespace detected
        print(f"Irregular line ({id_line}) in {file_path}!")
        return False #ignore line
    return True