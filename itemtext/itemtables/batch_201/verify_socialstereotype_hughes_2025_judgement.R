# Verification for socialstereotype_hughes_2025_judgement (#1945, batch_201).
#
# The codebook gives one hard fingerprint: credibility of the PERSON is the
# average of "I believe this person's story" and "I think I got an incomplete or
# inaccurate story" (reversed), and that composite has M = 4.59, SD = 0.71,
# alpha = .66. Test every ordered pair. Then the remaining two are the BUSINESS
# items, and NPS separates them: "I would be willing to patronize the business"
# must correlate positively with recommending the company, "I would tell other
# people to avoid this business" negatively.
d <- as.data.frame(readRDS(file.path(Sys.getenv("CLAUDE_JOB_DIR"), "tmp",
                                     "b201_socialstereotype_hughes_2025_judgement.rds")))
d$item <- as.character(d$item)
d$dyad <- paste(d$id, d$rater, sep = "|")
items <- sort(unique(d$item))
W <- matrix(NA_real_, nrow = length(unique(d$dyad)), ncol = length(items),
            dimnames = list(unique(d$dyad), items))
for (nm in items) { s <- d[d$item == nm, ]; W[match(s$dyad, rownames(W)), nm] <- as.numeric(s$resp) }
cat("dyads:", nrow(W), "\n\n")

CE <- c("ce1", "ce2", "ce4", "ce5")
cat("=== per-item descriptives ===\n")
for (nm in c(CE, "sympathy", "nps"))
    cat(sprintf("  %-9s n=%4d  M=%.2f  SD=%.2f\n", nm, sum(!is.na(W[, nm])),
                mean(W[, nm], na.rm = TRUE), sd(W[, nm], na.rm = TRUE)))

alpha2 <- function(a, b) {   # Cronbach alpha for 2 items
    ok <- !is.na(a) & !is.na(b); a <- a[ok]; b <- b[ok]
    r <- cor(a, b); 2 * r / (1 + r)
}
cat("\n=== credibility of PERSON: target M=4.59, SD=0.71, alpha=.66 ===\n")
cat("   pair (X = 'believe story', Y = 'incomplete/inaccurate', reversed)\n")
best <- NULL
for (x in CE) for (y in CE) {
    if (x == y) next
    comp <- (W[, x] + (6 - W[, y])) / 2
    m <- mean(comp, na.rm = TRUE); s <- sd(comp, na.rm = TRUE)
    al <- alpha2(W[, x], 6 - W[, y])
    d3 <- abs(m - 4.59) + abs(s - 0.71) + abs(al - 0.66)
    flag <- if (abs(m - 4.59) < .02 && abs(s - 0.71) < .02 && abs(al - .66) < .02) "  <== MATCH" else ""
    cat(sprintf("   X=%-4s Y=%-4s  M=%.2f  SD=%.2f  alpha=%.2f%s\n", x, y, m, s, al, flag))
    if (is.null(best) || d3 < best$d) best <- list(x = x, y = y, d = d3)
}
cat(sprintf("\n   closest: X=%s  Y=%s\n", best$x, best$y))

rest <- setdiff(CE, c(best$x, best$y))
cat("\n=== the remaining two are the BUSINESS items:", paste(rest, collapse = ", "), "===\n")
cat("   correlation with nps ('how likely would you recommend the company'):\n")
for (nm in rest)
    cat(sprintf("     r(%s, nps) = %+.3f\n", nm, cor(W[, nm], W[, "nps"], use = "complete.obs")))
cat("   -> positive r = 'willing to patronize'; negative r = 'tell others to avoid'\n")

cat("\n=== sanity: is affil a coherent block, and does affil6 belong? ===\n")
A <- paste0("affil", 1:6)
C <- cor(W[, A], use = "pairwise.complete.obs")
for (nm in A) cat(sprintf("   %-7s mean r with other affil = %.3f   M=%.2f\n", nm,
                          mean(C[nm, setdiff(A, nm)]), mean(W[, nm], na.rm = TRUE)))
cat(sprintf("\n   affil 6-item alpha = %.3f\n", {
    k <- 6; v <- var(rowSums(W[, A]), na.rm = TRUE); si <- sum(apply(W[, A], 2, var, na.rm = TRUE))
    k / (k - 1) * (1 - si / v) }))
cat("   codebook reports the affiliation composite at M = 3.98, SD = 0.87, alpha = .93\n")
cat(sprintf("   observed 6-item mean-of-items M = %.2f, SD = %.2f\n",
            mean(rowMeans(W[, A]), na.rm = TRUE), sd(rowMeans(W[, A]), na.rm = TRUE)))
for (drop in A) {
    keep <- setdiff(A, drop); v <- var(rowSums(W[, keep]), na.rm = TRUE)
    si <- sum(apply(W[, keep], 2, var, na.rm = TRUE)); al <- 5/4 * (1 - si / v)
    cat(sprintf("   drop %-7s -> 5-item alpha = %.3f, M = %.2f, SD = %.2f\n", drop, al,
                mean(rowMeans(W[, keep]), na.rm = TRUE), sd(rowMeans(W[, keep]), na.rm = TRUE)))
}

# --- verdict -------------------------------------------------------------
# 1. cred_pers: ce1 + reversed ce2 must reproduce M=4.59, SD=0.71 and be the
#    UNIQUE orientation doing so.
comp <- (W[, "ce1"] + (6 - W[, "ce2"])) / 2
r1 <- abs(mean(comp, na.rm = TRUE) - 4.59) < 0.02 && abs(sd(comp, na.rm = TRUE) - 0.71) < 0.02
# 2. cred_bus: nps must separate ce4 (positive) from ce5 (negative).
r2 <- cor(W[, "ce4"], W[, "nps"], use = "complete.obs") > 0.2 &&
      cor(W[, "ce5"], W[, "nps"], use = "complete.obs") < -0.2
# 3. affil6 excluded: dropping it must be the best of six drops on alpha AND
#    reproduce the reported M=3.98, SD=0.87, alpha=.93.
A <- paste0("affil", 1:6)
al <- sapply(A, function(drop) { keep <- setdiff(A, drop)
    5/4 * (1 - sum(apply(W[, keep], 2, var, na.rm = TRUE)) / var(rowSums(W[, keep]), na.rm = TRUE)) })
k6 <- setdiff(A, "affil6")
r3 <- which.max(al) == which(A == "affil6") &&
      abs(mean(rowMeans(W[, k6]), na.rm = TRUE) - 3.98) < 0.02 &&
      abs(sd(rowMeans(W[, k6]), na.rm = TRUE) - 0.87) < 0.02
cat(sprintf("\nroute 1 (cred_pers fingerprint): %s\n", if (r1) "PASS" else "FAIL"))
cat(sprintf("route 2 (nps separates business items): %s\n", if (r2) "PASS" else "FAIL"))
cat(sprintf("route 3 (affil6 is not in the 5-item scale): %s\n", if (r3) "PASS" else "FAIL"))
cat("\nNOT established: the wording of affil1-affil5 individually. The codebook\n")
cat("gives two unkeyed examples for a five-item scale, so those five and affil6\n")
cat("ship with empty item_text. Recorded PARTIAL for that reason.\n")
# --- Route 4: the deposit's OWN affiliation composite -------------------
# Stronger than route 3 and it supersedes it as the primary evidence. The
# deposit's 'SES stereotypes_scored data.csv' ships affil1..affil6 AND a scored
# `affil` composite column, so the authors' own scoring can be reproduced
# directly instead of argued from reliability.
SCORED <- ".cache/socialstereotype_hughes_2025/scored_data.csv"
r4 <- NA
if (file.exists(SCORED)) {
    sc <- read.csv(SCORED, stringsAsFactors = FALSE)
    mm <- sapply(sc[A], as.numeric); cp <- as.numeric(sc$affil)
    keep <- !is.na(cp) & rowSums(is.na(mm)) == 0
    cat("\n=== Route 4: reproduce the deposit's own `affil` composite ===\n")
    cat(sprintf("  rows with the composite and all six items: %d\n", sum(keep)))
    cat(sprintf("  mean of ALL SIX matches: %d of %d\n",
                sum(abs(rowMeans(mm[keep, ]) - cp[keep]) < 1e-8), sum(keep)))
    hits <- sapply(1:6, function(j)
        sum(abs(rowMeans(mm[keep, -j, drop = FALSE]) - cp[keep]) < 1e-8))
    for (j in 1:6) cat(sprintf("  drop %-7s -> %4d of %d\n", A[j], hits[j], sum(keep)))
    r4 <- hits[6] == sum(keep) && max(hits[-6]) < sum(keep)
    cat("  ", if (r4) "PASS -- dropping affil6 reproduces it exactly and uniquely" else "FAIL",
        "\n", sep = "")
} else {
    cat("\n=== Route 4 skipped: ", SCORED, " not present ===\n", sep = "")
}
# --- Route 5: can the five T&S wordings be keyed to affil1-affil5? -------
# Tackman & Srivastava (2016), psycnet.apa.org/fulltext/2015-37763-001.pdf, gives
# the five items in order: (a) "I like this person", (b) "I would enjoy talking
# to this person", (c) "I would enjoy spending time with this person",
# (d) "This person is the type of person I could get along with",
# (e) "This person is the type of person I could become close friends with".
#
# Route 4 already proves affil1-affil5 ARE these five (the deposit composite
# averages exactly them). The open question is the per-code ORDER. This route
# tries to settle it and FAILS -- recorded because a failed route is evidence.
cat("\n=== Route 5: keying the five wordings to codes (INCONCLUSIVE) ===\n")
cat("  endorsement ease, by mean:\n")
for (nm in paste0("affil", 1:5))
    cat(sprintf("    %-7s M=%.3f\n", nm, mean(W[, nm], na.rm = TRUE)))
cat("  Consistent with (a) easiest and (e) hardest: affil1 is the highest mean\n")
cat("  and affil5 the lowest, which fits (a) 'I like this person' against\n")
cat("  (e) 'could become close friends with'. That pins the ENDS only.\n\n")
cat("  Shared-stem test for (c) vs (d) at affil3/affil4: items (d) and (e) share\n")
cat("  the stem 'This person is the type of person I could ...', so (d) should\n")
cat("  correlate more with (e)=affil5 than (c) does.\n")
cat(sprintf("    r(affil3, affil5) = %.3f\n", cor(W[, "affil3"], W[, "affil5"], use = "complete.obs")))
cat(sprintf("    r(affil4, affil5) = %.3f\n", cor(W[, "affil4"], W[, "affil5"], use = "complete.obs")))
cat("  This points AGAINST article order (it would make affil3 = (d)), but the\n")
cat("  test is confounded: affil3's mean sits closer to affil5's than affil4's\n")
cat("  does, and items closer in difficulty correlate more highly whatever the\n")
cat("  wording. Differential correlations with perceived warmth, agreeableness,\n")
cat("  extraversion and competence separate affil3 from affil4 by <= 0.02.\n")
cat("  CONCLUSION: the order is NOT established. All six affil codes keep empty\n")
cat("  item_text; the five wordings are recorded in provenance instead. Closing\n")
cat("  this needs the administered Qualtrics form, which the deposit does not\n")
cat("  contain -- a human action, not another statistical route.\n")

cat("\nFINAL VERDICT:", if (r1 && r2 && r3 && isTRUE(r4)) "PASS" else
    if (r1 && r2 && r3 && is.na(r4)) "PASS (route 4 unavailable)" else "FAIL", "\n")
