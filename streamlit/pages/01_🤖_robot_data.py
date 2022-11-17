import sys, os
import datetime
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st

import data_model
import plot
import ui_helper
from template.page import Page

class RobotDataPage(Page):
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        # PAGE
        #
        
        # plots
        with st.spinner('Loading plots...'):
            tab1, tab2, tab3 = st.tabs(["all robot positions", "avg rot and pos", "starts and ends"])

            with tab1:
                st.write("""
                    This scatter plot shows all robot positions for all loaded days. 
                """)
                fig = plot.plot_all_positions(self.data_model.dates_dict, start_date=self.data_model.start_date, end_date=self.data_model.end_date, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, show=False, size=(15,15))
                st.pyplot(fig)
            with tab2:
                polar_density = st.checkbox("Polar density", value=True)
                st.header("average rotation and position heatmap")
                fig = plot.plot_rotations_and_heatmap(self.data_model.dates_dict, start_date=self.data_model.start_date, end_date=self.data_model.end_date, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, ignore_robot_standing=True, polar_density=polar_density, show=False)
                st.pyplot(fig)

            with tab3:
                st.header("robot start and end points")
                fig = plot.plot_starts_ends(data_model.dates_dict, start_date=self.data_model.start_date, end_date=self.data_model.end_date, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, show=False)
                st.pyplot(fig)
        
if __name__ == "__main__":
    st.set_page_config(
    page_title="Robot data",
    page_icon="🤖",
    layout="wide"
    )
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        
        page = RobotDataPage(st.session_state['data_model'])
        title = "Robot data"
        description =   """
                        This page shows general robot related plots like position heatmaps and average orientations.
                        """
        page.run_page(title, description)

    