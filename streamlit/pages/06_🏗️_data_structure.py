import streamlit as st
from template.page import Page
from PIL import Image

class DataStructurePage(Page):
    
    def run_page(self, title, description):
        super().run_page(title, description)
        
        #
        #PAGE
        #
        image = Image.open('data_structure.png')
        st.image(image, caption='Data structure')
        
        

if __name__ == "__main__":
    st.set_page_config(
        page_title="Data structure",
        page_icon="🏗️",
        layout="wide",
    )  
    if 'data_model' not in st.session_state or not st.session_state['data_model'].dates_dict:
        st.warning("Data not loaded! Go to Home to load data.", icon="⚠️")
    else:
        page = DataStructurePage(st.session_state['data_model'])
        title = "Data structure"
        description =   """
                        This page explains how the data is structured and saved
                        """
        page.run_page(title, description)