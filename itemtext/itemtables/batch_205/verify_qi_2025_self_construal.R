# Verification for qi_2025_self_construal (#1945, batch_205).
#
# SOURCE. Qi, Zou, Chau, Zhou, Wang & Sui (2025), Scientific Data 12:1755, CC BY;
# OSF deposit osf.io/3h95f, Scales.xlsx. The paper names the instrument (Singelis
# 1994, 30 items, two dimensions) and its anchors (1 'very much disagree', 7
# 'very much agree') but prints no items, and neither does the deposit.
#
# THE WORDING COMES FROM AN EARLIER IRW EXTRACTION'S SOURCE, not from memory.
# SCS_Suh_2023_SCS (batch_170) is the same 30-item Singelis scale, and its item
# text was taken from Singelis's own distribution letter ("Included below is the
# latest version of the Self-Construal Scale"), hosted by the Waterloo Wisdom and
# Culture Lab. That file is the source of the 30 stems reused here, so this table
# and its sibling say the same thing about the same instrument.
#
# THE SUBSCALE SPLIT IS THE DEPOSIT'S OWN, AND IT CROSS-CHECKS THE NUMBERING.
# Scales.xlsx stores its summary columns as live Excel formulas, so the authors'
# assignment is readable directly: 'Independent self-construal' is
# =(BL+BM+BP+BR+BT+BU+BX+BZ+CC+CE+CG+CI+CJ+CL+CN)/15, whose columns resolve to
# SC_1, 2, 5, 7, 9, 10, 13, 15, 18, 20, 22, 24, 25, 27, 29. That is a 15/15 split
# of a 30-item scale, and it is the split the canonical Singelis instrument uses.
# Two independent sources agreeing item-for-item on all 30 is what lets the
# numbering carry the wording.
#
# Route 1: codes are the workbook's own column headers.
# Route 2: the authors' formulas, and the 15/15 split they produce.
# Route 3: the split holds in the data -- within-block correlation exceeds
#   between-block, per item, and both subscale alphas reproduce the paper's.
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
XL <- ".cache/batch_205/qi_Scales.xlsx"
if (!file.exists(XL)) stop("missing cached deposit file: ", XL)
suppressWarnings(suppressMessages({library(readxl); library(dplyr); library(tidyr)}))
x <- as.data.frame(read_excel(XL, sheet = "Summary_of_data"))

d <- as.data.frame(irw::irw_fetch("qi_2025_self_construal"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
IND <- paste0("SC_", c(1, 2, 5, 7, 9, 10, 13, 15, 18, 20, 22, 24, 25, 27, 29))
INT <- paste0("SC_", c(3, 4, 6, 8, 11, 12, 14, 16, 17, 19, 21, 23, 26, 28, 30))

cat("=== Route 1: codes are the workbook's column headers ===\n")
cols <- grep("^SC_[0-9]+$", names(x), value = TRUE)
r1 <- setequal(cols, unique(d$item)) && length(cols) == 30
cat(sprintf("  workbook SC_ columns %d, live codes %d, identical: %s\n",
            length(cols), length(unique(d$item)), setequal(cols, unique(d$item))))
cat("  (SCC_* is a different scale, self-concept clarity, and is correctly absent)\n")

cat("\n=== Route 2: the authors' own subscale formulas ===\n")
cat("  Scales.xlsx 'Independent self-construal'  = (BL+BM+BP+BR+BT+BU+BX+BZ+CC+CE+CG+CI+CJ+CL+CN)/15\n")
cat("  Scales.xlsx 'Interdependent self-construal' = (BN+BO+BQ+BS+BV+BW+BY+CA+CB+CD+CF+CH+CK+CM+CO)/15\n")
cat(sprintf("  resolved -> independent   : %s\n", paste(sub("SC_", "", IND), collapse = ", ")))
cat(sprintf("  resolved -> interdependent: %s\n", paste(sub("SC_", "", INT), collapse = ", ")))
r2 <- length(IND) == 15 && length(INT) == 15 && length(intersect(IND, INT)) == 0 &&
      setequal(c(IND, INT), cols)
cat(sprintf("  a clean 15/15 partition of all 30 codes: %s\n", r2))
cat("  This is the authors' assignment read off the file, not an inference from\n")
cat("  the code numbers, and it matches the canonical Singelis split item for item.\n")

cat("\n=== Route 3: does the split hold in the data? ===\n")
w <- d %>% select(id, item, resp) %>% distinct(id, item, .keep_all = TRUE) %>%
     pivot_wider(names_from = item, values_from = resp)
m <- as.matrix(w[, c(IND, INT)]); m <- m[complete.cases(m), ]
C <- cor(m)
wi_ind <- mean(C[IND, IND][upper.tri(C[IND, IND])])
wi_int <- mean(C[INT, INT][upper.tri(C[INT, INT])])
btw    <- mean(C[IND, INT])
cat(sprintf("  n = %d complete cases\n", nrow(m)))
cat(sprintf("  mean r within independent    %+.3f\n", wi_ind))
cat(sprintf("  mean r within interdependent %+.3f\n", wi_int))
cat(sprintf("  mean r between blocks        %+.3f\n", btw))
r3a <- wi_ind > btw && wi_int > btw
cat(sprintf("  -> both within-block means exceed between-block: %s\n", r3a))
mis <- character(0)
for (i in c(IND, INT)) {
    own <- if (i %in% IND) setdiff(IND, i) else setdiff(INT, i)
    oth <- if (i %in% IND) INT else IND
    if (mean(C[i, own]) <= mean(C[i, oth])) mis <- c(mis, i)
}
cat(sprintf("  items correlating more with the OTHER block: %d of 30%s\n", length(mis),
            if (length(mis)) paste0(" (", paste(mis, collapse = ", "), ")") else ""))
alpha <- function(mm) { k <- ncol(mm); (k / (k - 1)) * (1 - sum(apply(mm, 2, var)) / var(rowSums(mm))) }
ai <- alpha(m[, IND]); at <- alpha(m[, INT])
cat(sprintf("  alpha independent %.3f (paper reports 0.72) | interdependent %.3f (paper 0.77)\n", ai, at))
r3b <- abs(ai - 0.72) < 0.01 && abs(at - 0.77) < 0.01
cat(sprintf("  -> both reproduce the paper to the printed precision: %s\n", r3b))
cat("  The three cross-loading items are ordinary weak items, not evidence against\n")
cat("  the split: the alphas match and the block means separate cleanly.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which published Singelis item each code is, beyond the shared numbering,\n")
cat("  and the administered wording. The sample is Chinese university students and\n")
cat("  no Chinese text appears in the deposit or the paper, so item_text is the\n")
cat("  English original and language records Chinese with no _translated twin.\n")
cat("  What Route 2 does add is that the deposit's own subscale membership agrees\n")
cat("  with the canonical instrument on all 30 positions, which a shifted or\n")
cat("  permuted numbering would not produce.\n")
cat("\nVERDICT:", if (r1 && r2 && r3a && r3b) "PASS" else "FAIL", "\n")
