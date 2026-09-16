# verify_yang_2026_igd_benefits.R
#
# CLAIM UNDER TEST. The paper (Yang, Wang & Ramos 2026, PLOS ONE
# 10.1371/journal.pone.0351550) prints its four single items in the Measures
# section in one fixed order and ties them to no code:
#   1 positive impact at present  (perceived SHORT-term benefits)
#   2 negative impact at present  (perceived SHORT-term costs)
#   3 positive impact in the future (perceived LONG-term benefits)
#   4 negative impact in the future (perceived LONG-term costs)
# The shipped mapping assigns those, in that order, to benefit_a..benefit_d
# (from source columns d28a..d28d / Sd28a..Sd28d).
#
# The falsifiable prediction: Table 3 publishes M(SD) for each of the four
# constructs SEPARATELY at T1 and T2, and the Results text publishes each
# construct's T2-T1 mean change with its SD and t. Those numbers differ item
# by item, so a permuted mapping breaks them. This script checks the live IRW
# data against them.
#
# What it does NOT establish: nothing in the live table names the items, so
# this is a numeric identification, not a label match. It does, however,
# distinguish EVERY item from EVERY other: the four T1 means (4.44, 5.04,
# 4.09, 5.76) are mutually separated by >= 0.35 -- roughly 5 published SDs of
# the per-item change -- and the two signed change means (+.68/+.53 vs
# -.38/-.62) separate the benefit pair from the cost pair independently.

suppressMessages(library(irw))

TABLE <- "yang_2026_igd_benefits"

# Paper Table 3, M +/- SD, N = 1032 (read from the table image t003.png).
PUB <- data.frame(
    item     = c("benefit_a", "benefit_b", "benefit_c", "benefit_d"),
    construct= c("short-term benefits", "short-term costs",
                 "long-term benefits",  "long-term costs"),
    m_t1     = c(4.44, 5.04, 4.09, 5.76),
    sd_t1    = c(2.34, 2.52, 2.32, 2.58),
    m_t2     = c(5.12, 4.66, 4.62, 5.15),
    sd_t2    = c(2.17, 2.17, 2.21, 2.37),
    # Results text: mean of change (T2 - T1) and its SD.
    m_chg    = c( 0.68, -0.38,  0.53, -0.62),
    stringsAsFactors = FALSE
)
TOL_MEAN <- 0.10   # paper used series-mean imputation at T1; IRW dropped those
                   # imputed (fractional) cells, so small residuals are expected
TOL_SD   <- 0.10
TOL_CHG  <- 0.15

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

cat(sprintf("live rows: %d | ids: %d | items: %d\n",
            nrow(d), length(unique(d$id)), length(unique(d$item))))

agg <- function(w) {
    s <- d[d$wave == w, ]
    data.frame(m = tapply(s$resp, s$item, mean)[PUB$item],
               sd = tapply(s$resp, s$item, stats::sd)[PUB$item])
}
a1 <- agg(1); a2 <- agg(2)

# paired change, on ids present at both waves for that item
w1 <- d[d$wave == 1, c("id", "item", "resp")]
w2 <- d[d$wave == 2, c("id", "item", "resp")]
mg <- merge(w1, w2, by = c("id", "item"), suffixes = c("_1", "_2"))
mg$chg <- mg$resp_2 - mg$resp_1
chg <- tapply(mg$chg, mg$item, mean)[PUB$item]
chg_n <- tapply(mg$chg, mg$item, length)[PUB$item]

cat("\n-- T1 M(SD): published vs live --\n")
cat(sprintf("%-10s %-20s %12s %12s %8s\n", "item", "construct", "published", "live", "diff"))
for (i in seq_len(nrow(PUB)))
    cat(sprintf("%-10s %-20s %6.2f(%4.2f) %6.2f(%4.2f) %8.3f\n",
                PUB$item[i], PUB$construct[i], PUB$m_t1[i], PUB$sd_t1[i],
                a1$m[i], a1$sd[i], a1$m[i] - PUB$m_t1[i]))

cat("\n-- T2 M(SD): published vs live --\n")
for (i in seq_len(nrow(PUB)))
    cat(sprintf("%-10s %-20s %6.2f(%4.2f) %6.2f(%4.2f) %8.3f\n",
                PUB$item[i], PUB$construct[i], PUB$m_t2[i], PUB$sd_t2[i],
                a2$m[i], a2$sd[i], a2$m[i] - PUB$m_t2[i]))

cat("\n-- mean change T2-T1: published vs live --\n")
for (i in seq_len(nrow(PUB)))
    cat(sprintf("%-10s %-20s %8.2f %8.3f %8.3f   (n pairs %d)\n",
                PUB$item[i], PUB$construct[i], PUB$m_chg[i], chg[i],
                chg[i] - PUB$m_chg[i], chg_n[i]))

# Cross-check that no permutation fits better: for each item, which published
# T1 mean is nearest?
cat("\n-- nearest published T1 mean for each live item (must be its own) --\n")
ok_assign <- TRUE
for (i in seq_len(nrow(PUB))) {
    j <- which.min(abs(PUB$m_t1 - a1$m[i]))
    cat(sprintf("%-10s live %.3f -> nearest published %.2f (%s)%s\n",
                PUB$item[i], a1$m[i], PUB$m_t1[j], PUB$construct[j],
                if (j == i) "" else "   <-- MISMATCH"))
    if (j != i) ok_assign <- FALSE
}

d1 <- max(abs(a1$m - PUB$m_t1)); s1 <- max(abs(a1$sd - PUB$sd_t1))
d2 <- max(abs(a2$m - PUB$m_t2)); s2 <- max(abs(a2$sd - PUB$sd_t2))
dc <- max(abs(chg - PUB$m_chg))
cat(sprintf("\nworst |diff|: T1 mean %.3f, T1 sd %.3f, T2 mean %.3f, T2 sd %.3f, change %.3f\n",
            d1, s1, d2, s2, dc))
cat(sprintf("tolerances:   mean %.2f, sd %.2f, change %.2f\n", TOL_MEAN, TOL_SD, TOL_CHG))
cat("Note: this identifies the four items numerically; it does not rest on any\n",
    "label in the data file, because the source file carries none.\n", sep = "")

pass <- ok_assign && d1 <= TOL_MEAN && s1 <= TOL_SD && d2 <= TOL_MEAN &&
        s2 <= TOL_SD && dc <= TOL_CHG
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
