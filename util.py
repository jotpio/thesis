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


def find_corresponding_timestamp(timestamps, timestamp, current_lineid):    
    compare_ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
    
    if np.abs((compare_ts - datetime.strptime(timestamps[current_lineid], '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) < 0.17:
        return current_lineid
    else:
        print("no timestamp closer than 0.1 seconds")
        print(current_lineid, timestamps[current_lineid], timestamp, timestamps)
        assert False
    
    
    
    # time_differences = [np.abs((compare_ts - datetime.strptime(ts, '%Y-%m-%d %H:%M:%S,%f')).total_seconds()) for ts in timestamps]
    # id_min = np.argmin(time_differences)
    # print(id_min)