# Verification for imos_2016 (#2228, batch_301).
# See verify_imos_common.R for what these tables are and the shared routes.
#
# 2016 IS THE ONE YEAR TRANSCRIBED BY EYE, and so the one year whose notation is
# correct. Its PDF carries a symbol-font text layer that extracts as mojibake
# (the header comes out as "▼♦♥❞❛②✱❏✉❧②✶✶✱✷✵✶✻" for "Monday, July 11, 2016"),
# the same failure as the Kruti-Dev Hindi booklets in batch_203. The pages were
# rendered at 150 dpi and read as images instead, which means superscripts and
# subscripts survive here -- P(n) = n^2 + n + 1, A_1 A_2 ... A_k -- where the
# text-extracted years lose them.
YEAR <- 2016
NOT_ESTABLISHED <- paste0(
"  Nothing about the notation, unusually for this batch: 2016 was read from\n",
"  rendered page images rather than the broken text layer, so superscripts and\n",
"  subscripts are preserved. What it shares with the other years is that the\n",
"  transcription is by hand and unverified symbol by symbol against the source.\n")
source("itemtables/batch_301/verify_imos_common.R")
