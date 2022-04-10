import re
import numpy as np
from datetime import datetime 

def parse_number_array_from_string(string):
    pattern = r"([-+]?\d*\.\d*)" # match unsigned or signed floating point numbers
    string_numbers = re.findall(pattern, string)
    numbers = [float(number) for number in string_numbers]
    return numbers

def distance(pos1, pos2):
    return np.linalg.norm(np.array(pos1)-np.array(pos2))

def get_all_positions(dates_dict, adjusted):
    all_positions = []
    
    dates_keys = dates_dict.keys()
    
    for date_key in dates_keys:    
        date_dict = dates_dict[date_key]

        instance_keys = date_dict.keys()
        for id_instance, instance_key in enumerate(instance_keys):
            instance = date_dict[instance_key]

            # combine positions
            if adjusted:
                instance_positions = instance["adjusted_positions"]
            else:
                instance_positions = instance["positions"]

            all_positions.extend(instance_positions)
    return all_positions


def find_corresponding_timestamp(timestamps, timestamp, current_lineid, timedelta=0.17):    
    compare_ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
    
    if np.abs((compare_ts - datetime.strptime(timestamps[current_lineid], '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) < timedelta:
        return current_lineid
    else:
        # print(f"timestamp not closer than {timedelta} seconds ({timestamps[current_lineid], timestamp}")
        # print(current_lineid, timestamps[current_lineid], timestamp, timestamps)
        return -1
    
    
    
    # time_differences = [np.abs((compare_ts - datetime.strptime(ts, '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) for ts in timestamps]
    # id_min = np.argmin(time_differences)
    # print(id_min)
    
def get_fish_pos_per_run(fish_instance, runs):
    fish_pos_all_runs = []
    if len(fish_instance) == 0:
        return []
    for id_run, run in enumerate(runs):
        fish_pos_run = []
        run_fish = fish_instance[run[0]:run[1]]

        # print(np.array(run_fish)[0])
        
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
        return np.array(runs)[np.array(challenges)]
    else:
        return []