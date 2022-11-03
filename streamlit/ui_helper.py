import streamlit as st
import datetime


def setup_sidebar(start_date, end_date):
    sidebar = st.sidebar
    with sidebar:
        st.header("Filter data")
        
        start_date = st.date_input(
                "Start date",
                # datetime.date(2022, 2, 1))
                datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date()).strftime("%Y-%m-%d")
        end_date = st.date_input(
                "End date",
                datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()).strftime("%Y-%m-%d")
        
        challenges = st.checkbox("use challenge runs")
        only_successful = st.checkbox("only use successful challenge runs")
    return sidebar, start_date, end_date, challenges, only_successful