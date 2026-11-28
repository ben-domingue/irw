#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.32031747.v1
# DOI: 10.6084/m9.figshare.32031747.v1 (data)
#   KDV PRASAD (2026). From Destination Image to Digital Advocacy: A Cognition–Affect–Involvement Model of Tourists’
#     eWOM Intentions [Dataset]. figshare.
# License: CC BY 4.0 (figshare record)
# Data: 630 Indian tourists across five destinations (coded 1-5, not keyed), 1-7 agreement items.
# Tables: cognitive image (25 attributes), affective image (4), vacation involvement (11; pleasure/interest and risk
#   statements in the Laurent-Kapferer style), eWOM intention (6): IRW's reading of the bracketed statements in
#   sheet order; items by position within block.
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: available in the headers but garbled by the depositor's export ('na' -> '6', 'no' -> '2', e.g.
#   'desti6tion'); not shipped
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

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/63781317',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 630,
  'range': (1, 7),
  'blocks': {'prasad_2026_cognitive_destination_image': ['Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Pleasant Weather]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Beautiful '
                                                         'Scenery]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Unique Flora and '
                                                         'Fau6 (Varied plants and wildlife)]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Green Cover '
                                                         '(6tural or planted vegetation)]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Excellent '
                                                         'Transport facilities]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Excellent Hotels '
                                                         'and Restaurants]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Pollution is '
                                                         'less]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Parking '
                                                         'facilities are adequate]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Good shopping '
                                                         'centres]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Adventure based '
                                                         'activities are present]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Amusement, '
                                                         'Recreation and Entertainment facilities are available]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Local Cuisine and '
                                                         'food outlets are excellent ]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Offers places of '
                                                         'historical or cultural interest]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Handicrafts '
                                                         'unique to the area]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Rich customs and '
                                                         'religious traditions]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Stable political '
                                                         'environment]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Less crime rate]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [A Safe and secure '
                                                         'desti6tion]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Hospitable and '
                                                         'friendly residents]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Easy to converse '
                                                         'with local people]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Good civic sense '
                                                         '(People at the desti6tion give importance to cleanliness '
                                                         'and follow rules)]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Quality of life '
                                                         'of the people at the desti6tion is good]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Eco2mic mode of '
                                                         'transportation is available]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Prices for food '
                                                         'and accommodation is reaso6ble]',
                                                         'Please indicate your extent of agreement with the '
                                                         'following statements/phrases about the destination you '
                                                         'visited on a scale of 1 to 7 where 7 indicates strongly '
                                                         'agree and 1 indicates strongly disagree [Appropriately '
                                                         'priced shopping merchandise]'],
             'prasad_2026_affective_destination_image': ['Please indicate your extent of agreement about the '
                                                         'emotions attributed to the destination you visited on a '
                                                         'scale of 1 to 7, where 7 indicates strongly agree and 1 '
                                                         'indicates strongly disagree [Pleasant Desti6tion]',
                                                         'Please indicate your extent of agreement about the '
                                                         'emotions attributed to the destination you visited on a '
                                                         'scale of 1 to 7, where 7 indicates strongly agree and 1 '
                                                         'indicates strongly disagree [Relaxing Desti6tion]',
                                                         'Please indicate your extent of agreement about the '
                                                         'emotions attributed to the destination you visited on a '
                                                         'scale of 1 to 7, where 7 indicates strongly agree and 1 '
                                                         'indicates strongly disagree [Arousing Desti6tion]',
                                                         'Please indicate your extent of agreement about the '
                                                         'emotions attributed to the destination you visited on a '
                                                         'scale of 1 to 7, where 7 indicates strongly agree and 1 '
                                                         'indicates strongly disagree [Exciting Desti6tion]'],
             'prasad_2026_vacation_involvement': ['Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [It gives me pleasure to purchase a '
                                                  'vacation]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [Buying a vacation is like buying a '
                                                  'gift for myself]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [A vacation is a pleasure to me.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [I attach great importance to a '
                                                  'vacation.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [One can say vacation destinations '
                                                  'interests me a lot.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [Whenever one buys a vacation, one '
                                                  'never really k2ws whether it is the one that should have been '
                                                  'bought.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [When I face a variety of vacation '
                                                  'choices, always feel a bit at loss to make my choice. ]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [Choosing a vacation desti6tion is '
                                                  'rather complicated.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [When one purchases a vacation, one '
                                                  'is never certain of one’s choice.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [It is really an2ying to purchase a '
                                                  'vacation that is 2t suitable.]',
                                                  'Indicate your extent of agreement about the following statements '
                                                  'on a scale of 1 to 7 where 7 indicates strongly agree and 1 '
                                                  'indicates strongly disagree [If, after I bought a vacation, my '
                                                  'choice proves to be poor, I would be really upset.]'],
             'prasad_2026_ewom_intention': ['Indicate your extent of agreement with the following statements about '
                                            'your intentions during/after the vacations on a scale of 1 to 7 where 7 '
                                            'indicates strongly agree and 1 indicates strongly disagree [I would '
                                            'share my desti6tion experiences with my friends or family online]',
                                            'Indicate your extent of agreement with the following statements about '
                                            'your intentions during/after the vacations on a scale of 1 to 7 where 7 '
                                            'indicates strongly agree and 1 indicates strongly disagree [When asked '
                                            'online by my friends or family members about the desti6tion, I will '
                                            'share my comments.]',
                                            'Indicate your extent of agreement with the following statements about '
                                            'your intentions during/after the vacations on a scale of 1 to 7 where 7 '
                                            'indicates strongly agree and 1 indicates strongly disagree [I would '
                                            'post about the desti6tion on my perso6l social networks (e.g. Facebook, '
                                            'Instagram, WhatsApp, twitter and Blogs)]',
                                            'Indicate your extent of agreement with the following statements about '
                                            'your intentions during/after the vacations on a scale of 1 to 7 where 7 '
                                            'indicates strongly agree and 1 indicates strongly disagree [I would '
                                            'share my comments on the desti6tion to strangers (people unknown to me) '
                                            'online]',
                                            'Indicate your extent of agreement with the following statements about '
                                            'your intentions during/after the vacations on a scale of 1 to 7 where 7 '
                                            'indicates strongly agree and 1 indicates strongly disagree [I would '
                                            'communicate about the desti6tion to strangers via online reviews or '
                                            'online communities (e.g., TripAdvisor, Google reviews, other official '
                                            'review websites)]',
                                            'Indicate your extent of agreement with the following statements about '
                                            'your intentions during/after the vacations on a scale of 1 to 7 where 7 '
                                            'indicates strongly agree and 1 indicates strongly disagree [When I see '
                                            'questions about the desti6tion from strangers in online forums, I will '
                                            'share my comments about the same]']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'Tourist Destination': 'coded background question without a key in the deposit',
                  'How long did you stay at the desti6tion': 'coded background question without a key in the deposit',
                  'Age': 'coded background question without a key in the deposit',
                  'Gender': 'coded background question without a key in the deposit',
                  'Highest Educatio6l Qualification': 'coded background question without a key in the deposit',
                  'Family Income Monthly (Approximate)': 'coded background question without a key in the deposit',
                  'Profession': 'coded background question without a key in the deposit',
                  'Have you posted your previous tourism experiences on online sites or forums? Please tick the appropriate option': 'coded '
                                                                                                                                     'background '
                                                                                                                                     'question '
                                                                                                                                     'without '
                                                                                                                                     'a '
                                                                                                                                     'key '
                                                                                                                                     'in '
                                                                                                                                     'the '
                                                                                                                                     'deposit',
                  'Have you used online reviews to research your destination prior to the trip?': 'coded background '
                                                                                                  'question without '
                                                                                                  'a key in the '
                                                                                                  'deposit',
                  'Which website do you use most to research your destination prior to your visit?': 'coded '
                                                                                                     'background '
                                                                                                     'question '
                                                                                                     'without a key '
                                                                                                     'in the deposit',
                  'Which website is your first choice to post holiday comments?': 'coded background question without '
                                                                                  'a key in the deposit'},
  'label': 'prasad_2026_destination_ewom',
  'item_names': {'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Pleasant Weather]': 'cdi1',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Beautiful Scenery]': 'cdi2',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Unique Flora and Fau6 (Varied plants and wildlife)]': 'cdi3',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Green Cover (6tural or planted vegetation)]': 'cdi4',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Excellent Transport facilities]': 'cdi5',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Excellent Hotels and Restaurants]': 'cdi6',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Pollution is less]': 'cdi7',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Parking facilities are adequate]': 'cdi8',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Good shopping centres]': 'cdi9',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Adventure based activities are present]': 'cdi10',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Amusement, Recreation and Entertainment facilities are available]': 'cdi11',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Local Cuisine and food outlets are excellent ]': 'cdi12',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Offers places of historical or cultural interest]': 'cdi13',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Handicrafts unique to the area]': 'cdi14',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Rich customs and religious traditions]': 'cdi15',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Stable political environment]': 'cdi16',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Less crime rate]': 'cdi17',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [A Safe and secure desti6tion]': 'cdi18',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Hospitable and friendly residents]': 'cdi19',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Easy to converse with local people]': 'cdi20',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Good civic sense (People at the desti6tion give importance to cleanliness and follow rules)]': 'cdi21',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Quality of life of the people at the desti6tion is good]': 'cdi22',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Eco2mic mode of transportation is available]': 'cdi23',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Prices for food and accommodation is reaso6ble]': 'cdi24',
                 'Please indicate your extent of agreement with the following statements/phrases about the destination you visited on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Appropriately priced shopping merchandise]': 'cdi25',
                 'Please indicate your extent of agreement about the emotions attributed to the destination you visited on a scale of 1 to 7, where 7 indicates strongly agree and 1 indicates strongly disagree [Pleasant Desti6tion]': 'adi1',
                 'Please indicate your extent of agreement about the emotions attributed to the destination you visited on a scale of 1 to 7, where 7 indicates strongly agree and 1 indicates strongly disagree [Relaxing Desti6tion]': 'adi2',
                 'Please indicate your extent of agreement about the emotions attributed to the destination you visited on a scale of 1 to 7, where 7 indicates strongly agree and 1 indicates strongly disagree [Arousing Desti6tion]': 'adi3',
                 'Please indicate your extent of agreement about the emotions attributed to the destination you visited on a scale of 1 to 7, where 7 indicates strongly agree and 1 indicates strongly disagree [Exciting Desti6tion]': 'adi4',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [It gives me pleasure to purchase a vacation]': 'inv1',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Buying a vacation is like buying a gift for myself]': 'inv2',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [A vacation is a pleasure to me.]': 'inv3',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [I attach great importance to a vacation.]': 'inv4',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [One can say vacation destinations interests me a lot.]': 'inv5',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Whenever one buys a vacation, one never really k2ws whether it is the one that should have been bought.]': 'inv6',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [When I face a variety of vacation choices, always feel a bit at loss to make my choice. ]': 'inv7',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [Choosing a vacation desti6tion is rather complicated.]': 'inv8',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [When one purchases a vacation, one is never certain of one’s choice.]': 'inv9',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [It is really an2ying to purchase a vacation that is 2t suitable.]': 'inv10',
                 'Indicate your extent of agreement about the following statements on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [If, after I bought a vacation, my choice proves to be poor, I would be really upset.]': 'inv11',
                 'Indicate your extent of agreement with the following statements about your intentions during/after the vacations on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [I would share my desti6tion experiences with my friends or family online]': 'ewom1',
                 'Indicate your extent of agreement with the following statements about your intentions during/after the vacations on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [When asked online by my friends or family members about the desti6tion, I will share my comments.]': 'ewom2',
                 'Indicate your extent of agreement with the following statements about your intentions during/after the vacations on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [I would post about the desti6tion on my perso6l social networks (e.g. Facebook, Instagram, WhatsApp, twitter and Blogs)]': 'ewom3',
                 'Indicate your extent of agreement with the following statements about your intentions during/after the vacations on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [I would share my comments on the desti6tion to strangers (people unknown to me) online]': 'ewom4',
                 'Indicate your extent of agreement with the following statements about your intentions during/after the vacations on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [I would communicate about the desti6tion to strangers via online reviews or online communities (e.g., TripAdvisor, Google reviews, other official review websites)]': 'ewom5',
                 'Indicate your extent of agreement with the following statements about your intentions during/after the vacations on a scale of 1 to 7 where 7 indicates strongly agree and 1 indicates strongly disagree [When I see questions about the desti6tion from strangers in online forums, I will share my comments about the same]': 'ewom6'}}]

# rows written per table (asserted)
EXPECT = {'prasad_2026_affective_destination_image': 2520,
 'prasad_2026_cognitive_destination_image': 15750,
 'prasad_2026_ewom_intention': 3780,
 'prasad_2026_vacation_involvement': 6930}


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
