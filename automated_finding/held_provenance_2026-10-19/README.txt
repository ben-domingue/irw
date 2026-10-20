gilbert_2026_dep_symptoms.csv -- built, validated, NOT staged for upload.

Held on provenance, not on quality: the deposit (10.7910/DVN/G68C5Y, CC
BY-NC-SA 4.0) describes this file as "9 dichotomous DSM-5 items in a
psychotherapy RCT" and its own analysis script refers to the data only as
"per McNeish, limit to C group only". It names no trial, paper or source
deposit, so the deposit's licence does not by itself establish the
originating trial's redistribution terms -- datastandard.md's "scraped or
relabelled third-party data" clause.

Resolution: irw#3120 asks Josh Gilbert to name the source (opened and
assigned 2026-10-19). One answer closes it, and
the table (256 patients x up to 28 sessions x 9 items = 49,598 responses)
is ready to move into irw_output/ unchanged if the answer is clean.

Rebuild with: python3 data/gilbert_2026_dep_symptoms.py
