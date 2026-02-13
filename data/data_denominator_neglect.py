from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_denominator_neglect.csv'
TASK_NAME = 'denominator_neglect'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'trial', 'resp_col': 'correct'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
