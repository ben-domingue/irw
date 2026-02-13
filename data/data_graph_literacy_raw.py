from fpt_common import convert_item_based_task

CSV_FILENAME = 'data_graph_literacy_raw.csv'
TASK_NAME = 'graph_literacy_raw'
CONVERTER = convert_item_based_task
KWARGS = {'item_prefix': 'Q'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
