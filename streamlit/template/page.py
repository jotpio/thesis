import streamlit as st
import ui_helper
import data_model

class Page():
    
    def __init__(self, data_model):
        self.data_model = data_model
        self.start_date = data_model.start_date
        self.end_date = data_model.end_date
        
    def run_page(self, title, description):
        #sidebar
        sidebar = ui_helper.setup_sidebar(self.data_model.start_date, self.data_model.end_date)
        
        #
        # PAGE
        #
        st.title(title)
        st.write(description)
        st.write("""---""")

    
    