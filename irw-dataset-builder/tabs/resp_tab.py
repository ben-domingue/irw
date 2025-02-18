import streamlit as st
import pandas as pd

def map_resp(original_df, indices_df, id_orientation, item_orientation):
    """Maps responses based on ID and item positions."""
    resp_values = []

    for id_idx, item_idx in zip(indices_df['id_idx'], indices_df['item_idx']):
        if id_orientation == "Row":
            row_idx = id_idx[0]  # Row position from id
            col_idx = item_idx[1]  # Column position from item
        else:  # id_orientation == "Column"
            row_idx = item_idx[0]  # Row position from item
            col_idx = id_idx[1]  # Column position from id
        
        row_idx = int(row_idx)
        col_idx = int(col_idx)
        
        try:
            resp = original_df.iat[row_idx, col_idx]
            resp_values.append(resp)
        except IndexError as e:
            st.error(f"Index error at position ({row_idx}, {col_idx}). Please check your data layout selection.")
            raise e

    return pd.DataFrame({'resp': resp_values})

def show_resp_tab():
    if not st.session_state.indices_df.empty:
        st.markdown("""
        ### Select Your Data Layout

        Please choose the layout that matches your data structure:
        """)

        # Create example DataFrames
        example_1 = pd.DataFrame({
            'ID': ['Student1', 'Student2', 'Student3'],
            'Item1': [1, 0, 1],
            'Item2': [0, 1, 1],
            'Item3': [1, 1, 0]
        })

        example_2 = pd.DataFrame({
            'Items': ['Item1', 'Item2', 'Item3'],
            'Student1': [1, 0, 1],
            'Student2': [0, 1, 1],
            'Student3': [1, 1, 0]
        })

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Layout Option 1")
            st.markdown("IDs as rows, Items as columns:")
            st.dataframe(example_1)
            option_1_selected = st.button("Select Layout 1")

        with col2:
            st.subheader("Layout Option 2")
            st.markdown("Items as rows, IDs as columns:")
            st.dataframe(example_2)
            option_2_selected = st.button("Select Layout 2")

        if option_1_selected:
            resp_df = map_resp(st.session_state.df, st.session_state.indices_df, "Row", "Column")
            st.session_state.irw_dataframe = pd.concat([
                st.session_state.irw_dataframe.reset_index(drop=True), 
                resp_df.reset_index(drop=True)
            ], axis=1)
            st.success("Layout 1 selected and responses mapped!")
            st.rerun()

        if option_2_selected:
            resp_df = map_resp(st.session_state.df, st.session_state.indices_df, "Column", "Row")
            st.session_state.irw_dataframe = pd.concat([
                st.session_state.irw_dataframe.reset_index(drop=True), 
                resp_df.reset_index(drop=True)
            ], axis=1)
            st.success("Layout 2 selected and responses mapped!")
            st.rerun()
    else:
        st.write("Please complete the IDs and items mapping first") 