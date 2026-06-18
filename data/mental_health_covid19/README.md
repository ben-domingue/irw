Chen 2022 Mental Health Dataset

This folder contains processing documentation for the Chen et al. 2022 mental health dataset from Science Data Bank.

Source

Dataset: Mental health dataset of college students during COVID-19
Source: Science Data Bank
DOI: 10.57760/sciencedb.000115.00089
Original license: CC BY-NC 4.0

Processed output files

Following Ben’s suggestion, the dataset is split into three construct-specific long-format tables:

* chen_2022_sasc.csv: SASC item responses
* chen_2022_cesd.csv: CESD-10 item responses
* chen_2022_gad.csv: GAD-7 item responses

Each table is in long format, with one row per participant-item response. Person-level covariates are included in each table using the cov_ prefix.

Output dimensions

* chen_2022_sasc.csv: 1,698,642 rows × 12 columns
* chen_2022_cesd.csv: 772,110 rows × 12 columns
* chen_2022_gad.csv: 540,477 rows × 12 columns

These correspond to:

* 77,211 participants × 22 SASC items
* 77,211 participants × 10 CESD-10 items
* 77,211 participants × 7 GAD-7 items

Processing script

The processing script is:

process_chen_2022_mental_health.R

The script:

* reads the original SPSS .sav file;
* removes SPSS value labels before reshaping;
* keeps person-level covariates in the main tables using the cov_ prefix;
* reshapes item responses into long format with item and resp columns;
* generates three construct-specific output tables for SASC, CESD-10, and GAD-7.

Notes

The processed CSV files are too large to upload directly through GitHub, so they were shared with Ben via Google Drive.
