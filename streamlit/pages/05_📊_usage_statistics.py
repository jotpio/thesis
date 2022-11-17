import sys, os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st
from fpdf import FPDF
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PIL import Image


import data_model
import plot_usage_statistics
import ui_helper
from template.page import Page        
        
class UsageStatisticsPage(Page):
    
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        #PAGE
        #
        if self.data_model.only_challenges_loaded:
            st.warning("Only challenge data can be loaded! Data in remote location does not contain non-challenge data. Use local streamlit at HU to get full usage statistics.", icon="⚠️")
        elif self.data_model.challenges or self.data_model.only_successful:
            st.warning("Deselect challenge and successful challenge checkboxes to get corrent usage statistics!", icon="⚠️")
                
        
        download_container = st.container()
        if self.data_model.dates_dict is not None:
            # init PDF
            pdf = create_pdf()

            # setup page
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["average time of day", "daily number visitors", "daily use times", "daily starts ends", "busiest weekdays"])
            with tab1:
                st.header("average time of day for each run")
                fig = plot_usage_statistics.plot_time_of_day_histogram(self.data_model.dates_dict, challenges=self.data_model.challenges, only_successful=self.data_model.only_successful, show=False)
                add_image_to_pdf(fig, pdf)
                st.pyplot(fig)
            with tab2:
                st.header("daily number of (unique) visitors")
                fig = plot_usage_statistics.plot_daily_number_runs(self.data_model.dates_dict, show=False)
                add_image_to_pdf(fig, pdf)
                st.pyplot(fig)
            with tab3:
                st.header("daily use times and operational times in hours")
                fig = plot_usage_statistics.plot_daily_use_times_and_operational_times(self.data_model.dates_dict, to_pdf=True, show=False)
                add_image_to_pdf(fig, pdf)
                st.pyplot(fig)
            with tab4:
                st.header("daily start and end times")
                fig = plot_usage_statistics.plot_daily_start_end_times(self.data_model.dates_dict, show=False)
                add_image_to_pdf(fig, pdf)
                st.pyplot(fig)
            with tab5:
                st.header("busiest weekdays by percentual use time, estimated visitors")
                fig = plot_usage_statistics.plot_weekday_business(self.data_model.dates_dict, show=False)
                add_image_to_pdf(fig, pdf)
                st.pyplot(fig)
            with download_container:
                st.header("Download")
                pdf_byte_arr = pdf_to_byte_array(pdf)
                st.download_button("Download PDF",  bytes(pdf_byte_arr), file_name=f"stats_{self.data_model.start_date}-{self.data_model.end_date}.pdf")

    
    
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    return pdf

def add_image_to_pdf(fig, pdf):
    # Converting Figure to an image:
    canvas = FigureCanvas(fig)
    canvas.draw()
    img = Image.fromarray(np.asarray(canvas.buffer_rgba()))
    
    # add image to pdf
    pdf.image(img, w=pdf.epw)  # Make the image full width


def pdf_to_byte_array(pdf):
    pdf_byte_arr = pdf.output()
    return pdf_byte_arr
    
if __name__ == "__main__":
    st.set_page_config(
        page_title="Usage statistics",
        page_icon="📊",
        layout="wide",
    )  
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        page = UsageStatisticsPage(st.session_state['data_model'])
        title = "Usage statistics"
        description =   """
                        This page shows usage statistics for the exhibit
                        """
        page.run_page(title, description)