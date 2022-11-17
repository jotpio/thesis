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
    layout="wide"

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
from template.page import Page



class MainPage(Page):
    def __init__(self, data_model, args):
        super().__init__(data_model)
        self.local = args.local
    
        if self.local:
            print("Using local data...")
            self.all_files = glob.glob(f".\..\loaded_data\dates_dict_*.npy")
        else:
            print("Using remote data...")
            self.all_files = get_all_remote_files()
        
        self.data_model.limit_start_date, self.data_model.limit_end_date = util.get_date_boundaries(self.all_files)
        self.initial_start_date = self.data_model.limit_start_date
        self.initial_end_date = self.data_model.limit_end_date
            
        
    
    def run_page(self, title, description):
        if self.data_model.limit_start_date is None or self.data_model.limit_end_date is None:
            st.warning("No files found!")
            return
        super().run_page(title, description)
        
        #
        # PAGE
        #
        
        #
        if self.data_model.dates_dict is not None:
            st.info(f"Currently loaded {self.data_model.min_start_date} to {self.data_model.max_end_date}")
        
        # select date window
        col1, col2 = st.columns(2)
        with col1:
            current_start_date = self.data_model.limit_start_date if self.data_model.min_start_date is None else self.data_model.min_start_date
            selected_start_date = st.date_input(
                "Start date",
                # datetime.date(2022, 2, 1))
                datetime.datetime.strptime(str(current_start_date), "%Y-%m-%d").date(),
                min_value=datetime.datetime.strptime(str(self.data_model.limit_start_date), "%Y-%m-%d").date(),
                max_value=datetime.datetime.strptime(str(self.data_model.limit_end_date), "%Y-%m-%d").date(),
                key="home_select_start_date"
                ).strftime("%Y-%m-%d")
            st.caption(f"Current start date is: {current_start_date}")

        with col2:
            current_end_date = self.data_model.limit_end_date if self.data_model.max_end_date is None else self.data_model.max_end_date
            selected_end_date = st.date_input(
                "End date",
                datetime.datetime.strptime(str(current_end_date), "%Y-%m-%d").date(),
                min_value=datetime.datetime.strptime(str(self.data_model.limit_start_date), "%Y-%m-%d").date(),
                max_value=datetime.datetime.strptime(str(self.data_model.limit_end_date), "%Y-%m-%d").date(),
                key="home_select_end_date"
                ).strftime("%Y-%m-%d")
            st.caption(f"Current end date is: {current_end_date}")

        st.markdown("""---""")   
        load_only_challenge_runs = st.checkbox("only load challenge runs", value=not self.local, help="Only loading challenge runs will immensly reduce loading times", disabled=not self.local)
        if not self.local:
            st.info("You can only load challenge data in this cloud-based streamlit application. Use a local instance to also load non-challenge data")
        st.markdown("""---""")   

        col1,col2,col3 = st.columns([1.5,1,1.5]) #center laod button
        with col2:
            load = st.button("Load data in time range")
        # load button clicked
        if load:
            self.data_model.start_date = selected_start_date
            self.data_model.end_date = selected_end_date
            self.data_model.only_challenges_loaded = load_only_challenge_runs

            # load data
            with st.spinner('Loading data... (This may take several minutes, depending on amount of data loaded)'):
                if self.local:
                    dates_dict = load_local_data(selected_start_date, selected_end_date, load_only_challenge_runs, local=self.local)
                else:
                    dates_dict = load_remote_data(selected_start_date, selected_end_date, load_only_challenge_runs, self.all_files, local=self.local)
                self.data_model.dates_dict = dates_dict
                self.data_model.min_start_date = selected_start_date
                self.data_model.max_end_date = selected_end_date 
            if self.data_model.dates_dict != None:
                st.success("Data successfully loaded!")

            # show basic metrics
            number_of_days_loaded = util.get_number_of_days(selected_start_date, selected_end_date)
            number_of_loaded_runs = util.get_number_of_runs(self.data_model.dates_dict, selected_start_date, selected_end_date)
            total_use_time = util.get_use_time(self.data_model.dates_dict, selected_start_date, selected_end_date)
            total_number_of_frames = util.get_number_of_frames(self.data_model.dates_dict, selected_start_date, selected_end_date)

            st.markdown("""---""")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("total number of days", number_of_days_loaded, delta=None)
            col2.metric("total number of runs", number_of_loaded_runs, delta=None)
            col3.metric("total use time", f"{total_use_time:.2f} hours", delta=None)
            col4.metric("total number of frames", total_number_of_frames, delta=None)

            st.markdown("""---""")

            st.session_state['data_model'] = self.data_model
        
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def load_local_data(start_date, end_date, only_challenges, local=True):
    
    # load preloaded files
    dates_dict = util.load_dates_from_npz(start_date, end_date, only_challenges, local=local)
    
    st.write("Loaded data for the first time (", start_date, ",", end_date, ")...")
    return dates_dict

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False, hash_funcs={"_thread.RLock": lambda _: None, "builtins.weakref": lambda _: None})
def load_remote_data(start_date, end_date, only_challenges, all_files, local=False):
    print("Loading data from deta drive...")
    deta = Deta(st.secrets["deta_key"])        # Initialize with a Project Key
    drive = deta.Drive("human_leadership_data_HF")
    dates_dict = util.load_dates_from_npz(start_date, end_date, only_challenges, local=local, remote_files=all_files, drive=drive)
    st.write("Loaded data for the first time (", start_date, ",", end_date, ")...")
    return dates_dict
                                                    
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False, hash_funcs={"_thread.RLock": lambda _: None, "builtins.weakref": lambda _: None})
def get_all_remote_files():
    print("Getting all remote files...")
    deta = Deta(st.secrets["deta_key"])        # Initialize with a Project Key
    drive = deta.Drive("human_leadership_data_HF")
    all_files = drive.list(limit=1000, prefix="challenges")["names"] # get all available remote files
    return all_files
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="load local data", action="store_true")
    args = parser.parse_args()
    if 'data_model' not in st.session_state:
        #initialize data model
        st.session_state["data_model"] = data_model

    page = MainPage(data_model, args)
    title = "Human leadership data Humboldt Forum"
    description =   """
                    This is the home page where you set the start and end date range of data to load.
                    """
    page.run_page(title, description)

    
