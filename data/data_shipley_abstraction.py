from fpt_common import convert_item_based_task

CSV_FILENAME = 'data_shipley_abstraction.csv'
TASK_NAME = 'shipley_abstraction'
CONVERTER = convert_item_based_task
KWARGS = {'item_prefix': 'shipley_abstraction_'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
