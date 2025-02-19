import streamlit as st
import pandas as pd

def highlight(cell, row_idx, col_idx, start_row, finish_row, start_col, finish_col):
    if start_row <= row_idx <= finish_row and start_col <= col_idx <= finish_col:
        return 'background-color: yellow'
    return ''

def process_row_as_column(data: pd.DataFrame, start_row: int, end_row: int, column_name="item") -> pd.DataFrame:
    """Process a row selection into a column if needed."""
    if end_row - start_row == 1:
        row_as_column = data.iloc[start_row, :].values
        new_column = pd.DataFrame({column_name: row_as_column})
        return new_column
    return data

def broadcasting_with_ranges(original_df: pd.DataFrame, 
                           id_row_range: tuple, 
                           id_col_range: tuple, 
                           item_row_range: tuple, 
                           item_col_range: tuple):
    """Creates broadcasted dataframes for IDs and items."""
    # Extract IDs and their indices
    ids = original_df.iloc[id_row_range[0]:id_row_range[1], id_col_range[0]:id_col_range[1]]
    ids_flat = ids.stack().reset_index(drop=True)
    id_indices = ids.stack().index

    # Extract items and their indices
    items = original_df.iloc[item_row_range[0]:item_row_range[1], item_col_range[0]:item_col_range[1]]
    items_flat = items.stack().reset_index(drop=True)
    item_indices = items.stack().index

    # Create Cartesian product
    repeated_ids = ids_flat.repeat(len(items_flat)).reset_index(drop=True)
    repeated_id_indices = pd.Index(id_indices.repeat(len(items_flat)))

    repeated_items = items_flat.values.tolist() * len(ids_flat)
    repeated_item_indices = pd.Index(item_indices.to_list() * len(ids_flat))

    # Create final DataFrames
    broadcasted_df = pd.DataFrame({
        'id': repeated_ids,
        'item': repeated_items
    })

    indices_df = pd.DataFrame({
        'id_idx': repeated_id_indices.map(lambda x: (x[0], x[1])),
        'item_idx': repeated_item_indices.map(lambda x: (x[0], x[1]))
    })

    return broadcasted_df, indices_df

def show_item_tab():
    st.header("Map items")
    if st.session_state.df is not None:
        data = st.session_state.df
        st.title("Interactive Item Mapping")
        st.write("Please specify the location of items in your dataset. Use the input boxes below to indicate the range of rows and columns.")

        # Input fields for range selection
        start_row = st.number_input("Item Start Row Number:", min_value=0, max_value=len(data), value=0)
        finish_row = st.number_input(f"Item Finish Row Number: (Last row is {len(data) - 1})", min_value=start_row, max_value=len(data), value=start_row)
        start_col = st.number_input("Item Start Column Number:", min_value=0, max_value=len(data.columns), value=0)
        finish_col = st.number_input(f"Item Finish Column Number: (Last column is {len(data.columns) - 1})", min_value=start_col, max_value=len(data.columns), value=start_col)

        # Highlight the selected area
        highlighted_data = data.style.apply(
            lambda row: [
                highlight(cell, row.name, col_idx, start_row, finish_row, start_col, finish_col) 
                for col_idx, cell in enumerate(row)
            ], axis=1
        )
        
        st.subheader("Highlighted Dataset Preview")
        st.write(highlighted_data)
        
        if st.button("Confirm Items Selection"):
            start_row_idx = start_row
            finish_row_idx = finish_row + 1
            start_col_idx = start_col
            finish_col_idx = finish_col + 1
            
            selected_items = data.iloc[start_row_idx:finish_row_idx, start_col_idx:finish_col_idx]
            st.success("Selection Confirmed!")
            st.write("Here are the selected items:")
            st.write(selected_items)
            
            st.session_state.item_row_range = (start_row_idx, finish_row_idx)
            st.session_state.item_col_range = (start_col_idx, finish_col_idx)
            
            items = process_row_as_column(selected_items, start_row=0, end_row=1)
            st.write(items)
            
            updated_df, indices_df = broadcasting_with_ranges(
                st.session_state.df, 
                st.session_state.id_row_range, 
                st.session_state.id_col_range,
                st.session_state.item_row_range, 
                st.session_state.item_col_range
            )
            
            st.session_state.irw_dataframe = updated_df    
            st.session_state.indices_df = indices_df      
            st.rerun()
    else:
        st.write("No data uploaded.") 