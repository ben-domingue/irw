import pandas as pd

def process_row_as_column(data: pd.DataFrame, start_row: int, end_row: int, column_name="id") -> pd.DataFrame:
    """
    Process a row selection into a column if needed.
    
    Args:
        data (pd.DataFrame): Input DataFrame
        start_row (int): Starting row index
        end_row (int): Ending row index
        column_name (str): Name for the resulting column
        
    Returns:
        pd.DataFrame: DataFrame with the processed column
    """
    if end_row - start_row == 1:
        row_as_column = data.iloc[start_row, :].values
        new_column = pd.DataFrame({column_name: row_as_column})
        return new_column
    return data

def broadcasting_with_ranges(original_df: pd.DataFrame, 
                           id_row_range: tuple, 
                           id_col_range: tuple, 
                           item_row_range: tuple, 
                           item_col_range: tuple) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create broadcasted dataframes for IDs and items.
    
    Args:
        original_df (pd.DataFrame): Original dataset
        id_row_range (tuple): (start, end) row indices for IDs
        id_col_range (tuple): (start, end) column indices for IDs
        item_row_range (tuple): (start, end) row indices for items
        item_col_range (tuple): (start, end) column indices for items
        
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (broadcasted_df, indices_df)
    """
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