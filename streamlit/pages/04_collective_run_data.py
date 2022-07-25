import sys, os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st

import data_model
import load_data
import util
import plot
import plot_usage_statistics 

default_bin_size=5
start_date = data_model.start_date
end_date = data_model.end_date


# set parameter
challenges = st.checkbox("only challenge runs")
only_successful = st.checkbox("only successful runs")

# plots

tab1, tab2, tab3, tab4 = st.tabs(["run length histogram", " ", " ", " "])
with tab1:
    st.header("run length histogram")
    st.write("Shows histogram with x - time for run in seconds and y - number of runs with time x")
    bin_size = st.number_input('Number of bins', default_bin_size)
    fig = plot.plot_run_length_hist(data_model.dates_dict, bin_size=bin_size, challenges=challenges, only_successful=only_successful, show=False)
    st.pyplot(fig)