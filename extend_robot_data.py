import numpy as np
from datetime import datetime
from util import distance
from util import get_successful_runs, get_challenge_runs


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

#             # detect time skips in timestamps and generate runs
            dt_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in timestamps]
#             time_steps = np.diff(dt_timestamps)

#             time_steps = [step.seconds+(step.microseconds/1000000) for step in time_steps]
#             time_skip_ids = np.where(np.array(time_steps)>=cutoff_run)[0] # get all ids where time skip is larger than 2 seconds
            
#             runs = []
#             current_run_start_id = 0
#             for time_skip in time_skip_ids:
#                 runs.append([current_run_start_id, time_skip])
#                 current_run_start_id = time_skip+1
#             runs.append([current_run_start_id,len(time_steps)-1]) #last run

#             # # remove too short runs
#             # filtered_runs = [run for run in runs if run[1]-run[0] > min_data_run]

#             # print(f"{date_key}: Removed {len(runs) - len(filtered_runs)} short runs from run list. ({len(runs)} - {len(filtered_runs)} = {len(runs) - len(filtered_runs)})")
#             print(f"{date_key}: Found {len(runs)} runs")
            
#             date_dict["runs_timeskip"] = runs


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

            # calculate velocities, speeds. run_length
            runs = date_dict["runs"]
            date_run_lengths = []
            for id_run, run in enumerate(runs):
                if run is None or len(run) != 2:
                    continue
                    
                # run length
                start_time = datetime.strptime(timestamps[run[0]], '%Y-%m-%d %H:%M:%S,%f')
                end_time = datetime.strptime(timestamps[run[1]], '%Y-%m-%d %H:%M:%S,%f')
                run_length = np.abs((end_time - start_time).total_seconds())
                date_run_lengths.append(run_length)
                
                # timestamp deltas for velocity and speed
                timestamps_run = dt_timestamps[run[0]:run[1]]
                timedeltas_run = [delta.total_seconds() for delta in np.diff(timestamps_run)]

                posxdeltas_run = np.diff(np.array(date_dict["positions"])[run[0]:run[1],0])
                posydeltas_run = np.diff(np.array(date_dict["positions"])[run[0]:run[1],1])

                velocity_x_run = posxdeltas_run / timedeltas_run
                velocity_y_run = posydeltas_run / timedeltas_run

                velocity_vectors_run = list(zip(velocity_x_run, velocity_y_run))
                speed_run = np.linalg.norm(velocity_vectors_run, axis=1) # magnitude of velocity vector is speed

                acceleration_run = np.diff(speed_run)
                
                # add successful runs
                

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
                
                
                
            # add runl lengths to date_dict
            date_dict["run_lengths"] = date_run_lengths
            # print(date_dict["run_lengths"])
            assert len(date_dict["run_lengths"]) == len(date_dict["runs"])
            if len(date_run_lengths) > 0:
                mean_length = np.mean(date_run_lengths)
                median_length = np.median(date_run_lengths)
                print(f"{date_key}: Mean run length: {mean_length:.2f}; median run length: {median_length:.2f}")

    dates_dict = get_successful_runs(dates_dict)

    print("Done")
    
    return dates_dict

def get_successful_runs(dates_dict):
    ### get successful runs
    for date_key in dates_dict.keys():
        date_dict = dates_dict[date_key]
        date_dict_runs = date_dict["runs"]
        date_dict_ch = date_dict["challenges"]
        date_dict_ts = date_dict["timestamps"]
        date_dict_pos = date_dict["positions"]
        date_dict_fish = date_dict["fish"]

        ch_runs, ch_run_ids = get_challenge_runs(date_dict_runs, date_dict_ch)
        # print(run_ids)
        successful_ch = [False for i in range(len(date_dict_runs))]
        for id_run, run in enumerate(ch_runs):

            # check for last N timesteps of run if robot in right pos and fish following
            for i in range(run[1] - run[0]-1):
                run_end_pos = date_dict_pos[run[1]-i]

                # end pos must be in target area (x<750; y>1250)
                if run_end_pos[0] < 750 and run_end_pos[1] > 1250:
                    # get target fish at last few timestamps of run and check if it is following

                    ts_fish = date_dict_fish[run[1]-i]
                    for fish in ts_fish:
                        if fish["id"] == 1:
                            if fish["following"]:
                                successful_ch[ch_run_ids[id_run]] = True
                                break
                            else:
                                pass
                                # print("Not following")

            # else:
            #     # print("Not in pos")

        date_dict["successful"] = successful_ch
        if len(successful_ch)>0:
            successful_challenge_runs = np.array(date_dict_runs)[successful_ch]
            print(f"{date_key}: Number of challenge runs:{len(ch_runs)}, successful:{len(successful_challenge_runs)} | {len(successful_challenge_runs) /len(ch_runs) * 100:.2f}% successful runs")
            
    return dates_dict