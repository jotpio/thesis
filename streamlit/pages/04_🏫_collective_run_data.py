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
        
class CollectiveDataPage(Page):
    
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        #PAGE
        #        
        
        default_bin_size=5

        # plots
        tab1, tab2, tab3, tab4 = st.tabs(["run length histogram", " ", " ", " "])
        with tab1:
            st.header("run length histogram")
            st.write("Shows histogram with:  X - time for run in seconds and  Y - number of runs with time x")
            bin_size = st.number_input('Bin size', min_value=0, max_value=100, value=default_bin_size)
            fig = plot.plot_run_length_hist(self.data_model.dates_dict, start_date=self.data_model.start_date, end_date=self.data_model.end_date, bin_size=bin_size, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, show=False)
            st.pyplot(fig)
        
        
if __name__ == "__main__":
    st.set_page_config(
        page_title="Collective run data",
        page_icon="🏫",
        layout="wide",
    )  
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        page = CollectiveDataPage(st.session_state['data_model'])
        title = "Collective run data"
        description =   """
                        This page shows analytics for all robot runs
                        """
        page.run_page(title, description)