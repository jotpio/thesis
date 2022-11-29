import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

from util import get_challenge_runs, get_successful_runs, distance, get_fish_pos_per_run, get_distance_to_goal, calculate_run_velocity_speed_acceleration, get_fish_following_per_run, flatten_2d_list, tolerant_mean, equalize_arrays


def plot_all_positions(dates_dict, start_date=None, end_date=None, ax=None, challenges=True, only_successful=True, show=True, size=(10,10)):
    # plot all positions
    all_positions = []
    dates_keys = dates_dict.keys()
    
    if start_date is not None:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        # print(date_key)
        date = datetime.strptime(date_key, '%Y-%m-%d')

        if start_date is not None and start_date > date:
            continue
        if end_date is not None and end_date < date:
            continue
        
        # collect positions
        date_positions = date_dict.get("positions",[])        
        if date_positions is not None:
            if only_successful:
                successful_runs, _ = get_successful_runs(date_dict["runs"], date_dict["successful"])
                for run in successful_runs:
                    try:
                        all_positions.extend(date_positions[run[0]:run[1]+1])
                    except:
                        print(run)
            elif challenges:
                challenge_runs, _ = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
                for run in challenge_runs:
                    all_positions.extend(date_positions[run[0]:run[1]+1])
            else:
                all_positions.extend(date_positions)

    # plot if positions available
    if len(all_positions) != 0:
        x = np.array(all_positions)[:,0]
        y = np.array(all_positions)[:,1]
        
        if ax is None:
            fig=plt.figure(num="all positions", figsize=size)
            ax = fig.add_subplot(111)
        else:
            fig=ax.get_figure()
        
        ax.set_xlim(2000)
        ax.set_ylim(2000)
        ax.invert_xaxis()
        ax.invert_yaxis()
        # plt.gca().invert_yaxis()
        ax.scatter(x,y,s=2)
        # plt.plot(x, y)
        if only_successful:
            title_run_modifier = "only successful runs"
        elif challenges:
            title_run_modifier = "all challenge runs"
        else:
            title_run_modifier = "all runs"
        ax.set_title(f"all positions: {start_date.strftime('%Y-%m-%d')}  -  {end_date.strftime('%Y-%m-%d')} - {title_run_modifier}")
        
        if show:
            plt.show()
        
        return fig

def plot_run(date_dict, id_run, date_key, challenges=True, only_successful=True, show=True):
    fig = plt.figure(num=date_key, figsize=(16,9))
    # get run
    date_runs = date_dict['runs']
    date_successful = date_dict['successful']
    date_challenges = date_dict['challenges']
    if only_successful:
        date_runs, _ = get_successful_runs(date_runs, date_successful)
    elif challenges:
        date_runs, _ = get_challenge_runs(date_runs, date_challenges)
    run = date_runs[id_run]
        
    dt_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in date_dict["timestamps"]]
    velocity_vectors_run, speed_run, acceleration_run = calculate_run_velocity_speed_acceleration(date_dict, run, dt_timestamps)
    
    #print(id_run)
    #print(run)
    #print(date_key)

    # positions
    ax1 = plt.subplot(321)
    x = np.array(date_dict["positions"])[run[0]:run[1]+1,0]
    y = np.array(date_dict["positions"])[run[0]:run[1]+1,1]

    ax1.set_xlim(2000)
    ax1.set_ylim(2000)
    ax1.invert_xaxis()
    ax1.invert_yaxis()
    ax1.axis('equal')
    ax1.scatter(x,y,s=2)
    ax1.plot(x, y)

    # plot start and end points
    ax1.plot(x[0], y[0], marker="o", markersize=12, color='green')
    ax1.plot(x[-1], y[-1], marker="X", markersize=12, color='red')

    ax1.set_title(f"positions {date_key}_{id_run}")
    # plt.show()

    # speeds    
    ax2 = plt.subplot(322)
    ax2.plot(speed_run)
    ax2.set_title(f"speeds {date_key}_{id_run}")

    # acceleration
    ax3 = plt.subplot(323)
    # run_accelerations = date_dict["accelerations"][id_run]
    ax3.plot(acceleration_run)
    ax3.set_title(f"accelerations {date_key}_{id_run}")

    # rotations
    ax4 = plt.subplot(324, projection='polar')
    run_rotations = np.radians(date_dict["rotation"][run[0]:run[1]+1])                
    circular_hist(ax4, run_rotations, bins=16, density=True, offset=0, gaps=True)
    ax4.set_title(f"rotations {date_key}_{id_run}")

    #
    if only_successful:
        title_run_modifier = "successful run"
    elif challenges:
        title_run_modifier = "challenge run"
    else:
        title_run_modifier = "run"
    fig.suptitle(f"{dt_timestamps[run[0]]} - {dt_timestamps[run[1]]}: {title_run_modifier}")#, fontsize=10)
    plt.tight_layout()
    if show:
        plt.show()
        
    return fig
                
def plot_runs(dates_dict, start_date=None, end_date=None, challenges=True, only_successful=True, show=True):              
    dates_keys = dates_dict.keys()

    for date_key in dates_keys:
        date_dict = dates_dict[date_key]

        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        date = datetime.strptime(date_key, '%Y-%m-%d')

        if start_date is not None and start_date_dt > date:
            continue
        if end_date is not None and end_date_dt < date:
            continue

        # plot if positions available
        if len(date_dict["positions"]) != 0:

            # traverse runs and plot each one separately
            if only_successful:
                runs, ids_runs = get_successful_runs(date_dict["runs"], date_dict["successful"])
            
            if challenges:
                runs, ids_runs = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
            else:
                runs = date_dict["runs"]
                ids_runs = list(range(len(runs)))
            
            for id_r, run in enumerate(runs):                
                id_run = ids_runs[id_r]
                plot_run(date_dict, id_run, date_key, challenges, only_successful)
                
# https://stackoverflow.com/questions/22562364/circular-polar-histogram-in-python
def circular_hist(ax, x, bins=16, density=True, offset=0, gaps=True):
    """
    Produce a circular histogram of angles on ax.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        axis instance created with subplot_kw=dict(projection='polar').

    x : array
        Angles to plot, expected in units of radians.

    bins : int, optional
        Defines the number of equal-width bins in the range. The default is 16.

    density : bool, optional
        If True plot frequency proportional to area. If False plot frequency
        proportional to radius. The default is True.

    offset : float, optional
        Sets the offset for the location of the 0 direction in units of
        radians. The default is 0.

    gaps : bool, optional
        Whether to allow gaps between bins. When gaps = False the bins are
        forced to partition the entire [-pi, pi] range. The default is True.

    Returns
    -------
    n : array or list of arrays
        The number of values in each bin.

    bins : array
        The edges of the bins.

    patches : `.BarContainer` or list of a single `.Polygon`
        Container of individual artists used to create the histogram
        or list of such containers if there are multiple input datasets.
    """
    # Wrap angles to [-pi, pi)
    x = (x+np.pi) % (2*np.pi) - np.pi

    # Force bins to partition entire circle
    if not gaps:
        bins = np.linspace(-np.pi, np.pi, num=bins+1)

    # Bin data and record counts
    n, bins = np.histogram(x, bins=bins)

    # Compute width of each bin
    widths = np.diff(bins)

    # By default plot frequency proportional to area
    if density:
        # Area to assign each bin
        area = n / x.size
        # Calculate corresponding bin radius
        radius = (area/np.pi) ** .5
    # Otherwise plot frequency proportional to radius
    else:
        radius = n

    # Plot data on ax
    patches = ax.bar(bins[:-1], radius, zorder=1, align='edge', width=widths,
                     edgecolor='C0', fill=False, linewidth=1)

    # Set the direction of the zero angle
    ax.set_theta_offset(offset)

    # Remove ylabels for area plots (they are mostly obstructive)
    if density:
        ax.set_yticks([])

    return n, bins, patches


def plot_position_hexmap(pos, ax=None):
    # plot position heatmap
    
    if ax is None:
        fig=plt.figure(num="position hexmap", figsize=(16,16))
        ax = fig.add_subplot(111)
    x = np.array(pos)[:,0]
    y = np.array(pos)[:,1]

    # sns.jointplot(x=x, y=y, kind="hex", color="#4CB391")
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.invert_yaxis()
    ax.hexbin(x,y, gridsize=80, bins='log', cmap='inferno') # use log bins to ignore positions where robot stands still
    plt.show()

    
def plot_starts_ends(dates_dict, start_date=None, end_date=None, challenges=True, only_successful=True, show=True):
    # all start and end positions challenge runs
    dates_keys = dates_dict.keys()
    
    all_starts = []
    all_ends = []

    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        
        
        # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]
    
        # plot if positions available
        if len(date_dict["positions"]) != 0:
            if only_successful:
                runs, _ = get_challenge_runs(date_dict["runs"], date_dict["successful"])
            elif challenges:
                runs, _ = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
            # print(challenge_runs)
            # traverse runs and collect start and end points
            for id_run, run in enumerate(runs):
                start = np.array(date_dict["positions"])[run[0]]
                end = np.array(date_dict["positions"])[run[1]]

                all_starts.append(start)
                all_ends.append(end)

        assert len(all_starts) == len(all_ends)

    if len(all_starts) > 0:
        fig = plt.figure(num=date_key, figsize=(15,15))
        plt.scatter(np.array(all_starts)[:,0], np.array(all_starts)[:,1], marker="o", s=15, color='green', label="Robot start positions")
        plt.scatter(np.array(all_ends)[:,0], np.array(all_ends)[:,1], marker="X", s=30, color='red', label="Robot end positions")

        if only_successful:
            run_descriptor = "successful challenge "
        elif challenges:
            run_descriptor = "challenge "
        else:
            run_descriptor = ""
        plt.title(f"[{start_date}]-[{end_date}] - all robot start and end positions of {run_descriptor}runs")
        plt.xlim(0,2000)
        plt.ylim(0,2000)
        plt.xlabel("x-coordinate (px)")
        plt.ylabel("y-coordinate (px)")
        plt.legend()
        if show:
            plt.show()
        else:
            return fig
    else:
        return plt.figure()       

    
def plot_rotations_and_heatmap(dates_dict, start_date=None, end_date=None, challenges=True, only_successful=True, ignore_robot_standing=True, polar_density=True, show=True):

    dates_keys = dates_dict.keys()

    all_rotations = []
    all_positions = []

    for date_key in dates_keys:    
        date_dict = dates_dict[date_key]
        
        
        # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]
        
        
        date_rotations = date_dict["rotation"]
        date_positions = date_dict["positions"]
        # combine positions and rotations
        if only_successful:
            successful_runs, ids = get_successful_runs(date_dict["runs"], date_dict["successful"])
            for id_cr, run in enumerate(successful_runs):
                # append challenge rotations
                all_rotations.extend(date_rotations[run[0]:run[1]+1])
                # append challenge positions
                all_positions.extend(date_positions[run[0]:run[1]+1])
        
        elif challenges:
            challenge_runs, ids = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
            for id_cr, run in enumerate(challenge_runs):
                # append challenge rotations
                all_rotations.extend(date_rotations[run[0]:run[1]+1])
                # append challenge positions
                all_positions.extend(date_positions[run[0]:run[1]+1])
        else:
            # append all rotations
            if date_rotations is not None:
                all_rotations.extend(date_rotations)
            
            # append all positions
            if date_positions is not None:
                all_positions.extend(date_positions)
    # remove positions and rotations where robot is not moving         
    if ignore_robot_standing:
        assert len(all_rotations) == len(all_positions)
        old_pos = [0,0]
        skipped = 0
        adjusted_positions = []
        adjusted_rotations = []

        # compare each pos to previous pos and skip if basically unchanged
        for id_pos, pos in enumerate(all_positions):
            if distance(pos, old_pos) < 0.1:
                skipped += 1
            else:
                adjusted_positions.append(pos)
                adjusted_rotations.append(all_rotations[id_pos])
            old_pos = pos
        all_positions = adjusted_positions
        all_rotations = adjusted_rotations

    # plot overall rotation 
    # fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection='polar'))
    fig = plt.figure(figsize=(20,10))
    fig.suptitle(f'[{start_date}]-[{end_date}] - robot: Average rotation circular histogram and positional heatmap', fontsize=14)
    ax1 = plt.subplot(121, projection='polar')
    ax1.set_title("binned robot rotation")
    circular_hist(ax1, np.radians(all_rotations),bins=16, density=polar_density, offset=0, gaps=True)


    # plot overall heatmap
    ax2 = plt.subplot(122)
    x = np.array(all_positions)[:,0]
    y = np.array(all_positions)[:,1]

    # sns.jointplot(x=x, y=y, kind="hex", color="#4CB391")
    plt.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    # plt.gca().invert_yaxis()
    plt.hexbin(x,y, gridsize=80, bins='log', cmap='inferno') # use log bins to ignore positions where robot stands still
    plt.title("hexbin plot of all loaded robot positions")
    
    if show:
        plt.show()
    else:
        return fig

    
def plot_inter_individual_distances(dates_dict_robot_fish, start_date=None, end_date=None, challenges=True, only_successful=True, bins=20, show=True):
    dates_keys = dates_dict_robot_fish.keys()

    if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    figs1 = []
    figs2 = []
    
    for date_key in dates_keys:
        
        # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]
        
        # generate data for plots
        all_mean_iid_per_bin = []
        date_dict = dates_dict_robot_fish[date_key]

        fish_instance = date_dict["fish"]
        runs = date_dict["runs"]
        if only_successful:
            runs, _ = get_successful_runs(runs,date_dict["successful"])
        elif challenges:
            runs, _ = get_challenge_runs(runs,date_dict["challenges"])
        else:
            runs = date_dict["runs"]

        if len(runs) > 0:
            fish_pos_runs = get_fish_pos_per_run(fish_instance,runs)
        else:
            continue

        for id_run, run in enumerate(runs):
            fish_pos_this_run = fish_pos_runs[id_run]
            robot_pos_run = np.array(date_dict['positions'][run[0]:run[1]+1])
            # sanity check
            if len(fish_pos_this_run) != len(robot_pos_run):
                assert False, f"Wrong array lengths: fish {len(fish_pos_this_run)} and robot {len(robot_pos_run)}"
            fish1_pos_this_run = np.array([fish[0] for fish in fish_pos_this_run]) # get first fish for each timestamp as it always is the target fish
            # plot all runs in one 
            ii_distances_r_f1_run = np.linalg.norm(fish1_pos_this_run-robot_pos_run, axis=1)
            plt.figure(num=f"{date_key} - inter-individual distances between robot and target fish (id 1)", figsize=(15,5))
            plt.plot(ii_distances_r_f1_run)

            # plot frame-binned
            indexes = list(range(len(fish_pos_this_run)))
            hist, bin_edges = np.histogram(indexes, bins=bins, range=None, weights=None, density=None) # bin the indexes to get sclice edges
            # slice the positions by frame-bins and take average per slice
            pointer = 0
            mean_iid_per_bin = []
            for id_edge, edge in enumerate(hist):
                # print(hist)
                # print(edge)
                slice_ = ii_distances_r_f1_run[pointer:pointer+edge]
                if len(slice_) > 0:
                    mean_dist_sclice = np.nanmean(slice_)
                else:
                    mean_dist_sclice = np.nan # is ignored later

                # print(mean_dist_sclice)
                mean_iid_per_bin.append(mean_dist_sclice)
                pointer = pointer + edge

            all_mean_iid_per_bin.append(mean_iid_per_bin)

        # skip dates with no data
        if all_mean_iid_per_bin == []:
            print(f"{date_key} No data? (usually on tuesdays)")
            continue

        overall_mean_iid_per_bin = np.nanmean(all_mean_iid_per_bin, axis=0)
        overall_std_iid_per_bin = np.nanstd(all_mean_iid_per_bin, axis=0)

        # plot all runs this day in one plot      
        fig = plt.figure(num=f"{date_key} - inter-individual distances between robot and target fish (id 1)", figsize=(15,5))  
        figs1.append(fig)
        plt.title(f"{date_key} - inter-individual distances between robot and target fish (id 1)")
        plt.ylim(0,3000)
        plt.ylabel("distance in px")
        plt.xlabel("frame")
        if show:
            plt.show()


        # bar plot all mean idds per bin
        fig = plt.figure(num=f"{date_key} - frame-scliced inter-individual distances between robot and target fish (id 1)", figsize=(15,5))
        figs2.append(fig)
        ticks = np.arange(len(overall_mean_iid_per_bin))
        plt.bar(x=ticks, height=overall_mean_iid_per_bin, yerr=overall_std_iid_per_bin, tick_label=ticks, color='black', ecolor="gray", capsize=4)
        plt.title(f"{date_key} - frame-binned average inter-individual distances between robot and target fish (id 1)")
        plt.xlabel("i-th part of frames")
        plt.ylabel("distance in px")
        plt.ylim(0,1500)
        '''
            challenge - zones
            zor: 40
            zoo: 100
            zoa: 220
        '''
        plt.axhline(40, linewidth=2, color='r', linestyle=(0,(2,2)), label="repulsion") # repulsion distance
        plt.axhline(100, linewidth=2, color='b', linestyle=(0,(2,2)), label="orientation") # orientation distance
        plt.axhline(220, linewidth=2, color='g', linestyle=(0,(2,2)), label="attraction") # attraction distance

        plt.legend()
        if show:
            plt.show()
            
    return figs1, figs2
   
    
def plot_run_length_hist(dates_dict, start_date=None, end_date=None, bin_size=10, challenges=True, only_successful=True, show=True):
    dates_keys = dates_dict.keys()

    all_run_lengths = []
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        
        # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]

        # collect start times for each (challenge/successful) run
        date_run_lengths = date_dict["run_lengths"]

        if only_successful:
            run_lengths, _ = get_successful_runs(date_run_lengths,date_dict["successful"])
        elif challenges:
            run_lengths, _ = get_challenge_runs(date_run_lengths,date_dict["challenges"])
        else:
            run_lengths = date_run_lengths

        # add date run lengths to all run lengths
        all_run_lengths.extend(run_lengths)

    fig = plt.figure(figsize=(15,5))
    fig.suptitle(f'[{start_date}]-[{end_date}] - run length histogram', fontsize=14)
    bins=list(range(0,200,bin_size))
    plt.xticks(bins)
    plt.hist(all_run_lengths, bins=bins,align="left")
    
    plt.xlabel("time for run (s)")
    plt.ylabel("number of runs")
    
    if show:
        plt.show()
    else:
        return fig


def plot_robot_distance_goal(dates_dict, start_date, end_date, challenges=True, only_successful=True, show=True):
    dates_keys = dates_dict.keys()

    if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    figs = []
    for date_key in dates_keys:
        
        # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]
        
        #
        fig = plt.figure(figsize=(15,5))
        figs.append(fig)
        date_dict = dates_dict[date_key]

        # collect goal distances for each run
        date_runs = date_dict["runs"]
        date_pos = date_dict["positions"]

        if only_successful:
            runs, _ = get_successful_runs(date_runs,date_dict["successful"])
        elif challenges:
            runs, _ = get_challenge_runs(date_runs,date_dict["challenges"])
        else:
            runs = date_runs
        all_robot_dist_goal = []
        for run in runs:
            robot_pos_run = date_pos[run[0]:run[1]+1]
            robot_dist_goal = get_distance_to_goal(robot_pos_run)
            all_robot_dist_goal.append(robot_dist_goal.tolist())
            plt.plot(robot_dist_goal)
        if len(all_robot_dist_goal) > 0:
            mean_dist_goal = np.mean(equalize_arrays(all_robot_dist_goal, 0), axis=0)
            plt.plot(mean_dist_goal, color='green', linewidth=6)
            
        plt.title(f"{date_key} - robot distance to target")
        plt.ylabel("distance to goal (px)")
        plt.xlabel("frames")
        if show:
            plt.show()
            
    return figs


def plot_following1(dates_dict, start_date=None, end_date=None, only_successful=True, challenges=True, show=True):
    dates_keys = dates_dict.keys()

    if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    daily_percentage_of_run_following = []
    daily_run_lengths = []
    for date_key in dates_keys:

        # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]

        # generate data for plots
        date_dict = dates_dict[date_key]

        fish_instance = date_dict["fish"]
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

        # filter run lengths
        run_lengths = np.array(run_lengths)[ids_runs]

        # get following status for all fish for all timesteps
        if len(runs) > 0:
            fish_following_runs = get_fish_following_per_run(fish_instance,runs)
        else:
            continue

        day_percentage_of_run_following = []
        for id_run, run in enumerate(runs):
            fish_following_this_run = fish_following_runs[id_run]

            # get target fish for each ts
            target_fish_following_this_run = []
            for ts in fish_following_this_run:
                target_fish_following_this_run.append(ts[0])
            target_fish_following_this_run = np.array(target_fish_following_this_run)
            # plt.plot(target_fish_following_this_run)
            # plt.show()

            # calc percentage of run following
            percentage_of_run_following = target_fish_following_this_run.sum() / len(target_fish_following_this_run)
            # print(target_fish_following_this_run.sum(), len(target_fish_following_this_run), run)
            day_percentage_of_run_following.append(percentage_of_run_following)
        # print(days_percentage_of_run_following)
        daily_percentage_of_run_following.append(day_percentage_of_run_following)
        daily_run_lengths.append(run_lengths)

    # print(all_percentage_of_run_following)

    # histogram following percentages
    flattened_percentage_of_run_following = [x for xs in daily_percentage_of_run_following for x in xs]
    fig = plt.figure(figsize=(15,8))
    plt.title(f"[{start_date}] - [{end_date}] - histogram of leading percentages per run ")
    plt.hist(flattened_percentage_of_run_following, bins=20)
    plt.xlabel("percentage of run time leading the target fish")
    plt.ylabel("number of runs")
    plt.show()

    # run length following percentage correlation plot
    flattened_daily_run_lengths = [x for xs in daily_run_lengths for x in xs]
    fig = plt.figure(figsize=(15,8))
    plt.title(f"[{start_date}] - [{end_date}] - correlation plot of run lengths and leading percentage")
    plt.scatter(flattened_daily_run_lengths, flattened_percentage_of_run_following)
    plt.xlabel("run time in seconds")
    plt.ylabel("percentage of run time leading the target")

    # linear regression        
    coef = np.polyfit(flattened_daily_run_lengths,flattened_percentage_of_run_following,1)
    poly1d_fn = np.poly1d(coef) 
    # poly1d_fn is now a function which takes in x and returns an estimate for y
    plt.plot(flattened_daily_run_lengths,flattened_percentage_of_run_following, 'bo', flattened_daily_run_lengths, poly1d_fn(flattened_daily_run_lengths), '--k') #'--k'=black dashed line, 'yo' = yellow circle marker

    # polynomial regression
    mymodel = np.poly1d(np.polyfit(flattened_daily_run_lengths, flattened_percentage_of_run_following, 10))
    myline = np.linspace(8, 180, 100)
    plt.plot(myline,  mymodel(myline), '--r')

    # plt.xlim(0, 5)
    # plt.ylim(0, 12)
    if show:
        plt.show()
    else:
        return fig
    

def plot_runlength_dist_goal_target_corr(dates_dict, start_date=None, end_date=None, only_successful=True, challenges=True, show=True):
    dates_keys = dates_dict.keys()

    if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    daily_initial_dist_robot_target_fish = []
    daily_initial_dist_robot_goal = []
    daily_run_lengths = []
    for date_key in dates_keys:

         # filter date range
        date = datetime.strptime(date_key, '%Y-%m-%d')
        if start_date is not None:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if start_date is not None and start_date_dt > date:
                continue
        else:
            start_date = list(dates_keys)[0]
        if end_date is not None:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_date is not None and end_date_dt < date:
                continue
        else:
            end_date = list(dates_keys)[-1]

        # generate data for plots
        date_dict = dates_dict[date_key]

        fish_instance = date_dict["fish"]
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
        # filter run lengths
        run_lengths = np.array(run_lengths)[ids_runs]

        # get pos for all fish for all timesteps
        if len(runs) > 0:
            fish_pos_runs = get_fish_pos_per_run(fish_instance,runs)
        else:
            print(f"No runs in {date_key}")
            continue

        day_initial_dist_robot_target_fish = []
        day_initial_dist_robot_goal = []
        for id_run, run in enumerate(runs):

            # get dist to target fish
            all_fish_pos_this_run = fish_pos_runs[id_run]       
            fish1_pos_this_run = np.array([fish[0] for fish in all_fish_pos_this_run])
            robot_pos_run = np.array(date_dict['positions'][run[0]:run[1]+1])

            initial_distance = distance(fish1_pos_this_run[0], robot_pos_run[0])
            day_initial_dist_robot_target_fish.append(initial_distance)

            # sanity check
            if len(all_fish_pos_this_run) != len(robot_pos_run):
                print(f"Wrong array lengths: fish and robot {run} {len(all_fish_pos_this_run)} {len(robot_pos_run)}")
                assert False
            # else:
            #     print("all good") 

            # get dist to goal
            inital_robot_pos_run = robot_pos_run[0]
            initial_dist_goal = get_distance_to_goal(inital_robot_pos_run)

            day_initial_dist_robot_goal.append(initial_dist_goal)

        daily_initial_dist_robot_target_fish.append(day_initial_dist_robot_target_fish)
        daily_run_lengths.append(run_lengths)
        daily_initial_dist_robot_goal.append(day_initial_dist_robot_goal)

    #fig1 = plt.figure(figsize=(15,9))

    #flatten arrays to plot
    flat_daily_run_lengths = flatten_2d_list(daily_run_lengths)
    flat_daily_initial_dist_robot_goal = flatten_2d_list(daily_initial_dist_robot_goal)
    flat_daily_initial_dist_robot_target_fish = flatten_2d_list(daily_initial_dist_robot_target_fish)


    # plot
    fig1 = plt.figure(figsize=(16,9))
    plt.scatter(flat_daily_run_lengths, flat_daily_initial_dist_robot_target_fish, label="distance to target fish", s=3)
    plt.scatter(flat_daily_run_lengths, flat_daily_initial_dist_robot_goal, label="distance to goal", s=3)

    plt.xlabel("run length in seconds")
    plt.ylabel("initial distance to target fish or goal area in px")
    plt.title(f"[{start_date}] - [{end_date}] - correlation from run length to distance to goal and target fish")
    plt.legend()
    if show:
        plt.show()

    #
    fig2 = plt.figure(figsize=(16,9))
    plt.scatter(flat_daily_run_lengths, np.abs(np.array(flat_daily_initial_dist_robot_goal)-np.array(flat_daily_initial_dist_robot_target_fish)), s=3)
    plt.title(f"[{start_date}] - [{end_date}] - correlation from run length to difference of distance to goal and distance to target")
    plt.xlabel("run length in seconds")
    plt.ylabel("difference between dist to goal and dist to target")
    if show:
        plt.show()
        
    return fig1, fig2

