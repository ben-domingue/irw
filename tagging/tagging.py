from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import openai
import yaml
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import argparse
from tqdm import tqdm

# Your existing functions
def label_data(labeling_prompt_raw, dataset_short_description, description_from_link):
    label_prompt = ChatPromptTemplate.from_template(labeling_prompt_raw)
    label_chain = label_prompt | llm | StrOutputParser()
    
    try:
        return label_chain.invoke({
            "dataset_short_description": dataset_short_description,
            "description_from_link": description_from_link,
        })
    except openai.APIConnectionError:
        return ""

def supervise_labels(supervisor_prompt_raw, dataset_short_description, description_from_link, label_json):
    supervisor_prompt = ChatPromptTemplate.from_template(supervisor_prompt_raw)
    supervisor_chain = supervisor_prompt | llm | StrOutputParser()
    
    try:
        return supervisor_chain.invoke({
            "dataset_short_description": dataset_short_description,
            "description_from_link": description_from_link,
            "label_json": label_json
        })
    except openai.APIConnectionError:
        return ""

# Function to create a description from a webpage
def create_description_from_link(link):
    try:
        response = requests.get(link)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Create a description from the page content (adjust the parsing logic as needed)
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        description = ' '.join(paragraphs[:5])  # Limit to first 5 paragraphs or adjust as needed
        return description
    
    except (requests.RequestException, ValueError) as e:
        print(f"Error accessing {link}: {e}")
        return ""

# Main function to process the dataset
def process_dataset(csv_path, labeling_prompt_raw, supervisor_prompt_raw):
    # Read the CSV file using Pandas
    df = pd.read_csv(csv_path)

    # Add new columns with a default value of 'Unknown'
    new_columns = [
        "Measurement Focus",
        "Response Type",
        "Target Population",
        "Domain of Measurement",
        "Scoring Methodology",
        "Data Structure",
        "Data Source",
        "Context of Use",
        "Item Format",
        "Geographic Location"
    ]

    for col in new_columns:
        df[col] = 'Unknown'


    # Iterate through each row in the dataset

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows"):
        link = row['URL']  # Assuming the CSV file has a 'link' column
        short_description = row['Description']
        
        # Step 1: Create a description from the link
        description_from_link = create_description_from_link(link)
        if not description_from_link:
            description_from_link = ""  # Skip to the next link if there's an issue

        # Step 2: Calculate labels for the description
        label_json = label_data(labeling_prompt_raw, short_description, description_from_link)
        if not label_json:
            continue  # Skip if label generation failed

        # Step 3: Run the guardrail check
        supervision_result = supervise_labels(supervisor_prompt_raw, short_description, description_from_link, label_json)
        if supervision_result:
            label_json = json.loads(supervision_result)  # Only if it's a JSON string
            if isinstance(label_json, dict):
                    df.at[index, 'Measurement Focus'] = label_json.get('Measurement Focus', 'Unknown')
                    df.at[index, 'Response Type'] = label_json.get('Response Type', 'Unknown')
                    df.at[index, 'Target Population'] = label_json.get('Target Population', 'Unknown')
                    df.at[index, 'Domain of Measurement'] = label_json.get('Domain of Measurement', 'Unknown')
                    df.at[index, 'Scoring Methodology'] = label_json.get('Scoring Methodology', 'Unknown')
                    df.at[index, 'Data Structure'] = label_json.get('Data Structure', 'Unknown')
                    df.at[index, 'Data Source'] = label_json.get('Data Source', 'Unknown')
                    df.at[index, 'Context of Use'] = label_json.get('Context of Use', 'Unknown')
                    df.at[index, 'Item Format'] = label_json.get('Item Format', 'Unknown')
                    df.at[index, 'Geographic Location'] = label_json.get('Geographic Location', 'Unknown')

    
    # Convert results to a DataFrame and save to CSV (optional)
    df.to_csv('labeled_results.csv', index=False)
    
    return df

# Usage example

## setup env and config
load_dotenv()
llm = ChatOpenAI()

config_file_path = 'config/config.yaml'
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)

labeling_prompt_raw = config.get('labeling_prompt')
supervisor_prompt_raw = config.get('supervisor_prompt')

parser = argparse.ArgumentParser(description="Tagging script with data path argument.")
parser.add_argument('--data-path', type=str, required=True, help="Path to the input CSV file")

# Parse the arguments
args = parser.parse_args()

# Read the CSV file from the provided data path
csv_path = args.data_path  # Path to your CSV file
# Run the process
df_results = process_dataset(csv_path, labeling_prompt_raw, supervisor_prompt_raw)
print("Processing complete. Results saved to 'labeled_results.csv'.")
