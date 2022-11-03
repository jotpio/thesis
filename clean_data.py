from util import get_fish_pos_per_run, distance

# cleans all challenge runs
def clean_data(dates_dict, debug=False):
    max_dist_to_starting_pos = 40
    
    dates_keys = dates_dict.keys()
    # iterate over every run run
    for date_key in dates_keys:
        print(f"Cleaning {date_key}...")
        date_dict = dates_dict[date_key]
        
        runs = date_dict["runs"]
        all_fish = date_dict["fish"]
        all_difficulties = date_dict["difficulties"]
        all_challenge_runs = date_dict["challenges"]
        fish_pos_runs = get_fish_pos_per_run(all_fish, runs)

        
        for id_run, run in enumerate(runs):
            # skip non challenge runs
            if not all_challenge_runs[id_run]:
                continue

            # cut off start
            # check if number of fish stays the same during run and cut off starts of runs, which change number of fish in the beginning
            run_fish = all_fish[run[0]:run[1]]
            run_difficulty = all_difficulties[id_run]
            
            run, previous_cutoff = start_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=debug)
            # check if fish in starting position at start of run and cut off start if not
            fish_pos_this_run = fish_pos_runs[id_run][previous_cutoff:]
            run_fish = run_fish[previous_cutoff:]
            run, previous_cutoff = start_check_if_target_in_fixed_starting_pos(fish_pos_this_run, run, max_dist_to_starting_pos, debug=debug)
            
            # cut off end
            run_fish = run_fish[previous_cutoff:]
            run, end_cutoff = end_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=debug)
            
    return dates_dict

                
def start_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=False):
    # compare num of fish in ts to expected number of fish (difficulty+1)
    current_cut_off = -1
    for id_ts, fish_in_ts in enumerate(run_fish):
        if run_difficulty != len(fish_in_ts)-1:
            if id_ts == current_cut_off+1:
                current_cut_off = id_ts
            else:
                if debug:
                    print(f"Jump in number of fish not in first consecutive time steps({current_cut_off} and {id_ts}) : {run} (aborting start cut off for this run), number of fish:  {run_difficulty}expected, got  {len(fish_in_ts)}")
                return run, 0
            # print(f"{run_difficulty} and {len(fish_in_ts)-1} different in timestep {id_ts}")
            
    # cut off start of run
    if current_cut_off != -1:
        # check if run long enough to be cut off
        if (run[1] - run[0]) > current_cut_off:
            if debug:
                print(f"Cutting off {current_cut_off+1} from beginning of {run} because number of fish not consistent with difficulty")
            run[0] = run[0] + current_cut_off+1
        else:
            if debug:
                print(f"Run to short to be cut off: {current_cut_off}")
    # print(f"inside diff {run}")
    return run, current_cut_off+1

def start_check_if_target_in_fixed_starting_pos(fish_pos_this_run, run, max_dist_to_starting_pos, debug=False):
    starting_pos=[1500,500]
    current_cut_off = -1
    # print(f"inside positions {run}")
    assert len(fish_pos_this_run) == (run[1] - run[0]), f"Wrong fish positions? len fish: {len(fish_pos_this_run)}; len run: {run[1] - run[0]}"
    
    # check if initial pos approximately close to expected starting pos
    for all_fishpos_ts in fish_pos_this_run:
        target_fish_pos = all_fishpos_ts[0]
        # print(target_fish_pos)
        dist = distance(target_fish_pos, starting_pos)
        if dist > max_dist_to_starting_pos:
            current_cut_off += 1
        else: 
            break
    # cut off start of run
    if current_cut_off != -1:
        # check if run long enough to be cut off
        if (run[1] - run[0]) > current_cut_off:
            if debug:
                print(f"Cutting off {current_cut_off+1} from beginning of {run} because fish is not in starting position")
            run[0] = run[0] + current_cut_off+1
        else:
            if debug:
                print(f"Run to short to be cut off: {current_cut_off+1}")
        
    return run, current_cut_off+1

def end_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=False):
    assert len(run_fish) == (run[1] - run[0]), "bad run_fish?"
                                                                              
    # compare num of fish in ts to expected number of fish (difficulty+1)
    cut_off = -1
    for id_ts, fish_in_ts in enumerate(run_fish):
        if run_difficulty != len(fish_in_ts)-1:
            if debug:
                print(f"{run_difficulty} and {len(fish_in_ts)-1} different in timestep {id_ts}")
            cut_off=id_ts
            break #stop when found
            
    # cut off start of run
    if cut_off != -1:
        # check if run long enough to be cut off
        if (run[1] - run[0]) > cut_off:
            if debug:
                print(f"Cutting off at index {cut_off+1} from end of {run} because number of fish not consistent with difficulty")
            run[1] = run[0] + cut_off-1 #TODO maybe check if -1 correct?
        else:
            if debug:
                print(f"Run to short to be cut off: run-{run}, cut_off:{cut_off}")
    # print(f"inside diff {run}")
    return run, cut_off