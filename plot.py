import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np


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
        
        
        instance_keys = date_dict.keys()
        for id_instance, instance_key in enumerate(instance_keys):
            instance = date_dict[instance_key]
            instance_positions = instance.get("positions",[])
            if instance_positions is not None:
                all_positions.extend(instance_positions)
            # print(instance)

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
        # plt.gca().invert_yaxis()
        ax.scatter(x,y,s=2)
        # plt.plot(x, y)
        ax.set_title(f"all positions: {date_key[0]} - {date_key[-1]}")
        plt.show()
                
                
def plot_runs(dates_dict, start_date=None, end_date=None):              
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

        instance_keys = date_dict.keys()
        for id_instance, instance_key in enumerate(instance_keys):
            instance = date_dict[instance_key]
            # print(instance)

            # plot if positions available
            if len(instance["positions"]) != 0:

                # traverse runs and plot each one separately
                for id_run, run in enumerate(instance["runs"]):
                    plt.figure(num=instance_key, figsize=(16,9))

                    # positions
                    ax1 = plt.subplot(321)
                    x = np.array(instance["positions"])[run[0]:run[1],0]
                    y = np.array(instance["positions"])[run[0]:run[1],1]

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

                    ax1.set_title(f"positions {date_key} - {instance_key}_{id_run}")
                    # plt.show()

                    # speeds
                    ax2 = plt.subplot(322)
                    run_speeds = instance["speeds"][id_run]
                    ax2.plot(run_speeds)
                    ax2.set_title(f"speeds {date_key} - {instance_key}_{id_run}")

                    # acceleration
                    ax3 = plt.subplot(323)
                    run_accelerations = instance["accelerations"][id_run]
                    ax3.plot(run_accelerations)
                    ax3.set_title(f"accelerations {date_key} - {instance_key}_{id_run}")

                    # rotations
                    ax4 = plt.subplot(324, projection='polar')
                    run_rotations = np.radians(instance["rotation"][run[0]:run[1]])                
                    circular_hist(ax4, run_rotations, bins=16, density=True, offset=0, gaps=True)
                    ax4.set_title(f"rotations {date_key} - {instance_key}_{id_run}")

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