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

start_date = data_model.start_date
end_date = data_model.end_date


def main():
    '''
        PAGE
    '''
    st.title("Robot and target fish")
    st.write("This page shows plots and data for robot, target area and target fish relations")
    st.markdown("""---""")
    
    with st.expander("inter individual distances between robot and target fish (daily)"):
        col1, col2 = st.columns(2)
        figs1, figs2 = plot.plot_inter_individual_distances(data_model.dates_dict, start_date, end_date, challenges=True, only_successful=True, bins=10, show=False)
        with col1:
            for fig in figs1:
                st.pyplot(fig)
        with col2:
            for fig in figs2:
                st.pyplot(fig)
                
    with st.expander("robot distance to goal (daily)"):
        figs = plot.plot_robot_distance_goal(data_model.dates_dict, start_date, end_date, challenges=True, only_successful=True, show=False)
        for fig in figs:
            st.pyplot(fig)
        
if __name__ == "__main__":
    main()
    