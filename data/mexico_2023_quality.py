"""mexico_2023_quality_*: INEGI ENCIG 2023 and ENCIG 2021 (Encuesta Nacional de Calidad e Impacto Gubernamental).

Replaces data/mexico_2023_quality.do (irw#2415). The .do appended ENCIG 2021 under 2023 BY VARIABLE NAME, but
INEGI renumbered questions between the waves (2023 inserted 5.7 IMSS-Bienestar and 5.11 Cablebus/Mexicable, renamed
section A, and zero-padded several item numbers), so several tables pooled answers to different questions under one
code, and 2021 answers whose names changed were silently dropped. This script renames each 2021 variable to the 2023
variable that asks the same question (RENAME_2021, built from both official questionnaires and checked pair by pair
on value distributions; evidence in oneoff/mexico-2415/map_notes.md) before stacking the waves, and records the wave
as cov_year. ENCIG waves are independent cross-sections (different people), so this is a covariate, not `wave`.

The 2023 rows are identical to the tables the .do produced (verified cell for cell against the live Redivis tables),
as are the ids of every row. Tables asked only in 2023 (wellbeingservice = IMSS-Bienestar, cablecars) carry 2023 rows
only. Transforms per table are the .do's: yes/no items recoded 1->0, 2->1; codes 9, 98, 99 set to missing.

Inputs (INEGI open data, CSV release) in the working directory:
  encig{2023,2021}_02_residentes_sec_2.csv, encig{2023,2021}_01_sec1_A_3_4_5_8_9_10.csv, encig{2023,2021}_01_sec_11.csv
Output: one CSV per table in BLOCKS, in the working directory.
"""
import numpy as np
import pandas as pd

# 2021 name -> 2023 name for every 2021 variable that asks a 2023 table item under a different name (irw#2415)
RENAME_2021 = {'apa_1_1': 'a1_1',
 'apa_1_2': 'a1_2',
 'apa_1_3': 'a1_3',
 'apa_1_4': 'a1_4',
 'apa_1_5': 'a1_5',
 'apa_1_6': 'a1_6',
 'apa_1_7': 'a1_7',
 'p11_1_1': 'p11_1_01',
 'p11_1_2': 'p11_1_02',
 'p11_1_3': 'p11_1_03',
 'p11_1_4': 'p11_1_04',
 'p11_1_5': 'p11_1_05',
 'p11_1_6': 'p11_1_06',
 'p11_1_7': 'p11_1_07',
 'p11_1_8': 'p11_1_08',
 'p11_1_9': 'p11_1_09',
 'p3_1_1': 'p3_1_01',
 'p3_1_2': 'p3_1_02',
 'p3_1_3': 'p3_1_03',
 'p3_1_4': 'p3_1_04',
 'p3_1_5': 'p3_1_05',
 'p3_1_6': 'p3_1_06',
 'p3_1_7': 'p3_1_07',
 'p3_1_8': 'p3_1_08',
 'p3_1_9': 'p3_1_09',
 'p3_3_1': 'p3_3_01',
 'p3_3_2': 'p3_3_02',
 'p3_3_3': 'p3_3_03',
 'p3_3_4': 'p3_3_04',
 'p3_3_5': 'p3_3_05',
 'p3_3_6': 'p3_3_06',
 'p3_3_7': 'p3_3_07',
 'p3_3_8': 'p3_3_08',
 'p3_3_9': 'p3_3_09',
 'p5_10_1': 'p5_12_1',
 'p5_10_2': 'p5_12_2',
 'p5_10_3': 'p5_12_3',
 'p5_10_4': 'p5_12_4',
 'p5_10_5': 'p5_12_5',
 'p5_10a': 'p5_12a',
 'p5_11_1': 'p5_13_1',
 'p5_11_2': 'p5_13_2',
 'p5_11_3': 'p5_13_3',
 'p5_11_4': 'p5_13_4',
 'p5_11_5': 'p5_13_5',
 'p5_11a': 'p5_13a',
 'p5_1_1': 'p5_1_01',
 'p5_1_10': 'p5_1_12',
 'p5_1_2': 'p5_1_02',
 'p5_1_3': 'p5_1_03',
 'p5_1_4': 'p5_1_04',
 'p5_1_5': 'p5_1_05',
 'p5_1_6': 'p5_1_07',
 'p5_1_7': 'p5_1_08',
 'p5_1_8': 'p5_1_09',
 'p5_1_9': 'p5_1_11',
 'p5_4_1': 'p5_4_01',
 'p5_4_2': 'p5_4_02',
 'p5_4_3': 'p5_4_03',
 'p5_4_4': 'p5_4_04',
 'p5_4_5': 'p5_4_05',
 'p5_4_6': 'p5_4_06',
 'p5_4_7': 'p5_4_07',
 'p5_4_8': 'p5_4_08',
 'p5_4_9': 'p5_4_09',
 'p5_5_1': 'p5_5_01',
 'p5_5_2': 'p5_5_02',
 'p5_5_3': 'p5_5_03',
 'p5_5_4': 'p5_5_04',
 'p5_5_5': 'p5_5_05',
 'p5_5_6': 'p5_5_06',
 'p5_5_7': 'p5_5_07',
 'p5_5_8': 'p5_5_08',
 'p5_5_9': 'p5_5_09',
 'p5_6_1': 'p5_6_01',
 'p5_6_2': 'p5_6_02',
 'p5_6_3': 'p5_6_03',
 'p5_6_4': 'p5_6_04',
 'p5_6_5': 'p5_6_05',
 'p5_6_6': 'p5_6_06',
 'p5_6_7': 'p5_6_07',
 'p5_6_8': 'p5_6_08',
 'p5_6_9': 'p5_6_09',
 'p5_7_1': 'p5_8_1',
 'p5_7_2': 'p5_8_2',
 'p5_7_3': 'p5_8_3',
 'p5_7a': 'p5_8a',
 'p5_8_1': 'p5_9_1',
 'p5_8_2': 'p5_9_2',
 'p5_8_3': 'p5_9_3',
 'p5_8_4': 'p5_9_4',
 'p5_8_5': 'p5_9_5',
 'p5_8_6': 'p5_9_6',
 'p5_8_7': 'p5_9_7',
 'p5_8_8': 'p5_9_8',
 'p5_8a': 'p5_9a',
 'p5_9_1': 'p5_10_1',
 'p5_9_2': 'p5_10_2',
 'p5_9_3': 'p5_10_3',
 'p5_9_4': 'p5_10_4',
 'p5_9_5': 'p5_10_5',
 'p5_9_6': 'p5_10_6',
 'p5_9_7': 'p5_10_7',
 'p5_9_8': 'p5_10_8',
 'p5_9a': 'p5_10a'}

# 2023 item names that have a 2021 counterpart (a table none of whose items is here is 2023-only)
ASKED_2021 = ['a1_1', 'a1_2', 'a1_3', 'a1_4', 'a1_5', 'a1_6', 'a1_7', 'p10_1_1', 'p10_1_2', 'p10_1_3', 'p10_1_4',
 'p10_1_5', 'p10_1_6', 'p11_1_01', 'p11_1_02', 'p11_1_03', 'p11_1_04', 'p11_1_05', 'p11_1_06', 'p11_1_07',
 'p11_1_08', 'p11_1_09', 'p11_1_10', 'p11_1_11', 'p11_1_12', 'p11_1_13', 'p11_1_14', 'p11_1_15', 'p11_1_16',
 'p11_1_17', 'p11_1_18', 'p11_1_19', 'p11_1_20', 'p11_1_21', 'p11_1_22', 'p11_1_23', 'p11_1_24', 'p11_1_25',
 'p3_1_01', 'p3_1_02', 'p3_1_03', 'p3_1_04', 'p3_1_05', 'p3_1_06', 'p3_1_07', 'p3_1_08', 'p3_1_09', 'p3_1_10',
 'p3_1_11', 'p3_1_99', 'p3_2', 'p3_3_01', 'p3_3_02', 'p3_3_03', 'p3_3_04', 'p3_3_05', 'p3_3_06', 'p3_3_07',
 'p3_3_08', 'p3_3_09', 'p3_3_10', 'p3_3_11', 'p3_3_12', 'p3_3_13', 'p3_3_14', 'p3_3_15', 'p3_3_16', 'p3_3_17',
 'p3_3_18', 'p3_3_19', 'p3_3_20', 'p3_3_21', 'p3_3_22', 'p3_3_23', 'p3_3_24', 'p4_1_1', 'p4_1_2', 'p4_1_3',
 'p4_1_4', 'p4_1_5', 'p4_1_6', 'p4_1_7', 'p4_1a', 'p4_2_1', 'p4_2_2', 'p4_2_3', 'p4_2_4', 'p4_2a', 'p4_3_1',
 'p4_3_2', 'p4_3_3', 'p4_3a', 'p4_4_1', 'p4_4_2', 'p4_4_3', 'p4_4_4', 'p4_4a', 'p4_5_1', 'p4_5_2', 'p4_5_3',
 'p4_5a', 'p4_6_1', 'p4_6_2', 'p4_6a', 'p4_7_1', 'p4_7_2', 'p4_7_3', 'p4_7_4', 'p4_7a', 'p4_8_1', 'p4_8_2',
 'p4_8_3', 'p4_8_4', 'p4_8a', 'p5_10_1', 'p5_10_2', 'p5_10_3', 'p5_10_4', 'p5_10_5', 'p5_10_6', 'p5_10_7',
 'p5_10_8', 'p5_10a', 'p5_12_1', 'p5_12_2', 'p5_12_3', 'p5_12_4', 'p5_12_5', 'p5_12a', 'p5_13_1', 'p5_13_2',
 'p5_13_3', 'p5_13_4', 'p5_13_5', 'p5_13a', 'p5_1_01', 'p5_1_02', 'p5_1_03', 'p5_1_04', 'p5_1_05', 'p5_1_07',
 'p5_1_08', 'p5_1_09', 'p5_1_11', 'p5_1_12', 'p5_2_1', 'p5_2_2', 'p5_2_3', 'p5_2_4', 'p5_2_5', 'p5_2_6',
 'p5_2_7', 'p5_2_8', 'p5_2_9', 'p5_2a', 'p5_3_1', 'p5_3_2', 'p5_3_3', 'p5_3_4', 'p5_3_5', 'p5_3_6', 'p5_3_7',
 'p5_3_8', 'p5_3a', 'p5_4_01', 'p5_4_02', 'p5_4_03', 'p5_4_04', 'p5_4_05', 'p5_4_06', 'p5_4_07', 'p5_4_08',
 'p5_4_09', 'p5_4_10', 'p5_4_11', 'p5_4a', 'p5_5_01', 'p5_5_02', 'p5_5_03', 'p5_5_04', 'p5_5_05', 'p5_5_06',
 'p5_5_07', 'p5_5_08', 'p5_5_09', 'p5_5_10', 'p5_5_11', 'p5_5a', 'p5_6_01', 'p5_6_02', 'p5_6_03', 'p5_6_04',
 'p5_6_05', 'p5_6_06', 'p5_6_07', 'p5_6_08', 'p5_6_09', 'p5_6_10', 'p5_6_11', 'p5_6a', 'p5_8_1', 'p5_8_2',
 'p5_8_3', 'p5_8a', 'p5_9_1', 'p5_9_2', 'p5_9_3', 'p5_9_4', 'p5_9_5', 'p5_9_6', 'p5_9_7', 'p5_9_8', 'p5_9a',
 'p8_1', 'p8_2', 'p8_3_1', 'p8_3_2', 'p8_3_3', 'p9_1', 'p9_7']

# every 2023 item used by a table: a 2021 column carrying one of these names that is not itself a rename target
# asks a DIFFERENT question in 2021 and is dropped before stacking
ITEMS_2023 = ['a1_1', 'a1_2', 'a1_3', 'a1_4', 'a1_5', 'a1_6', 'a1_7', 'p10_1_1', 'p10_1_2', 'p10_1_3', 'p10_1_4',
 'p10_1_5', 'p10_1_6', 'p11_1_01', 'p11_1_02', 'p11_1_03', 'p11_1_04', 'p11_1_05', 'p11_1_06', 'p11_1_07',
 'p11_1_08', 'p11_1_09', 'p11_1_10', 'p11_1_11', 'p11_1_12', 'p11_1_13', 'p11_1_14', 'p11_1_15', 'p11_1_16',
 'p11_1_17', 'p11_1_18', 'p11_1_19', 'p11_1_20', 'p11_1_21', 'p11_1_22', 'p11_1_23', 'p11_1_24', 'p11_1_25',
 'p3_1_01', 'p3_1_02', 'p3_1_03', 'p3_1_04', 'p3_1_05', 'p3_1_06', 'p3_1_07', 'p3_1_08', 'p3_1_09', 'p3_1_10',
 'p3_1_11', 'p3_1_99', 'p3_2', 'p3_3_01', 'p3_3_02', 'p3_3_03', 'p3_3_04', 'p3_3_05', 'p3_3_06', 'p3_3_07',
 'p3_3_08', 'p3_3_09', 'p3_3_10', 'p3_3_11', 'p3_3_12', 'p3_3_13', 'p3_3_14', 'p3_3_15', 'p3_3_16', 'p3_3_17',
 'p3_3_18', 'p3_3_19', 'p3_3_20', 'p3_3_21', 'p3_3_22', 'p3_3_23', 'p3_3_24', 'p4_1_1', 'p4_1_2', 'p4_1_3',
 'p4_1_4', 'p4_1_5', 'p4_1_6', 'p4_1_7', 'p4_1a', 'p4_2_1', 'p4_2_2', 'p4_2_3', 'p4_2_4', 'p4_2a', 'p4_3_1',
 'p4_3_2', 'p4_3_3', 'p4_3a', 'p4_4_1', 'p4_4_2', 'p4_4_3', 'p4_4_4', 'p4_4a', 'p4_5_1', 'p4_5_2', 'p4_5_3',
 'p4_5a', 'p4_6_1', 'p4_6_2', 'p4_6a', 'p4_7_1', 'p4_7_2', 'p4_7_3', 'p4_7_4', 'p4_7a', 'p4_8_1', 'p4_8_2',
 'p4_8_3', 'p4_8_4', 'p4_8a', 'p5_10_1', 'p5_10_2', 'p5_10_3', 'p5_10_4', 'p5_10_5', 'p5_10_6', 'p5_10_7',
 'p5_10_8', 'p5_10a', 'p5_11_1', 'p5_11_2', 'p5_11_3', 'p5_11_4', 'p5_11_5', 'p5_11_6', 'p5_11_7', 'p5_11_8',
 'p5_11a', 'p5_12_1', 'p5_12_2', 'p5_12_3', 'p5_12_4', 'p5_12_5', 'p5_12a', 'p5_13_1', 'p5_13_2', 'p5_13_3',
 'p5_13_4', 'p5_13_5', 'p5_13a', 'p5_1_01', 'p5_1_02', 'p5_1_03', 'p5_1_04', 'p5_1_05', 'p5_1_06', 'p5_1_07',
 'p5_1_08', 'p5_1_09', 'p5_1_10', 'p5_1_11', 'p5_1_12', 'p5_2_1', 'p5_2_2', 'p5_2_3', 'p5_2_4', 'p5_2_5',
 'p5_2_6', 'p5_2_7', 'p5_2_8', 'p5_2_9', 'p5_2a', 'p5_3_1', 'p5_3_2', 'p5_3_3', 'p5_3_4', 'p5_3_5', 'p5_3_6',
 'p5_3_7', 'p5_3_8', 'p5_3a', 'p5_4_01', 'p5_4_02', 'p5_4_03', 'p5_4_04', 'p5_4_05', 'p5_4_06', 'p5_4_07',
 'p5_4_08', 'p5_4_09', 'p5_4_10', 'p5_4_11', 'p5_4a', 'p5_5_01', 'p5_5_02', 'p5_5_03', 'p5_5_04', 'p5_5_05',
 'p5_5_06', 'p5_5_07', 'p5_5_08', 'p5_5_09', 'p5_5_10', 'p5_5_11', 'p5_5a', 'p5_6_01', 'p5_6_02', 'p5_6_03',
 'p5_6_04', 'p5_6_05', 'p5_6_06', 'p5_6_07', 'p5_6_08', 'p5_6_09', 'p5_6_10', 'p5_6_11', 'p5_6a', 'p5_7_01',
 'p5_7_02', 'p5_7_03', 'p5_7_04', 'p5_7_05', 'p5_7_06', 'p5_7_07', 'p5_7_08', 'p5_7_09', 'p5_7_10', 'p5_7_11',
 'p5_7a', 'p5_8_1', 'p5_8_2', 'p5_8_3', 'p5_8a', 'p5_9_1', 'p5_9_2', 'p5_9_3', 'p5_9_4', 'p5_9_5', 'p5_9_6',
 'p5_9_7', 'p5_9_8', 'p5_9a', 'p8_1', 'p8_2', 'p8_3_1', 'p8_3_2', 'p8_3_3', 'p9_1', 'p9_7']

BLOCKS = [{'table': 'mexico_2023_quality_administration',
  'items': ['a1_1', 'a1_2', 'a1_3', 'a1_4', 'a1_5', 'a1_6', 'a1_7'],
  'destring': [],
  'destring_all': False,
  'yesno': [],
  'missing': [98, 99]},
 {'table': 'mexico_2023_quality_problems',
  'items': ['p3_1_01', 'p3_1_02', 'p3_1_03', 'p3_1_04', 'p3_1_05', 'p3_1_06', 'p3_1_07', 'p3_1_08', 'p3_1_09',
            'p3_1_10', 'p3_1_11', 'p3_1_99'],
  'destring': [],
  'destring_all': False,
  'yesno': [],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_corruptionperception',
  'items': ['p3_2', 'p3_3_01', 'p3_3_02', 'p3_3_03', 'p3_3_04', 'p3_3_05', 'p3_3_06', 'p3_3_07', 'p3_3_08',
            'p3_3_09', 'p3_3_10', 'p3_3_11', 'p3_3_12', 'p3_3_13', 'p3_3_14', 'p3_3_15', 'p3_3_16', 'p3_3_17',
            'p3_3_18', 'p3_3_19', 'p3_3_20', 'p3_3_21', 'p3_3_22', 'p3_3_23', 'p3_3_24'],
  'destring': [],
  'destring_all': False,
  'yesno': [],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_water',
  'items': ['p4_1_1', 'p4_1_2', 'p4_1_3', 'p4_1_4', 'p4_1_5', 'p4_1_6', 'p4_1_7', 'p4_1a'],
  'destring': ['p4_1a'],
  'destring_all': False,
  'yesno': ['p4_1_1', 'p4_1_2', 'p4_1_3', 'p4_1_4', 'p4_1_5', 'p4_1_6', 'p4_1_7'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_drainage',
  'items': ['p4_2_1', 'p4_2_2', 'p4_2_3', 'p4_2_4', 'p4_2a'],
  'destring': ['p4_2a'],
  'destring_all': False,
  'yesno': ['p4_2_1', 'p4_2_2', 'p4_2_3', 'p4_2_4'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_lightning',
  'items': ['p4_3_1', 'p4_3_2', 'p4_3_3', 'p4_3a'],
  'destring': ['p4_3a'],
  'destring_all': False,
  'yesno': ['p4_3_1', 'p4_3_2', 'p4_3_3'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_parks',
  'items': ['p4_4_1', 'p4_4_2', 'p4_4_3', 'p4_4_4', 'p4_4a'],
  'destring': ['p4_4a'],
  'destring_all': False,
  'yesno': ['p4_4_1', 'p4_4_2', 'p4_4_3', 'p4_4_4'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_trash',
  'items': ['p4_5_1', 'p4_5_2', 'p4_5_3', 'p4_5a'],
  'destring': ['p4_5a'],
  'destring_all': False,
  'yesno': ['p4_5_1', 'p4_5_2', 'p4_5_3'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_police',
  'items': ['p4_6_1', 'p4_6_2', 'p4_6a'],
  'destring': ['p4_6a'],
  'destring_all': False,
  'yesno': ['p4_6_1', 'p4_6_2'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_roads',
  'items': ['p4_7_1', 'p4_7_2', 'p4_7_3', 'p4_7_4', 'p4_7a'],
  'destring': ['p4_7a'],
  'destring_all': False,
  'yesno': ['p4_7_1', 'p4_7_2', 'p4_7_3', 'p4_7_4'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_streets',
  'items': ['p4_8_1', 'p4_8_2', 'p4_8_3', 'p4_8_4', 'p4_8a'],
  'destring': ['p4_8a'],
  'destring_all': False,
  'yesno': ['p4_8_1', 'p4_8_2', 'p4_8_3', 'p4_8_4'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_low',
  'items': ['p5_1_01', 'p5_1_02', 'p5_1_03', 'p5_1_04', 'p5_1_05', 'p5_1_06', 'p5_1_07', 'p5_1_08', 'p5_1_09',
            'p5_1_10', 'p5_1_11', 'p5_1_12'],
  'destring': ['p5_1_09', 'p5_1_10', 'p5_1_11'],
  'destring_all': False,
  'yesno': ['p5_1_01', 'p5_1_02', 'p5_1_03', 'p5_1_04', 'p5_1_05', 'p5_1_06', 'p5_1_07', 'p5_1_08', 'p5_1_09',
            'p5_1_10', 'p5_1_11', 'p5_1_12'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_schooling',
  'items': ['p5_2_1', 'p5_2_2', 'p5_2_3', 'p5_2_4', 'p5_2_5', 'p5_2_6', 'p5_2_7', 'p5_2_8', 'p5_2_9',
            'p5_2a'],
  'destring': ['p5_2_1', 'p5_2_2', 'p5_2_3', 'p5_2_4', 'p5_2_5', 'p5_2_6', 'p5_2_7', 'p5_2_8', 'p5_2_9',
               'p5_2a'],
  'destring_all': True,
  'yesno': ['p5_2_1', 'p5_2_2', 'p5_2_3', 'p5_2_4', 'p5_2_5', 'p5_2_6', 'p5_2_7', 'p5_2_8', 'p5_2_9'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_university',
  'items': ['p5_3_1', 'p5_3_2', 'p5_3_3', 'p5_3_4', 'p5_3_5', 'p5_3_6', 'p5_3_7', 'p5_3_8', 'p5_3a'],
  'destring': ['p5_3_1', 'p5_3_2', 'p5_3_3', 'p5_3_4', 'p5_3_5', 'p5_3_6', 'p5_3_7', 'p5_3_8', 'p5_3a'],
  'destring_all': True,
  'yesno': ['p5_3_1', 'p5_3_2', 'p5_3_3', 'p5_3_4', 'p5_3_5', 'p5_3_6', 'p5_3_7', 'p5_3_8'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_health',
  'items': ['p5_4_01', 'p5_4_02', 'p5_4_03', 'p5_4_04', 'p5_4_05', 'p5_4_06', 'p5_4_07', 'p5_4_08', 'p5_4_09',
            'p5_4_10', 'p5_4_11', 'p5_4a'],
  'destring': ['p5_4_01', 'p5_4_02', 'p5_4_03', 'p5_4_04', 'p5_4_05', 'p5_4_06', 'p5_4_07', 'p5_4_08',
               'p5_4_09', 'p5_4_10', 'p5_4_11'],
  'destring_all': True,
  'yesno': ['p5_4_01', 'p5_4_02', 'p5_4_03', 'p5_4_04', 'p5_4_05', 'p5_4_06', 'p5_4_07', 'p5_4_08', 'p5_4_09',
            'p5_4_10', 'p5_4_11'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_wellbeing',
  'items': ['p5_5_01', 'p5_5_02', 'p5_5_03', 'p5_5_04', 'p5_5_05', 'p5_5_06', 'p5_5_07', 'p5_5_08', 'p5_5_09',
            'p5_5_10', 'p5_5_11', 'p5_5a'],
  'destring': ['p5_5_01', 'p5_5_02', 'p5_5_03', 'p5_5_04', 'p5_5_05', 'p5_5_06', 'p5_5_07', 'p5_5_08',
               'p5_5_09', 'p5_5_10', 'p5_5_11'],
  'destring_all': True,
  'yesno': ['p5_5_01', 'p5_5_02', 'p5_5_03', 'p5_5_04', 'p5_5_05', 'p5_5_06', 'p5_5_07', 'p5_5_08', 'p5_5_09',
            'p5_5_10', 'p5_5_11'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_healthservice',
  'items': ['p5_6_01', 'p5_6_02', 'p5_6_03', 'p5_6_04', 'p5_6_05', 'p5_6_06', 'p5_6_07', 'p5_6_08', 'p5_6_09',
            'p5_6_10', 'p5_6_11', 'p5_6a'],
  'destring': ['p5_6_01', 'p5_6_02', 'p5_6_03', 'p5_6_04', 'p5_6_05', 'p5_6_06', 'p5_6_07', 'p5_6_08',
               'p5_6_09', 'p5_6_10', 'p5_6_11'],
  'destring_all': True,
  'yesno': ['p5_6_01', 'p5_6_02', 'p5_6_03', 'p5_6_04', 'p5_6_05', 'p5_6_06', 'p5_6_07', 'p5_6_08', 'p5_6_09',
            'p5_6_10', 'p5_6_11'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_wellbeingservice',
  'items': ['p5_7_01', 'p5_7_02', 'p5_7_03', 'p5_7_04', 'p5_7_05', 'p5_7_06', 'p5_7_07', 'p5_7_08', 'p5_7_09',
            'p5_7_10', 'p5_7_11', 'p5_7a'],
  'destring': ['p5_7_01', 'p5_7_02', 'p5_7_03', 'p5_7_04', 'p5_7_05', 'p5_7_06', 'p5_7_07', 'p5_7_08',
               'p5_7_09', 'p5_7_10', 'p5_7_11'],
  'destring_all': True,
  'yesno': ['p5_7_01', 'p5_7_02', 'p5_7_03', 'p5_7_04', 'p5_7_05', 'p5_7_06', 'p5_7_07', 'p5_7_08', 'p5_7_09',
            'p5_7_10', 'p5_7_11'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_homelightning',
  'items': ['p5_8_1', 'p5_8_2', 'p5_8_3', 'p5_8a'],
  'destring': ['p5_8_1', 'p5_8_2', 'p5_8_3'],
  'destring_all': True,
  'yesno': ['p5_8_1', 'p5_8_2', 'p5_8_3'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_buses',
  'items': ['p5_9_1', 'p5_9_2', 'p5_9_3', 'p5_9_4', 'p5_9_5', 'p5_9_6', 'p5_9_7', 'p5_9_8', 'p5_9a'],
  'destring': ['p5_9_1', 'p5_9_2', 'p5_9_3', 'p5_9_4', 'p5_9_5', 'p5_9_6', 'p5_9_7', 'p5_9_8'],
  'destring_all': True,
  'yesno': ['p5_9_1', 'p5_9_2', 'p5_9_3', 'p5_9_4', 'p5_9_5', 'p5_9_6', 'p5_9_7', 'p5_9_8'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_transportationstations',
  'items': ['p5_10_1', 'p5_10_2', 'p5_10_3', 'p5_10_4', 'p5_10_5', 'p5_10_6', 'p5_10_7', 'p5_10_8', 'p5_10a'],
  'destring': ['p5_10_1', 'p5_10_2', 'p5_10_3', 'p5_10_4', 'p5_10_5', 'p5_10_6', 'p5_10_7', 'p5_10_8'],
  'destring_all': True,
  'yesno': ['p5_10_1', 'p5_10_2', 'p5_10_3', 'p5_10_4', 'p5_10_5', 'p5_10_6', 'p5_10_7', 'p5_10_8'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_cablecars',
  'items': ['p5_11_1', 'p5_11_2', 'p5_11_3', 'p5_11_4', 'p5_11_5', 'p5_11_6', 'p5_11_7', 'p5_11_8', 'p5_11a'],
  'destring': ['p5_11_1', 'p5_11_2', 'p5_11_3', 'p5_11_4', 'p5_11_5', 'p5_11_6', 'p5_11_7', 'p5_11_8'],
  'destring_all': True,
  'yesno': ['p5_11_1', 'p5_11_2', 'p5_11_3', 'p5_11_4', 'p5_11_5', 'p5_11_6', 'p5_11_7', 'p5_11_8'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_trains',
  'items': ['p5_12_1', 'p5_12_2', 'p5_12_3', 'p5_12_4', 'p5_12_5', 'p5_12a'],
  'destring': ['p5_12_1', 'p5_12_2', 'p5_12_3', 'p5_12_4', 'p5_12_5'],
  'destring_all': True,
  'yesno': ['p5_12_1', 'p5_12_2', 'p5_12_3', 'p5_12_4', 'p5_12_5'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_highways',
  'items': ['p5_13_1', 'p5_13_2', 'p5_13_3', 'p5_13_4', 'p5_13_5', 'p5_13a'],
  'destring': ['p5_13_1', 'p5_13_2', 'p5_13_3', 'p5_13_4', 'p5_13_5'],
  'destring_all': True,
  'yesno': ['p5_13_1', 'p5_13_2', 'p5_13_3', 'p5_13_4', 'p5_13_5'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_corruption',
  'items': ['p8_1', 'p8_2', 'p8_3_1', 'p8_3_2', 'p8_3_3'],
  'destring': ['p8_1', 'p8_2', 'p8_3_1', 'p8_3_2', 'p8_3_3'],
  'destring_all': True,
  'yesno': ['p8_1', 'p8_2', 'p8_3_1', 'p8_3_2', 'p8_3_3'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_generalcorruption',
  'items': ['p9_1', 'p9_7'],
  'destring': ['p9_1', 'p9_7'],
  'destring_all': True,
  'yesno': ['p9_1', 'p9_7'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_electricgovernment',
  'items': ['p10_1_1', 'p10_1_2', 'p10_1_3', 'p10_1_4', 'p10_1_5', 'p10_1_6'],
  'destring': ['p10_1_1', 'p10_1_2', 'p10_1_3', 'p10_1_4', 'p10_1_5', 'p10_1_6'],
  'destring_all': True,
  'yesno': ['p10_1_1', 'p10_1_2', 'p10_1_3', 'p10_1_4', 'p10_1_5', 'p10_1_6'],
  'missing': [9, 98, 99]},
 {'table': 'mexico_2023_quality_confidence',
  'items': ['p11_1_01', 'p11_1_02', 'p11_1_03', 'p11_1_04', 'p11_1_05', 'p11_1_06', 'p11_1_07', 'p11_1_08',
            'p11_1_09', 'p11_1_10', 'p11_1_11', 'p11_1_12', 'p11_1_13', 'p11_1_14', 'p11_1_15', 'p11_1_16',
            'p11_1_17', 'p11_1_18', 'p11_1_19', 'p11_1_20', 'p11_1_21', 'p11_1_22', 'p11_1_23', 'p11_1_24',
            'p11_1_25'],
  'destring': [],
  'destring_all': True,
  'yesno': [],
  'missing': [9, 98, 99]}]


def read(name):
    df = pd.read_csv(name, dtype=str, keep_default_na=False, na_values=[])
    df = df.drop(columns=[c for c in df.columns if c == "" or c.startswith("Unnamed")])
    df.columns = [c.lower() for c in df.columns]
    return df


def wave(year):
    res = read(f"encig{year}_02_residentes_sec_2.csv")
    s1 = read(f"encig{year}_01_sec1_A_3_4_5_8_9_10.csv")
    s11 = read(f"encig{year}_01_sec_11.csv")
    a = res.merge(s1, on="id_per", how="inner", suffixes=("", "__s1"))
    a = a[[c for c in a.columns if not c.endswith("__s1")]]
    b = a.merge(s11, on="id_per", how="outer", suffixes=("", "__s11"))
    b = b[[c for c in b.columns if not c.endswith("__s11")]].fillna("")
    return b.sort_values("id_per", kind="stable").reset_index(drop=True)


def numeric(df):
    """A column is numeric iff every non-blank value parses as a number (as Stata's import delimited decides)."""
    types = {}
    for c in df.columns:
        v = df[c][df[c].str.strip() != ""]
        types[c] = "num" if pd.to_numeric(v, errors="coerce").notna().all() else "str"
    out = df.copy()
    for c, k in types.items():
        if k == "num":
            out[c] = pd.to_numeric(out[c].where(out[c].str.strip() != ""), errors="coerce")
    return out, types


def load():
    d23, d21 = wave("2023"), wave("2021")
    keep = set(RENAME_2021) | set(RENAME_2021.values()) | set(ASKED_2021)   # renamed, or same name and same question
    clash = [c for c in d21.columns if c in ITEMS_2023 and c not in keep]
    d21 = d21.drop(columns=clash).rename(columns=RENAME_2021)
    d23["cov_year"], d21["cov_year"] = "2023", "2021"
    (d23, t23), (d21, t21) = numeric(d23), numeric(d21)
    for c in set(d23.columns) & set(d21.columns):
        if t23[c] != t21[c]:          # never blank a wave on a storage-type clash (the .do's append, force did)
            d23[c] = pd.to_numeric(d23[c], errors="coerce")
            d21[c] = pd.to_numeric(d21[c], errors="coerce")
    df = pd.concat([d23, d21], ignore_index=True, sort=False)
    df = df.rename(columns={"p1_1": "cov_hhsize", "sexo": "cov_sex", "edad": "cov_age", "niv": "cov_education"})
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].where(df[c] != "NA", "")
    df.insert(0, "id", np.arange(1, len(df) + 1))
    return df.copy()


def build(df, block):
    items = block["items"]
    covs = [c for c in df.columns if c.startswith("cov_")]
    sub = df[["id"] + covs + [i for i in items if i in df.columns]].copy()
    if not set(ASKED_2021) & set(items):
        sub = sub[sub["cov_year"] == 2023]
    for v in (items if block["destring_all"] else block["destring"]):
        if v in sub.columns:
            sub[v] = pd.to_numeric(sub[v].replace("", np.nan), errors="coerce")
    for v in block["yesno"]:
        if v in sub.columns:
            sub[v] = sub[v].replace({1: 0, 2: 1})
    long = sub.melt(id_vars=["id"] + covs, value_vars=[i for i in items if i in sub.columns],
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"].replace("", np.nan), errors="coerce")
    long.loc[long["resp"].isin(block["missing"]), "resp"] = np.nan
    long = long.sort_values(["id", "item"], kind="stable")
    long[["id", "item", "resp"] + covs].to_csv(block["table"] + ".csv", index=False, na_rep="")
    return len(long)


if __name__ == "__main__":
    data = load()
    for blk in BLOCKS:
        print(blk["table"], build(data, blk))
