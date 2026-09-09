# verify_lu_2017_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes PHQ_1..PHQ_9 carry the canonical PHQ-9
# wording in canonical numbering (PHQ_1 = "Little interest or pleasure in doing
# things" ... PHQ_9 = "Thoughts that you would be better off dead or of hurting
# yourself in some way"), and resp 0..3 = Not at all / Several days / More than
# half the days / Nearly every day in that ascending order.
#
# Nothing in the study ties those codes to text. data/lu_2017_pss10_battery.py
# melts the deposit's own columns PHQ_1..PHQ_9 by name (var_name="item"), so the
# IRW code IS the source column name -- there is no positional step. But the
# deposit (S2 File, an .xlsx) carries no variable labels: its headers are the
# bare strings "PHQ_1".."PHQ_9", the only Chinese text anywhere in the sheet is
# in the header of the excluded functional-impairment column
# "PHQ_F(1-毫无困难;2-有点困难;3-非常困难;4-极度困难)", and the paper never
# reproduces an item. So the tie rests on the official PHQ-9 form's own printed
# numbering 1-9, and has to be tested against content.
#
# Predictions:
#   P0  live wave-1 PHQ cells are cell-for-cell identical to the deposit's own
#       PHQ_1..PHQ_9 columns (confirms the code IS the source column name).
#   P1  PHQ_9 (suicidal ideation) is the least endorsed item in this community
#       student sample -- route 7, marker item.
#   P2  argmax_i corr(PHQ_i, GAD_5) == PHQ_8. GAD_5 ("Being so restless that it
#       is hard to sit still") is answered by the same respondents in the same
#       file; PHQ_8 is the PHQ-9's only psychomotor agitation/retardation item.
#   P3  argmax_j corr(PHQ_8, GAD_j) == GAD_5 (the reciprocal of P2).
#   P4  option axis: the deposit's own PHQ9 total column equals the raw,
#       unreversed sum of PHQ_1..PHQ_9 exactly, and that total reproduces the
#       paper's published "PHQ score 4.3 +/- 3.1". A flipped 0-3 coding would
#       put the mean at 27 - 4.3 = 22.7.
#
# WHAT THIS DOES NOT ESTABLISH: it pins PHQ_9 and PHQ_8 only. PHQ_1, PHQ_2,
# PHQ_3, PHQ_4, PHQ_5, PHQ_6 and PHQ_7 are NOT distinguished from one another --
# none has a content twin in the GAD-7 or PSS-10 specific enough to separate it
# from its six neighbours, and the paper publishes no per-item statistics. The
# P2 margin is also narrow (PHQ_8 0.45 vs PHQ_7 0.43). Status is therefore
# PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "lu_2017_phq9"
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0189543.s002")

phq <- paste0("PHQ_", 1:9)
gad <- paste0("GAD_", 1:7)

# --- live IRW data, main-test wave only -------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[d$wave == 1, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", phq)]

# --- the study's deposit (the GAD-7 half and the total column) --------------
tf <- tempfile(fileext = ".xlsx")
utils::download.file(S2, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tf))
names(x)[names(x) == "No."] <- "id"
tot_col <- grep("^PHQ9", names(x), value = TRUE)[1]

m <- merge(w, x[, c("id", gad, tot_col)], by = "id")
cat(sprintf("merged n = %d respondents (live wave 1 x S2 File)\n\n", nrow(m)))

r <- function(a, b) cor(m[[a]], m[[b]], use = "complete.obs")

# --- P0 ---------------------------------------------------------------------
xx <- x[match(m$id, x$id), ]
same <- sapply(phq, function(p) all(m[[p]] == xx[[p]]))
cat(sprintf("P0 live wave-1 cells identical to deposit columns: %d/%d items\n\n",
            sum(same), length(phq)))

# --- P1: marker item --------------------------------------------------------
mu   <- sapply(phq, function(p) mean(m[[p]]))
zero <- sapply(phq, function(p) 100 * mean(m[[p]] == 0))
cat("item mean and % at zero (route 7 / route 8)\n")
for (p in names(sort(mu))) cat(sprintf("  %-6s mean %5.3f   %%zero %4.1f\n", p, mu[p], zero[p]))
lo <- names(which.min(mu))
cat(sprintf("  -> least endorsed: %s (predicted PHQ_9, the suicidal-ideation item)\n\n", lo))

# --- P2 ---------------------------------------------------------------------
c5 <- sapply(phq, r, b = "GAD_5")
cat("corr(PHQ_i, GAD_5)  [GAD-7's restlessness item]\n")
for (p in phq) cat(sprintf("  %-6s %6.3f\n", p, c5[p]))
top5 <- names(which.max(c5))
cat(sprintf("  -> strongest: %s (predicted PHQ_8)\n\n", top5))

# --- P3 ---------------------------------------------------------------------
c8 <- sapply(gad, function(g) r("PHQ_8", g))
cat("corr(PHQ_8, GAD_j) across all seven GAD-7 items\n")
for (g in gad) cat(sprintf("  %-6s %6.3f\n", g, c8[g]))
top8 <- names(which.max(c8))
cat(sprintf("  -> strongest: %s (predicted GAD_5)\n\n", top8))

# --- P4: option axis --------------------------------------------------------
raw <- rowSums(m[, phq])
dd  <- max(abs(raw - m[[tot_col]]))
cat(sprintf("deposit total column '%s' vs raw sum of PHQ_1..PHQ_9: max |diff| = %.1f\n",
            tot_col, dd))
cat(sprintf("raw total: mean %.2f  SD %.2f  range %d-%d   (paper reports 4.3 +/- 3.1;\n",
            mean(raw), sd(raw), min(raw), max(raw)))
cat("  a flipped 0-3 coding would give mean 27 - 4.3 = 22.7)\n\n")
p4 <- dd == 0 && abs(mean(raw) - 4.3) < 0.2

ok <- c(P0 = all(same), P1 = lo == "PHQ_9", P2 = top5 == "PHQ_8",
        P3 = top8 == "GAD_5", P4 = p4)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins PHQ_9 and PHQ_8 only. PHQ_1..PHQ_7 are NOT distinguished from\n",
    "one another by this route -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
