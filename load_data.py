import glob, os, time
from util import parse_number_array_from_string, find_corresponding_timestamp
from datetime import datetime
import json
import numpy as np

def load_robot_data(robot_dir, start_date=None, end_date=None):
    '''
    robot_dir:     directory of robot log files
    start_date:    starting date from which to get data from
    end_date:      end date from which to get data from
    '''

    print(f"Loading robot data from {robot_dir}")
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
            date_dict["runs_lengths"] = []
            date_dict["challenges"] = []
            date_dict["fish"] = []
            date_dict["successful"] = []
        
        
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
    print(f"Loading fish data from {fish_dir}")
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

def load_behavior_data(behavior_dir, dates_dict=None, start_date=None, end_date=None):
    # load behavior output data and detect challenges
    '''
    robot_dir:     directory of behavior log files
    start_date:    starting date from which to get data from
    end_date:      end date from which to get data from
    '''
    print(f"Loading behavior data from {behavior_dir}")

    # get robot files
    file_paths = glob.glob(behavior_dir+"/behavior_prints.*")

    # dates to datetime
    if start_date is not None:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # load from behavior files
    if dates_dict is None:
        dates_dict = {}

    # previous date
    prev_date = None

    # current timestamp id 
    timestamp_pointer = 0

    all_tic = time.time()
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

        # finish last run of the previous date
        if prev_date is not None:
            if prev_date != date:
                #finish last run of previous date (append last timestamp to last run)
                prev_date_dict = dates_dict[prev_date]

                prev_runs = prev_date_dict["runs"]
                if len(prev_runs) > 0 and len(prev_runs[-1]) == 1:
                    timestamps = prev_date_dict["timestamps"]
                    last_run = prev_runs[-1]
                    if len(last_run):
                        last_run.append(len(timestamps)-1)
                        prev_date_dict["runs"] = prev_runs
                        dates_dict[prev_date] = prev_date_dict

                # set timestamp id to zero
                timestamp_pointer = 0

        prev_date = date

        # load line by line and add to corresponding day
        with open(file_path, "r") as file:
            print(f"Loading {file_path}...")

            date_timestamps = date_dict["timestamps"]
            date_runs = date_dict["runs"]
            date_challenges = date_dict["challenges"]

            # get last run
            if date_runs != [] and date_runs is not None:
                if len(date_runs[-1]) == 1:
                    current_run = date_runs[-1].copy()
                    date_runs = date_runs[:-1]
                    date_dict["runs"] = date_runs
                else:
                    current_run = []
            else:
                current_run = []

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
                date = split_line[0].replace("\t","")
                if date.startswith("\x00"):
                    print(file_path, id_line, line)
                current_timestamp = f"{split_line[0]} {split_line[1]}".replace("\t","")
                rest = line[27:]

                # clean up message
                rest_split = rest.split('-')
                source = rest_split[0].replace(" ","")
                log_type = rest_split[1].replace(" ","")
                message = rest_split[2].replace("\t","")[1:]            

                ''' 
                filter message to get relevant information
                    - add runs: challenge and non-challenge

                '''
                # get start of new run (joystick connected)
                if message.startswith("JOYSTICK: Server connected by"):
                    # find corresponding timestamp and set this run to non-challenge run
                    id_timestamp = find_corresponding_timestamp(date_timestamps, current_timestamp, timestamp_pointer, timedelta=0.5, checkall=True)
                    if id_timestamp != -1:
                        # print(f"\tJOYSTICK: Found in {id_timestamp}-th timestamp! {date_timestamps[id_timestamp], current_timestamp}")
                        
                        # add new run to challenges; if challenge message is found, set this bool to True
                        date_challenges.append(False)
                        
                        # start timestamp - run
                        if len(current_run) == 0:
                            current_run.append(id_timestamp)


                        # this triggers if joystick not disconnected somehow (crashed)
                        # get timestamp before new joystick connected(should be the one before this timestamp)
                        # add finished run to all runs
                        elif len(current_run) == 1:
                            print(f"Opening joystick on although last not ended.... {current_timestamp}")
                            current_run.append(id_timestamp-1)

                            date_runs.append(current_run)
                            date_dict["runs"] = date_runs
                            # next run starts with current timestamp
                            current_run=[id_timestamp]
                        # update timestamp_pointer to speed up code
                        timestamp_pointer = id_timestamp
                    else:
                        print(f"\tJOYSTICK: Did not find corresponding timestamp for this message! {current_timestamp}")


    #             # filter by non-challenge runs
    #             if message == "COMMAND: Received ['reset_fish', 20]":
    #                 # find corresponding timestamp and set this run to non-challenge run
    #                 id_timestamp = find_corresponding_timestamp(date_timestamps, current_timestamp, 0, timedelta=0.5, checkall=True)
    #                 if id_timestamp != -1:
    #                     print(f"\tNon-challenge: Found in {id_timestamp}-th timestamp! {date_timestamps[id_timestamp], current_timestamp}")
    #                     # compare found timestmap with end of last run; if not the same the last run is maybe too long
    #                     if len(date_runs) > 0:
    #                         last_run_id = date_runs[-1][-1]
    #                         print(last_run_id, id_timestamp)
    #                 else:
    #                     print(f"\tNon-challenge: Did not find corresponding timestamp for this message! {current_timestamp}")


    #                 date_challenges.append(False)


                # get end of joystick connections and check if this corresponds with end of runs
                elif message == "JOYSTICK: Closing socket!":
                    # find corresponding timestamp, end this current run and add to all runs
                    id_timestamp = find_corresponding_timestamp(date_timestamps, current_timestamp, timestamp_pointer, timedelta=0.3, checkall=True)
                    if id_timestamp != -1:

                        # error timestamp - run
                        if len(current_run) == 0:
                            print(f"Closing joystick on uninitiated run.... {current_timestamp}")

                        # finish current run
                        # add finished run to all runs
                        elif len(current_run) == 1:
                            current_run.append(id_timestamp)

                            date_runs.append(current_run)
                            date_dict["runs"] = date_runs
                            # next run starts empty
                            current_run=[]
                        # update timestamp_pointer to speed up code
                        timestamp_pointer = id_timestamp



    #                     # print(f"\tzone tester: Found in {id_timestamp}-th timestamp!{date_timestamps[id_timestamp], current_timestamp}")
    #                     # compare found timestmap with end of last run; if not the same the last run is maybe too long
    #                     if len(date_runs) > 0:
    #                         last_run_id = date_runs[-1][-1]
    #                         print(date_runs[-1])
    #                         if last_run_id > id_timestamp:
    #                             print(f"Joystick connection closed during run: {last_run_id}, id_timestamp: {id_timestamp}")
                    else:
                        # print(f"\tzone tester: Did not find corresponding timestamp for this message! {current_timestamp}")
                        pass

                # # filter by zone-tester scenes
                # elif message == "COMMAND: Received ['reset_fish', 80]":
                #     # find corresponding timestamp, end this current run and add to all runs
                #     id_timestamp = find_corresponding_timestamp(date_timestamps, current_timestamp, 0, timedelta=1, checkall=True)
                #     if id_timestamp != -1:
                #         # print(f"\tzone tester: Found in {id_timestamp}-th timestamp!{date_timestamps[id_timestamp], current_timestamp}")
                #         # compare found timestmap with end of last run; if not the same the last run is maybe too long
                #         if len(date_runs) > 0:
                #             last_run_id = date_runs[-1][-1]
                #             print(date_runs[-1])
                #             if last_run_id > id_timestamp:
                #                 print(f"Run is maybe still running after user lost control: last_run_id: {last_run_id}, id_timestamp: {id_timestamp}")
                #     else:
                #         # print(f"\tzone tester: Did not find corresponding timestamp for this message! {current_timestamp}")
                #         pass

                # filter by challenge runs 
                elif message in ["COMMAND: Received ['reset_fish', 2]", "COMMAND: Received ['reset_fish', 4]","COMMAND: Received ['reset_fish', 6]"]:

                    if len(date_challenges) > 0:
                        date_challenges[-1] = True # update current run to challenge
                    else:
                        print(f"Received challenge message before joystick message! {current_timestamp, id_line, file_path}")


                    # update date dict in dates_dict
                    dates_dict[date] = date_dict

            # file done; add current run to all runs
            if current_run != [] and current_run is not None:
                date_runs.append(current_run)
                date_dict["runs"] = date_runs
                current_run = []
            # close file
            file.close()
            toc=time.time()
            print(f"{toc-tic} seconds elapsed")


    # finish last run of last date (append last timestamp to last run)
    prev_date_dict = dates_dict[prev_date]

    prev_runs = prev_date_dict["runs"]
    if len(prev_runs) > 0 and len(prev_runs[-1]) == 1:
        timestamps = prev_date_dict["timestamps"]
        last_run = prev_runs[-1]
        if len(last_run) == 1:
            last_run.append(len(timestamps)-1)
            prev_date_dict["runs"] = prev_runs
            dates_dict[prev_date] = prev_date_dict

    # print some stats 
    for date_key in dates_dict.keys():
        date_dict = dates_dict[date_key]
        date_runs = np.array(date_dict["runs"])
        date_cha = np.array(date_dict["challenges"])
        if len(date_runs):
            date_cha_runs = date_runs[date_cha]
            print(f"{date_key} - Number of runs: {len(date_runs)}; Number of challenges: {len(date_cha_runs)}")
        else:
            print(f"{date_key} - No runs found!")

    all_toc=time.time()
    print(f"Loading behavior files took {all_toc-all_tic} seconds")
    
    return dates_dict