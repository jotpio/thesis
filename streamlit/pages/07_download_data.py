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

def main():
    start_date = data_model.start_date
    end_date = data_model.end_date
    only_challenges = data_model.only_challenges_loaded
    dates_dict = data_model.dates_dict
    
    st.title("Download data")
    st.markdown("""---""")
        
    sidebar, start_date, end_date, only_challenges, only_successful = ui_helper.setup_sidebar(start_date, end_date)   
    
    st.write(f"Click the button to download data files for the date range: {start_date} - {end_date}")

    prepare = st.button("Prepare data for download")
    if prepare:
        zip_name = zip_data(start_date, end_date, dates_dict, only_challenges)
        with open(zip_name, "rb") as fp:
            btn = st.download_button(
                label="Download ZIP",
                data=fp,
                file_name=zip_name,
                mime="application/zip"
            )
    

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def zip_data(start_date, end_date, dates_dict, only_challenges):
    # Create a ZipFile Object
    zip_name = f"{start_date}-{end_date}.zip"
    with ZipFile(zip_name, 'w') as zipObj:
        # Add date files to the zip
        for key in dates_dict.keys():
            date = dates_dict[key]
            if only_challenges:
                file_name = f"challenges_dates_dict_{key}.npy"
            else:
                file_name = f"dates_dict_{key}.npy"
            print(f"Adding {key} to zip")
            np.save(file_name, date, allow_pickle=True)
            zipObj.write(file_name)
            os.remove(file_name) # remove locally after adding to zip
    return zip_name
    
    
if __name__ == "__main__":
    main()
    

    