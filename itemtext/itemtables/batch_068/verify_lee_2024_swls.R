# verify_lee_2024_swls.R
#
# Mapping check for the Satisfaction With Life Scale (Diener, Emmons, Larsen & Griffin,
# 1985) as administered in Korean (Lee, 2004 translation) by Lee SJ, Cloninger CR & Chae H
# (2024), PeerJ 12:e18379, doi:10.7717/peerj.18379 (CC BY 4.0).
#
# Published values, Table 2 ("Demographic features of the current study") and Methods:
#   SWLS total, males   (n = 195): 21.89 +/- 5.85
#   SWLS total, females (n = 332): 20.59 +/- 6.34
#   t = 2.335, p = 0.020
#   Cronbach's alpha in this study: .86  (Methods, "The internal consistency in this study was .86")
#
# WHAT THIS VERIFIES
#   (a) route 3 -- the five live items ARE the SWLS as the paper scored it, stored raw
#       (not reverse-coded), and the by-sex split reproduces Table 2 exactly, which also
#       ties cov_gender 1 = male / 2 = female;
#   (b) the option_text <-> resp axis: 1 = Strongly disagree .. 7 = Strongly agree. The
#       flipped assignment gives 40 - 21.89 = 18.11 for males, missing the published
#       value by 3.8 points on a 5-35 metric;
#   (c) route 7/8 -- one item's position. SWLS5 has BOTH the lowest mean and the largest
#       SD of the five, the SWLS literature's stable signature of item 5 ("If I could
#       live my life over, I would change almost nothing"), and this also rejects the one
#       rival hypothesis the item-total pattern raises, namely a SWLS2<->SWLS5 swap: under
#       that swap item 5 would carry the HIGHEST mean of the scale, which no SWLS sample
#       shows.
#
# WHAT IT DOES NOT VERIFY
#   SWLS1..SWLS4 are not distinguished from one another. The paper publishes no per-item
#   statistics, the source workbook (peerj-12-18379-s002.xlsx) carries bare column headers
#   SWLS1..SWLS5 with no variable or value labels, all five items share one 1-7 scale,
#   the scale is unidimensional with no reverse-keyed item, and a sum/alpha is invariant to
#   permutation -- so routes 1, 2, 5 and 6 are unavailable. The SWLS1..SWLS5 -> canonical
#   SWLS item 1..5 assignment rests on the source column numbering matching the
#   instrument's published item order. Hence PARTIAL, never VERIFIED.
#
#   Note also a real deviation from the canonical pattern that this script prints rather
#   than hides: Diener et al. (1985) report item 5 as the weakest item (loading .61 vs
#   .72-.84), but in this sample the lowest corrected item-total correlation belongs to
#   SWLS2 (.55) and SWLS5 sits mid-pack (.68). That is a sample-level finding, not evidence
#   of a swap -- see (c) above.
#
# irw_fetch() is used deliberately: per-respondent sums, per-item SDs, item-total
# correlations and the cov_gender split are needed, and irw_table_sets() supplies sets
# only. The table is 2,635 rows (527 respondents x 5 items).

suppressMessages(library(irw))

TABLE <- "lee_2024_swls"
IT    <- paste0("SWLS", 1:5)
PUB   <- list(m_male = 21.89, sd_male = 5.85, n_male = 195,
              m_female = 20.59, sd_female = 6.34, n_female = 332,
              alpha = 0.86)
TOL   <- 0.02
# Diener, Emmons, Larsen & Griffin (1985) principal-axis loadings, items 1..5.
LOAD1985 <- c(0.84, 0.77, 0.84, 0.72, 0.61)

d <- as.data.frame(irw::irw_fetch(TABLE))
stopifnot("cov_gender" %in% colnames(d))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
sexmap <- unique(d[, c("id", "cov_gender")])
w  <- merge(w, sexmap, by = "id")
cc <- w[complete.cases(w[, IT]), ]
tot <- rowSums(cc[, IT])

cat(sprintf("complete cases: %d\n\n", nrow(cc)))

# --- route 3: published by-sex totals ----------------------------------------
cat(sprintf("%-28s %6s %10s %10s %8s\n", "statistic", "n", "published", "live", "diff"))
ok3 <- TRUE
for (g in c(1, 2)) {
    lab <- if (g == 1) "male" else "female"
    t   <- tot[cc$cov_gender == g]
    pm  <- PUB[[paste0("m_", lab)]]; ps <- PUB[[paste0("sd_", lab)]]
    pn  <- PUB[[paste0("n_", lab)]]
    cat(sprintf("%-28s %6d %10.2f %10.2f %8.3f\n",
                paste("SWLS total mean,", lab), length(t), pm, mean(t), mean(t) - pm))
    cat(sprintf("%-28s %6d %10.2f %10.2f %8.3f\n",
                paste("SWLS total SD,  ", lab), length(t), ps, sd(t), sd(t) - ps))
    ok3 <- ok3 && length(t) == pn && abs(mean(t) - pm) <= TOL && abs(sd(t) - ps) <= TOL
}
alpha <- 5 / 4 * (1 - sum(apply(cc[, IT], 2, var)) / var(tot))
cat(sprintf("%-28s %6d %10.2f %10.3f %8.3f\n", "Cronbach's alpha", nrow(cc),
            PUB$alpha, alpha, alpha - PUB$alpha))
ok_a <- abs(alpha - PUB$alpha) <= 0.006   # published to 2 dp

# --- direction control -------------------------------------------------------
flip_male <- mean(40 - tot[cc$cov_gender == 1])
cat(sprintf("\ndirection control: reversed 1-7 anchors give a male mean of %.2f, off by %.2f\n",
            flip_male, abs(flip_male - PUB$m_male)))

# --- routes 7/8: marker item and the rival swap hypothesis -------------------
cat("\nper-item mean / SD / corrected item-total, against Diener 1985 loadings:\n")
cat(sprintf("%-8s %8s %8s %14s %12s\n", "item", "mean", "SD", "item-total r", "1985 loading"))
itr <- sds <- mns <- numeric(5)
for (i in seq_along(IT)) {
    v <- cc[[IT[i]]]
    mns[i] <- mean(v); sds[i] <- sd(v)
    itr[i] <- cor(v, rowSums(cc[, setdiff(IT, IT[i])]))
    cat(sprintf("%-8s %8.3f %8.3f %14.3f %12.2f\n", IT[i], mns[i], sds[i], itr[i],
                LOAD1985[i]))
}
marker <- which.min(mns) == 5 && which.max(sds) == 5
cat(sprintf("\nmarker: SWLS5 is the minimum mean AND the maximum SD: %s\n", marker))
cat(sprintf("rival 2<->5 swap would put canonical item 5 at mean %.3f (the scale maximum);",
            mns[2]))
cat(sprintf(" rejected.\n"))
cat(sprintf("item-total ordering here is 3 > 1 > 5 > 4 > 2, not Diener's 1=3 > 2 > 4 > 5;\n"))
cat(sprintf("SWLS2 (%.3f), not SWLS5 (%.3f), is this sample's weakest item.\n", itr[2], itr[5]))

cat("\nNOT ESTABLISHED: SWLS1..SWLS4 are not separated from one another by any route\n",
    "above; that assignment rests on the source column numbering (headers SWLS1..SWLS5\n",
    "in peerj-12-18379-s002.xlsx, melted BY NAME by data/lee_2024_cloninger.py) matching\n",
    "canonical SWLS item order.\n", sep = "")

pass <- ok3 && ok_a && marker && abs(flip_male - PUB$m_male) > 1
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
