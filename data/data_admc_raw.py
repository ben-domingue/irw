from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_admc_raw.csv'
TASK_NAME = 'admc_raw'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'admc_id', 'resp_col': 'admc_response'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
