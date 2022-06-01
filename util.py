import re
import numpy as np
from datetime import datetime 
import glob


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
            run_positions = date_dict["positions"][run[0]:run[1]]
            all_positions.extend(run_positions)
            
    return all_positions


def find_corresponding_timestamp(timestamps, timestamp, current_lineid, timedelta=0.17, checkall=False):    
    compare_ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
    
    # check full timestamp array; start at current_lineid
    if checkall:
        for i in range(current_lineid, len(timestamps)):
            ts = datetime.strptime(timestamps[i], '%Y-%m-%d %H:%M:%S,%f')
            delta = np.abs((compare_ts - ts).total_seconds())
            
            if delta < timedelta:
                return i
            
        return -1 # not found
    
    # check only timestamp at current_lineid
    else:
        if np.abs((compare_ts - datetime.strptime(timestamps[current_lineid], '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) < timedelta:
            return current_lineid
        else:
            # print(f"timestamp not closer than {timedelta} seconds ({timestamps[current_lineid], timestamp}")
            # print(current_lineid, timestamps[current_lineid], timestamp, timestamps)
            return -1
    
    
    
    # time_differences = [np.abs((compare_ts - datetime.strptime(ts, '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) for ts in timestamps]
    # id_min = np.argmin(time_differences)
    # print(id_min)
    
def get_fish_pos_per_run(all_fish_pos, runs):
    fish_pos_all_runs = []
    if len(all_fish_pos) == 0:
        return []
    for id_run, run in enumerate(runs):
        fish_pos_run = []
        run_fish = all_fish_pos[run[0]:run[1]]
        
        for all_fish_in_ts in run_fish:
            fish_pos_ts = []
            for fish in all_fish_in_ts:
                if fish['id'] != 0:
                    fish_pos_ts.append(fish["position"])
                    
            # print(fish_pos_ts[0])
            fish_pos_run.append(fish_pos_ts)

        fish_pos_all_runs.append(fish_pos_run)

    return fish_pos_all_runs

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
        return [], []

# https://stackoverflow.com/questions/5254838/calculating-distance-between-a-point-and-a-rectangular-box-nearest-point
def get_distance_to_goal(pos):
    # goal (x<750; y>1250)
    goal_min_x = 0
    goal_max_x = 750
    goal_min_y = 1250
    goal_max_y = 2000
    pos = np.array(pos)
    dx = np.fmax(np.fmax(goal_min_x - pos[:,0], 0), pos[:,0] - goal_max_x)
    dy = np.fmax(np.fmax(goal_min_y - pos[:,1], 0), pos[:,1] - goal_max_y)
    return np.sqrt(dx*dx + dy*dy)


def save_dates_to_npz(dates_dict):
    # save day by day into npy files
    for key in dates_dict.keys():
        date = dates_dict[key]
        file_name = f".\loaded_data\dates_dict_{key}.npy"
        print(f"Saving {key} to {file_name}")
        np.save(file_name, date, allow_pickle=True)
        
def load_dates_from_npz(start_date, end_date):
    # load dates from npy files
    date_files = glob.glob(f".\loaded_data\dates_dict_*.npy")
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