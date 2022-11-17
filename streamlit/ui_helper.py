import streamlit as st
import datetime
import data_model

def setup_sidebar(start_date, end_date):
    
    sidebar = st.sidebar
    with sidebar:
        if start_date is None or end_date is None:
            return sidebar
        st.header("Filter data")
        st.caption(f"Data in the range of {data_model.min_start_date} to {data_model.max_end_date} was loaded. Select the date range you want to process.")

        # date range selector
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
        data_model.start_date = start_date
        data_model.end_date = end_date
        
        # challenge and successful filter checkboxes
        if data_model.only_challenges_loaded:
            challenges = st.checkbox("use challenge runs", value=True, disabled=True, help="There are no non-challenges loaded. Go to Home if you also want to load test runs")
        else:
            challenges = st.checkbox("use challenge runs")
        only_successful = st.checkbox("only use successful challenge runs")
        
        data_model.challenges = challenges
        data_model.only_successful = only_successful
        
        return sidebar