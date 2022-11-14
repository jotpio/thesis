import sys, os, argparse
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
if parent not in sys.path:
    sys.path.insert(0, parent)
    print("Adding parent to sys path")

import streamlit as st
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
sns.set()

from deta import Deta  # Import Deta

import datetime

import data_model
import load_data
import util
import plot
import plot_usage_statistics 


def main(args):
    local = args.local
    
    if local:
        print("Using local data...")
    else:
        print("Using remote data...")
    
    #initialize
    start_date = "2021-11-19"
    end_date = "2022-10-25"
    
    st.title('Human leadership data Humboldt Forum')
    st.subheader('Set date range to load...')


    # select date window
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            # datetime.date(2022, 2, 1))
            datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date(),
            min_value=datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date(),
            max_value=datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()
            ).strftime("%Y-%m-%d")
        data_model.start_date = start_date
        st.caption(f"Current start date is: {start_date}")

    with col2:
        end_date = st.date_input(
            "End date",
            datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date(),
            min_value=datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date(),
            max_value=datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()
            ).strftime("%Y-%m-%d")
        data_model.end_date = end_date
        st.caption(f"Current end date is: {end_date}")
        
    st.markdown("""---""")   
    load_only_challenge_runs = st.checkbox("only load challenge runs", value=True, help="Only loading challenge runs will immensly reduce loading times")
    data_model.only_challenges_loaded = load_only_challenge_runs
    st.markdown("""---""")   
    
    col1,col2,col3 = st.columns(3)
    with col2:
        load = st.button("Load data in time range")
    if load:
        # load data
        with st.spinner('Loading data... (This may take several minutes, depending on amount of data loaded)'):
            if local:
                dates_dict = load_local_data(start_date, end_date, load_only_challenge_runs, local=True)
            else:
                dates_dict = load_remote_data(start_date, end_date, load_only_challenge_runs)
            data_model.dates_dict = dates_dict
            data_model.min_start_date = start_date
            data_model.max_end_date = end_date 
        if data_model.dates_dict != None:
            st.success("Data successfully loaded!")

        # show basic metrics
        number_of_days_loaded = util.get_number_of_days(start_date, end_date)
        number_of_loaded_runs = util.get_number_of_runs(data_model.dates_dict, start_date, end_date)
        total_use_time = util.get_use_time(data_model.dates_dict, start_date, end_date)
        total_number_of_frames = util.get_number_of_frames(data_model.dates_dict, start_date, end_date)

        st.markdown("""---""")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("total number of days", number_of_days_loaded, delta=None)
        col2.metric("total number of runs", number_of_loaded_runs, delta=None)
        col3.metric("total use time", f"{total_use_time:.2f} hours", delta=None)
        col4.metric("total number of frames", total_number_of_frames, delta=None)

        st.markdown("""---""")
        
        
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def load_local_data(start_date, end_date, only_challenges, local=False):
    
    # load preloaded files
    dates_dict = util.load_dates_from_npz(start_date, end_date, only_challenges, local=local)
    
    st.write("Loaded data for the first time (", start_date, ",", end_date, ")...")
    return dates_dict

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False, hash_funcs={"_thread.RLock": lambda _: None, "builtins.weakref": lambda _: None})
def load_remote_data(start_date, end_date, only_challenges):
    print("Loading data from deta drive...")
    
    deta = Deta(st.secrets["deta_key"])        # Initialize with a Project Key
    drive = deta.Drive("human_leadership_data_HF")

    all_files = drive.list(limit=1000, prefix="challenges")["names"] #https://docs.deta.sh/docs/drive/sdk#list
    print(all_files[0:100])
    return all_files
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="load local data", action="store_true")
    args = parser.parse_args()
    main(args)
    
