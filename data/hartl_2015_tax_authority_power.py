#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/_Does_the_Sole_Description_of_a_Tax_Authority_Affect_Tax_Evasion_The_Impact_of_Described_Coercive_and_Legitimate_Power_/1398631
# DOI: 10.1371/journal.pone.0123355 (data)
#   Hartl, B., Hofmann, E., Gangl, K., Hartner-Tiefenthaler, M., & Kirchler, E. (2015). Does the sole description of
#     a tax authority affect tax evasion? The impact of described coercive and legitimate power. PLOS ONE 10(4):
#     e0123355. Supporting information S1-S3 Data.
# License: CC BY 4.0 (PLOS ONE supporting information)
# Data: Three Austrian tax-evasion experiments (S1 108, S2 250, S3 368 participants) in which a tax authority is
#   described with high/low coercive and legitimate power, followed by German questionnaires on 1-7 scales. The 4
#   coercive-power and 22 legitimate-power items are asked in all three and stacked with cov_study (ids prefixed);
#   S2 and S3 rate a second description later in the session (*_02 / *_A columns), and only the first rating is
#   shipped. S1 alone also carries reason-based and implicit trust, committed/enforced/voluntary cooperation,
#   service/antagonistic/confidence climate and two 3-item measures coded te and ta (kept as codes).
# Tables: item = the deposit's item stem code (cp01.., lp01.., rbt01..), unified across studies (S2 CO_01_01 ->
#   cp01, LP_01_01 -> lp01; S3 cplp_cp01_01 -> cp01).
# Covariates: cov_study, cov_condition (study-specific condition code, prefixed by study), cov_age (S1, S3); gender
#   is coded without a key and not carried
# PII: none found (string columns screened)
# Item text: available -- S1/S3 SPSS variable labels carry the German statement endings (stem 'Die Steuerbehörde
#   ...' in the questionnaire, S1 Table PDF)
# Built by the 2026-11-20 repos leads (lane 2) from a shared template; one self-contained script per deposit.

import io
import os
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "irw-pipeline/1.0"}

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/6747000',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 108,
  'range': (1, 7),
  'blocks': {'hartl_2015_coercive_power': ['cp01_01', 'cp02_02', 'cp03_03', 'cp04_04'],
             'hartl_2015_legitimate_power': ['lp01_05',
                                             'lp02_06',
                                             'lp03_07',
                                             'lp04_08',
                                             'lp05_09',
                                             'lp06_10',
                                             'lp07_11',
                                             'lp08_12',
                                             'lp09_13',
                                             'lp10_14',
                                             'lp11_15',
                                             'lp12_16',
                                             'lp13_17',
                                             'lp14_18',
                                             'lp15_19',
                                             'lp16_20',
                                             'lp17_21',
                                             'lp18_22',
                                             'lp19_23',
                                             'lp20_24',
                                             'lp21_25',
                                             'lp22_26'],
             'hartl_2015_reason_based_trust': ['rbt01_27',
                                               'rbt02_28',
                                               'rbt03_29',
                                               'rbt04_30',
                                               'rbt05_31',
                                               'rbt06_32',
                                               'rbt07_33'],
             'hartl_2015_implicit_trust': ['it01_34', 'it02_35', 'it03_36'],
             'hartl_2015_committed_cooperation': ['comc01_38', 'comc02_39', 'comc03_40'],
             'hartl_2015_enforced_compliance': ['enfc01_41', 'enfc02_42', 'enfc03_43'],
             'hartl_2015_voluntary_cooperation': ['volc01_44', 'volc02_45', 'volc03_46'],
             'hartl_2015_service_climate': ['servcl01_47', 'servcl02_48', 'servcl03_49'],
             'hartl_2015_antagonistic_climate': ['antcl01_50', 'antcl02_51', 'antcl03_52'],
             'hartl_2015_confidence_climate': ['concl01_53', 'concl02_54', 'concl03_55'],
             'hartl_2015_te': ['te01_56', 'te02_57', 'te03_58'],
             'hartl_2015_ta': ['ta01_59', 'ta02_60', 'ta03_61']},
  'covs': {'Bedingung': 'cov_condition', 'alter': 'cov_age'},
  'cov_maps': {'cov_condition': {'          ,5': 's1_0.5', '         1,0': 's1_1.0', '         2,0': 's1_2.0'}},
  'not_shipped': {'Datum': 'experiment record (tax contributions, date, participant number)',
                  'TeilnNr': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag01': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag02': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag03': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag04': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag05': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag06': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag07': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag08': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag09': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag10': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag11': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag12': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag13': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag14': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag15': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag16': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag17': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag18': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag19': 'experiment record (tax contributions, date, participant number)',
                  'Steuerbeitrag20': 'experiment record (tax contributions, date, participant number)',
                  'relStb01': 'experiment record (tax contributions, date, participant number)',
                  'relStb02': 'experiment record (tax contributions, date, participant number)',
                  'relStb03': 'experiment record (tax contributions, date, participant number)',
                  'relStb04': 'experiment record (tax contributions, date, participant number)',
                  'relStb05': 'experiment record (tax contributions, date, participant number)',
                  'relStb06': 'experiment record (tax contributions, date, participant number)',
                  'relStb07': 'experiment record (tax contributions, date, participant number)',
                  'relStb08': 'experiment record (tax contributions, date, participant number)',
                  'relStb09': 'experiment record (tax contributions, date, participant number)',
                  'relStb10': 'experiment record (tax contributions, date, participant number)',
                  'relStb11': 'experiment record (tax contributions, date, participant number)',
                  'relStb12': 'experiment record (tax contributions, date, participant number)',
                  'relStb13': 'experiment record (tax contributions, date, participant number)',
                  'relStb14': 'experiment record (tax contributions, date, participant number)',
                  'relStb15': 'experiment record (tax contributions, date, participant number)',
                  'relStb16': 'experiment record (tax contributions, date, participant number)',
                  'relStb17': 'experiment record (tax contributions, date, participant number)',
                  'relStb18': 'experiment record (tax contributions, date, participant number)',
                  'relStb19': 'experiment record (tax contributions, date, participant number)',
                  'relStb20': 'experiment record (tax contributions, date, participant number)',
                  'geschl': 'post-experiment check or background code without a key',
                  'pruefwahr': 'post-experiment check or background code without a key',
                  'strafe': 'post-experiment check or background code without a key',
                  'nation': 'post-experiment check or background code without a key',
                  'ausbildung': 'post-experiment check or background code without a key',
                  'studienrichtung': 'post-experiment check or background code without a key',
                  'einkommen': 'post-experiment check or background code without a key',
                  'arbeit': 'post-experiment check or background code without a key',
                  'arbeitsverh': 'post-experiment check or background code without a key',
                  'arbeitszeit': 'post-experiment check or background code without a key',
                  'erfahrung_steuern': 'post-experiment check or background code without a key'},
  'label': 'hartl_2015_tax_authority_power_s1',
  'item_names': {'cp01_01': 'cp01',
                 'cp02_02': 'cp02',
                 'cp03_03': 'cp03',
                 'cp04_04': 'cp04',
                 'lp01_05': 'lp01',
                 'lp02_06': 'lp02',
                 'lp03_07': 'lp03',
                 'lp04_08': 'lp04',
                 'lp05_09': 'lp05',
                 'lp06_10': 'lp06',
                 'lp07_11': 'lp07',
                 'lp08_12': 'lp08',
                 'lp09_13': 'lp09',
                 'lp10_14': 'lp10',
                 'lp11_15': 'lp11',
                 'lp12_16': 'lp12',
                 'lp13_17': 'lp13',
                 'lp14_18': 'lp14',
                 'lp15_19': 'lp15',
                 'lp16_20': 'lp16',
                 'lp17_21': 'lp17',
                 'lp18_22': 'lp18',
                 'lp19_23': 'lp19',
                 'lp20_24': 'lp20',
                 'lp21_25': 'lp21',
                 'lp22_26': 'lp22',
                 'rbt01_27': 'rbt01',
                 'rbt02_28': 'rbt02',
                 'rbt03_29': 'rbt03',
                 'rbt04_30': 'rbt04',
                 'rbt05_31': 'rbt05',
                 'rbt06_32': 'rbt06',
                 'rbt07_33': 'rbt07',
                 'it01_34': 'it01',
                 'it02_35': 'it02',
                 'it03_36': 'it03',
                 'comc01_38': 'comc01',
                 'comc02_39': 'comc02',
                 'comc03_40': 'comc03',
                 'enfc01_41': 'enfc01',
                 'enfc02_42': 'enfc02',
                 'enfc03_43': 'enfc03',
                 'volc01_44': 'volc01',
                 'volc02_45': 'volc02',
                 'volc03_46': 'volc03',
                 'servcl01_47': 'servcl01',
                 'servcl02_48': 'servcl02',
                 'servcl03_49': 'servcl03',
                 'antcl01_50': 'antcl01',
                 'antcl02_51': 'antcl02',
                 'antcl03_52': 'antcl03',
                 'concl01_53': 'concl01',
                 'concl02_54': 'concl02',
                 'concl03_55': 'concl03',
                 'te01_56': 'te01',
                 'te02_57': 'te02',
                 'te03_58': 'te03',
                 'ta01_59': 'ta01',
                 'ta02_60': 'ta02',
                 'ta03_61': 'ta03'},
  'id_prefix': 's1',
  'const_covs': {'cov_study': 'study1'}},
 {'url': 'https://ndownloader.figshare.com/files/6747003',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 250,
  'range': (1, 7),
  'blocks': {'hartl_2015_coercive_power': ['CO_01_01', 'CO_02_01', 'CO_03_01', 'CO_04_01'],
             'hartl_2015_legitimate_power': ['LP_01_01',
                                             'LP_02_01',
                                             'LP_03_01',
                                             'LP_04_01',
                                             'LP_05_01',
                                             'LP_06_01',
                                             'LP_07_01',
                                             'LP_08_01',
                                             'LP_09_01',
                                             'LP_10_01',
                                             'LP_11_01',
                                             'LP_12_01',
                                             'LP_13_01',
                                             'LP_14_01',
                                             'LP_15_01',
                                             'LP_16_01',
                                             'LP_17_01',
                                             'LP_18_01',
                                             'LP_19_01',
                                             'LP_20_01',
                                             'LP_21_01',
                                             'LP_22_01']},
  'covs': {'BED': 'cov_condition'},
  'cov_maps': {'cov_condition': {1.0: 's2_1',
                                 2.0: 's2_2',
                                 3.0: 's2_3',
                                 4.0: 's2_4',
                                 5.0: 's2_5',
                                 6.0: 's2_6',
                                 7.0: 's2_7',
                                 8.0: 's2_8'}},
  'not_shipped': {'TEILNR': 'experiment record, second-description rating, or background code',
                  'Intensität1': 'experiment record, second-description rating, or background code',
                  'Intensität2': 'experiment record, second-description rating, or background code',
                  'Macht': 'experiment record, second-description rating, or background code',
                  'VPNNR': 'experiment record, second-description rating, or background code',
                  'ST_01': 'experiment record, second-description rating, or background code',
                  'ST_02': 'experiment record, second-description rating, or background code',
                  'ST_03': 'experiment record, second-description rating, or background code',
                  'ST_04': 'experiment record, second-description rating, or background code',
                  'ST_05': 'experiment record, second-description rating, or background code',
                  'ST_06': 'experiment record, second-description rating, or background code',
                  'ST_07': 'experiment record, second-description rating, or background code',
                  'ST_08': 'experiment record, second-description rating, or background code',
                  'ST_09': 'experiment record, second-description rating, or background code',
                  'ST_10': 'experiment record, second-description rating, or background code',
                  'ST_11': 'experiment record, second-description rating, or background code',
                  'ST_12': 'experiment record, second-description rating, or background code',
                  'ST_13': 'experiment record, second-description rating, or background code',
                  'ST_14': 'experiment record, second-description rating, or background code',
                  'ST_15': 'experiment record, second-description rating, or background code',
                  'ST_16': 'experiment record, second-description rating, or background code',
                  'ST_17': 'experiment record, second-description rating, or background code',
                  'ST_18': 'experiment record, second-description rating, or background code',
                  'ST_19': 'experiment record, second-description rating, or background code',
                  'ST_20': 'experiment record, second-description rating, or background code',
                  'relST_01': 'experiment record, second-description rating, or background code',
                  'relST_02': 'experiment record, second-description rating, or background code',
                  'relST_03': 'experiment record, second-description rating, or background code',
                  'relST_04': 'experiment record, second-description rating, or background code',
                  'relST_05': 'experiment record, second-description rating, or background code',
                  'relST_06': 'experiment record, second-description rating, or background code',
                  'relST_07': 'experiment record, second-description rating, or background code',
                  'relST_08': 'experiment record, second-description rating, or background code',
                  'relST_09': 'experiment record, second-description rating, or background code',
                  'relST_10': 'experiment record, second-description rating, or background code',
                  'relST_11': 'experiment record, second-description rating, or background code',
                  'relST_12': 'experiment record, second-description rating, or background code',
                  'relST_13': 'experiment record, second-description rating, or background code',
                  'relST_14': 'experiment record, second-description rating, or background code',
                  'relST_15': 'experiment record, second-description rating, or background code',
                  'relST_16': 'experiment record, second-description rating, or background code',
                  'relST_17': 'experiment record, second-description rating, or background code',
                  'relST_18': 'experiment record, second-description rating, or background code',
                  'relST_19': 'experiment record, second-description rating, or background code',
                  'relST_20': 'experiment record, second-description rating, or background code',
                  'ST_21': 'experiment record, second-description rating, or background code',
                  'ST_22': 'experiment record, second-description rating, or background code',
                  'ST_23': 'experiment record, second-description rating, or background code',
                  'ST_24': 'experiment record, second-description rating, or background code',
                  'ST_25': 'experiment record, second-description rating, or background code',
                  'ST_26': 'experiment record, second-description rating, or background code',
                  'ST_27': 'experiment record, second-description rating, or background code',
                  'ST_28': 'experiment record, second-description rating, or background code',
                  'ST_29': 'experiment record, second-description rating, or background code',
                  'ST_30': 'experiment record, second-description rating, or background code',
                  'ST_31': 'experiment record, second-description rating, or background code',
                  'ST_32': 'experiment record, second-description rating, or background code',
                  'ST_33': 'experiment record, second-description rating, or background code',
                  'ST_34': 'experiment record, second-description rating, or background code',
                  'ST_35': 'experiment record, second-description rating, or background code',
                  'ST_36': 'experiment record, second-description rating, or background code',
                  'ST_37': 'experiment record, second-description rating, or background code',
                  'ST_38': 'experiment record, second-description rating, or background code',
                  'ST_39': 'experiment record, second-description rating, or background code',
                  'ST_40': 'experiment record, second-description rating, or background code',
                  'relST_21': 'experiment record, second-description rating, or background code',
                  'relST_22': 'experiment record, second-description rating, or background code',
                  'relST_23': 'experiment record, second-description rating, or background code',
                  'relST_24': 'experiment record, second-description rating, or background code',
                  'relST_25': 'experiment record, second-description rating, or background code',
                  'relST_26': 'experiment record, second-description rating, or background code',
                  'relST_27': 'experiment record, second-description rating, or background code',
                  'relST_28': 'experiment record, second-description rating, or background code',
                  'relST_29': 'experiment record, second-description rating, or background code',
                  'relST_30': 'experiment record, second-description rating, or background code',
                  'relST_31': 'experiment record, second-description rating, or background code',
                  'relST_32': 'experiment record, second-description rating, or background code',
                  'relST_33': 'experiment record, second-description rating, or background code',
                  'relST_34': 'experiment record, second-description rating, or background code',
                  'relST_35': 'experiment record, second-description rating, or background code',
                  'relST_36': 'experiment record, second-description rating, or background code',
                  'relST_37': 'experiment record, second-description rating, or background code',
                  'relST_38': 'experiment record, second-description rating, or background code',
                  'relST_39': 'experiment record, second-description rating, or background code',
                  'relST_40': 'experiment record, second-description rating, or background code',
                  'CO_01_02': 'experiment record, second-description rating, or background code',
                  'CO_02_02': 'experiment record, second-description rating, or background code',
                  'CO_03_02': 'experiment record, second-description rating, or background code',
                  'CO_04_02': 'experiment record, second-description rating, or background code',
                  'LP_01_02': 'experiment record, second-description rating, or background code',
                  'LP_02_02': 'experiment record, second-description rating, or background code',
                  'LP_03_02': 'experiment record, second-description rating, or background code',
                  'LP_04_02': 'experiment record, second-description rating, or background code',
                  'LP_05_02': 'experiment record, second-description rating, or background code',
                  'LP_06_02': 'experiment record, second-description rating, or background code',
                  'LP_07_02': 'experiment record, second-description rating, or background code',
                  'LP_08_02': 'experiment record, second-description rating, or background code',
                  'LP_09_02': 'experiment record, second-description rating, or background code',
                  'LP_10_02': 'experiment record, second-description rating, or background code',
                  'LP_11_02': 'experiment record, second-description rating, or background code',
                  'LP_12_02': 'experiment record, second-description rating, or background code',
                  'LP_13_02': 'experiment record, second-description rating, or background code',
                  'LP_14_02': 'experiment record, second-description rating, or background code',
                  'LP_15_02': 'experiment record, second-description rating, or background code',
                  'LP_16_02': 'experiment record, second-description rating, or background code',
                  'LP_17_02': 'experiment record, second-description rating, or background code',
                  'LP_18_02': 'experiment record, second-description rating, or background code',
                  'LP_19_02': 'experiment record, second-description rating, or background code',
                  'LP_20_02': 'experiment record, second-description rating, or background code',
                  'LP_21_02': 'experiment record, second-description rating, or background code',
                  'LP_22_02': 'experiment record, second-description rating, or background code',
                  'DM_01': 'experiment record, second-description rating, or background code',
                  'DM_02': 'experiment record, second-description rating, or background code',
                  'DM_03': 'experiment record, second-description rating, or background code',
                  'DM_04': 'experiment record, second-description rating, or background code',
                  'DM_05': 'experiment record, second-description rating, or background code',
                  'DM_06': 'experiment record, second-description rating, or background code',
                  'DM_07': 'experiment record, second-description rating, or background code',
                  'DM_08': 'experiment record, second-description rating, or background code',
                  'DM_09': 'experiment record, second-description rating, or background code'},
  'label': 'hartl_2015_tax_authority_power_s2',
  'item_names': {'CO_01_01': 'cp01',
                 'CO_02_01': 'cp02',
                 'CO_03_01': 'cp03',
                 'CO_04_01': 'cp04',
                 'LP_01_01': 'lp01',
                 'LP_02_01': 'lp02',
                 'LP_03_01': 'lp03',
                 'LP_04_01': 'lp04',
                 'LP_05_01': 'lp05',
                 'LP_06_01': 'lp06',
                 'LP_07_01': 'lp07',
                 'LP_08_01': 'lp08',
                 'LP_09_01': 'lp09',
                 'LP_10_01': 'lp10',
                 'LP_11_01': 'lp11',
                 'LP_12_01': 'lp12',
                 'LP_13_01': 'lp13',
                 'LP_14_01': 'lp14',
                 'LP_15_01': 'lp15',
                 'LP_16_01': 'lp16',
                 'LP_17_01': 'lp17',
                 'LP_18_01': 'lp18',
                 'LP_19_01': 'lp19',
                 'LP_20_01': 'lp20',
                 'LP_21_01': 'lp21',
                 'LP_22_01': 'lp22'},
  'id_prefix': 's2',
  'const_covs': {'cov_study': 'study2'}},
 {'url': 'https://ndownloader.figshare.com/files/6747006',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 368,
  'range': (1, 7),
  'blocks': {'hartl_2015_coercive_power': ['cplp_cp01_01', 'cplp_cp02_02', 'cplp_cp03_03', 'cplp_cp04_04'],
             'hartl_2015_legitimate_power': ['cplp_lp01_05',
                                             'cplp_lp02_06',
                                             'cplp_lp03_07',
                                             'cplp_lp04_08',
                                             'cplp_lp05_09',
                                             'cplp_lp06_10',
                                             'cplp_lp07_11',
                                             'cplp_lp08_12',
                                             'cplp_lp09_13',
                                             'cplp_lp10_14',
                                             'cplp_lp11_15',
                                             'cplp_lp12_16',
                                             'cplp_lp13_17',
                                             'cplp_lp14_18',
                                             'cplp_lp15_19',
                                             'cplp_lp16_20',
                                             'cplp_lp17_21',
                                             'cplp_lp18_22',
                                             'cplp_lp19_23',
                                             'cplp_lp20_24',
                                             'cplp_lp21_25',
                                             'cplp_lp22_26']},
  'covs': {'Bedingung': 'cov_condition', 'alter': 'cov_age'},
  'cov_maps': {'cov_condition': {1.0: 's3_1',
                                 2.0: 's3_2',
                                 3.0: 's3_3',
                                 4.0: 's3_4',
                                 5.0: 's3_5',
                                 6.0: 's3_6',
                                 7.0: 's3_7',
                                 8.0: 's3_8',
                                 9.0: 's3_9',
                                 10.0: 's3_10',
                                 11.0: 's3_11',
                                 12.0: 's3_12'}},
  'not_shipped': {'TeilnNr': 'experiment record, second-description rating (_A), or background code',
                  'Teilnehmer': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag40': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag01': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag02': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag03': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag04': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag05': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag06': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag07': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag08': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag09': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag10': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag11': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag12': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag13': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag14': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag15': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag16': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag17': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag18': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag19': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag20': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag21': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag22': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag23': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag24': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag25': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag26': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag27': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag28': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag29': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag30': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag31': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag32': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag33': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag34': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag35': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag36': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag37': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag38': 'experiment record, second-description rating (_A), or background code',
                  'Steuerbeitrag39': 'experiment record, second-description rating (_A), or background code',
                  'cplp_cp01_01_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_cp02_02_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_cp03_03_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_cp04_04_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp01_05_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp02_06_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp03_07_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp04_08_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp05_09_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp06_10_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp07_11_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp08_12_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp09_13_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp10_14_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp11_15_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp12_16_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp13_17_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp14_18_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp15_19_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp16_20_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp17_21_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp18_22_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp19_23_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp20_24_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp21_25_A': 'experiment record, second-description rating (_A), or background code',
                  'cplp_lp22_26_A': 'experiment record, second-description rating (_A), or background code',
                  'geschl': 'experiment record, second-description rating (_A), or background code',
                  'nation': 'experiment record, second-description rating (_A), or background code',
                  'ausbildung': 'experiment record, second-description rating (_A), or background code',
                  'einkommen': 'experiment record, second-description rating (_A), or background code',
                  'arbeit': 'experiment record, second-description rating (_A), or background code',
                  'arbeitsverh': 'experiment record, second-description rating (_A), or background code',
                  'arbeitszeit': 'experiment record, second-description rating (_A), or background code',
                  'erfahrung_steuern': 'experiment record, second-description rating (_A), or background code',
                  'relST_01': 'experiment record, second-description rating (_A), or background code',
                  'relST_02': 'experiment record, second-description rating (_A), or background code',
                  'relST_03': 'experiment record, second-description rating (_A), or background code',
                  'relST_04': 'experiment record, second-description rating (_A), or background code',
                  'relST_05': 'experiment record, second-description rating (_A), or background code',
                  'relST_06': 'experiment record, second-description rating (_A), or background code',
                  'relST_07': 'experiment record, second-description rating (_A), or background code',
                  'relST_08': 'experiment record, second-description rating (_A), or background code',
                  'relST_09': 'experiment record, second-description rating (_A), or background code',
                  'relST_10': 'experiment record, second-description rating (_A), or background code',
                  'relST_11': 'experiment record, second-description rating (_A), or background code',
                  'relST_12': 'experiment record, second-description rating (_A), or background code',
                  'relST_13': 'experiment record, second-description rating (_A), or background code',
                  'relST_14': 'experiment record, second-description rating (_A), or background code',
                  'relST_15': 'experiment record, second-description rating (_A), or background code',
                  'relST_16': 'experiment record, second-description rating (_A), or background code',
                  'relST_17': 'experiment record, second-description rating (_A), or background code',
                  'relST_18': 'experiment record, second-description rating (_A), or background code',
                  'relST_19': 'experiment record, second-description rating (_A), or background code',
                  'relST_20': 'experiment record, second-description rating (_A), or background code',
                  'relST_21': 'experiment record, second-description rating (_A), or background code',
                  'relST_22': 'experiment record, second-description rating (_A), or background code',
                  'relST_23': 'experiment record, second-description rating (_A), or background code',
                  'relST_24': 'experiment record, second-description rating (_A), or background code',
                  'relST_25': 'experiment record, second-description rating (_A), or background code',
                  'relST_26': 'experiment record, second-description rating (_A), or background code',
                  'relST_27': 'experiment record, second-description rating (_A), or background code',
                  'relST_28': 'experiment record, second-description rating (_A), or background code',
                  'relST_29': 'experiment record, second-description rating (_A), or background code',
                  'relST_30': 'experiment record, second-description rating (_A), or background code',
                  'relST_31': 'experiment record, second-description rating (_A), or background code',
                  'relST_32': 'experiment record, second-description rating (_A), or background code',
                  'relST_33': 'experiment record, second-description rating (_A), or background code',
                  'relST_34': 'experiment record, second-description rating (_A), or background code',
                  'relST_35': 'experiment record, second-description rating (_A), or background code',
                  'relST_36': 'experiment record, second-description rating (_A), or background code',
                  'relST_37': 'experiment record, second-description rating (_A), or background code',
                  'relST_38': 'experiment record, second-description rating (_A), or background code',
                  'relST_39': 'experiment record, second-description rating (_A), or background code',
                  'relST_40': 'experiment record, second-description rating (_A), or background code'},
  'label': 'hartl_2015_tax_authority_power_s3',
  'item_names': {'cplp_cp01_01': 'cp01',
                 'cplp_cp02_02': 'cp02',
                 'cplp_cp03_03': 'cp03',
                 'cplp_cp04_04': 'cp04',
                 'cplp_lp01_05': 'lp01',
                 'cplp_lp02_06': 'lp02',
                 'cplp_lp03_07': 'lp03',
                 'cplp_lp04_08': 'lp04',
                 'cplp_lp05_09': 'lp05',
                 'cplp_lp06_10': 'lp06',
                 'cplp_lp07_11': 'lp07',
                 'cplp_lp08_12': 'lp08',
                 'cplp_lp09_13': 'lp09',
                 'cplp_lp10_14': 'lp10',
                 'cplp_lp11_15': 'lp11',
                 'cplp_lp12_16': 'lp12',
                 'cplp_lp13_17': 'lp13',
                 'cplp_lp14_18': 'lp14',
                 'cplp_lp15_19': 'lp15',
                 'cplp_lp16_20': 'lp16',
                 'cplp_lp17_21': 'lp17',
                 'cplp_lp18_22': 'lp18',
                 'cplp_lp19_23': 'lp19',
                 'cplp_lp20_24': 'lp20',
                 'cplp_lp21_25': 'lp21',
                 'cplp_lp22_26': 'lp22'},
  'id_prefix': 's3',
  'const_covs': {'cov_study': 'study3'}}]

# rows written per table (asserted)
EXPECT = {'hartl_2015_antagonistic_climate': 321,
 'hartl_2015_coercive_power': 2900,
 'hartl_2015_committed_cooperation': 321,
 'hartl_2015_confidence_climate': 321,
 'hartl_2015_enforced_compliance': 321,
 'hartl_2015_implicit_trust': 321,
 'hartl_2015_legitimate_power': 15950,
 'hartl_2015_reason_based_trust': 749,
 'hartl_2015_service_climate': 321,
 'hartl_2015_ta': 321,
 'hartl_2015_te': 321,
 'hartl_2015_voluntary_cooperation': 321}


def load(content, kind, read_kw):
    if kind == "csv":
        return pd.read_csv(io.BytesIO(content), **read_kw)
    if kind == "excel":
        return pd.read_excel(io.BytesIO(content), **read_kw)
    if kind in ("sav", "dta"):
        import pyreadstat
        with tempfile.NamedTemporaryFile(suffix="." + kind, delete=False) as fh:
            fh.write(content)
        try:
            reader = pyreadstat.read_sav if kind == "sav" else pyreadstat.read_dta
            df, _ = reader(fh.name, **read_kw)
        finally:
            os.unlink(fh.name)
        return df
    raise ValueError(kind)


def fetch(url):
    for attempt in range(6):  # Mendeley's public-files endpoint returns transient 502s
        try:
            r = requests.get(url, timeout=300, headers=UA)
        except requests.RequestException:
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code < 500:
            break
        time.sleep(20 * (attempt + 1))
    r.raise_for_status()
    return r.content


def build_source(src):
    d = load(fetch(src["url"]), src["kind"], src.get("read_kw", {}))
    d.columns = [" ".join(str(c).split()) for c in d.columns]
    d = d.rename(columns=src.get("rename", {}))
    if src.get("drop_empty_rows"):
        d = d.dropna(how="all")
    assert len(d) == src["n_rows"], (src["label"], len(d))
    before = len(d)
    if src.get("keep_col_eq"):
        col, val = src["keep_col_eq"]
        d = d[d[col] == val]
    if src.get("keep_any_item"):
        d = d[d[[c for cols in src["blocks"].values() for c in cols]].notna().any(axis=1)]
    if len(d) != before:
        print(f"{src['label']}: kept {len(d)} of {before} rows ({src.get('keep_reason', '')})")
    # The books: every source column is shipped (item or covariate), the id, or skipped for a stated reason.
    items = [c for cols in src["blocks"].values() for c in cols]
    special = [x["col"] for x in (src.get("wave"), src.get("treat")) if x]
    used = set(items) | set(src.get("covs", {})) | set(src.get("not_shipped", {})) | set(special)
    if src.get("id_col"):
        used.add(src["id_col"])
    unaccounted = [c for c in d.columns if c not in used]
    assert not unaccounted, (src["label"], unaccounted)
    missing = [c for c in used if c not in d.columns]
    assert not missing, (src["label"], missing)
    if src.get("id_col"):
        if src.get("wave"):
            assert not d.duplicated([src["id_col"], src["wave"]["col"]]).any(), "id x wave not unique"
        else:
            assert d[src["id_col"]].notna().all() and d[src["id_col"]].is_unique, "id not unique"
        d["id"] = d[src["id_col"]].astype(str)
    else:
        d["id"] = [str(k) for k in range(1, len(d) + 1)]
    if src.get("id_prefix"):
        d["id"] = src["id_prefix"] + "_" + d["id"]
    for col, bad in src.get("invalid", {}).items():
        # out-of-range codes isolated to one item: data-entry errors, set missing (see header)
        hit = d[col].isin(bad)
        print(f"{src['label']}: {col}: {int(hit.sum())} cell(s) {bad} set missing")
        d.loc[hit, col] = None
    extra = []
    for key in ("wave", "treat"):
        spec = src.get(key)
        if spec:
            m = spec.get("map")
            v = d[spec["col"]]
            if m is not None:
                bad = [x for x in v.dropna().unique() if x not in m]
                assert not bad, (key, bad)
                v = v.map(m)
            d[key] = v
            extra.append(key)
    for k, v in src.get("const", {}).items():
        d[k] = v
        extra.append(k)
    covs = []
    for col, cov in src.get("covs", {}).items():
        m = src.get("cov_maps", {}).get(cov)
        if m is not None:
            vals = d[col].map(lambda v: m.get(v, m.get(str(v).strip())) if pd.notna(v) else None)
            bad = [v for v in d[col].dropna().unique() if v not in m and str(v).strip() not in m]
            assert len(bad) == 0, (cov, bad[:10])
            d[cov] = vals
        else:
            d[cov] = d[col]
        covs.append(cov)
    for k, v in src.get("const_covs", {}).items():
        d[k] = v
        covs.append(k)
    names = src.get("item_names", {})
    out = {}
    for name, cols in src["blocks"].items():
        t = d[["id"] + extra + covs + cols].melt(id_vars=["id"] + extra + covs, var_name="item", value_name="resp")
        rec = src.get("recode", {})
        if rec:
            def _rc(v):
                if pd.isna(v):
                    return v
                k = " ".join(str(v).split())
                assert k in rec or not isinstance(v, str), (name, v)
                return rec.get(k, v)
            t["resp"] = t["resp"].map(_rc)
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        miss = src.get("missing_codes", [])
        if miss:
            t.loc[t["resp"].isin(miss), "resp"] = None
        t = t.dropna(subset=["resp"])
        t["item"] = t["item"].map(lambda c: names.get(c, c))
        lo, hi = src.get("ranges", {}).get(name, src["range"])
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        assert t["resp"].between(lo, hi).all(), (name, t["resp"].min(), t["resp"].max())
        t["resp"] = t["resp"].astype(int)
        out[name] = (t, (lo, hi))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {}
    for src in SOURCES:
        for name, (t, rng) in build_source(src).items():
            tables.setdefault(name, []).append((t, rng))
    for name, parts in tables.items():
        lo = min(r[0] for _, r in parts)
        hi = max(r[1] for _, r in parts)
        t = pd.concat([p for p, _ in parts], ignore_index=True)
        lead = [c for c in ("wave", "treat") if c in t.columns]
        covs = [c for c in t.columns if c.startswith("cov_")]
        t = t[["id", "item", "resp"] + lead + covs].sort_values(["id", "item"] + lead[:1], kind="stable")
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t.columns else [])).any(), name
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() >= 3, (name, t["item"].nunique())
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert len(name) <= 40, name
        if EXPECT:
            assert len(t) == EXPECT[name], (name, len(t), EXPECT[name])
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    if EXPECT:
        assert set(EXPECT) == set(tables), sorted(set(EXPECT) ^ set(tables))


if __name__ == "__main__":
    main()
