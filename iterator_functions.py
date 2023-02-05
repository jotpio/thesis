from util import daterange, get_fast_runs, get_successful_runs, get_challenge_runs
from datetime import datetime
from util import load_dates_from_npz
from extend_robot_data import extend_robot_data
import numpy as np


def iteratively_evaluate_dates_files(start_date, end_date, eval_date_function, load_only_challenge_data, challenges=True, only_successful=True, fast_runs_percentiles=None, verbose=False):
    
    all_returns = []
    
    # prepare output structure 
    if type(fast_runs_percentiles) is int:
        fast_runs_percentiles = [fast_runs_percentiles]
    if fast_runs_percentiles is not None:
        all_returns = [[] for i in range(len(fast_runs_percentiles))]
        
    # load days one by one
    dt_start_date = datetime.strptime(start_date, "%Y-%m-%d")
    dt_end_date = datetime.strptime(end_date, "%Y-%m-%d")
    for single_date in daterange(dt_start_date, dt_end_date):
        print(single_date)
        current_date_str = single_date.strftime("%Y-%m-%d")
        #load day
        dates_dict = load_dates_from_npz(current_date_str, current_date_str, only_challenges=load_only_challenge_data, verbose=False)
        # extend day data
        dates_dict = extend_robot_data(dates_dict)
        # get current date dict
        date_dict = dates_dict.get(current_date_str,{})
        #
        
        # filter runs
        if fast_runs_percentiles is not None:
            for id_fast_runs_percentile, fast_runs_percentile in enumerate(fast_runs_percentiles):
                # apply evaluation function
                all_returns[id_fast_runs_percentile].append(eval_date_function(date_dict,challenges, only_successful, fast_runs_percentile))
        else:
            # apply evaluation function
            print("No fast run percentile assigned.")
            # apply evaluation function
            all_returns.append(eval_date_function(date_dict,challenges, only_successful, None))
        
    return all_returns

def iteratively_collect_and_filter_dates_files(start_date, end_date, load_only_challenge_data, percentile_value=200, challenges=True, only_successful=True, verbose=False):
    out_dates_dict = dict()
        
    # load days one by one
    dt_start_date = datetime.strptime(start_date, "%Y-%m-%d")
    dt_end_date = datetime.strptime(end_date, "%Y-%m-%d")
    for single_date in daterange(dt_start_date, dt_end_date):
        print(single_date)
        current_date_str = single_date.strftime("%Y-%m-%d")
        #load day
        dates_dict = load_dates_from_npz(current_date_str, current_date_str, only_challenges=load_only_challenge_data, verbose=verbose)
        # extend day data
        dates_dict = extend_robot_data(dates_dict)
        # get current date dict
        date_dict = dates_dict.get(current_date_str,{})
        # filter date_dict
        date_dict = filter_date_dict(date_dict, percentile_value, challenges, only_successful)
        
        # add filtered date_dict in new dates_dict
        if date_dict:
            out_dates_dict[current_date_str] = date_dict
    return out_dates_dict


def iteratively_evaluate_dates_files_runwise(eval_run_function, start_date, end_date, load_only_challenge_data=True, challenges=True, only_successful=True, fast_runs_percentiles=None, run_arguments=None, plot=False, verbose=False):
    all_returns = []
    
    # prepare output structure 
    if type(fast_runs_percentiles) is int:
        fast_runs_percentiles = [fast_runs_percentiles]
    if fast_runs_percentiles is not None:
        all_returns = [[] for i in range(len(fast_runs_percentiles))]

    #load days one by one
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    for single_date in daterange(start_date, end_date):
        current_date_str = single_date.strftime("%Y-%m-%d")
        print(current_date_str)
        #load day
        dates_dict = load_dates_from_npz(current_date_str, current_date_str, only_challenges=load_only_challenge_data, verbose=verbose)
        # extend day data
        dates_dict = extend_robot_data(dates_dict)
        # get current date dict
        date_dict = dates_dict.get(current_date_str,{})
        # apply evaluation function
        for date_key in dates_dict:
            # check if date in specified date range
            date = datetime.strptime(date_key, '%Y-%m-%d')
            if start_date is not None and start_date > date:
                continue
            if end_date is not None and end_date < date:
                continue

            # get date from dict
            date_dict = dates_dict[date_key]

            runs = date_dict["runs"]
            run_lengths = date_dict["run_lengths"]

            # filter runs
            if only_successful:
                runs, ids_runs = get_successful_runs(runs,date_dict["successful"])
                run_lengths = np.asarray(run_lengths)[ids_runs]
            elif challenges:
                runs, ids_runs = get_challenge_runs(runs,date_dict["challenges"])
                run_lengths = np.asarray(run_lengths)[ids_runs]
            else:
                runs = date_dict["runs"]
                ids_runs = list(range(len(runs)))
            
            if fast_runs_percentiles is not None:
                for id_fast_runs_percentile, fast_runs_percentile in enumerate(fast_runs_percentiles):
                    # filter good runs
                    fast_runs, fast_ids_runs = get_fast_runs(runs, ids_runs, run_lengths, percentile=fast_runs_percentile)

                    if len(fast_runs) == 0:
                        print(f"No runs in {date_key}")
                    
                    # apply evaluation function on all runs
                    for id_run, run in enumerate(fast_runs):
                        # apply evaluation function
                        all_returns[id_fast_runs_percentile].append(eval_run_function(run, fast_ids_runs[id_run], date_dict, run_arguments, plot=False))
        
            else:
                # apply evaluation function on all runs
                print("No fast run percentile assigned. Evaluating all runs...")
                for id_run, run in enumerate(runs):
                    # apply evaluation function
                    all_returns.append(eval_run_function(run, ids_runs[id_run], date_dict, run_arguments, plot=False))

    return all_returns

def iteratively_evaluate_all_runs_in_dates_dict(eval_run_function, dates_dict, start_date=None, end_date=None, challenges=True, only_successful=True, fast_runs_percentile=None, run_arguments=None, plot=False, verbose=False):
    all_returns = []
    
    if start_date is not None:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
   
    for date_key in dates_dict:
        
        # check if date in specified date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None and start_date > date:
            continue
        if end_date is not None and end_date < date:
            continue
        
        # get date from dict
        date_dict = dates_dict[date_key]
        
        runs = date_dict["runs"]
        run_lengths = date_dict["run_lengths"]
    
        # filter runs
        if only_successful:
            runs, ids_runs = get_successful_runs(runs,date_dict["successful"])
        elif challenges:
            runs, ids_runs = get_challenge_runs(runs,date_dict["challenges"])
        else:
            runs = date_dict["runs"]
            ids_runs = list(range(len(runs)))

        if fast_runs_percentile is not None:
            # filter good runs
            run_lengths = np.asarray(run_lengths)[ids_runs]
            runs, ids_runs = get_fast_runs(runs, ids_runs, run_lengths, percentile=fast_runs_percentile)

        if len(runs) == 0:
            print(f"No runs in {date_key}")
        
        # apply evaluation function on all runs
        for id_run, run in enumerate(runs):
            # apply evaluation function
            all_returns.append(eval_run_function(run, ids_runs[id_run], date_dict, run_arguments, plot=False))
        
    return all_returns


def forward_rolling_window_apply(array, window_size, function):
    result = []
    for idx, x in enumerate(array):
        if idx+window_size > len(array):
            break
        window = array[idx:idx+window_size]
        result.append(function(window))
    return result

def filter_date_dict(date_dict, percentile_value=200, challenges=True, only_successful=True):
    filtered_dict = date_dict.copy()
    
    if not filtered_dict:
        return dict()
    
    # filter runs
    runs = filtered_dict["runs"]
    run_lengths = filtered_dict["run_lengths"]
    if only_successful:
        runs, ids_runs = get_successful_runs(runs,filtered_dict["successful"])
    elif challenges:
        runs, ids_runs = get_challenge_runs(runs,filtered_dict["challenges"])
    else:
        runs = filtered_dict["runs"]
        ids_runs = list(range(len(runs)))

    if percentile_value is not None:
        # filter quick runs
        run_lengths = np.asarray(run_lengths)[ids_runs]
        runs, ids_runs = get_fast_runs(runs, ids_runs, run_lengths, percentile=percentile_value)
                
    if len(runs) == 0:
        return dict()
    
        
    # apply filter to all dict arrays
    filtered_dict['run_lengths'] = np.array(filtered_dict['run_lengths'])[ids_runs]
    filtered_dict['difficulties'] = np.array(filtered_dict['difficulties'])[ids_runs]
    filtered_dict['challenges'] = np.array(filtered_dict['challenges'])[ids_runs]
    filtered_dict['successful'] = np.array(filtered_dict['successful'])[ids_runs]
    
    filtered_timestamps = []
    filtered_positions = []
    filtered_orientation = []
    filtered_rotation = []
    filtered_fish = []
    for run in runs:
        filtered_timestamps.extend(filtered_dict['timestamps'][run[0]:run[1]+1])
        filtered_positions.extend(filtered_dict['positions'][run[0]:run[1]+1])
        filtered_orientation.extend(filtered_dict['orientation'][run[0]:run[1]+1])
        filtered_rotation.extend(filtered_dict['rotation'][run[0]:run[1]+1])
        filtered_fish.extend(filtered_dict['fish'][run[0]:run[1]+1])
    filtered_dict['timestamps'] = filtered_timestamps
    filtered_dict['positions'] = filtered_positions
    filtered_dict['orientation'] = filtered_orientation
    filtered_dict['rotation'] = filtered_rotation
    filtered_dict['fish'] = filtered_fish
    
    # zero runs as we filtered out only selected runs
    zeroed_runs = []
    current_index = 0
    for run in runs:
        zeroed_runs.append([current_index, current_index+(run[1]-run[0])])
        current_index = current_index+(run[1]-run[0])+1
    filtered_dict['runs'] = zeroed_runs
    
    
    return filtered_dict