import streamlit as st
import datetime
import data_model

def setup_sidebar(start_date, end_date):
    sidebar = st.sidebar
    with sidebar:
        st.header("Filter data")
        
        start_date = st.date_input(
                "Start date",
                value=datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date(),
                min_value=datetime.datetime.strptime(data_model.min_start_date, "%Y-%m-%d").date(),
                max_value=datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()
                ).strftime("%Y-%m-%d")
        end_date = st.date_input(
                "End date",
                datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date(),
                min_value=datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date(),
                max_value=datetime.datetime.strptime(data_model.max_end_date, "%Y-%m-%d").date()
                ).strftime("%Y-%m-%d")
        
        
        if data_model.only_challenges_loaded:
            challenges = st.checkbox("use challenge runs", value=True, disabled=True, help="There are no non-challenges loaded. Go to Home if you also want to load test runs")
        else:
            challenges = st.checkbox("use challenge runs")
        only_successful = st.checkbox("only use successful challenge runs")
    return sidebar, start_date, end_date, challenges, only_successful