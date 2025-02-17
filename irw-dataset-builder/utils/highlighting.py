def highlight_selection(cell, row_idx: int, col_idx: int, 
                       start_row: int, finish_row: int, 
                       start_col: int, finish_col: int) -> str:
    """
    Highlight cells within the selected range.
    
    Args:
        cell: Cell value
        row_idx (int): Current row index
        col_idx (int): Current column index
        start_row (int): Selection start row
        finish_row (int): Selection end row
        start_col (int): Selection start column
        finish_col (int): Selection end column
        
    Returns:
        str: CSS style string for highlighting
    """
    if start_row <= row_idx <= finish_row and start_col <= col_idx <= finish_col:
        return 'background-color: yellow'
    return '' 