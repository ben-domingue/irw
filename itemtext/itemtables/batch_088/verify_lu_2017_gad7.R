# verify_lu_2017_gad7.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes GAD_1..GAD_7 carry the canonical GAD-7
# wording in canonical numbering (GAD_1 = "Feeling nervous, anxious or on edge"
# ... GAD_7 = "Feeling afraid as if something awful might happen").
#
# Nothing in the study ties those codes to text. data/lu_2017_pss10_battery.py
# melts the deposit's own columns GAD_1..GAD_7 by name, so the IRW code IS the
# source column name -- there is no positional step. What is inferred is what
# the source column NAME means, and the deposit (S2 File, an .xlsx) carries no
# variable labels: its headers are the bare strings "GAD_1".."GAD_7" and the
# only Chinese label anywhere in the sheet is on the PHQ functional-impairment
# column. So the tie rests on the GAD-7 form's own printed numbering, and has
# to be tested against content.
#
# The test is cross-instrument. The same respondents completed the PHQ-9 and
# the PSS-10 in the same file, and two GAD-7 items have a near-unique content
# twin there:
#
#   GAD_5 "Being so restless that it is hard to sit still"
#         <-> PHQ_8, the PHQ-9's only psychomotor item
#   GAD_6 "Becoming easily annoyed or irritable"
#         <-> PSS_9, the PSS-10's anger item ("angered because of things that
#             were outside of your control")
#
# Predictions, all of which would break under a permutation of the GAD labels:
#   P1  argmax_i corr(GAD_i, PHQ_8) == GAD_5
#   P2  argmax_j corr(GAD_5, PHQ_j) == PHQ_8
#   P3  argmax_i corr(GAD_i, PSS_9) == GAD_6
#
# OPTION AXIS (option_text <-> resp), tested separately:
#   P4  the deposit's own GAD-7 total column equals the raw unreversed sum of
#       GAD_1..GAD_7 exactly, and that total's mean/SD reproduces the paper's
#       published "GAD scores 2.8 +/- 2.9". A flipped 0-3 coding would put the
#       mean at 21 - 2.8 = 18.2.
#
# WHAT THIS DOES NOT ESTABLISH: it pins GAD_5 and GAD_6 only. GAD_1, GAD_2,
# GAD_3, GAD_4 and GAD_7 are NOT distinguished from one another -- none has a
# comparably specific content twin in the PHQ-9 or the PSS-10. Status is
# therefore PARTIAL, not VERIFIED. P3 also assumes the deposit's PSS_1..PSS_10
# are in canonical PSS-10 order; that is the assumption the paper's own PSS-10
# validation rests on, but it is an assumption.

suppressMessages(library(irw))

TABLE <- "lu_2017_gad7"
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0189543.s002")

gad <- paste0("GAD_", 1:7)
phq <- paste0("PHQ_", 1:9)

# --- live IRW data (the GAD half), main-test wave only ----------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[d$wave == 1, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", gad)]

# --- the study's deposit (the PHQ-9 / PSS-10 half) --------------------------
tf <- tempfile(fileext = ".xlsx")
utils::download.file(S2, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tf))
names(x)[names(x) == "No."] <- "id"
tot_col <- grep("^GAD7", names(x), value = TRUE)[1]

m <- merge(w, x[, c("id", phq, "PSS_9")], by = "id")
cat(sprintf("merged n = %d respondents (live wave 1 x S2 File)\n\n", nrow(m)))

r <- function(a, b) cor(m[[a]], m[[b]], use = "complete.obs")

# --- P1 ---------------------------------------------------------------------
c8 <- sapply(gad, r, b = "PHQ_8")
cat("corr(GAD_i, PHQ_8)  [PHQ-9's only psychomotor restlessness item]\n")
for (i in gad) cat(sprintf("  %-6s %6.3f\n", i, c8[i]))
top8 <- names(which.max(c8))
cat(sprintf("  -> strongest: %s (predicted GAD_5)\n\n", top8))

# --- P2 ---------------------------------------------------------------------
c5 <- sapply(phq, function(p) r("GAD_5", p))
cat("corr(GAD_5, PHQ_j) across all nine PHQ-9 items\n")
for (p in phq) cat(sprintf("  %-6s %6.3f\n", p, c5[p]))
top5 <- names(which.max(c5))
cat(sprintf("  -> strongest: %s (predicted PHQ_8)\n\n", top5))

# --- P3 ---------------------------------------------------------------------
c9 <- sapply(gad, r, b = "PSS_9")
cat("corr(GAD_i, PSS_9)  [PSS-10's anger item]\n")
for (i in gad) cat(sprintf("  %-6s %6.3f\n", i, c9[i]))
top9 <- names(which.max(c9))
cat(sprintf("  -> strongest: %s (predicted GAD_6)\n\n", top9))

# --- P4: option axis --------------------------------------------------------
raw <- rowSums(x[, gad])
dd  <- max(abs(raw - x[[tot_col]]))
cat(sprintf("deposit total column '%s' vs raw sum of GAD_1..GAD_7: max |diff| = %.1f\n",
            tot_col, dd))
cat(sprintf("raw total: mean %.2f  SD %.2f  range %d-%d   (paper reports 2.8 +/- 2.9;\n",
            mean(raw), sd(raw), min(raw), max(raw)))
cat("  a flipped 0-3 coding would give mean 21 - 2.8 = 18.2)\n\n")
p4 <- dd == 0 && abs(mean(raw) - 2.8) < 0.2

# --- corroboration only (route 8) -------------------------------------------
mu <- sapply(gad, function(i) mean(m[[i]]))
cat("item means (corroborative, not a pass condition)\n")
for (i in names(sort(mu, decreasing = TRUE))) cat(sprintf("  %-6s %5.3f\n", i, mu[i]))
cat(sprintf("  -> lowest two: %s (expected GAD_7 and GAD_5, the two items GAD-7\n",
            paste(names(sort(mu))[1:2], collapse = ", ")))
cat("     community samples routinely endorse least)\n\n")

ok <- c(P1 = top8 == "GAD_5", P2 = top5 == "PHQ_8",
        P3 = top9 == "GAD_6", P4 = p4)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins GAD_5 and GAD_6 only. GAD_1/GAD_2/GAD_3/GAD_4/GAD_7 are NOT\n",
    "distinguished from one another by this route -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
