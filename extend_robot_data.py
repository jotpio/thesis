import numpy as np
from datetime import datetime
from util import distance


def extend_robot_data(dates_dict, ignore_standing_pos):
    # parameters
    cutoff_run = 2 # seconds after new run is started
    min_data_run = 15 # ~5 seconds of data at 3fps


    # add derived data to dates
    dates_keys = dates_dict.keys()

    for date_key in dates_keys:    
        date_dict = dates_dict[date_key]
        
        timestamps = date_dict["timestamps"]
        if len(timestamps) > 1:
            # add day length
            first_datetime = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S,%f')
            last_datetime = datetime.strptime(timestamps[-1], '%Y-%m-%d %H:%M:%S,%f')

            difference = last_datetime - first_datetime
            date_dict["day_length"] = difference.seconds

            # detect time skips in time stamps and generate runs
            dt_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in timestamps]
            time_steps = np.diff(dt_timestamps)

            time_steps = [step.seconds+(step.microseconds/1000000) for step in time_steps]
            time_skip_ids = np.where(np.array(time_steps)>=cutoff_run)[0] # get all ids where time skip is larger than 2 seconds
            
            runs = []
            current_run_start_id = 0
            for time_skip in time_skip_ids:
                runs.append([current_run_start_id, time_skip])
                current_run_start_id = time_skip+1
            runs.append([current_run_start_id,len(time_steps)-1]) #last run

            # # remove too short runs
            # filtered_runs = [run for run in runs if run[1]-run[0] > min_data_run]

            # print(f"{date_key}: Removed {len(runs) - len(filtered_runs)} short runs from run list. ({len(runs)} - {len(filtered_runs)} = {len(runs) - len(filtered_runs)})")
            print(f"{date_key}: Found {len(runs)} runs")
            
            date_dict["runs_timeskip"] = runs
            # date_dict["challenges"] = np.zeros(len(runs), dtype=bool) # init challenges for future addition 


            # ignore robot standing still
            if ignore_standing_pos:
                old_pos = [0,0]
                skipped = 0
                adjusted_positions = []
                positions = date_dict["positions"]

                # compare each pos to previous pos and skip if basically unchanged
                for pos in positions:
                    if distance(pos, old_pos) < 0.1:
                        skipped += 1
                    else:
                        adjusted_positions.append(pos)
                    old_pos = pos
                date_dict["adjusted_positions"] = adjusted_positions
                print(f"{date_key}: {skipped} unchanged positions skipped! ({(skipped/len(positions))*100:.2f}% of all positions)")

            # calculate velocities, speeds
            runs = date_dict["runs"]
            for id_run, run in enumerate(runs):
                if run is None or len(run) != 2:
                    continue
                timestamps_run = dt_timestamps[run[0]:run[1]]
                timedeltas_run = [delta.total_seconds() for delta in np.diff(timestamps_run)]

                posxdeltas_run = np.diff(np.array(date_dict["positions"])[run[0]:run[1],0])
                posydeltas_run = np.diff(np.array(date_dict["positions"])[run[0]:run[1],1])

                velocity_x_run = posxdeltas_run / timedeltas_run
                velocity_y_run = posydeltas_run / timedeltas_run

                velocity_vectors_run = list(zip(velocity_x_run, velocity_y_run))
                speed_run = np.linalg.norm(velocity_vectors_run, axis=1) # magnitude of velocity vector is speed

                acceleration_run = np.diff(speed_run)

                # add results to dict
                velocities = date_dict.get("velocities",[])
                velocities.append(velocity_vectors_run)
                date_dict["velocities"] = velocities

                speeds = date_dict.get("speeds",[])
                speeds.append(speed_run)
                date_dict["speeds"] = speeds

                accelerations = date_dict.get("accelerations",[])
                accelerations.append(acceleration_run)
                date_dict["accelerations"] = accelerations




    print("Done")
    
    return dates_dict