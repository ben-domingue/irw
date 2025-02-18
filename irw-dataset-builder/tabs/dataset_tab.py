import streamlit as st
import pandas as pd

def show_dataset_tab():
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file is not None:
        # Load the data
        if st.session_state.df is None:
            st.session_state.df = pd.read_csv(uploaded_file, header=None)
            st.rerun()
        else:
            st.title("Extend DataFrame:")
            st.write("You can extend the dataframe by adding a column or a row.")
            col1, col2 = st.columns(2)
            
            # Add Column button
            if col1.button("Add Column", key="add_col"):
                new_df = st.session_state.df.copy()
                current_cols = len(new_df.columns)
                new_df.insert(0, current_cols, range(len(new_df)))
                new_df.columns = range(len(new_df.columns))
                st.session_state.df = new_df
                st.dataframe(st.session_state.df)
                st.rerun()
                
            # Add Row button    
            if col2.button("Add Row", key="add_row"):
                new_df = st.session_state.df.copy()
                new_row = pd.DataFrame([range(0, len(new_df.columns))])
                new_row.columns = new_df.columns
                st.session_state.df = pd.concat([new_row, new_df]).reset_index(drop=True)
                st.dataframe(st.session_state.df)
                st.rerun()

        st.write("DataFrame:")
        st.dataframe(st.session_state.df) 