import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

from util import get_challenge_runs, distance, get_fish_pos_per_run


def plot_all_positions(dates_dict, start_date=None, end_date=None, ax=None):
    # plot all positions
    all_positions = []
    dates_keys = dates_dict.keys()
    for date_key in dates_keys:
        date_dict = dates_dict[date_key]
        # print(date_key)
        if start_date is not None:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date is not None:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        date = datetime.strptime(date_key, '%Y-%m-%d')

        if start_date is not None and start_date > date:
            continue
        if end_date is not None and end_date < date:
            continue
        
        
        
        date_positions = date_dict.get("positions",[])
        if date_positions is not None:
            all_positions.extend(date_positions)

    # plot if positions available
    if len(all_positions) != 0:
        x = np.array(all_positions)[:,0]
        y = np.array(all_positions)[:,1]
        
        if ax is None:
            fig=plt.figure(num="all positions", figsize=(16,16))
            ax = fig.add_subplot(111)
        
        ax.set_xlim(2000)
        ax.set_ylim(2000)
        ax.invert_xaxis()
        ax.invert_yaxis()
        # plt.gca().invert_yaxis()
        ax.scatter(x,y,s=2)
        # plt.plot(x, y)
        ax.set_title(f"all positions: {date_key[0]} - {date_key[-1]}")
        plt.show()
                
                
def plot_runs(dates_dict, start_date=None, end_date=None, challenges=True):              
    dates_keys = dates_dict.keys()

    for date_key in dates_keys:
        date_dict = dates_dict[date_key]

        if start_date is not None:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date is not None:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        date = datetime.strptime(date_key, '%Y-%m-%d')

        if start_date is not None and start_date > date:
            continue
        if end_date is not None and end_date < date:
            continue

        # plot if positions available
        if len(date_dict["positions"]) != 0:

            # traverse runs and plot each one separately
            if challenges:
                runs, _ = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
            else:
                runs = date_dict["runs"]
            
            for id_run, run in enumerate(runs):
                plt.figure(num=date_key, figsize=(16,9))

                # positions
                ax1 = plt.subplot(321)
                x = np.array(date_dict["positions"])[run[0]:run[1],0]
                y = np.array(date_dict["positions"])[run[0]:run[1],1]

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
                run_speeds = date_dict["speeds"][id_run]
                ax2.plot(run_speeds)
                ax2.set_title(f"speeds {date_key}_{id_run}")

                # acceleration
                ax3 = plt.subplot(323)
                run_accelerations = date_dict["accelerations"][id_run]
                ax3.plot(run_accelerations)
                ax3.set_title(f"accelerations {date_key}_{id_run}")

                # rotations
                ax4 = plt.subplot(324, projection='polar')
                run_rotations = np.radians(date_dict["rotation"][run[0]:run[1]])                
                circular_hist(ax4, run_rotations, bins=16, density=True, offset=0, gaps=True)
                ax4.set_title(f"rotations {date_key}_{id_run}")

                #
                plt.tight_layout()
                plt.show()
                
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
        fig=plt.figure(num="position heatmap", figsize=(16,16))
        ax = fig.add_subplot(111)
    x = np.array(pos)[:,0]
    y = np.array(pos)[:,1]

    # sns.jointplot(x=x, y=y, kind="hex", color="#4CB391")
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.invert_yaxis()
    ax.hexbin(x,y, gridsize=80, bins='log', cmap='inferno') # use log bins to ignore positions where robot stands still
    
    plt.show()
    
def plot_starts_ends(dates_dict, challenges=True):
    # all start and end positions challenge runs
    dates_keys = dates_dict.keys()

    all_starts = []
    all_ends = []

    for date_key in dates_keys:
        date_dict = dates_dict[date_key]

        # plot if positions available
        if len(date_dict["positions"]) != 0:
            challenge_runs, _ = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
            # print(challenge_runs)
            # traverse runs and collect start and end points
            for id_run, run in enumerate(challenge_runs):
                start = np.array(date_dict["positions"])[run[0]:run[1]][0]
                end = np.array(date_dict["positions"])[run[0]:run[1]][-1]

                all_starts.append(start)
                all_ends.append(end)

        assert len(all_starts) == len(all_ends)

        if len(all_starts) > 0:
            plt.figure(num=date_key, figsize=(15,15))
            plt.scatter(np.array(all_starts)[:,0], np.array(all_starts)[:,1], marker="o", s=5, color='green', label="Start positions")
            plt.scatter(np.array(all_ends)[:,0], np.array(all_ends)[:,1], marker="X", s=3, color='red', label="End positions")

            plt.title(f"{date_key} - all start and end positions of challenge runs")
            plt.xlim(0,2000)
            plt.ylim(0,2000)
            plt.xlabel("x-coordinate (px)")
            plt.ylabel("y-coordinate (px)")
            plt.legend()
            plt.show()
            
def plot_rotations_and_heatmap(dates_dict, challenges=True, ignore_robot_standing=True, polar_density=True):

    dates_keys = dates_dict.keys()

    all_rotations = []
    all_positions = []

    for date_key in dates_keys:    
        date_dict = dates_dict[date_key]
        date_rotations = date_dict["rotation"]
        date_positions = date_dict["positions"]
        # combine positions and rotations
        if challenges:
            challenge_runs, ids = get_challenge_runs(date_dict["runs"], date_dict["challenges"])
            
            for id_cr, run in enumerate(challenge_runs):
                # append challenge rotations
                # id_ = ids[id_cr]
                all_rotations.extend(date_rotations[run[0]:run[1]])
                
                # append challenge positions
                all_positions.extend(date_positions[run[0]:run[1]])
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
    ax1 = plt.subplot(121, projection='polar')
    circular_hist(ax1, np.radians(all_rotations),bins=16, density=polar_density, offset=0, gaps=True)


    # plot overall heatmap
    ax2 = plt.subplot(122)
    x = np.array(all_positions)[:,0]
    y = np.array(all_positions)[:,1]

    # sns.jointplot(x=x, y=y, kind="hex", color="#4CB391")
    plt.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    # plt.gca().invert_yaxis()
    plt.hexbin(x,y, gridsize=80, bins='log', cmap='inferno') # use log bins to ignore positions where robot stands still

    plt.show()
    
def plot_inter_individual_distances(dates_dict_robot_fish, challenges=True, bins=20):
    dates_keys = dates_dict_robot_fish.keys()

    for date_key in dates_keys:

        all_mean_iid_per_bin = []
        date_dict = dates_dict_robot_fish[date_key]

        fish_instance = date_dict["fish"]
        runs = date_dict["runs"]
        if challenges:
            runs, _ = get_challenge_runs(runs,date_dict["challenges"])
        else:
            runs = date_dict["runs"]

        if len(runs) > 0:
            fish_pos_runs = get_fish_pos_per_run(fish_instance,runs)
        else:
            continue

        for id_run, run in enumerate(runs):
            fish_pos_this_run = fish_pos_runs[id_run]
            robot_pos_run = np.array(date_dict['positions'][run[0]:run[1]])
            # sanity check
            if len(fish_pos_this_run) != len(robot_pos_run):
                print("Wrong array lengths: fish and robot")
                assert False
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
        plt.figure(num=f"{date_key} - inter-individual distances between robot and target fish (id 1)", figsize=(15,5))        
        plt.title(f"{date_key} - inter-individual distances between robot and target fish (id 1)")
        plt.ylim(0,3000)
        plt.ylabel("distance in px")
        plt.xlabel("frame")
        plt.show()


        # bar plot all mean idds per bin
        plt.figure(num=f"{date_key} - frame-scliced inter-individual distances between robot and target fish (id 1)", figsize=(15,5))
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
        plt.show()