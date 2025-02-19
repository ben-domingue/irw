import streamlit as st
import pandas as pd
from utils.highlighting import highlight_selection

def show_id_tab():
    st.header("Map IDs")
    if st.session_state.df is not None:
        data = st.session_state.df
        st.title("Interactive ID Mapping")
        st.write("Please specify the location of IDs in your dataset. Use the input boxes below to indicate the range of rows and columns.")

        # Input fields for range selection
        start_row = st.number_input("ID Start Row Number :", min_value=0, max_value=len(data), value=0)
        finish_row = st.number_input(f"ID Finish Row Number (Last row is {len(data) - 1}):", min_value=start_row, max_value=len(data), value=start_row)
        start_col = st.number_input("ID Start Column Number :", min_value=0, max_value=len(data.columns), value=0)
        finish_col = st.number_input(f"ID Finish Column Number (Last column is {len(data.columns) - 1}):", min_value=start_col, max_value=len(data.columns), value=start_col)

        # Adjusting for 0-indexing in Python
        start_row_idx = start_row
        finish_row_idx = finish_row + 1
        start_col_idx = start_col
        finish_col_idx = finish_col + 1

        # Highlight the selected area
        highlighted_data = data.style.apply(
            lambda row: [
                highlight_selection(cell, row.name, col_idx, start_row, finish_row, start_col, finish_col) 
                for col_idx, cell in enumerate(row)
            ], axis=1
        )
        
        st.subheader("Highlighted Dataset Preview")
        st.write(highlighted_data)
        
        if st.button("Confirm Selection"):
            selected_ids = data.iloc[start_row_idx:finish_row_idx, start_col_idx:finish_col_idx]
            st.session_state.id_row_range = (start_row_idx,finish_row_idx)
            st.session_state.id_col_range = (start_col_idx,finish_col_idx)
            st.success("Selection Confirmed!")
            st.write("Here are the selected IDs:")
            st.write(selected_ids)
            selected_ids.rename(columns={selected_ids.columns[0]: "id"}, inplace=True)
            st.session_state.irw_dataframe = selected_ids
            st.rerun()
    else:
        st.write("No data uploaded.") 