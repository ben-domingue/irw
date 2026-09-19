# verify_yang_2023_emotional_eating_eesr.R
#
# CLAIM UNDER TEST. data/yang_2023_emotional_eating.py assigns item codes
# POSITIONALLY: ees_cols = ["When you have the following emotions, the degree of
# desire to eat is"] + [every column whose header starts with "@10"], then
# EESR_{i+1} := ees_cols[i].  The shipped item_text is the header sitting at that
# same position (prefix "@10." / "@10," stripped), so the whole mapping rests on
# the claim that live EESR_i IS raw column 4+(i-1) of the PLOS S1 workbook.
#
# That is falsifiable two ways, both run below:
#   (a) BLOCK MEMBERSHIP. The workbook carries a pre-computed "EESR" total column.
#       Only the 23-column window starting at index 4 reproduces it, for all 494
#       respondents.  Shifted windows fail on hundreds of rows.
#   (b) PER-ITEM IDENTITY. Every live item's mean/sd must equal the raw column at
#       its claimed position, exactly (same 494 responses, no imputation). The 23
#       raw column means are pairwise distinct, so ANY permutation of two items
#       breaks this -- which is the thing a positional off-by-one or a swap would
#       do.
#
# Source: PLOS ONE 10.1371/journal.pone.0280701 S1 Data (CC BY 4.0), sheet "12.5".

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "yang_2023_emotional_eating_eesr"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0280701.s001"
cands <- c("itemtext/.cache/yang_2023_emotional_eating_eesr/s001.xlsx",
           ".cache/yang_2023_emotional_eating_eesr/s001.xlsx")
path <- cands[file.exists(cands)][1]
if (is.na(path)) {
    path <- tempfile(fileext = ".xlsx")
    download.file(S1, path, mode = "wb", quiet = TRUE)
}
raw <- as.data.frame(read_excel(path, sheet = "12.5"))

OFFSET <- 5                      # 1-based column of EESR_1 (0-based 4 in pandas)
blk <- raw[, OFFSET:(OFFSET + 22)]
blk[] <- lapply(blk, function(v) suppressWarnings(as.numeric(v)))

cat("== (a) block membership: which 23-column window reproduces the stored EESR total ==\n")
for (st in 3:9) {
    w <- raw[, st:(st + 22)]
    w[] <- lapply(w, function(v) suppressWarnings(as.numeric(v)))
    hit <- sum(rowSums(w) == raw$EESR, na.rm = TRUE)
    cat(sprintf("  start col %d: %3d / %d rows match%s\n",
                st, hit, nrow(raw), if (st == OFFSET) "   <- claimed" else ""))
}
a_ok <- sum(rowSums(blk) == raw$EESR, na.rm = TRUE) == nrow(raw)

cat("\n== (b) per-item identity: live table vs raw column at the claimed position ==\n")
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
cat(sprintf("%-9s %6s %6s %9s %9s %9s %9s %11s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "sd_raw", "sd_live", "mean_diff"))
worst <- 0
for (i in 1:23) {
    it <- paste0("EESR_", i)
    v <- blk[[i]]; v <- v[!is.na(v) & v >= 1 & v <= 5]
    lv <- d$resp[d$item == it]; lv <- lv[!is.na(lv)]
    dm <- mean(lv) - mean(v)
    worst <- max(worst, abs(dm))
    cat(sprintf("%-9s %6d %6d %9.4f %9.4f %9.4f %9.4f %11.2e\n",
                it, length(v), length(lv), mean(v), mean(lv), sd(v), sd(lv), dm))
}
gaps <- as.matrix(dist(sapply(1:23, function(i) mean(blk[[i]], na.rm = TRUE))))
diag(gaps) <- Inf
cat(sprintf("\nsmallest gap between any two raw column means: %.4f -- so a swap of any\n", min(gaps)))
cat("two items would move at least one mean by that much, far above the 1e-12 tolerance.\n")
cat(sprintf("largest observed |mean_live - mean_raw|: %.3e\n", worst))

cat("\nWhat this does NOT establish: EESR_1 ships BLANK item_text, because the header at\n")
cat("that position is the matrix-question stem (an export quirk) rather than that item's\n")
cat("own emotion label, which the deposit does not preserve. Its POSITION is verified by\n")
cat("both checks above; its wording is simply absent, not inferred. Note also that the\n")
cat("deposit's English collapses two pairs of distinct items onto identical labels\n")
cat("(EESR_5/EESR_20 'hostile', EESR_13/EESR_22 'depressed'); their codes are verified,\n")
cat("their English text cannot be told apart.\n")

cat(if (a_ok && worst < 1e-12) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
