import sys, os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st

import data_model
import util
import plot
import ui_helper
from template.page import Page

class RobotTargetInteractionsPage(Page):
    
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        #PAGE
        #
        tab1, tab2 = st.tabs(["inter individual distances between robot and target fish (daily)", "robot distance to goal (daily)"])
        with tab1:
            bins = st.number_input("Bins", min_value=0, max_value=100, value=10)
            col1, col2 = st.columns(2)
            figs1, figs2 = plot.plot_inter_individual_distances(self.data_model.dates_dict, start_date=self.data_model.start_date, end_date=self.data_model.end_date, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, bins=bins, show=False)
            with col1:
                for fig in figs1:
                    st.pyplot(fig)
            with col2:
                for fig in figs2:
                    st.pyplot(fig)

        with tab2:
            figs = plot.plot_robot_distance_goal(data_model.dates_dict, start_date=self.data_model.start_date, end_date=self.data_model.end_date, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, show=False)
            for fig in figs:
                st.pyplot(fig)
    
        
if __name__ == "__main__":
    st.set_page_config(
        page_title="Robot - target interactions",
        page_icon="🎯",
        layout="wide",
    )  
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        page = RobotTargetInteractionsPage(st.session_state['data_model'])
        title = "Robot and target fish interactions"
        description =   """
                        This page shows robot and target fish interaction plots and data
                        """
        page.run_page(title, description)
