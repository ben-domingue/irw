from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_impossible_question.csv'
TASK_NAME = 'impossible_question'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'id', 'resp_col': 'correct'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
