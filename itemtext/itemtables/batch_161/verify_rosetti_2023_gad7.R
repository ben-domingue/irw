# verify_rosetti_2023_gad7.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes GAD7_q1..GAD7_q7 carry the canonical
# GAD-7 wording in canonical numbering (GAD7_q1 = "Feeling nervous, anxious or
# on edge" ... GAD7_q7 = "Feeling afraid as if something awful might happen").
#
# Nothing in the study ties those codes to text. data/rosetti_2023_climate_anxiety.py
# melts the figshare deposit's own columns GAD7_q1..GAD7_q7 by name (the item
# code IS the source column name -- no positional step), and the deposit is a
# single flat CSV whose headers are the bare strings "GAD7_q1".."GAD7_q7" with
# no label row and no codebook. The paper (Ecopsychology 15(2):184-192,
# doi:10.1089/eco.2022.0049) is closed access and could not be read. So the tie
# rests on the assumption that the depositors numbered the items in the GAD-7
# form's own printed order, and that has to be tested against content.
#
# ROUTE 1 (cross-sample per-item means). Comparator: Martinez-Vazquez S,
# Martinez-Galiano JM, Peinado-Molina RA, Gutierrez-Sanchez B,
# Hernandez-Martinez A (2022) "Validation of General Anxiety Disorder (GAD-7)
# questionnaire in Spanish nursing students", PeerJ 10:e14296,
# doi:10.7717/peerj.14296, Table 2 -- 170 SPANISH-LANGUAGE university students,
# the closest published item-level comparator to this Mexican university sample.
#
#   P1  Spearman(live means, published means) >= 0.80 under the identity mapping
#   P2  the identity mapping sits in the top 2% of all 5040 relabellings of the
#       seven live columns, scored by that same Spearman correlation
#   P3  the three least-endorsed live items are exactly {q2, q5, q7}, which are
#       the three least-endorsed items in the comparator (0.82, 0.83, 0.91)
#
# OPTION AXIS (option_text <-> resp), tested separately:
#   P4  the deposit's own GAD7_sum column equals the raw UNREVERSED sum of
#       GAD7_q1..GAD7_q7 exactly, and correlates positively with the same
#       respondents' climate-anxiety total -- the paper's own reported direction.
#       Under a flipped 0-3 coding the total mean would be 21 - 8.74 = 12.26 and
#       the CAS association would invert.
#
# WHAT THIS DOES NOT ESTABLISH: it separates the low-mean block {q2, q5, q7}
# from the high-mean block {q1, q3, q4, q6}, and pins q2 as the single lowest
# item. It does NOT distinguish q1, q3, q4 and q6 from one another: their live
# means span only 1.329-1.462, and the comparator's own items 1 and 3 are tied
# at 1.38. A permutation within that block of four would survive this route.
# Status is therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "rosetti_2023_gad7"
DEPOSIT <- "https://ndownloader.figshare.com/files/40839032"
gad <- paste0("GAD7_q", 1:7)

# Martinez-Vazquez et al. (2022) PeerJ 10:e14296, Table 2, items 1-7.
PUBLISHED <- c(1.38, 0.82, 1.38, 1.18, 0.83, 1.12, 0.91)

# --- live IRW data ----------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
mu <- tapply(d$resp, d$item, mean)[gad]
n  <- tapply(d$resp, d$item, length)[gad]

cat(sprintf("%-9s %5s %10s %10s\n", "item", "n", "published", "live mean"))
for (i in gad) cat(sprintf("%-9s %5d %10.2f %10.3f\n", i, n[i], PUBLISHED[which(gad == i)], mu[i]))

# --- P1 ---------------------------------------------------------------------
rho <- suppressWarnings(cor(as.numeric(mu), PUBLISHED, method = "spearman"))
cat(sprintf("\nP1  Spearman(live, published) under identity mapping = %.4f\n", rho))

# --- P2: permutation test ---------------------------------------------------
perms <- function(x) if (length(x) == 1) list(x) else
    do.call(c, lapply(seq_along(x), function(i)
        lapply(perms(x[-i]), function(p) c(x[i], p))))
P <- perms(1:7)
rs <- vapply(P, function(p) suppressWarnings(
        cor(as.numeric(mu)[p], PUBLISHED, method = "spearman")), numeric(1))
rank_id <- sum(rs > rho) + 1
cat(sprintf("P2  identity ranks %d of %d relabellings (top %.2f%%); best r = %.3f\n",
            rank_id, length(P), 100 * rank_id / length(P), max(rs)))

# --- P3: bottom-three set ---------------------------------------------------
low_live <- sort(names(sort(mu))[1:3])
low_pub  <- sort(gad[order(PUBLISHED)][1:3])
cat(sprintf("P3  three lowest live: %s | three lowest published: %s\n",
            paste(low_live, collapse = ", "), paste(low_pub, collapse = ", ")))

# --- P4: option axis, from the deposit --------------------------------------
tf <- tempfile(fileext = ".csv")
utils::download.file(DEPOSIT, tf, quiet = TRUE, mode = "wb")
x <- read.csv(tf)
raw <- rowSums(x[, gad])
dd  <- max(abs(raw - x$GAD7_sum))
rc  <- cor(x$GAD7_sum, x$CAS_sum, use = "complete.obs")
cat(sprintf("P4  deposit GAD7_sum vs raw sum of GAD7_q1..q7: max |diff| = %.1f\n", dd))
cat(sprintf("    raw total: mean %.2f  SD %.2f  range %d-%d  (a flipped 0-3 coding\n",
            mean(raw), sd(raw), min(raw), max(raw)))
cat(sprintf("    would give 21 - %.2f = %.2f); corr(GAD7_sum, CAS_sum) = %+.3f,\n",
            mean(raw), 21 - mean(raw), rc))
cat("    positive as the paper reports climate anxiety tracking general anxiety\n")

ok <- c(P1 = rho >= 0.80,
        P2 = rank_id <= 0.02 * length(P),
        P3 = identical(low_live, low_pub),
        P4 = dd == 0 && rc > 0)
cat("\n"); for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: separates {GAD7_q2, GAD7_q5, GAD7_q7} from {GAD7_q1, GAD7_q3,\n",
    "GAD7_q4, GAD7_q6} and pins GAD7_q2 as the lowest item. It does NOT\n",
    "distinguish q1/q3/q4/q6 from one another -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
