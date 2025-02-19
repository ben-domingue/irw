import streamlit as st
import pandas as pd

def show_review_tab():
    st.title("Review and Save")

    # Divide the page into two columns
    left_col, right_col = st.columns(2)

    # Left column: Review the dataset
    with left_col:
        st.subheader("Review Your Created Dataset")
        st.write("Below is the dataset you have created. Please review it before downloading.")
        st.dataframe(st.session_state.irw_dataframe)

    # Right column: Download the dataset
    with right_col:
        st.subheader("Download Your Dataset")
        st.write("Click the button below to download the dataset in CSV format.")
        
        # Convert DataFrame to CSV
        csv = st.session_state.irw_dataframe.to_csv(index=False).encode('utf-8')
        
        # Download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="created_dataset.csv",
            mime="text/csv"
        ) 