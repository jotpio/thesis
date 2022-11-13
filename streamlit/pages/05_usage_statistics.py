import sys, os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st
st.set_page_config(
     page_title="Usage statistics",
     page_icon="📈",
     layout="wide"
)


from fpdf import FPDF
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PIL import Image


import data_model
import plot_usage_statistics
import ui_helper

start_date = data_model.start_date
end_date = data_model.end_date

def main():
    sidebar, start_date, end_date, challenges, only_successful = ui_helper.setup_sidebar(start_date, end_date)   
    
    if data_model.dates_dict is not None:
        # init
        pdf = create_pdf()
        
        # setup page
        st.header("average time of day for each run")
        fig = plot_usage_statistics.plot_time_of_day_histogram(data_model.dates_dict, challenges=challenges, only_successful=only_successful, show=False)
        add_image_to_pdf(fig, pdf)
        st.pyplot(fig)

        st.header("daily number of (unique) visitors")
        fig = plot_usage_statistics.plot_daily_number_runs(data_model.dates_dict, show=False)
        add_image_to_pdf(fig, pdf)
        st.pyplot(fig)

        st.header("daily use times and operational times in hours")
        fig = plot_usage_statistics.plot_daily_use_times_and_operational_times(data_model.dates_dict, to_pdf=True, show=False)
        add_image_to_pdf(fig, pdf)
        st.pyplot(fig)

        st.header("daily start and end times")
        fig = plot_usage_statistics.plot_daily_start_end_times(data_model.dates_dict, show=False)
        add_image_to_pdf(fig, pdf)
        st.pyplot(fig)

        st.header("busiest weekdays by percentual use time, estimated visitors")
        fig = plot_usage_statistics.plot_weekday_business(data_model.dates_dict, show=False)
        add_image_to_pdf(fig, pdf)
        st.pyplot(fig)
        
        st.header("Download")
        pdf_byte_arr = pdf_to_byte_array(pdf)
        st.download_button("Download PDF",  bytes(pdf_byte_arr), file_name=f"stats_{start_date}-{end_date}.pdf")
    
    
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
    main()