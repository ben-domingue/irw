import pandas as pd

def add_student_ids(data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a column 'id' to the dataset with unique student IDs in the format 'student_001', 'student_002', etc.
    
    Args:
        data (pd.DataFrame): The input DataFrame to which the 'id' column will be added.

    Returns:
        pd.DataFrame: The DataFrame with the 'id' column added.
    """
    # Create a list of student ids in the format student_001, student_002, ...
    student_ids = [f"student_{str(i+1).zfill(3)}" for i in range(len(data))]
    
    # Add the 'id' column to the DataFrame
    data['id'] = student_ids
    
    return data

data = pd.read_csv("CBI Data 2080 Cases.csv")
updated_data = add_student_ids(data)
updated_data.to_csv("example.csv",index=False)