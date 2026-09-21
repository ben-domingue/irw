# verify_mekheimer_2026_paf.R -- batch_288, 2026-09-20.
#
# CLAIM UNDER TEST: that the appendix wording of the Perceived Academic Freedom
# (PAF) Scale can be attached to the live item codes PAF_1..PAF_10.
#
# The claim FAILS. This script is the re-runnable record of WHY the table was
# blocked, so it PASSES when the three defects below all reproduce. Each is a
# mapping-level fact, not a plumbing check: none of them would survive if the
# deposited PAF_* columns really were the ten appendix statements.
#
#   (D1) The live resp set runs 1..7, but the study's own questionnaire appendix
#        (Additional file 4, 40862_2025_378_MOESM4_ESM.docx) prints the PAF grid
#        with exactly five anchors, Strongly Disagree .. Strongly Agree. 23% of
#        stored responses lie outside the printed grid, so no published anchor
#        can be mapped onto resp and option_text is unattachable.
#
#   (D2) The paper's own per-item descriptives (Additional file 2,
#        40862_2025_378_MOESM2_ESM.xlsx, N=496) number the questionnaire q1..q38
#        and its section subtotals fix PAF = q1..q10. The live PAF_1..PAF_10
#        means match NO window of that q series -- including their own q1..q10.
#        (Sibling check, batch_287: the same file's CAI_* columns match q15..q32
#        rather than the q11..q28 the paper assigns them, i.e. shifted +4. The
#        deposit's column labelling is demonstrably unreliable.)
#
#   (D3) PAF_7 = PAF_3 + 1 for all 160 respondents, exactly. Two distinct
#        instrument items cannot stand in a deterministic affine relation over
#        every respondent, so at least one of these two codes does not carry the
#        responses to the statement its position implies.
#
# Published values below are hard-coded from Additional file 2's "Mean" row so
# the script needs only the live IRW table.

suppressMessages({library(irw); library(dplyr); library(tidyr)})

TABLE <- "mekheimer_2026_paf"

# Additional file 2 (N=496 SPSS FREQUENCIES), questionnaire items q1..q38.
Q <- c(4.2, 4.0, 3.8, 4.1, 3.9, 4.0, 3.8, 3.5, 3.4, 3.9,
       3.6, 3.8, 4.4, 3.6, 3.9, 3.9, 3.9, 3.7, 3.8,
       4.0, 4.0, 3.8, 4.0, 3.0, 3.2, 3.2, 3.0, 3.2,
       3.3, 3.3, 3.1, 3.2, 3.9, 3.7, 3.5, 3.6, 3.8, 3.7)
# PAF section subtotals published in the same table.
PUB_SEC1 <- 20.0; PUB_SEC2 <- 18.5; PUB_TOT <- 38.5

d <- irw::irw_fetch(TABLE)
w <- d %>% select(id, item, resp) %>% pivot_wider(names_from = item, values_from = resp)
items <- paste0("PAF_", 1:10)
m <- as.matrix(w[, items])
lv <- colMeans(m, na.rm = TRUE)

cat("=== (D1) live resp set vs the appendix's printed 5-point PAF grid ===\n")
tb <- table(d$resp)
print(tb)
off <- sum(d$resp > 5); tot <- sum(!is.na(d$resp))
cat(sprintf("  appendix anchors: 5 (Strongly Disagree .. Strongly Agree)\n"))
cat(sprintf("  live resp range : %d..%d\n", min(d$resp), max(d$resp)))
cat(sprintf("  responses above the printed top anchor: %d of %d (%.1f%%)\n",
            off, tot, 100 * off / tot))
d1 <- max(d$resp) > 5
cat("  -> D1 reproduces:", d1, "\n")

cat("\n=== (D2) live PAF means vs every 10-wide window of the paper's q1..q38 ===\n")
cat(sprintf("  published PAF (q1..q10): %s\n", paste(sprintf("%.2f", Q[1:10]), collapse = " ")))
cat(sprintf("  live PAF_1..PAF_10     : %s\n", paste(sprintf("%.2f", lv), collapse = " ")))
tab <- data.frame()
for (o in 0:28) {
  dd <- lv - Q[(o + 1):(o + 10)]
  tab <- rbind(tab, data.frame(window = sprintf("q%d..q%d", o + 1, o + 10),
                               maxabs = max(abs(dd)), rmse = sqrt(mean(dd^2))))
}
print(head(tab[order(tab$rmse), ], 5), row.names = FALSE, digits = 4)
own <- tab$rmse[tab$window == "q1..q10"]
best <- min(tab$rmse)
cat(sprintf("\n  rmse against its OWN published window q1..q10 = %.4f\n", own))
cat(sprintf("  best rmse over all 29 windows                 = %.4f (no window matches)\n", best))
cat(sprintf("  published PAF section/total: %.1f / %.1f / %.1f\n", PUB_SEC1, PUB_SEC2, PUB_TOT))
cat(sprintf("  live     PAF section/total: %.1f / %.1f / %.1f\n",
            sum(lv[1:5]), sum(lv[6:10]), sum(lv)))
d2 <- best > 0.10
cat("  -> D2 reproduces (nothing within 0.10):", d2, "\n")

cat("\n=== (D3) PAF_7 is an exact affine function of PAF_3 ===\n")
dif <- m[, "PAF_7"] - m[, "PAF_3"]
cat(sprintf("  distinct values of PAF_7 - PAF_3 over %d respondents: %s\n",
            nrow(m), paste(unique(dif), collapse = ", ")))
cat(sprintf("  cor(PAF_3, PAF_7) = %.12f\n", cor(m[, "PAF_3"], m[, "PAF_7"])))
cat("  mean r of each item with the other nine:\n")
cm <- cor(m, use = "pairwise")
print(round((rowSums(cm) - 1) / 9, 3))
d3 <- length(unique(dif)) == 1
cat("  -> D3 reproduces:", d3, "\n")

cat("\nWhat this does NOT establish: it does not show WHICH appendix statement any\n")
cat("PAF_n actually carries, and it does not rule out that some subset of the codes\n")
cat("is correctly labelled. It establishes only that the deposit gives no sound\n")
cat("basis for attaching the appendix wording to these codes, which is why no\n")
cat("__items.csv was written. PAF_5 being the table's sole negatively-keyed item\n")
cat("(mean r = -0.88) is consistent with the appendix's Section 1 item 5 '(R)'\n")
cat("marker, but one corroborated position cannot rescue the other nine.\n")

cat(if (d1 && d2 && d3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
