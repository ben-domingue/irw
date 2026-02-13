from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_number_series.csv'
TASK_NAME = 'number_series'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'ns_id', 'resp_col': 'correct'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
