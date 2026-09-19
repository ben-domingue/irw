# Verification for imos_2003 (#2228, batch_301).
# See verify_imos_common.R for what these tables are and the shared routes.
YEAR <- 2003
NOT_ESTABLISHED <- paste0(
"  THE MATHEMATICAL NOTATION. item_text is a plain-text extraction of the\n",
"  official English PDF, so display equations are flattened inline and\n",
"  superscripts and fractions are lost: n^2 appears as 'n2', a_1 as 'a1', and\n",
"  1/n as '1 n'. Mechanical artefacts were repaired (big delimiters, lost fi/fl\n",
"  ligatures, stray page numbers) but the flattening is inherent and is NOT a\n",
"  transcription this project can vouch for symbol by symbol. A reader who\n",
"  needs the exact statement should consult the source PDF named in\n",
"  source_ref. Shipped this way deliberately, per #2228.\n")
source("itemtables/batch_301/verify_imos_common.R")
