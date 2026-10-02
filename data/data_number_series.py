from fpt_common import convert_trial_based_task

# NS_6 ("200, 198, 192, 174, ___"): FRI's key is 165 (main + pilot files), but the
# differences 2, 6, 18 imply 120; only 1.1% of respondents match 165 (modal answers
# 150 and 120). We keep the source scoring on purpose (irw#2513, decided 2026-09-28);
# the typed answer belongs in resp_raw so users can rescore.
CSV_FILENAME = 'data_number_series.csv'
TASK_NAME = 'number_series'
CONVERTER = convert_trial_based_task
KWARGS = {'item_col': 'ns_id', 'resp_col': 'correct'}

CONFIG = (CSV_FILENAME, TASK_NAME, CONVERTER, KWARGS)
