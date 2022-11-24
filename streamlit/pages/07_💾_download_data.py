import sys, os
import numpy as np
from zipfile import ZipFile
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
import ui_helper

from template.page import Page
from io import BytesIO

class DownloadPage(Page):
    
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        #PAGE
        #
        st.info(f"Click the button to download data files for the date range: {self.data_model.start_date} to {self.data_model.end_date}")

        prepare = st.button("Prepare data for download")
        with st.spinner("Preparing ZIP file..."):
            if prepare:
                zip_name, mem_zip = zip_data(self.data_model.start_date, self.data_model.end_date, self.data_model.dates_dict, self.data_model.only_challenges_loaded)
                btn = st.download_button(
                    label="Download ZIP",
                    data=mem_zip,
                    file_name=zip_name,
                    mime="application/zip",
                )    


@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def zip_data(start_date, end_date, dates_dict, only_challenges_loaded):
    # Create a ZipFile Object
    zip_name = f"{start_date}-{end_date}.zip"
    mem_zip = BytesIO()
    with ZipFile(mem_zip, 'w') as zipObj:
        # Add date files to the zip
        for key in dates_dict.keys():
            date = dates_dict[key]
            if only_challenges_loaded:
                file_name = f"challenges_dates_dict_{key}.npy"
            else:
                file_name = f"dates_dict_{key}.npy"
            print(f"Adding {key} to zip")
            np.save(file_name, date, allow_pickle=True)
            zipObj.write(file_name)
            os.remove(file_name) # remove locally after adding to zip
    return zip_name, mem_zip.getvalue()

def remove_zip(file,zip_name):
    print(f"Removing {zip_name}")
    file.close()
    os.remove(zip_name)
    
if __name__ == "__main__":
    st.set_page_config(
        page_title="Download",
        page_icon="💾",
        layout="wide",
    )  
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        page = DownloadPage(st.session_state['data_model'])
        title = "Download"
        description =   """
                        This page provides the opportunity to download selected data
                        """
        page.run_page(title, description)