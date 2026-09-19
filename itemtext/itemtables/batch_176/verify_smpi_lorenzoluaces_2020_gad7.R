# verify_smpi_lorenzoluaces_2020_gad7.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: live item codes GAD_1..GAD_7 carry the canonical GAD-7
# wording in the instrument's own numbering (GAD_1 = "Feeling nervous, anxious
# or on edge" ... GAD_7 = "Feeling afraid as if something awful might happen"),
# and resp 0..3 = Not at all .. Nearly every day (raw, unreversed).
#
# Derivation: data/smpi_lorenzoluaces.py renames the OSF deposit columns
# gad1..gad7 -> GAD_1..GAD_7 (number-preserving). The deposit ("SMPI data.csv",
# osf.io/69nwe) has bare headers and no labels, and the paper never prints the
# GAD-7 items, so what gad<i> MEANS rests on the instrument's printed order and
# has to be tested against content.
#
# The same 487 respondents answered the PHQ-9 and the SMPI in the same file.
# Three GAD-7 items have a content twin there:
#   GAD_6 "Becoming easily annoyed or irritable"
#       <-> SMPIb_2 "I find that I become distinctly more irritable and/or
#           angry when I'm depressed" (paper Table 1, Scale B item 2)
#   GAD_5 "Being so restless that it is hard to sit still"
#       <-> PHQ_8, the PHQ-9's only psychomotor (fidgety/restless) item
#   GAD_4 "Trouble relaxing"
#       <-> PHQ_3, the PHQ-9 sleep item (weaker twin)
#
# Predictions (each breaks under a permutation of the pinned labels):
#   P0  live GAD_i equals deposit gad<i> for every respondent (the rename)
#   P1  argmax_i corr(GAD_i, SMPIb_2) == GAD_6
#   P2  argmax_i corr(GAD_i, PHQ_8)   == GAD_5
#   P3  argmax_i corr(GAD_i, PHQ_3)   == GAD_4
#   P4  option axis: deposit GAD total == raw sum of items; PHQ-9 total in the
#       same file reproduces the paper's 9.80 (SD 6.40); and GAD total
#       correlates with PHQ total at the paper's r = .73 (a reversed GAD coding
#       would make that negative).
#
# WHAT THIS DOES NOT ESTABLISH: GAD_1, GAD_2, GAD_3 and GAD_7 are NOT
# distinguished from one another. The GAD_2-GAD_3 pair is the strongest
# inter-item correlation (consistent with the two worry items) but that does
# not separate 2 from 3, and the trait-worry SMPI item B11 correlates highest
# with GAD_1 (.53) rather than with GAD_2/GAD_3 (.51/.51). Status PARTIAL.

suppressMessages(library(irw))

TABLE <- "smpi_lorenzoluaces_2020_gad7"
SRC   <- "https://osf.io/download/ygzhj/"   # SMPI data.csv, osf.io/69nwe

g_live <- paste0("GAD_", 1:7)
g_src  <- paste0("gad", 1:7)

# --- live IRW data (3,409 rows) ---------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(w$id), c("id", g_live)]

# --- the study's deposit ----------------------------------------------------
tf <- tempfile(fileext = ".csv")
utils::download.file(SRC, tf, quiet = TRUE, mode = "wb")
x <- read.csv(tf, check.names = FALSE, fileEncoding = "UTF-8-BOM")
x$id <- seq_len(nrow(x))   # processing script: id = row number

m <- merge(w, x, by = "id")
cat(sprintf("merged n = %d respondents (live x deposit)\n\n", nrow(m)))

# --- P0 ---------------------------------------------------------------------
mism <- sum(as.matrix(m[, g_live]) != as.matrix(m[, g_src]), na.rm = TRUE)
cat(sprintf("P0 cells where live GAD_i != deposit gad<i>: %d of %d\n\n",
            mism, nrow(m) * 7))

r <- function(a, b) cor(m[[a]], m[[b]], use = "pairwise.complete.obs")
pin <- function(twin, label, expect) {
    cc <- sapply(g_live, r, b = twin)
    cat(sprintf("corr(GAD_i, %s)  [%s]\n", twin, label))
    for (i in g_live) cat(sprintf("  %-6s %6.3f\n", i, cc[i]))
    top <- names(which.max(cc))
    cat(sprintf("  -> strongest: %s (predicted %s)\n\n", top, expect))
    top == expect
}

p1 <- pin("SMPIb_2", "SMPI B2: more irritable and/or angry when depressed", "GAD_6")
p2 <- pin("PHQ_8",   "PHQ-9 item 8: psychomotor slowed / fidgety-restless", "GAD_5")
p3 <- pin("PHQ_3",   "PHQ-9 item 3: sleep", "GAD_4")

# --- P4: option axis --------------------------------------------------------
gsum <- rowSums(m[, g_live])
phq  <- rowSums(m[, paste0("PHQ_", 1:9)])
dd   <- max(abs(gsum - m$GAD))
rgp  <- cor(gsum, phq, use = "complete.obs")
cat(sprintf("deposit GAD column vs raw sum of GAD_1..GAD_7: max |diff| = %.1f\n", dd))
cat(sprintf("GAD-7 total: mean %.2f SD %.2f range %d-%d\n",
            mean(gsum), sd(gsum), min(gsum), max(gsum)))
cat(sprintf("PHQ-9 total (complete n=%d): mean %.2f SD %.2f  (paper: 9.80, SD 6.40)\n",
            sum(!is.na(phq)), mean(phq, na.rm = TRUE), sd(phq, na.rm = TRUE)))
cat(sprintf("corr(GAD-7 total, PHQ-9 total) = %.3f  (paper: r = .73)\n\n", rgp))
p4 <- dd == 0 && abs(mean(phq, na.rm = TRUE) - 9.80) < 0.05 && abs(rgp - 0.73) < 0.02

# --- corroboration only -----------------------------------------------------
mu <- sapply(g_live, function(i) mean(m[[i]]))
cat("item means (corroborative, not a pass condition)\n")
for (i in names(sort(mu, decreasing = TRUE))) cat(sprintf("  %-6s %5.3f\n", i, mu[i]))
ic <- cor(m[, g_live])
diag(ic) <- NA
wp <- which(ic == max(ic, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("strongest inter-item pair: %s-%s r=%.3f (expected the two worry items GAD_2-GAD_3)\n",
            g_live[wp[1]], g_live[wp[2]], max(ic, na.rm = TRUE)))
cat(sprintf("corr(GAD_i, SMPIb_11 trait worry): %s  (does NOT single out GAD_2/GAD_3)\n\n",
            paste(sprintf("%.2f", sapply(g_live, r, b = "SMPIb_11")), collapse = " ")))

ok <- c(P0 = mism == 0, P1 = p1, P2 = p2, P3 = p3, P4 = p4)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins GAD_4, GAD_5, GAD_6 and the option direction. GAD_1/GAD_2/GAD_3/GAD_7\n",
    "are NOT distinguished from one another by this route -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
