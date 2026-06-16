# Mental health dataset of college students during COVID-19

## Source

Repository: Science Data Bank

Dataset title: Mental health dataset of college students during COVID-19

DOI: 10.57760/sciencedb.000115.00089

License: CC BY-NC 4.0

Authors: Yaru Chen, Qisheng Zhang, Zhengkui Liu

Published: 2022-10-12

Survey period: April 13–23, 2020

## Sample

The dataset contains responses from 77,211 Chinese college students during the COVID-19 period.

## Measures

The dataset includes item-level responses from three psychological scales:

- Smartphone Addiction Scale for College Students (SAS-C): SASC01–SASC22
- Center for Epidemiological Studies Depression Scale, 10-item version (CES-D-10): CESD01–CESD10
- Generalized Anxiety Disorder Scale (GAD-7): GAD01–GAD07

## IRW standardization

The original dataset was distributed as an SPSS `.sav` file. I converted the file using R `haven::read_sav()`, reshaped the item-level responses into long format, and standardized the output according to the IRW data standard.

The IRW-standard item response file uses the following columns:

- `id`: anonymous respondent identifier
- `item`: item identifier
- `resp`: numeric item response
- `item_family`: scale membership, including SAS-C, CES-D-10, and GAD-7

Person-level covariates are stored separately using the `cov_` prefix.

## Processed outputs

The local processed files include:

- `irw_standard_responses.csv`: IRW-standard item response file with `id`, `item`, `resp`, and `item_family`
- `irw_standard_covariates.csv`: person-level covariates using the `cov_` prefix
- `irw_standard_item_summary.csv`: item-level response range and missingness
- `codebook_variables.csv`: variable labels from the original SPSS file
- `codebook_value_labels.csv`: value labels from the original SPSS file
- `scale_missing_summary.csv`: missingness summary by scale
- `process_mental_health_covid19.R`: reproducible R processing script

## Notes

This dataset appears suitable for IRW because it contains clear item-level responses from three psychological scales in a large Chinese college student sample.

The main IRW-ready file is `irw_standard_responses.csv`.
