import redivis
import argparse
import os
import sys
from dotenv import load_dotenv

# 1. Read the file name or directory name in the arguments
# 2. Check if the file or directory exists
# 3. Create a list. If it is a file, read in all files
# 4. Check if the files are already present on the Redivis backend. If so, check with the user if they would like to update
# 5. Post the table to Redivis

def set_working_directory_to_current():
    """Set the working directory to the path of this script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

def is_valid_table(file_path):
    """Check if the file has a .csv extension"""
    return file_path.lower().endswith('.csv')

def parse_table():
    """Read the dataset/datasets in the directory"""
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process a file or directory name.")
    # Add an argument to accept a file or directory name
    parser.add_argument('path', type=str, help="File or directory name")

    args = parser.parse_args()
    path = args.path

    file_list = []
    dir_path = ""
    # Check if the provided path is a file or a directory
    if os.path.isfile(path):
        print(f"'{path}' is a file. Processing the dataset.\n")
        if is_valid_table(path):
            file_list.append(path)
        else:
            print(f"'{path}' is not a CSV file. Exiting.")
            sys.exit(1)
    elif os.path.isdir(path):
        print(f"'{path}' is a directory. Processing all datasets within it.\n")
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                # Store the relative path to the outer-most directory
                relative_path = os.path.relpath(file_path, path)
                if is_valid_table(file_path):
                    file_list.append(path + '/' +  relative_path)
                else:
                    print(f"'{file_path}' is not a CSV file. Skipping it.")
    else:
        print(f"'{path}' does not exist. Exiting. \n")
        sys.exit(1)
    return file_list

def upload_table(dataset, file_list, common_items, if_replace):
    """ Upload the datasets in file_list to Redivis """
    print(f"\nUploading '{file_list}' to Redivis. \n")
    count = 0
    total_file = len(file_list)
    for file in file_list:
        count+=1
        file_path = file.split('/')[-1]
        file_name = file_path.split('.')[0]
        table = None
        # If this is a new table, create one on Redivis.
        if file_path not in common_items:
            table = (
                dataset
                .table(file_name) # Get the file name without type
                .create()
            )
        else:
            table = dataset.table(file_name)
        upload = table.upload(file_name)

        # Upload the dataset
        with open(file, "rb") as f:
            upload.create(
                f, 
                type="delimited",
                remove_on_fail=True,    # Remove the upload if a failure occurs
                wait_for_finish=True,   # Wait for the upload to finish processing
                raise_on_fail=True,      # Raise an error on failure
                replace_on_conflict=if_replace
            )
        print(f"'{file}' has been uploaded. {count} / {total_file}")

def check_if_table_already_exist(dataset, file_list):
    """Check if the datasets are already on Redivis and ask wether to replace them"""
    tables = dataset.list_tables()
    processed_df = []
    for table in tables:
        table.get()
        # Properties will now contain the table.get API representation
        processed_df.append(table.properties["name"])
    processed_df_csv = [x +".csv" for x in processed_df]
    file_list_temp = [x.split('/')[-1] for x in file_list]
    common_items = list(set(processed_df_csv) & set(file_list_temp))

    if_replace = False
    # Examine if there are already-uploaded datasets
    if len(common_items) > 0:
        while True:
            user_input = input(f"'{common_items}' have already been included in the IRW. Do you want to update them?(y/n)").lower()
            if user_input == 'y':
                if_replace = True
                break
            elif user_input == 'n':
                if_replace = False
                break
            else:
                print(f"Invalid input. Please try again.\n")

    file_list = [item for item in file_list if item.split('/')[-1] not in common_items] if if_replace == False else file_list
    if len(file_list) == 0:
        print("All specified tables have been uploaded to IRW. Exiting")
        sys.exit(1)
    return file_list, common_items, if_replace

def main():
    set_working_directory_to_current()
    file_list = parse_table()

    load_dotenv()
    TOKEN = os.getenv("REDIVIS_API_TOKEN")

    if not TOKEN:
        print("Error: REDIVIS_API_TOKEN is not set in the .env file.")
        sys.exit(1)

    # Authenticate with Redivis
    redivis.authenticate()

    # Set API in terminal as: export REDIVIS_API_TOKEN=your_access_token
    dataset = redivis.user("bdomingu").dataset("IRW_text",version="next")
    file_list, common_items, if_replace = check_if_table_already_exist(dataset, file_list)
    upload_table(dataset, file_list, common_items, if_replace)

if __name__ == "__main__":
    main()
