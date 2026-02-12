from fpt_common import convert_item_based_task

CSV_FILENAME = 'data_shipley_vocabulary.csv'
TASK_NAME = 'shipley_vocabulary'
CONVERTER = convert_item_based_task
KWARGS = {'item_prefix': 'shipley_vocab_'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
