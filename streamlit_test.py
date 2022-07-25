import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
sns.set()

import datetime


from load_data import load_robot_data, load_behavior_data, load_fish_data
from util import distance, get_fish_pos_per_run, get_challenge_runs, get_successful_runs, get_distance_to_goal, save_dates_to_npz, load_dates_from_npz, get_hours_minutes_seconds_from_decimal_hours
from plot import plot_all_positions, plot_runs, circular_hist, plot_starts_ends, plot_rotations_and_heatmap, plot_inter_individual_distances, plot_run_length_hist, plot_robot_distance_goal
from plot_usage_statistics import plot_daily_number_runs, plot_time_of_day_histogram, plot_daily_use_times_and_operational_times, plot_daily_start_end_times


def main():
    page = st.sidebar.selectbox(
        "Select a Page",
        [
            "Homepage"
        ]
    )

    if page == "Homepage":
        homepage()

        
def homepage():
    #initialize
    start_date = "2022-02-01"
    end_date = "2022-02-05"
    
    st.title('Human leadership data Humboldt Forum')

    # select date window
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start date",
            # datetime.date(2022, 2, 1))
            datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date()).strftime("%Y-%m-%d")
        st.write('Current start date is:', start_date)

    with col2:
        end_date = st.date_input(
            "End date",
            datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()).strftime("%Y-%m-%d")
        st.write('Current end date is:', end_date)

    
    # load data
    dates_dict = load_data(start_date, end_date)
    
    # plots
    with st.expander("All positions"):
        st.write("""
            This scatter plot shows all robot positions for all loaded days. 
        """)
        result= st.button('Show plot')
        if result:
            # plot all positions
            fig = plot_all_positions(dates_dict, start_date=start_date, end_date=end_date, challenges=True, only_successful=True, show=False, size=(15,15))
            st.pyplot(fig)

    load_tabs(dates_dict)
    

        
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_data(start_date, end_date):
    st.write("Cache miss: load data(", start_date, ",", end_date, ") ran")
    
    # load preloaded files
    dates_dict = load_dates_from_npz(start_date, end_date)
    
    return dates_dict

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_tabs(dates_dict):
    tab1, tab2, tab3 = st.tabs(["avg rot and pos", "run length", "num visitors"])

    with tab1:
        st.header("average rotation and position heatmap")
        fig= plot_rotations_and_heatmap(dates_dict, challenges=True, only_successful=True, ignore_robot_standing=True, polar_density=True, show=False)
        st.pyplot(fig)

    with tab2:
        st.header("run length histogram")
        fig = plot_run_length_hist(dates_dict, bin_size=5, challenges=True, only_successful=False, show=False)
        st.pyplot(fig)

    with tab3:
        st.header("number of (unique) visitors for each day")
        fig = plot_daily_number_runs(dates_dict, show=False)
        st.pyplot(fig)
    
if __name__ == "__main__":
    main()
    
