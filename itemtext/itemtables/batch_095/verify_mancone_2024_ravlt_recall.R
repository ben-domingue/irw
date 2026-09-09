# verify_mancone_2024_ravlt_recall.R
#
# What is at stake. item_text is blank for all five items (the RAVLT immediate-
# recall trials publish no per-item wording; the 2026-09-05 picture-stimulus
# ruling applies), so the only mapping claim this table makes is what the item
# CODES denote: SESS_1..SESS_5 are the five successive immediate-recall trials
# of the RAVLT, in that order, with SESS_5 the fifth (final) trial.
#
# Falsifiable predictions, from Mancone, Tosti, Corrado & Diotaiuti (2024),
# PeerJ 12:e18195 (CC BY 4.0):
#   * Table 2 is titled "Differences in immediate recall performance across
#     groups in the FIFTH SESSION", and Table 1's "Immediate recall mean/std"
#     per group is that same fifth-session score. So Table 1 pins SESS_5
#     outright -- and no other SESS_k should reproduce it.
#   * A list-learning task produces a monotonically rising learning curve across
#     trials 1..5, so the ordering of the remaining codes is testable too.
#
# The table is 800 rows, so irw_fetch() here is a trivial export.

suppressMessages(library(irw))
TABLE <- "mancone_2024_ravlt_recall"

d <- irw::irw_fetch(TABLE)
d$g <- as.integer(as.character(d$cov_group))

# Table 1, "Immediate recall mean" / "Immediate recall std", groups 1-4.
PUB_M  <- c(12.35, 8.10, 10.80, 12.60)
PUB_SD <- c( 1.73, 1.43,  2.02,  1.22)
# Table 2, mean differences in the fifth session (G1-G2, G1-G3, G1-G4, G2-G3, G2-G4, G3-G4)
PUB_D  <- c(-4.25, -1.55, 0.25, 2.70, 4.50, 1.80)

cat("=== Which SESS_k reproduces Table 1's per-group immediate-recall mean (SD)? ===\n")
cat(sprintf("%-8s %s\n", "", paste(sprintf("%14s", sprintf("G%d pub %.2f", 1:4, PUB_M)), collapse = "")))
best <- rep(NA_real_, 5)
for (k in 1:5) {
    it <- sprintf("SESS_%d", k)
    m  <- sapply(1:4, function(g) mean(d$resp[d$item == it & d$g == g]))
    best[k] <- max(abs(m - PUB_M))
    cat(sprintf("%-8s %s   max|diff| %6.3f\n", it,
                paste(sprintf("%14s", sprintf("%.2f", m)), collapse = ""), best[k]))
}
sd5 <- sapply(1:4, function(g) sd(d$resp[d$item == "SESS_5" & d$g == g]))
cat(sprintf("SESS_5 SDs  published %s   observed %s\n",
            paste(sprintf("%.2f", PUB_SD), collapse = "/"),
            paste(sprintf("%.2f", sd5),    collapse = "/")))

ok_five  <- best[5] <= 0.005 && max(abs(sd5 - PUB_SD)) <= 0.006
ok_uniq  <- min(best[1:4]) > 0.5      # no other trial comes close

cat("\n=== Table 2 fifth-session group contrasts, recomputed from SESS_5 ===\n")
prs <- list(c(1,2), c(1,3), c(1,4), c(2,3), c(2,4), c(3,4))
obs_d <- sapply(prs, function(p)
    mean(d$resp[d$item == "SESS_5" & d$g == p[1]]) -
    mean(d$resp[d$item == "SESS_5" & d$g == p[2]]))
# The paper reports G1 vs G2 as -4.25 while G1 scores HIGHER, i.e. it tabulates
# (second - first); compare on that convention.
obs_d <- -obs_d
for (i in seq_along(prs))
    cat(sprintf("G%d vs G%d   published %6.2f   observed %6.2f   diff %6.3f\n",
                prs[[i]][1], prs[[i]][2], PUB_D[i], obs_d[i], obs_d[i] - PUB_D[i]))
ok_diff <- max(abs(obs_d - PUB_D)) <= 0.005

cat("\n=== Learning curve: item means must rise across SESS_1..SESS_5 ===\n")
mm <- sapply(1:5, function(k) mean(d$resp[d$item == sprintf("SESS_%d", k)]))
cat(paste(sprintf("SESS_%d %.3f", 1:5, mm), collapse = "   "), "\n")
ok_mono <- all(diff(mm) > 0)

cat("\nWhat this does NOT establish: SESS_5 is pinned by published numbers, but\n",
    "SESS_1..SESS_4 are ordered only by the rising learning curve plus the codes'\n",
    "own numbering -- the paper publishes no per-trial statistics for trials 1-4.\n",
    "Nothing about item_text is at stake: it is blank for every row.\n", sep = "")

cat(sprintf("\nchecks: SESS_5==Table1 %s | unique to SESS_5 %s | Table2 contrasts %s | monotone %s\n",
            ok_five, ok_uniq, ok_diff, ok_mono))
cat(if (ok_five && ok_uniq && ok_diff && ok_mono) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
