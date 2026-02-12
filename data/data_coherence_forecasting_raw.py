from fpt_common import convert_trial_based_task

CSV_FILENAME = 'data_coherence_forecasting_raw.csv'
TASK_NAME = 'coherence_forecasting_raw'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'trial', 'resp_col': 'response'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
