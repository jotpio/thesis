from util import daterange
from datetime import datetime
from util import load_dates_from_npz
from extend_robot_data import extend_robot_data
def iteratively_evaluate_dates(start_date, end_date, eval_date_function, load_only_challenge_data, verbose=False):
    all_returns = []
    #load days one by one
    dt_start_date = datetime.strptime(start_date, "%Y-%m-%d")
    dt_end_date = datetime.strptime(end_date, "%Y-%m-%d")
    for single_date in daterange(dt_start_date, dt_end_date):
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