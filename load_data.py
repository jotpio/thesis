import glob, os, time
from util import parse_number_array_from_string, find_corresponding_timestamp
from datetime import datetime
import json

def load_robot_data(robot_dir, start_date=None, end_date=None):
    '''
    robot_dir:     directory of robot log files
    start_date:    starting date from which to get data from
    end_date:      end date from which to get data from
    '''

    # get robot files
    file_paths = glob.glob(robot_dir+"/robot.*")
    
    # dates to datetime
    if start_date is not None:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_tic = time.time()
    # load from robot files
    dates_dict = {}
    for id_file_path, file_path in enumerate(file_paths):
        tic = time.time()
        # check if file in given date range and skip if not
        file_name = os.path.basename(file_path)
        split_file_path = file_name.split(".")
        
        if len(split_file_path) > 1:
            file_date = split_file_path[1][:10] #[robot][<YYYY-mm-dd>_HH]
            file_date_dt = datetime.strptime(file_date, '%Y-%m-%d')
            if start_date is not None and file_date_dt < start_date_dt:
                continue
            if end_date is not None and file_date_dt > end_date_dt:
                continue
        else:
            print(f"Skipped {file_path}")
            continue
        
        
        # get dict for this day
        date = file_date
        date_dict = dates_dict.get(date, dict())
        
        # init arrays for new date_dict 
        if len(date_dict.keys()) == 0:
            date_dict["timestamps"] = []
            date_dict["positions"] = []
            date_dict["adjusted_positions"] = []
            date_dict["orientation"] = []
            date_dict["rotation"] = []
            date_dict["velocities"] = []
            date_dict["speeds"] = []
            date_dict["accelerations"] = []
            date_dict["runs"] = []
            date_dict["challenges"] = []
            date_dict["fish"] = []
        
        
        # load line by line and add to corresponding day
        with open(file_path, "r") as file:
            print(f"Loading {file_path}...")
            for id_line, line in enumerate(file):
                # remove \n
                line = line.replace("\n", "")

                # remove \x00
                line = line.replace("\x00", "")

                # split line at white spaces
                split_line = line.split(" ")

                # check if line is irregular
                if len(split_line) == 1: #no whitespace detected
                    print(f"Irregular line ({id_line}) in {file_path}!")
                    continue #ignore line

                # get prefixed time stamp
                date = split_line[0]
                if date.startswith("\x00"):
                    print(file_path, id_line, line)
                # print(date)
                timestamp = f"{split_line[0]} {split_line[1]}"
                rest = line[28:]

                # # skip lines without positions
                # if split_line[3] == "Started":
                #     continue


                if split_line[3] != "Started":
                    # update date dict with file data
                    timestamps = date_dict.get("timestamps",[])
                    timestamps.append(timestamp)
                    date_dict["timestamps"] = timestamps

                    # split rest up into distinct data
                    split_rest = rest.split(', ')
                    # add data to dict
                    positions = date_dict.get("positions",[])
                    position = parse_number_array_from_string(split_rest[0])
                    if len(split_rest) > 0: positions.append(position)
                    date_dict["positions"] = positions

                    orientations = date_dict.get("orientation",[])
                    if len(split_rest) > 1:
                        orientation = parse_number_array_from_string(split_rest[1])
                        orientations.append(orientation)
                    date_dict["orientation"] = orientations

                    rotations = date_dict.get("rotation",[])
                    if len(split_rest) > 2:
                        rotation = parse_number_array_from_string(split_rest[2])
                        rotations.append(rotation)
                    date_dict["rotation"] = rotations

                # update date_dict in date_dicts
                dates_dict[date] = date_dict

            file.close()
            toc=time.time()
            print(f"{toc-tic:.4f} seconds elapsed")

    print(f"{len(dates_dict.keys())} day(s) loaded!")
    all_toc=time.time()
    print(f"Loading robot files took {all_toc-all_tic} seconds")
    return dates_dict


def load_fish_data(fish_dir, dates_dict=None, start_date=None, end_date=None):
    '''
    robot_dir:     directory of fish log files
    start_date:    starting date from which to get data from
    end_date:      end date from which to get data from
    '''

    # get robot files
    file_paths = glob.glob(fish_dir+"/fish.*")
    
    # dates to datetime
    if start_date is not None:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # load from fish files
    if dates_dict is None:
        dates_dict = dict()
        
    # previous date
    prev_date = None
            
    all_tic = time.time()
    current_line_id = 0
    for id_file_path, file_path in enumerate(file_paths):
        tic = time.time()
        # check if file in given date range and skip if not
        file_name = os.path.basename(file_path)
        split_file_path = file_name.split(".")
                
        if len(split_file_path) > 1:
            file_date = split_file_path[1][:10] #[robot][<YYYY-mm-dd>_HH]
            file_date_dt = datetime.strptime(file_date, '%Y-%m-%d')
            if start_date is not None and file_date_dt < start_date:
                continue
            if end_date is not None and file_date_dt > end_date:
                continue
        else:
            print(f"Skipped {file_path}")
            continue
            
        # get dict for this day
        date = file_date
        date_dict = dates_dict.get(date, dict())
        
        # finish last run of the previous date
        if prev_date is not None:
            if prev_date != date:
                current_line_id = 0 
        prev_date = date
            
        # load line by line and add to corresponding day
        with open(file_path, "r") as file:
            print(f"Loading {file_path}...")
            
            for id_line, line in enumerate(file):
                # remove \n
                line = line.replace("\n", "")

                # remove \x00
                line = line.replace("\x00", "")

                # split line at white spaces
                split_line = line.split(" ")

                # check if line is irregular
                if len(split_line) == 1: #no whitespace detected
                    print(f"Irregular line ({id_line}) in {file_path}!")
                    continue #ignore line

                # get prefixed time stamp
                date = split_line[0]
                if date.startswith("\x00"):
                    print(file_path, id_line, line)
                # print(date)
                timestamp = f"{split_line[0]} {split_line[1]}"
                rest = line[28:]           
                
                if split_line[3] != "Started":
                    # make line json compliant
                    rest = rest.replace("\'", "\"")
                    rest = rest.replace("True", "true")
                    rest = rest.replace("False", "false")
                    rest = json.loads(rest)  
                    
                    # find corresponding timestamp in existing data and add fish data
                    id_timestamp = find_corresponding_timestamp(date_dict["timestamps"], timestamp, current_line_id)
                    
                    if id_timestamp == -1:
                        print(f"No corresponding timestmap found for {timestamp}")
                        continue
                    fish_array = date_dict.get("fish", [])
                    
                    #
                    if len(fish_array) == id_timestamp:
                        fish_array.append(rest)
                    elif len(fish_array) < id_timestamp:
                        # add empty arrays until index of new timestamp is reached
                        for i in range(len(fish_array), id_timestamp):
                            fish_array.append([])
                            if len(fish_array) == id_timestamp:
                                fish_array.append(rest)
                    else: #if array already exists at this index, overwrite
                        print(len(fish_array), id_timestamp)
                        fish_array[id_timestamp] = rest
                    # print(fish_array)
                    current_line_id += 1
                    
                    date_dict["fish"] = fish_array
                    
                # update date_dict in date_dicts
                dates_dict[date] = date_dict
                
            file.close()
            toc=time.time()
            print(f"{toc-tic:.4f} seconds elapsed")

    all_toc=time.time()
    print(f"Loading fish files took {all_toc-all_tic} seconds")            
                # print(timestamp)
                # print(type(list(rest)))
    return dates_dict

def load_behavior(behavior_dir, dates_dict=None, start_date=None, end_date=None):
    pass