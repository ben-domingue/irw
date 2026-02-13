from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_raven.csv'
TASK_NAME = 'raven'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'stimulus', 'resp_col': 'correct'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
