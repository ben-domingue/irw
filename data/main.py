import pandas as pd
import os
import importlib

from fpt_common import (
    load_session_metadata,
    load_aig_version_metadata,
    convert_berlin_numeracy,
    convert_trial_based_task,
    convert_item_based_task,
    convert_scores_dataset,
    convert_admc_scores,
    post_process_and_save,
)

TASK_MODULES = [
    'data_berlin_numeracy',
    'data_raven',
    'data_number_series',
    'data_impossible_question',
    'data_cognitive_reflection',
    'data_bayesian_update',
    'data_denominator_neglect',
    'data_leapfrog',
    'data_admc_raw',
    'data_graph_literacy_raw',
    'data_coherence_forecasting_raw',
    'data_shipley_abstraction',
    'data_shipley_vocabulary',
]


def _get_task_configs():
    configs = []
    for modname in TASK_MODULES:
        try:
            mod = importlib.import_module(modname)
            configs.append(mod.CONFIG)
        except Exception as e:
            print(f"Warning: Could not load {modname}: {e}")
    return configs


def convert_fpt_to_irw():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    task_dir = os.path.join(script_dir, 'task_datasets')
    output_dir = os.path.join(script_dir, 'irw_format')

    session_meta = load_session_metadata()
    aig_meta = load_aig_version_metadata()
    task_configs = _get_task_configs()

    all_data = []
    for (filename, task_name, converter, kwargs) in task_configs:
        filepath = os.path.join(task_dir, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename} - file not found")
            continue

        print(f"\nProcessing {filename}...")
        try:
            df = pd.read_csv(filepath)
            print(f"  Loaded {len(df)} rows")

            kwargs = kwargs or {}
            if converter == convert_berlin_numeracy:
                df_irw = converter(df, session_meta, aig_meta)
            elif converter == convert_admc_scores:
                df_irw = converter(df, session_meta, aig_meta)
            elif converter == convert_trial_based_task:
                df_irw = converter(df, session_meta, task_name, aig_meta=aig_meta, **kwargs)
            elif converter == convert_item_based_task:
                df_irw = converter(df, session_meta, task_name, aig_meta=aig_meta, **kwargs)
            elif converter == convert_scores_dataset:
                df_irw = converter(df, session_meta, task_name, aig_meta=aig_meta, **kwargs)
            else:
                continue

            if df_irw is not None:
                all_data.append(df_irw)
                print(f"  Converted to {len(df_irw)} rows")
            else:
                print(f"  Conversion failed")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()

    if all_data:
        os.makedirs(output_dir, exist_ok=True)
        for df_task in all_data:
            post_process_and_save(df_task, output_dir)
        print(f"\n\nConversion complete!")
        print(f"Created {len(all_data)} IRW format files in {output_dir}/")
        return all_data
    else:
        print("No data converted!")
        return None


if __name__ == '__main__':
    convert_fpt_to_irw()
