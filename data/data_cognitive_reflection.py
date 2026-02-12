from fpt_common import convert_item_based_task

CSV_FILENAME = 'data_cognitive_reflection.csv'
TASK_NAME = 'cognitive_reflection'
CONVERTER = convert_item_based_task
KWARGS = {'item_prefix': 'crt_correct_', 'use_correct': True}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
