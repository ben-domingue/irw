# verify_extremera_2016_swls.R
#
# Mapping check for the Satisfaction With Life Scale (Diener, Emmons, Larsen & Griffin,
# 1985) as administered in Spanish by Extremera & Rey (2016), PLOS ONE 11(9):e0163656.
#
# Published values, Table 1 (a table IMAGE; read from
# journals.plos.org/plosone/article/figure/image?size=large&id=10.1371/journal.pone.0163656.t001):
#   Life satisfaction (SWLS): M = 4.25, SD = 1.27, alpha = .83  (item metric, 1-7)
#   r(SWLS, WLEIS EI) = .38 ; r(SWLS, SBQ-R) = -.28
#
# WHAT THIS VERIFIES
#   (a) that the five live items ARE the SWLS, stored raw (no reverse-coding), and
#   (b) the option_text<->resp axis: 1 = Strongly disagree .. 7 = Strongly agree.
#       The flipped assignment gives 8 - 4.254 = 3.746, missing the published 4.25 by
#       ~0.51 on a 1-7 metric, and flips the sign of both published correlations.
#   (c) one item's position: swls5 has the lowest corrected item-total correlation and
#       the largest SD, which is the SWLS literature's stable signature of item 5
#       ("If I could live my life over, I would change almost nothing"; Diener et al.
#       1985 loading .61 against .72-.84 for items 1-4).
#
# WHAT IT DOES NOT VERIFY
#   swls1..swls4 are not distinguished from one another. A sum/alpha is invariant to
#   permutation, no per-item statistics are published for this sample, all five items
#   share one 1-7 scale, there is one unidimensional subscale and no reverse-keyed item,
#   so routes 1, 2, 5 and 6 are unavailable. That assignment rests on the source .sav's
#   column numbering (swls1..swls5, melted BY NAME by
#   data/extremera_2016_unemployment_wellbeing.py) matching canonical SWLS item order.
#   Hence PARTIAL, never VERIFIED.
#
# irw_fetch() is used deliberately: per-respondent sums and item-total correlations are
# needed and irw_table_sets() supplies sets only. The table is 5,623 rows.

suppressMessages(library(irw))

TABLE <- "extremera_2016_swls"
PUB   <- list(mean = 4.25, sd = 1.27, alpha = 0.83, r_ei = 0.38, r_sbq = -0.28)
TOL   <- 0.02
IT    <- paste0("swls", 1:5)
# Diener, Emmons, Larsen & Griffin (1985) principal-axis loadings, items 1..5.
LOAD1985 <- c(0.84, 0.77, 0.84, 0.72, 0.61)

wide <- function(tbl) {
    d <- as.data.frame(irw::irw_fetch(tbl))
    w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
                 direction = "wide")
    colnames(w) <- sub("^resp\\.", "", colnames(w))
    w
}

w  <- wide(TABLE)
cat("live items (", length(setdiff(colnames(w), "id")), "): ",
    paste(sort(setdiff(colnames(w), "id")), collapse = ", "), "\n\n", sep = "")
cc  <- w[complete.cases(w[, IT]), ]
tot <- rowSums(cc[, IT]) / 5      # item metric, as the paper reports it

cat(sprintf("complete cases: %d\n", nrow(cc)))
cat(sprintf("%-24s %10s %10s %8s\n", "statistic", "published", "live", "diff"))
alpha <- 5 / 4 * (1 - sum(apply(cc[, IT], 2, var)) / var(rowSums(cc[, IT])))
stats <- c(mean = mean(tot), sd = sd(tot), alpha = alpha)
for (k in c("mean", "sd", "alpha"))
    cat(sprintf("%-24s %10.3f %10.3f %8.3f\n", paste("SWLS", k), PUB[[k]], stats[[k]],
                stats[[k]] - PUB[[k]]))

# --- direction control -------------------------------------------------------
flip <- mean(8 - rowSums(cc[, IT]) / 5)
cat(sprintf("\ndirection control: reversed 1-7 anchors give mean %.3f, off by %.3f\n",
            flip, abs(flip - PUB$mean)))

# --- convergent correlations (same respondents, sibling IRW tables) -----------
r_ei <- r_sbq <- NA_real_
ok <- TRUE
for (sib in c("extremera_2016_ei", "extremera_2016_sbq")) {
    s <- try(wide(sib), silent = TRUE)
    if (inherits(s, "try-error")) { ok <- FALSE; next }
    sc <- setdiff(colnames(s), "id")
    s$m <- rowMeans(s[, sc], na.rm = TRUE)
    m <- merge(data.frame(id = cc$id, swls = tot), s[, c("id", "m")], by = "id")
    r <- cor(m$swls, m$m, use = "complete.obs")
    if (sib == "extremera_2016_ei") r_ei <- r else r_sbq <- r
}
if (!is.na(r_ei))
    cat(sprintf("r(SWLS, EI)  published %6.2f  live %6.3f\n", PUB$r_ei, r_ei))
if (!is.na(r_sbq))
    cat(sprintf("r(SWLS, SBQ) published %6.2f  live %6.3f\n", PUB$r_sbq, r_sbq))

# --- route 7: marker item ----------------------------------------------------
cat("\nper-item mean / SD / corrected item-total, against Diener 1985 loadings:\n")
cat(sprintf("%-8s %8s %8s %14s %12s\n", "item", "mean", "SD", "item-total r", "1985 loading"))
itr <- numeric(5)
for (i in seq_along(IT)) {
    v <- cc[[IT[i]]]
    itr[i] <- cor(v, rowSums(cc[, setdiff(IT, IT[i])]))
    cat(sprintf("%-8s %8.3f %8.3f %14.3f %12.2f\n", IT[i], mean(v), sd(v), itr[i],
                LOAD1985[i]))
}
cat(sprintf("Spearman r(item-total, 1985 loadings) = %.3f\n",
            cor(itr, LOAD1985, method = "spearman")))
marker <- which.min(itr) == 5 && which.max(apply(cc[, IT], 2, sd)) == 5
cat(sprintf("marker: swls5 is the minimum item-total AND the maximum SD: %s\n", marker))

cat("\nNOT ESTABLISHED: swls1..swls4 are not separated by any route above; that\n",
    "assignment rests on the source column numbering matching canonical SWLS order.\n",
    sep = "")

pass <- abs(stats[["mean"]]  - PUB$mean)  <= TOL &&
        abs(stats[["sd"]]    - PUB$sd)    <= TOL &&
        abs(stats[["alpha"]] - PUB$alpha) <= TOL &&
        marker &&
        (is.na(r_ei)  || abs(r_ei  - PUB$r_ei)  <= 0.03) &&
        (is.na(r_sbq) || abs(r_sbq - PUB$r_sbq) <= 0.03)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
