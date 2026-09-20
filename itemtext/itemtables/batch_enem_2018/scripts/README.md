# How batch_enem_2018 was built

The pipeline is in `itemtext/enem_pipeline/`, one copy for every
year. This file records the pinned versions that produced THIS
batch, so the build can be reproduced exactly:

    cd itemtext/enem_pipeline
    python3 42_rebuild.py --year 2018
    python3 31_assemble_batch.py --year 2018

| script | pin used | md5 |
|---|---|---|
| 12_parse_booklet_pdf.py | 12_parse_booklet_pdf.v10.py | `3b22ee3ce113c770ce7b2b1f98e3c1f7` |
| 13_join.py | 13_join.v10.py | `d8f8c3fe64e6cb3e723f4d448c2b21ef` |
| 14_fill_gaps.py | 14_fill_gaps.v2.py | `b5c20097b459d08e1082cb9fa96a0d04` |
| 17_decode_2018.py | 17_decode_2018.v3.py | `9cbaf8812005c0df61d26cf700ec358f` |
| 20_geom_options.py | 20_geom_options.v2.py | `5b57dccf440a07aa2e8e1bc1a32ba62d` |
| 20_verify_gabarito_microdata.py | 20_verify_gabarito_microdata.v3.py | `b8f9628250df9dd5ff7cb3bb14b30efa` |
| 23_decode_symbolmt.py | 23_decode_symbolmt.v2.py | `a88f54b15f7658a46b5c5548e364b088` |
| 25_repair_2021.py | 25_repair_2021.v1.py | `2dc1f84f6a30b6f95907adc4e4fe17ce` |
| 26_strip_page_furniture.py | 26_strip_page_furniture.v10.py | `04847b7ab76f905b52818633cc415965` |
| 29_decode_2021_notation.py | 29_decode_2021_notation.v3.py | `d9c0fa833f287e1ce128cd363bd4dac1` |
| 43_normalize_glyphs.py | 43_normalize_glyphs.v1.py | `90db23205f06ad41a9ccd0d4f119b7a8` |
| 46_strip_option_letter.py | 46_strip_option_letter.v3.py | `86b69494098458373fb90d662417ddde` |
| 48_mark_scripts.py | 48_mark_scripts.v6.py | `286d15d03b799de95c40dc9b00d41124` |
| 49_option_conventions.py | 49_option_conventions.v2.py | `a7c7870a5774efa50e1ce52d3e1acb66` |
| 53_stacked_fractions.py | 53_stacked_fractions.v1.py | `eecd7aa92e357e3e1d05c548ab64624c` |
| 54_relocate_descriptions.py | 54_relocate_descriptions.v1.py | `5445a1f88bd48a2f315dfa1c29182f88` |
