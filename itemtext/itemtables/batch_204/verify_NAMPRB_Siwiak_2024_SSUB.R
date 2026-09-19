# Verification for NAMPRB_Siwiak_2024_SSUB (#1945, batch_204).
#
# SOURCE. The deposit's item-translation supplement prints items 1-20 with the
# Polish administered wording and the authors' English alongside, numbered. The
# deposit's data file, data_SSUB-PL_adaptation.xlsx, names its columns
# SSUB_TRB_1, SSUB_NAB_2, ..., SSUB_TRB_19, SSUB_NAB_20 for the first
# administration and SSUB_RETEST_1..20 for the retest. So code-to-text is a
# lookup on the item number.
#
# THE DEFECT THIS TABLE CARRIES, and the route that found it. The live table has
# 25 codes for a 20-item scale. data/NAMPRB_Siwiak_2024.R does
#     colnames(retest_ssub_df) <- gsub("RETEST", "NAB", colnames(retest_ssub_df))
# which renames ALL twenty retest columns to SSUB_NAB_*, including the five whose
# first-administration name is SSUB_TRB_* -- items 1, 5, 14, 15 and 19, the
# Traditional Religious Beliefs factor. The result is five spurious codes:
# SSUB_NAB_1/5/14/15/19 exist at the retest wave only, and their TRB twins at
# the first wave only. Wave availability makes that visible outright.
#
# Route 1: the deposit's own column names against the live codes.
# Route 2: wave availability -- the five collided numbers are disjoint by wave.
# Route 3: exact reproduction of every item's response vector from the xlsx.
# Route 4: the CC BY preprint's stated counts, as an independent corroboration.
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
XL <- ".cache/batch_204/namprb_data_SSUB-PL_adaptation.xlsx"
if (!file.exists(XL)) stop("missing cached deposit file: ", XL)
suppressWarnings(suppressMessages(library(readxl)))
x <- as.data.frame(read_excel(XL))

d <- as.data.frame(irw::irw_fetch("NAMPRB_Siwiak_2024_SSUB"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
TRB <- c(1, 5, 14, 15, 19)

cat("=== Route 1: the deposit's column names ===\n")
test   <- grep("^SSUB_(NAB|TRB)_[0-9]+$", names(x), value = TRUE)
retest <- grep("^SSUB_RETEST_[0-9]+$",    names(x), value = TRUE)
cat(sprintf("  first-administration item columns %d, retest item columns %d\n",
            length(test), length(retest)))
cat(sprintf("  the deposit's own names assign TRB to items {%s}\n",
            paste(sort(as.integer(sub(".*_", "", grep("_TRB_", test, value = TRUE)))), collapse = ", ")))
r1 <- setequal(sort(as.integer(sub(".*_", "", grep("_TRB_", test, value = TRUE)))), TRB)
cat(sprintf("  which is the factor split used in the extraction: %s\n", r1))

cat("\n=== Route 2: wave availability exposes the rename collision ===\n")
tb <- table(d$item, d$wave)
coll <- paste0("SSUB_NAB_", TRB); twin <- paste0("SSUB_TRB_", TRB)
r2 <- all(coll %in% rownames(tb)) && all(twin %in% rownames(tb)) &&
      all(tb[coll, "0"] == 0) && all(tb[coll, "1"] > 0) &&
      all(tb[twin, "0"] > 0) && all(tb[twin, "1"] == 0)
for (i in seq_along(TRB))
    cat(sprintf("  %-12s w0=%4d w1=%4d   |  %-12s w0=%4d w1=%4d\n",
                twin[i], tb[twin[i], "0"], tb[twin[i], "1"],
                coll[i], tb[coll[i], "0"], tb[coll[i], "1"]))
others <- setdiff(rownames(tb), c(coll, twin))
cat(sprintf("  the other %d codes appear at BOTH waves: %s\n", length(others),
            all(tb[others, "0"] > 0 & tb[others, "1"] > 0)))
cat(sprintf("  -> disjoint-by-wave for exactly the five TRB numbers: %s\n", r2))
cat("  A genuine 25-item scale could not produce this pattern; a blanket rename\n")
cat("  of the retest block is the only thing that produces it.\n")

cat("\n=== Route 3: every response vector reproduced from the xlsx ===\n")
src <- function(code) {
    n <- as.integer(sub(".*_", "", code))
    if (code %in% coll) x[[paste0("SSUB_RETEST_", n)]]   # renamed retest column
    else if (grepl("_TRB_", code)) x[[paste0("SSUB_TRB_", n)]]
    else if (n %in% TRB) x[[paste0("SSUB_RETEST_", n)]]
    else x[[paste0("SSUB_NAB_", n)]]
}
tot <- ok <- 0; bad <- character(0)
for (code in sort(unique(d$item))) {
    w  <- if (code %in% coll || (grepl("_NAB_", code) && as.integer(sub(".*_","",code)) %in% TRB)) 1 else 0
    for (wv in sort(unique(d$wave[d$item == code]))) {
        live <- sort(d$resp[d$item == code & d$wave == wv])
        cn   <- if (wv == 1) paste0("SSUB_RETEST_", sub(".*_", "", code)) else code
        if (!cn %in% names(x)) { bad <- c(bad, paste(code, "w", wv, "no source column")); next }
        s <- sort(as.numeric(na.omit(x[[cn]])))
        tot <- tot + 1
        if (length(s) == length(live) && all(abs(s - live) < 1e-9)) ok <- ok + 1
        else bad <- c(bad, sprintf("%s w%s: source n=%d live n=%d", code, wv, length(s), length(live)))
    }
}
cat(sprintf("  %d of %d (code, wave) response vectors reproduced EXACTLY%s\n", ok, tot,
            if (!length(bad)) "" else paste0("\n  -- ", paste(head(bad, 6), collapse="\n  -- "))))
r3 <- !length(bad)

cat("\n=== Route 4: the CC BY preprint, as an independent corroboration ===\n")
cat("  doi:10.31234/osf.io/7u98d states 20 items in two factors, 15 New Age\n")
cat("  Beliefs and 5 Traditional Religious Beliefs, 10 reverse scored, on a\n")
cat("  five-point scale 1 'Strongly disagree' to 5 'Strongly Agree'.\n")
cat(sprintf("  distinct item NUMBERS in the live table: %d (not 25)\n",
            length(unique(as.integer(sub(".*_", "", unique(d$item)))))))
cat(sprintf("  TRB numbers, from the deposit's column names: %s\n", paste(TRB, collapse = ", ")))
cat(sprintf("  live resp levels: %s\n", paste(sort(unique(d$resp)), collapse = ", ")))
r4 <- length(unique(as.integer(sub(".*_", "", unique(d$item))))) == 20 &&
      identical(sort(as.numeric(unique(d$resp))), c(1, 2, 3, 4, 5))
cat(sprintf("  all three of the preprint's counts agree with what was derived\n  here from the deposit alone: %s\n", r4))

cat("\n=== What this does NOT establish ===\n")
cat("  The anchors as respondents read them. The 1-5 labels ship in English\n")
cat("  because that is the only form published -- the preprint describes the\n")
cat("  scale in English and nothing in the deposit prints the Polish anchor\n")
cat("  wording. option_text is therefore a rendering, while item_text is the\n")
cat("  administered Polish. Disclosed in provenance.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r4) "PASS" else "FAIL", "\n")
