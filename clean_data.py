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
        assert len(runs) == len(all_difficulties) == len(all_challenge_runs), f"{len(runs),len(all_difficulties),len(all_challenge_runs)}"
        fish_pos_runs = get_fish_pos_per_run(all_fish, runs)
        
        for id_run, run in enumerate(runs):
            # skip non challenge runs
            if not all_challenge_runs[id_run]:
                continue

                
            run_fish = all_fish[run[0]:run[1]+1]
            fish_pos_this_run = fish_pos_runs[id_run]
            run_difficulty = all_difficulties[id_run]
            
            # cut off start
            # check if number of fish stays the same during run and cut off starts of runs, which change number of fish in the beginning
            run, previous_cutoff = start_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=debug)
            run_fish = run_fish[previous_cutoff:]
            fish_pos_this_run = fish_pos_this_run[previous_cutoff:]
            
            # check if fish in starting position at start of run and cut off start if not
            assert len(fish_pos_this_run) == len(run_fish), f"{len(fish_pos_this_run)}\n{len(fish_pos_this_run)}"
            run, previous_cutoff = start_check_if_target_in_fixed_starting_pos(fish_pos_this_run, run, max_dist_to_starting_pos, debug=debug)
            run_fish = run_fish[previous_cutoff:]
            fish_pos_this_run = fish_pos_this_run[previous_cutoff:]
            
            # cut off end
            run, end_cutoff = end_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=debug)
            
            
        # remove short runs
        new_runs = []
        new_all_difficulties = []
        new_all_challenge_runs = []
        for id_run, run in enumerate(runs):
            if run[1]-run[0] > 3:
                new_runs.append(run)
                new_all_difficulties.append(all_difficulties[id_run])
                new_all_challenge_runs.append(all_challenge_runs[id_run])
            else:
                print(f"Removed short run: {run}")
        date_dict["runs"] = new_runs
        date_dict["difficulties"] = new_all_difficulties
        date_dict["challenges"] = new_all_challenge_runs
        
        print(f"Removed {len(runs)-len(new_runs)} short runs") 
            
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
                    print(f"\tLater jump in number of fish found which is not in first consecutive time steps({current_cut_off} and {id_ts}) : {run}, number of fish:  {run_difficulty+1} expected, got  {len(fish_in_ts)}")
                    break
            # print(f"{run_difficulty} and {len(fish_in_ts)-1} different in timestep {id_ts}")
            
    # cut off start of run
    if current_cut_off != -1:
        # check if run long enough to be cut off
        if (run[1] - run[0]) > current_cut_off:
            if debug:
                print(f"\tCutting off {current_cut_off+1} from beginning of {run} because number of fish not consistent with difficulty")
            run[0] = run[0] + current_cut_off + 1
        else:
            if debug:
                print(f"\tRun too short to be cut off... Removing instead: (run-{run}; cut-off:{current_cut_off}; run length:{run[1] - run[0]}) - START const num fish")
            run[1] = run[0] # set run to length 1 to later be removed
                
    # print(f"inside diff {run}")
    return run, current_cut_off+1

def start_check_if_target_in_fixed_starting_pos(fish_pos_this_run, run, max_dist_to_starting_pos, debug=False):
    starting_pos=[1500,500]
    current_cut_off = -1
    # print(f"inside positions {run}")
    
    if len(fish_pos_this_run) > 0:
        assert len(fish_pos_this_run) == (run[1] - run[0]+1), f"Wrong fish positions? len fish: {len(fish_pos_this_run)}; len run: {run[1] - run[0]+1}; run: {run}"

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
                    print(f"\tCutting off {current_cut_off+1} from beginning of {run} because fish is not in starting position")
                run[0] = run[0] + current_cut_off+1
            else:
                if debug:
                    print(f"\tRun to short to be cut off... Removing instead: (run-{run}; cut-off:{current_cut_off}; run length:{run[1] - run[0]}) - START target pos")
                    run[1] = run[0]
        
    return run, current_cut_off+1

def end_check_if_num_fish_constant_for_run(run_fish, run_difficulty, run, debug=False):                                                                              
    # compare num of fish in ts to expected number of fish (difficulty+1)
    cut_off = -1
    
    if len(run_fish) > 0:
    
        assert len(run_fish) == (run[1] - run[0]+1), f"bad run_fish?: len run fish-{len(run_fish)}, len run-{run[1] - run[0]+1}"

        for id_ts, fish_in_ts in enumerate(run_fish):
            if run_difficulty != len(fish_in_ts)-1:
                if debug:
                    print(f"\tEND: {run_difficulty} and {len(fish_in_ts)-1} different in timestep {id_ts}")
                cut_off=id_ts
                break #stop when found

        # cut off end of run
        if cut_off != -1:
            # check if run long enough to be cut off
            if (run[1] - run[0]) > cut_off:
                if debug:
                    print(f"\tCutting off at index {cut_off+1} from end of {run} because number of fish not consistent with difficulty")
                run[1] = run[0] + cut_off-1
            else:
                if debug:
                    print(f"\tRun to short to be cut off... Removing instead: run-{run}, cut_off:{cut_off}, run length:{run[1] - run[0]} - END const num fish")
                    run[1] = run[0]
        # print(f"inside diff {run}")
    return run, cut_off
