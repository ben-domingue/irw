from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_bayesian_update.csv'
TASK_NAME = 'bayesian_update'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'unique_trial', 'resp_col': 'score'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
