import glob, os
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
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # load from robot files
    dates_dict = {}
    current_instance = 0
    for id_file_path, file_path in enumerate(file_paths):
        # check if file in given date range and skip if not
        file_name = os.path.basename(file_path)
        split_file_path = file_name.split(".")
        
        if len(split_file_path) > 1:
            file_date = split_file_path[1][:10] #[robot][<YYYY-mm-dd>_HH]
            file_date = datetime.strptime(file_date, '%Y-%m-%d')
            if start_date is not None and file_date < start_date:
                continue
            if end_date is not None and file_date > end_date:
                continue
        else:
            print(f"Skipped {file_path}")
            continue
        
        
        # load line by line and add to corresponding day
        with open(file_path, "r") as file:
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

                # new instance when robot was loaded again
                if split_line[3] == "Started":
                    current_instance += 1

                # get dict for this day
                date_dict = dates_dict.get(date, dict())
                # get dict for this instance
                instance_dict = date_dict.get(current_instance, dict())

                if split_line[3] != "Started":
                    # update instance dict with file data
                    timestamps = instance_dict.get("timestamps",[])
                    timestamps.append(timestamp)
                    instance_dict["timestamps"] = timestamps

                    # split rest up into distinct data
                    split_rest = rest.split(', ')
                    # add data to dict
                    positions = instance_dict.get("positions",[])
                    position = parse_number_array_from_string(split_rest[0])
                    if len(split_rest) > 0: positions.append(position)
                    instance_dict["positions"] = positions

                    orientations = instance_dict.get("orientation",[])
                    if len(split_rest) > 1:
                        orientation = parse_number_array_from_string(split_rest[1])
                        orientations.append(orientation)
                    instance_dict["orientation"] = orientations

                    rotations = instance_dict.get("rotation",[])
                    if len(split_rest) > 2:
                        rotation = parse_number_array_from_string(split_rest[2])
                        rotations.append(rotation)
                    instance_dict["rotation"] = rotations


                else:
                    # init arrays for new instance 
                    instance_dict["timestamps"] = []
                    instance_dict["positions"] = []
                    instance_dict["adjusted_positions"] = []
                    instance_dict["orientation"] = []
                    instance_dict["rotation"] = []
                    instance_dict["velocities"] = []
                    instance_dict["speeds"] = []
                    instance_dict["accelerations"] = []
                    instance_dict["runs"] = []
                    instance_dict["challenges"] = []
                    instance_dict["fish"] = []


                # update instance dict in date_dict
                date_dict[current_instance] = instance_dict
                dates_dict[date] = date_dict

            file.close()

    print(f"{len(dates_dict.keys())} day(s) loaded!")
    
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
        dates_dict = {}
    current_instance = 0
    current_instance_line_id = 0
    for id_file_path, file_path in enumerate(file_paths):
        # check if file in given date range and skip if not
        file_name = os.path.basename(file_path)
        split_file_path = file_name.split(".")
                
        if len(split_file_path) > 1:
            file_date = split_file_path[1][:10] #[robot][<YYYY-mm-dd>_HH]
            file_date = datetime.strptime(file_date, '%Y-%m-%d')
            if start_date is not None and file_date < start_date:
                continue
            if end_date is not None and file_date > end_date:
                continue
        else:
            print(f"Skipped {file_path}")
            continue
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
                
                # new instance when robot was loaded again
                if split_line[3] == "Started":
                    current_instance += 1
                    current_instance_line_id = 0
                else:
                    # make line json compliant
                    rest = rest.replace("\'", "\"")
                    rest = rest.replace("True", "true")
                    rest = rest.replace("False", "false")
                    rest = json.loads(rest)
                

                
                # get dict for this day
                date_dict = dates_dict.get(date, dict())
                # get dict for this instance
                instance_dict = date_dict.get(current_instance, dict()) # TODO are instances for each log type the same?
                
                
                if split_line[3] != "Started":
                    # find corresponding timestamp in existing data and add fish data
                    id_timestamp = find_corresponding_timestamp(instance_dict["timestamps"], timestamp, current_instance_line_id)
                    fish_array = instance_dict.get("fish", [])
                    
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
                        fish_array[id_timestamp] = rest
                    # print(fish_array)
                    current_instance_line_id += 1
                    
                    instance_dict["fish"] = fish_array
            file.close()    
                
                # print(timestamp)
                # print(type(list(rest)))
    return dates_dict