import streamlit as st
import sys, os, time
import numpy as np
import pandas as pd
from datetime import datetime
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import matplotlib.pyplot as plt

import data_model
import util
import plot
import ui_helper
from template.page import Page

class RunDataPage(Page):
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        #PAGE
        #

        # select date
        col1, col2 = st.columns(2)
        with col1:
            date_selection = st.selectbox(
                label='Select the date you wish to visualize a run from',
                options=self.data_model.dates_dict.keys(),
                index=0)

        with col2:
            if self.data_model.only_successful:
                descriptor_runs = f"successful challenge runs on selected date {date_selection}"
            elif self.data_model.challenges:
                descriptor_runs = f"challenge runs on selected date {date_selection}"
            else:
                descriptor_runs = f"runs on selected date {date_selection}"
            number_of_runs = get_number_of_runs(self.data_model.only_successful, self.data_model.challenges, date_selection, date_selection)

            st.metric(descriptor_runs, number_of_runs)    

        # select run
        date_runs = self.data_model.dates_dict[date_selection]['runs']
        date_successful = self.data_model.dates_dict[date_selection]['successful']
        date_challenges = self.data_model.dates_dict[date_selection]['challenges']
        if self.data_model.only_successful:
            date_runs, _ = util.get_successful_runs(date_runs, date_successful)
        elif self.data_model.challenges:
            date_runs, _ = util.get_challenge_runs(date_runs, date_challenges)
        
        run_selection = st.selectbox(
            label='Select the run you wish to visualize',
            options=range(len(date_runs)),
            format_func=lambda x: f"{date_runs[x]}, length:{date_runs[x][1]-date_runs[x][0]+1}",
            index=0)
        st.markdown("""---""")

        # run selector
        #st.write(f"Please select the run or a range of runs you wish to generate plots for")    
        #date_run_tuples = get_date_run_tuples(only_successful, challenges)
        #start_run, end_run = st.select_slider('Select the range of runs',
                        #options=date_run_tuples,
                        #value=(date_run_tuples[10], date_run_tuples[13]),
                        #format_func=format_date_run_tuples)
        #st.markdown("""---""")
        
        # show plots
        st.subheader(f"Run {date_selection} - {date_runs[run_selection]}")
        #plot_selected_runs(date_run_tuples, start_run, end_run)
        fig = plot.plot_run(self.data_model.dates_dict[date_selection], id_run=run_selection, date_key=date_selection, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, show=False)
        st.pyplot(fig, clear_figure=True)
        st.markdown("""---""")

        # show data
        df_run = create_run_dataframe(self.data_model.dates_dict[date_selection], id_run=run_selection, only_successful=self.data_model.only_successful, challenges=self.data_model.challenges) # create dataframe
        run_type = get_run_type(self.data_model.dates_dict[date_selection], id_run=run_selection)
        run_time = np.abs((df_run["timestamps"].iloc[0] - df_run["timestamps"].iloc[-1]).total_seconds())

        col1,col2 = st.columns([2,1])
        col1.metric("type", run_type)
        col2.metric("time in seconds", run_time)
        st.markdown("""---""")
        st.dataframe(data=df_run, use_container_width=False)

    
    

@st.experimental_memo(suppress_st_warning=True)
def get_number_of_runs(only_successful, challenges, start_date, end_date):
    return util.get_number_of_runs(data_model.dates_dict, start_date, end_date, successful=only_successful, challenges=challenges)

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_date_run_tuples(only_successful, challenges):
    return util.get_date_run_tuples(data_model.dates_dict, only_successful, challenges)

def plot_selected_runs(date_run_tuples, start_date_run_tuple, end_date_run_tuple):
    # st.write(start_date_run_tuple)
    # st.write(end_date_run_tuple)
    id_start_tuple = date_run_tuples.index(start_date_run_tuple, 0)
    id_end_tuple = date_run_tuples.index(end_date_run_tuple, id_start_tuple)
    # st.write(id_start_tuple)
    # st.write(id_end_tuple)
    selected_date_run_tuples = date_run_tuples[id_start_tuple:id_end_tuple+1]
    # st.write(selected_date_run_tuples)
    for date_run_tuple in selected_date_run_tuples:
        st.write(format_date_run_tuples(date_run_tuple))
        fig = plot.plot_run(data_model.dates_dict[date_run_tuple[0]], id_run=date_run_tuple[1], date_key=date_run_tuple[0], show=False)
        st.pyplot(fig, clear_figure=True)
        st.markdown("""---""")
    
def format_date_run_tuples(date_run_tuple):
    return f"{date_run_tuple[0]} - run {date_run_tuple[1]}"

def create_run_dataframe(date_dict, id_run, only_successful, challenges):
    date_runs = date_dict['runs']
    date_successful = date_dict['successful']
    date_challenges = date_dict['challenges']
    if only_successful:
        date_runs, _ = util.get_successful_runs(date_runs, date_successful)
    elif challenges:
        date_runs, _ = util.get_challenge_runs(date_runs, date_challenges)
    
    run = date_runs[id_run]
    run_timestamps = date_dict["timestamps"][run[0]:run[1]+1]
    dt_run_timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f') for timestamp in run_timestamps]
    #print(list(date_dict.keys()))
    run_positions = date_dict["positions"][run[0]:run[1]+1]
    run_rotations = date_dict["rotation"][run[0]:run[1]+1]
    run_orientations = date_dict["orientation"][run[0]:run[1]+1]
    
    run_dict={"timestamps":dt_run_timestamps, "positions":run_positions, "rotations":run_rotations, "orientations (x,y)":run_orientations}
    df = pd.DataFrame(data=run_dict)
    
    return df

def get_run_type(date_dict, id_run):
    if date_dict["successful"][id_run]:
        return "successful"
    elif date_dict["challenges"][id_run]:
        return "challenge - unsuccessful"
    else:
        return "test run"


if __name__ == "__main__":
    st.set_page_config(
    page_title="Run data",
    page_icon="🏃",
    layout="wide"
    )  
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        page = RunDataPage(st.session_state['data_model'])
        title = "Individual robot runs"
        description =   """
                        This page shows plots and data for individual robot runs
                        """
        page.run_page(title, description)

    