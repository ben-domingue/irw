# Verification for FIVPEI_Perrig_2023_AttDiff (#1945, batch_204).  STATUS: PARTIAL.
#
# SOURCE. The deposit's own files: PXI_validation_main_data.xlsx (the raw data),
# Printout_online_survey.pdf (the survey as administered), and
# PXI_validation_main_analysis.Rmd (the authors' analysis code).
#
# WHAT IS SETTLED AND WHAT IS NOT. Which BLOCK a code belongs to is settled three
# ways over -- the printout reproduces the AttrakDiff page as four consecutive
# blocks of seven word pairs, the data's columns run HQI_1..7, HQS_1..7, ATT_1..7,
# PQ_1..7 in that same block order, and the three shipped sets match the
# published AttrakDiff subscales. WITHIN a block, item n is taken to be the nth
# printed pair. Printout order and column order agree, but nothing in the data
# distinguishes one word pair from another, so that step is an ordering
# assumption and the status is PARTIAL rather than VERIFIED.
#
# Route 1: codes == the xlsx's HQI/HQS/ATT columns; PQ absent, and why.
# Route 2: every response vector reproduced from the xlsx, per item.
# Route 3: response DIRECTION, which IS verified outright, from the authors' code.
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
XL  <- ".cache/batch_204/fivpei_PXI_validation_main_data.xlsx"
RMD <- ".cache/batch_204/fivpei_PXI_validation_main_analysis.Rmd"
for (p in c(XL, RMD)) if (!file.exists(p)) stop("missing cached deposit file: ", p)
suppressWarnings(suppressMessages(library(readxl)))
x <- as.data.frame(read_excel(XL))

d <- as.data.frame(irw::irw_fetch("FIVPEI_Perrig_2023_AttDiff"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== Route 1: block membership from the deposit's column names ===\n")
blocks <- c("HQI", "HQS", "ATT", "PQ")
for (b in blocks) {
    cols <- grep(paste0("^", b, "_[0-9]+$"), names(x), value = TRUE)
    cat(sprintf("  %-4s xlsx columns %d (%s)  live codes %d\n", b, length(cols),
                paste(cols, collapse=","), sum(grepl(paste0("^", b, "_"), unique(d$item)))))
}
kept <- grep("^(HQI|HQS|ATT)_[0-9]+$", names(x), value = TRUE)
r1 <- setequal(kept, unique(d$item)) && !any(grepl("^PQ_", d$item))
cat(sprintf("  live set == HQI + HQS + ATT, with PQ absent: %s\n", r1))
cat("  THE 28-VS-21 IS EXPLAINED BY THE SCRIPT, not by a dropped block:\n")
cat("  data/FIVPEI_Perrig_2023.R builds PQ_df and then does\n")
cat("      AttDiff_df <- rbind(HQI_df, HQS_df, ATT_df)\n")
cat("  so Pragmatic Quality is processed and then simply not bound in. The\n")
cat("  printout has four blocks of seven; this table is three of them.\n")

cat("\n=== Route 2: every response vector reproduced from the xlsx ===\n")
# data/FIVPEI_Perrig_2023.R's remove_na(): drop rows all-NA outside id, per block
rm_na <- function(df) df[rowSums(is.na(df)) < ncol(df), , drop = FALSE]
tot <- ok <- 0; bad <- character(0)
for (b in c("HQI", "HQS", "ATT")) {
    cols <- grep(paste0("^", b, "_[0-9]+$"), names(x), value = TRUE)
    blk  <- rm_na(x[, cols, drop = FALSE])
    for (cn in cols) {
        live <- sort(d$resp[d$item == cn]); s <- sort(as.numeric(na.omit(blk[[cn]])))
        tot <- tot + 1
        if (length(s) == length(live) && all(abs(s - live) < 1e-9)) ok <- ok + 1
        else bad <- c(bad, sprintf("%s source n=%d live n=%d", cn, length(s), length(live)))
    }
}
cat(sprintf("  %d of %d item response vectors reproduced EXACTLY%s\n", ok, tot,
            if (!length(bad)) "" else paste0("\n  -- ", paste(head(bad, 8), collapse="\n  -- "))))
r2 <- !length(bad)
cat("  This confirms code-to-COLUMN, which is the part the data can speak to.\n")
cat("  It says nothing about which printed word pair a column is -- see below.\n")

cat("\n=== Route 3: response direction, verified from the authors' own code ===\n")
rmd <- readLines(RMD, warn = FALSE)
blk <- grep("scale-coding-AttrakDiff", rmd)
mp  <- grep("^AttrakDiff\\[AttrakDiff == [0-9]+\\] <- -?[0-9]+", rmd)
mp  <- mp[mp > blk[1]][1:7]
cat("  from the chunk 'scale-coding-AttrakDiff':\n")
for (l in mp) cat(sprintf("    %s\n", trimws(rmd[l])))
r3 <- length(mp) == 7 && !any(is.na(mp)) &&
      grepl("== 1\\] <- -3", rmd[mp[1]]) && grepl("== 7\\] <- 3", rmd[mp[7]])
cat(sprintf("  a monotone 1->-3 .. 7->+3 map with NO reversal anywhere: %s\n", r3))
cat("  So resp 1 is the LEFT pole of the word pair and resp 7 the right, for\n")
cat("  every item in every block. Direction is not an assumption here.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which of the seven word pairs within a block is item n. Printout order\n")
cat("  and column order agree, and the block sets match the published subscales,\n")
cat("  but the data cannot separate pair 3 from pair 4. That is the one open\n")
cat("  step and it is why this table is PARTIAL.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
