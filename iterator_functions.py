from util import daterange, get_fast_runs, get_successful_runs, get_challenge_runs
from datetime import datetime
from util import load_dates_from_npz
from extend_robot_data import extend_robot_data
import numpy as np


def iteratively_evaluate_dates_files(start_date, end_date, eval_date_function, load_only_challenge_data, verbose=False):
    all_returns = []
    #load days one by one
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
        # apply evaluation function
        all_returns.append(eval_date_function(date_dict))
    return all_returns


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