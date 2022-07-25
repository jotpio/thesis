import sys, os, time
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
if parent not in sys.path:
    sys.path.append(parent)
    print("Adding parent to sys path")
    print(sys.path)

import streamlit as st
import matplotlib.pyplot as plt

import data_model
import load_data
import util
import plot
import plot_usage_statistics 

start_date = data_model.start_date
end_date = data_model.end_date

def main():
    '''
        PAGE
    '''
    st.title("Individual robot runs")
    st.write("This page shows plots and data for individual robot runs")
    st.markdown("""---""")
    
    # filter parameters
    st.subheader("Here you can set filter parameters to get specific runs")
    
    col1, col2 = st.columns(2)
    with col1:
        challenges = st.checkbox("only challenge runs")
        only_successful = st.checkbox("only successful runs")

        if only_successful:
            descriptor_runs = "successful challenge runs"
        elif challenges:
            descriptor_runs = "challenge runs"
        else:
            descriptor_runs = "runs"
    number_of_runs = get_number_of_runs(only_successful, challenges)
    
    with col2:
        st.metric(descriptor_runs, number_of_runs)
        st.caption(f"in selected timeframe {start_date} - {end_date}")

    st.markdown("""---""")
    
    # run selector
    st.write(f"Please select the run or a range of runs you wish to generate plots for")    
    date_run_tuples = get_date_run_tuples(only_successful, challenges)
    start_run, end_run = st.select_slider('Select the range of runs',
                    options=date_run_tuples,
                    value=(date_run_tuples[10], date_run_tuples[13]),
                    format_func=format_date_run_tuples)
    
    # plot runs
    st.markdown("""---""")
    st.subheader("Plots")
    plot_selected_runs(date_run_tuples, start_run, end_run)

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_number_of_runs(only_successful, challenges):
    st.write("Counting runs for the first time")
    return util.get_number_of_runs(data_model.dates_dict, start_date, end_date, successful=only_successful, challenges=challenges)

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_date_run_tuples(only_successful, challenges):
    return util.get_date_run_tuples(data_model.dates_dict, only_successful, challenges)

def plot_selected_runs(date_run_tuples, start_date_run_tuple, end_date_run_tuple):
    # st.write(start_date_run_tuple)
    # st.write(end_date_run_tuple)
    id_start_tuple = date_run_tuples.index(start_date_run_tuple, 0)
    id_end_tuple = date_run_tuples.index(end_date_run_tuple, id_start_tuple)
    # st.write(id_start_tuple)
    # st.write(id_end_tuple)
    selected_date_run_tuples = date_run_tuples[id_start_tuple:id_end_tuple+1]
    # st.write(selected_date_run_tuples)
    for date_run_tuple in selected_date_run_tuples:
        st.write(format_date_run_tuples(date_run_tuple))
        fig = plot.plot_run(data_model.dates_dict[date_run_tuple[0]], id_run=date_run_tuple[1], date_key=date_run_tuple[0], show=False)
        st.pyplot(fig, clear_figure=True)
        st.markdown("""---""")
    
def format_date_run_tuples(date_run_tuple):
    return f"{date_run_tuple[0]} - run {date_run_tuple[1]}"


if __name__ == "__main__":
    main()
    

    