import matplotlib.pyplot as plt
import seaborn as sns

from util import get_challenge_runs, get_successful_runs, get_hours_minutes_seconds_from_decimal_hours, daterange
from datetime import datetime
import numpy as np

def plot_time_of_day_histogram(dates_dict, challenges=True, only_successful=True, show=True):
    # bar plot average time of day for each run
    dates_keys = dates_dict.keys()

    start_times = []
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        
        # collect start times for each (challenge/successful) run
        date_runs = date_dict["runs"]
        date_timestamps = date_dict["timestamps"]
        
        if only_successful:
            runs, _ = get_successful_runs(date_runs,date_dict["successful"])
        elif challenges:
            runs, _ = get_challenge_runs(date_runs,date_dict["challenges"])
        else:
            runs = date_runs
        for run in runs:
            start_time = date_timestamps[run[0]]
            start_times.append(start_time)


    # hist plot start times
    start_times_hours = [datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S,%f').hour for start_time in start_times]
    # print(len(start_times_hours))
    time_bins = list(range(8,23))
    fig = plt.figure(figsize=(15,5))
    plt.xlabel("hour of the day")
    plt.ylabel("number of runs")
    if only_successful:
        ch_or_s = "successful challenge "
    elif challenges:
        ch_or_s = "challenge "
    else:
        ch_or_s = ""
    plt.title(f"total number of {ch_or_s}runs for each hour of the day\n{list(dates_keys)[0]} - {list(dates_keys)[-1]}")
    plt.xticks(time_bins)
    _,_,_=plt.hist(start_times_hours, time_bins, label=time_bins, align="left")
    
    if show:
        plt.show()
    
    return fig


def plot_daily_number_runs(dates_dict, start_date=None, end_date=None, show=True):
    # bar plot number of (unique) visitors for each day
    dates_keys = dates_dict.keys()
    if start_date is not None:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = datetime.strptime(list(dates_dict.keys())[0], '%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.strptime(list(dates_dict.keys())[-1], '%Y-%m-%d')

    num_runs_per_day = []
    num_challenge_runs_per_day = []
    num_successful_runs_per_day = []
    num_non_ch_runs_per_day = []
        
    for single_date in daterange(start_date, end_date):
        current_date_str = single_date.strftime("%Y-%m-%d")
        date = datetime.strptime(current_date_str, '%Y-%m-%d')
        
        if start_date is not None and start_date > date:
            continue
        if end_date is not None and end_date < date:
            continue
        
        
        date_dict = dates_dict.get(current_date_str,{})
        if not date_dict:
            num_runs_per_day.append(0)
            num_challenge_runs_per_day.append(0)
            num_successful_runs_per_day.append(0)
            num_non_ch_runs_per_day.append(0)
            continue
            
        date_runs = date_dict["runs"]

        num_runs_per_day.append(len(date_dict['runs']))
        num_challenge_runs_per_day.append(len(get_challenge_runs(date_runs,date_dict["challenges"])[0]))
        num_successful_runs_per_day.append(len(get_successful_runs(date_runs,date_dict["successful"])[0]))
        estimated_num_visitors = len(date_dict['runs']) - len(get_challenge_runs(date_runs,date_dict["challenges"])[0])
        num_non_ch_runs_per_day.append(estimated_num_visitors)

    # print(num_successful_runs_per_day)

    # hist plot number of runs per day
    fig = plt.figure(figsize=(20,10))
    # plt.xlabel("day")
    plt.ylabel("number of runs")

    plt.title(f"run numbers and estimated visitors for each day\n{list(dates_keys)[0]} - {list(dates_keys)[-1]}")
    ax = plt.gca()
    date_range = [day.strftime("%Y-%m-%d") for day in list(daterange(start_date, end_date))]
    tot = ax.bar(list(date_range), num_runs_per_day, label='total number of runs')
    cha = ax.bar(list(date_range), num_challenge_runs_per_day, label='total number of challenge runs')
    suc = ax.bar(list(date_range), num_successful_runs_per_day, label='total number of successful runs')

    ax2 = ax.twinx()
    ax2.get_yaxis().set_visible(False)
    ax2.sharey(ax)
    ax2.grid(False)
    # ax.get_yaxis().set_visible(False)

    est, = ax2.plot(num_non_ch_runs_per_day, 'ko-', label='estimated daily number of visitors')
    mean_est_visitors = plt.axhline(y = np.mean(num_non_ch_runs_per_day), color = 'r', linestyle = '-', label='mean daily estimated number of visitors')

    # print(ax2.get_yticklabels())
    # ax2.get_yticklabels()[2].set_visible(False)

    # annotate line plot points
    for i, point in enumerate(num_non_ch_runs_per_day):
        ax2.annotate(point,(i, point+3), ha='center', color='black', size=18)

    # ax3 = fig.add_subplot(122)
    # est, = ax2.plot(num_non_ch_runs_per_day, 'ko-', label='estimated number of visitors')

    plt.legend(handles=[tot,cha,suc,est, mean_est_visitors])
    fig.autofmt_xdate()
    plt.tight_layout()
    if show:
        plt.show()
    return fig

    
def plot_daily_use_times_and_operational_times(dates_dict, to_pdf=False, show=True):
    # bar plot use time for each day in minutes
    dates_keys = dates_dict.keys()

    day_lengths = []
    day_use_times = []
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        date_run_lengths = date_dict["run_lengths"]

        day_lengths.append(date_dict.get("day_length",0)/60/60)
        day_use_times.append(np.sum(date_run_lengths)/60/60)

    # plot
    title = f"date range: {list(dates_keys)[0]} - {list(dates_keys)[-1]}"
    fig = plt.figure(num=title, figsize=(20,6))
    plt.title(title)
    plt.xlabel("dates")
    plt.ylabel("time in hours")
    plt.bar(dates_keys,day_lengths, label="approximate operating time")
    plt.bar(dates_keys,day_use_times, label="time of use")

    # calc and plot means and percentages
    day_lengths = np.array(day_lengths)
    day_use_times = np.array(day_use_times)
    mean_operating_time = np.nanmean(day_lengths[day_lengths>1])
    mean_use_time = np.nanmean(day_use_times[day_use_times>0.1])
    mot_hours, mot_minutes, mot_seconds = get_hours_minutes_seconds_from_decimal_hours(mean_operating_time)
    mut_hours, mut_minutes, mut_seconds = get_hours_minutes_seconds_from_decimal_hours(mean_use_time)

    perc_use_time = np.divide(day_use_times, day_lengths,out=np.zeros_like(day_use_times), where=day_lengths!=0) * 100
    mean_perc_use_time = np.nanmean(perc_use_time[perc_use_time>0])
    
    text =  f"mean operating time*:    ~{mot_hours:d}h {int(mot_minutes)}min\n" \
            f"mean use time*:             ~{mut_hours:d}h {int(mut_minutes):d}min\n" \
            f"mean percentual daily use time of daily operating time*:     {mean_perc_use_time:.2f}%"
    if to_pdf:
        plt.gcf().text(0.1, 0.1, text, ha="left", va="baseline", fontsize=18)
        disclaimer = f"*very low use and operation time where filtered out to omit Tuesdays"
        plt.gcf().text(0.69, 0.1, disclaimer, ha="left", va="baseline", fontsize=10)
    else:
        plt.gcf().text(0.1, -0.1, text, ha="left", va="baseline", fontsize=18)
        disclaimer = f"*very low use and operation time where filtered out to omit Tuesdays"
        plt.gcf().text(0.69, -0.1, disclaimer, ha="left", va="baseline", fontsize=10)

    plt.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    # plt.subplots_adjust(left=0.3, right=0.9, bottom=0.5, top=0.9)
    if to_pdf:
        plt.gcf().subplots_adjust(bottom=0.4)

    if show:
        plt.show()
        
    return fig


def plot_daily_start_end_times(dates_dict, show=True):

    # plot daily operation time
    dates_keys = dates_dict.keys()

    day_starts = []
    day_ends = []
    operating_time = []
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        date_ts = date_dict["timestamps"]


        if date_ts != []:
            start = datetime.strptime(date_ts[0], '%Y-%m-%d %H:%M:%S,%f')
            end = datetime.strptime(date_ts[-1], '%Y-%m-%d %H:%M:%S,%f')
            day_starts.append(start.strftime("%H.%M"))
            day_ends.append(end.strftime("%H.%M"))
            delta = end - start
            operating_time.append(delta.seconds / 60 / 60)

        else:
            start = datetime.strptime(date_key+" 00:00:00,000", '%Y-%m-%d %H:%M:%S,%f')
            end = datetime.strptime(date_key+" 01:00:00,000", '%Y-%m-%d %H:%M:%S,%f')
            day_starts.append(start.strftime("%H.%M"))
            day_ends.append(end.strftime("%H.%M"))
            delta = end - start
            operating_time.append(delta.seconds / 60 / 60)


    # plot
    title = f"daily operting times\n{list(dates_keys)[0]} - {list(dates_keys)[-1]}"
    fig = plt.figure(num=title, figsize=(25,10))

    with sns.axes_style("darkgrid"):

        plt.rcParams['xtick.major.size'] = 7
        plt.rcParams['xtick.major.width'] = 2
        plt.rcParams['xtick.bottom'] = True

        ax=plt.gca()

        #
        day_ends = np.array(day_ends, dtype=float)
        day_starts = np.array(day_starts, dtype=float)
        operating_time = np.array(operating_time,dtype=float)

        plt.bar(x=list(dates_keys), height=operating_time, bottom=day_starts, width=0.7, label="daily operating times", align='center')

        # horizontal line for mean start and end time
        mean_start = np.mean(day_starts[day_starts>0])
        mean_end = np.mean(day_ends[day_ends>9])
        plt.axhline(y=mean_start, color='g', linestyle='--', label="usual startup time")
        plt.axhline(y=mean_end, color='r', linestyle='--', label="usual shutdown time")

        # weekly vertical lines
        for id_date, date in enumerate(dates_keys):
            date_dt = datetime.strptime(date+" 01:00:00,000", '%Y-%m-%d %H:%M:%S,%f')
            if date_dt.weekday() == 0:
                plt.axvline(x = id_date-0.5, color = 'k', linestyle='-')


        #
        plt.ylim((9,23))
        plt.yticks(np.arange(9, 24, 1.0))

        plt.xlim(ax.patches[0].get_x()-0.1, ax.patches[-1].get_x())
        plt.title(title)
        plt.xlabel("dates")
        plt.ylabel("hour of the day")
        # fig.autofmt_xdate()
        plt.xticks(rotation=90)


        plt.legend()
        # plt.tight_layout()
        
        if show:
            plt.show()
        
        return fig

def plot_weekday_business(dates_dict, show=True):
    # plot busiest weekdays by percentual use time, estimated visitors

    dates_keys = dates_dict.keys()

    weekday_perc_use_times = [[] for i in range(7)] #setup weekday array; 0 is monday
    weekday_visitors = [[] for i in range(7)]

    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        date_ts = date_dict["timestamps"]
        date_run_lengths = date_dict["run_lengths"]
        date_runs = date_dict["runs"]

        # percentual use time
        day_length = date_dict.get("day_length",0)/60/60
        day_use_time = np.sum(date_run_lengths)/60/60
        perc_use_time = np.divide(day_use_time, day_length,out=np.zeros_like(day_use_time), where=day_length!=0) * 100

        # estimated num of visitors
        estimated_num_visitors = len(date_dict['runs']) - len(get_challenge_runs(date_runs,date_dict["challenges"])[0])


        # get current weekday 
        date_weekday = datetime.strptime(date_key+" 01:00:00,000", '%Y-%m-%d %H:%M:%S,%f').weekday()

        # fill weekday arrays
        weekday_perc_use_times[date_weekday].append(perc_use_time)
        weekday_visitors[date_weekday].append(estimated_num_visitors)

    # get means
    mean_weekday_perc_use_times = []
    for weekday in weekday_perc_use_times:
        if len(weekday) == 0:
            mean_weekday_perc_use_times.append(0)
        else:
            mean_weekday_perc_use_times.append(np.mean(weekday))
    # mean_weekday_perc_use_times = np.mean(weekday_perc_use_times, axis=1)
    mean_weekday_visitors = []
    for weekday in weekday_visitors:
        if len(weekday) == 0:
            mean_weekday_visitors.append(0)
        else:
            mean_weekday_visitors.append(np.mean(weekday))
    # mean_weekday_visitors = np.mean(weekday_visitors, axis=1)

    with sns.axes_style("darkgrid"):
        # plot
        title = f"average weekday use times and visitors \n{list(dates_keys)[0]} - {list(dates_keys)[-1]}"
        fig, ax1 = plt.subplots(num=title, figsize=(13,7))

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        ax2 = ax1.twinx()
        num_vis_plot = ax1.bar(weekdays, mean_weekday_visitors, color='g', label='mean number of estimated visitors per weekday')
        perc_plot = ax2.plot(mean_weekday_perc_use_times, 'bo', ms=10, label='mean percentual use time of operational time')

        import matplotlib.ticker as mtick
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter())


        ax1.set_xlabel('weekdays')
        ax1.set_ylabel('number of estimated visitors', color='g')
        ax2.set_ylabel('percentual use time of running time (in %)', color='b')

        print(ax1,ax2)
        from matplotlib import rcParams
        rcParams.update({'figure.autolayout': True})
        # nticks = 7
        # import matplotlib
        # ax1.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(nticks))
        # ax2.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(nticks))
        ax1.grid(None)
        ax2.grid(None)
        # ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))

        ax1.legend(handles=[num_vis_plot,perc_plot[0]])
        
        if show:
            plt.show()
        
        return fig
