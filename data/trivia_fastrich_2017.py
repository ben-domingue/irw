import pandas as pd
import numpy as np

def convert_to_irw(input_csv, output_csv):
    df = pd.read_csv(input_csv, encoding='latin-1')
    
    covariates = {
        'Age': 'cov_age',
        'Education': 'cov_education',
        'English': 'cov_english',
        'Gender': 'cov_gender',
        'Confidence': 'cov_confidence',
        'Curiosity': 'cov_curiosity',
        'Interest': 'cov_interest',
        'Question': 'cov_question',
        'corrAnswer': 'cov_corranswer'
    }
    
    df_wave1 = df[['id', 'QuestionID', 'TimeDif', 'Trial', 'Response', 'Date'] + list(covariates.keys())].copy()
    df_wave1['resp'] = 0  # Per instructions: all guesses in session 1 were incorrect
    df_wave1['wave'] = 1
    df_wave1 = df_wave1.rename(columns={
        'QuestionID': 'item',
        'TimeDif': 'rt',
        'Trial': 'cov_trial',
        'Response': 'cov_response',
        'Date': 'date',
        **covariates
    })
    
    df_wave2 = df[['id', 'QuestionID', 'TimeDif2', 'Trial2', 'Response2', 'Date2', 'Memory.sACC'] + list(covariates.keys())].copy()
    df_wave2['wave'] = 2
    df_wave2 = df_wave2.rename(columns={
        'QuestionID': 'item',
        'TimeDif2': 'rt',
        'Trial2': 'cov_trial',
        'Response2': 'cov_response',
        'Date2': 'date',
        'Memory.sACC': 'resp',
        **covariates
    })
    
    df_long = pd.concat([df_wave1, df_wave2], ignore_index=True)
    
    df_long['date'] = pd.to_datetime(df_long['date'], errors='coerce', utc=True)
    df_long['date'] = df_long['date'].apply(
        lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA
    ).astype('Int64')
    
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long = df_long.dropna(subset=['resp'])
    df_long['resp'] = df_long['resp'].astype(int)
    
    for col in ['cov_age', 'cov_confidence', 'cov_curiosity', 'cov_interest']:
        df_long[col] = pd.to_numeric(df_long[col], errors='coerce').astype('Int64')
    
    df_long['item'] = df_long['item'].astype(str)

    final_cols = ['id', 'item', 'resp', 'wave', 'rt', 'date', 'cov_trial', 'cov_response'] + list(covariates.values())
    df_long = df_long[final_cols]
    
    df_long = df_long.sort_values(
        by=['id', 'wave', 'item'],
        key=lambda x: x.str.extract(r'(\d+)')[0].fillna(999).astype(int) if x.name == 'item' else x
    )

    df_long.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv} with shape: {df_long.shape}")


if __name__ == "__main__":
    convert_to_irw('raw_data/TriviaQuestionData.csv', 'processed/trivia_fastrich_2017.csv')