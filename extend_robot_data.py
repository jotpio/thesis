import numpy as np
from datetime import datetime
from util import distance


def extend_robot_data(dates_dict, ignore_standing_pos):
    # parameters
    cutoff_run = 2 # seconds after new run is started
    min_data_run = 15 # ~5 seconds of data at 3fps


    # add derived data to instances
    dates_keys = dates_dict.keys()

    for date_key in dates_keys:    
        date_dict = dates_dict[date_key]

        instance_keys = date_dict.keys()
        for id_instance, instance_key in enumerate(instance_keys):
            instance = date_dict[instance_key]

            # add instance length
            timestamps = instance["timestamps"]
            if len(timestamps) > 1:
                first_datetime = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S,%f')
                last_datetime = datetime.strptime(timestamps[-1], '%Y-%m-%d %H:%M:%S,%f')

                difference = last_datetime - first_datetime
                instance["time_length"] = difference.seconds

                # detect time skips in time stamps and generate runs
                dt_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in timestamps]
                time_steps = np.diff(dt_timestamps)

                time_steps = [step.seconds+(step.microseconds/1000000) for step in time_steps]

                # plt.plot(time_steps)
                # plt.show()
                # print(time_steps)

                time_skip_ids = np.where(np.array(time_steps)>=cutoff_run)[0] # get all ids where time skip is larger than 2 seconds
                # print(time_skip_ids)
                runs = []
                current_run_start_id = 0
                for time_skip in time_skip_ids:
                    runs.append([current_run_start_id, time_skip])
                    current_run_start_id = time_skip+1
                runs.append([current_run_start_id,len(time_steps)-1]) #last run

                # remove too short runs
                filtered_runs = [run for run in runs if run[1]-run[0] > min_data_run]

                print(f"{date_key} instance {instance_key}: Removed {len(runs) - len(filtered_runs)} short runs from run list. ({len(runs)} - {len(filtered_runs)} = {len(runs) - len(filtered_runs)})")
                print(f"{date_key} instance {instance_key}: Found {len(filtered_runs)} runs")
                instance["runs"] = filtered_runs

                
                # ignore robot standing still
                if ignore_standing_pos:
                    old_pos = [0,0]
                    skipped = 0
                    adjusted_instance_positions = []
                    instance_positions = instance["positions"]

                    # compare each pos to previous pos and skip if basically unchanged
                    for pos in instance_positions:
                        if distance(pos, old_pos) < 0.1:
                            skipped += 1
                        else:
                            adjusted_instance_positions.append(pos)
                        old_pos = pos
                    instance["adjusted_positions"] = adjusted_instance_positions
                    print(f"Instance {instance_key}: {skipped} unchanged positions skipped! ({(skipped/len(instance_positions))*100}% of all positions)")

                # calculate velocities, speeds
                for id_run, run in enumerate(filtered_runs):                
                    timestamps_run = dt_timestamps[run[0]:run[1]]
                    timedeltas_run = [delta.total_seconds() for delta in np.diff(timestamps_run)]

                    posxdeltas_run = np.diff(np.array(instance["positions"])[run[0]:run[1],0])
                    posydeltas_run = np.diff(np.array(instance["positions"])[run[0]:run[1],1])

                    velocity_x_run = posxdeltas_run / timedeltas_run
                    velocity_y_run = posydeltas_run / timedeltas_run

                    velocity_vectors_run = list(zip(velocity_x_run, velocity_y_run))
                    speed_run = np.linalg.norm(velocity_vectors_run, axis=1) # magnitude of velocity vector is speed

                    acceleration_run = np.diff(speed_run)

                    # add results to dict
                    velocities = instance.get("velocities",[])
                    velocities.append(velocity_vectors_run)
                    instance["velocities"] = velocities

                    speeds = instance.get("speeds",[])
                    speeds.append(speed_run)
                    instance["speeds"] = speeds

                    accelerations = instance.get("accelerations",[])
                    accelerations.append(acceleration_run)
                    instance["accelerations"] = accelerations
                    
                


    print("Done")
    
    return dates_dict