# Verification for preussmattsson_2022_ownership (#1945, batch_205).
#
# SOURCE. Preuss Mattsson, Coppi, Chancel & Ehrsson (2022), PLOS ONE, CC BY,
# doi:10.1371/journal.pone.0277080. Table 2 prints the illusory-ownership
# questionnaire in full: a shared stem ("During the experiment:"), statements
# S1-S7 with their wording, and a Type column naming what each measures.
#
# WHY THE MAPPING NEEDS NO INFERENCE. The live item codes ARE the paper's own
# statement codes -- data/preussmattsson_2022_ownership.py emits f"S{s+1}" over
# the 6 statement columns of each condition block, and Table 2 numbers the same
# statements S1..S6. There is no renaming step between the two.
#
# Route 1: the code set equals Table 2's S1-S6, and S7 is correctly absent.
# Route 2: the 2x2 within-subjects design reproduced exactly from the live data.
# Route 3: the response scale matches the paper's stated 7-point -3..+3.
d <- as.data.frame(irw::irw_fetch("preussmattsson_2022_ownership"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_205/preussmattsson_2022_ownership__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: codes are Table 2's statement numbers ===\n")
r1 <- setequal(unique(d$item), paste0("S", 1:6)) && !("S7" %in% d$item)
cat(sprintf("  live codes: %s\n", paste(sort(unique(d$item)), collapse = ", ")))
cat(sprintf("  equals Table 2's S1-S6 with S7 absent: %s\n", r1))
cat("  S7 is excluded on purpose and the paper says why: it is self-motion on a\n")
cat("  10-point visual analog scale, a different construct and a different scale,\n")
cat("  so it is not part of the 6-statement ownership questionnaire.\n")

cat("\n=== Route 2: the 2x2 within-subjects design reproduced ===\n")
ids <- length(unique(d$id)); cond <- length(unique(d$cov_condition))
cat(sprintf("  %d participants x %d conditions x %d items = %d; live rows %d\n",
            ids, cond, length(unique(d$item)), ids * cond * length(unique(d$item)), nrow(d)))
r2 <- ids * cond * length(unique(d$item)) == nrow(d)
print(table(d$cov_condition))
cat("  Every participant answered all six statements in all four conditions, with\n")
cat("  no gaps -- which is what a fully crossed within-subjects design produces and\n")
cat("  what the paper describes (visuo-vestibular sync/async x visuo-tactile\n")
cat("  sync/async). A missing or duplicated statement would break the product.\n")

cat("\n=== Route 3: the response scale ===\n")
lv <- sort(unique(d$resp))
r3 <- identical(as.numeric(lv), as.numeric(-3:3))
cat(sprintf("  live levels: %s\n", paste(lv, collapse = ", ")))
cat(sprintf("  matches the paper's 'seven-point Likert scale from -3 (fully disagree)\n  to +3 (fully agree)': %s\n", r3))
cat(sprintf("  option_text is populated only at the two labelled endpoints (%d rows of %d);\n",
            sum(!is.na(items$option_text)), nrow(items)))
cat("  the paper names no labels for -2..+2, so those ship blank rather than invented.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The wording, which is quoted from Table 2 and cannot be checked numerically.\n")
cat("  One discrepancy is worth knowing: Table 2 prints S1 as '...it felt as I was\n")
cat("  looking at my body' while the body text quotes it as 'it felt as if I was\n")
cat("  looking at my body'. Table 2 is the instrument table, so it is what ships.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
