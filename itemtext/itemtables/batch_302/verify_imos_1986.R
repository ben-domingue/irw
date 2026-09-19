# Verification for imos_1986 (#2228, batch_302).
# See verify_imos_common.R for what these tables are and the shared routes.
# Same treatment as the nine Olympiad years in batch_301: the problem
# statements come from the official English paper and the notation is shipped
# flattened, per #2228.
YEAR <- 1986
NOT_ESTABLISHED <- paste0(
"  THE MATHEMATICAL NOTATION. item_text is a plain-text extraction of the\n",
"  official English PDF, so display equations run inline and superscripts and\n",
"  fractions are lost. Mechanical artefacts were repaired (big delimiters, lost\n",
"  fi/fl ligatures, stray page numbers) but the flattening is inherent. A reader\n",
"  needing the exact statement should use the source PDF in source_ref.\n")
source("itemtables/batch_302/verify_imos_common.R")
