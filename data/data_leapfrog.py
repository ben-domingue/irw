from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_leapfrog.csv'
TASK_NAME = 'leapfrog'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'trial', 'resp_col': 'optimal_choice'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
