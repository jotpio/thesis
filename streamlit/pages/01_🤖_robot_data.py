import sys, os
import datetime
import ui_helper
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st

import data_model
import plot
import plot_usage_statistics

start_date = data_model.start_date
end_date = data_model.end_date

st.title("Robot data")
st.write("""
        This page shows general robot related plots like position heatmaps and average orientations.
        """)
# sidebar
sidebar, start_date, end_date, challenges, only_successful = ui_helper.setup_sidebar(start_date, end_date)

# plots
tab1, tab2, tab3 = st.tabs(["all robot positions", "avg rot and pos", "starts and ends"])

with tab1:
    st.write("""
        This scatter plot shows all robot positions for all loaded days. 
    """)
    fig = plot.plot_all_positions(data_model.dates_dict, start_date=start_date, end_date=end_date, challenges=challenges, only_successful=only_successful, show=False, size=(15,15))
    st.pyplot(fig)
with tab2:
    st.header("average rotation and position heatmap")
    fig = plot.plot_rotations_and_heatmap(data_model.dates_dict, challenges=True, only_successful=True, ignore_robot_standing=True, polar_density=True, show=False)
    st.pyplot(fig)

with tab3:
    st.header("robot start and end points")
    fig = plot.plot_starts_ends(data_model.dates_dict, challenges=True, only_successful=True, show=False)
    st.pyplot(fig)

    
    