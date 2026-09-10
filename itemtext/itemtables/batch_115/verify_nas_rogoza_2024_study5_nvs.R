# verify_nas_rogoza_2024_study5_nvs.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST. data/nas_rogoza_2024.R pivots 'Study 5 NAS.sav' long with
# names_to = "item", so the IRW code IS the .sav column name (NVS1..NVS4) -- but
# that .sav carries NO variable labels and NO value labels, so which adjective
# NVS1 holds is an ORDER inference (mapping_basis = paper_order) off three of the
# study's own documents, all of which list the four NVS adjectives in the same
# order:
#   OSF u93eq 'Codebooks, Data and Scripts/Study 5/Study 5 Codebook - Daily.docx'
#       NVS: Zleckeważony, Urażony, Niezrozumiany, Niedoceniony
#   OSF u93eq 'Study 6 Codebook - State.docx'  (same four, same order)
#   Rogoza et al. (2024) Psych. Assessment, Study 5 Measures:
#       "we used four items from the NVS (Ignored, Resentful, Misunderstood,
#        Underappreciated)"
# So the shipped mapping is NVS1=Ignored, NVS2=Resentful, NVS3=Misunderstood,
# NVS4=Underappreciated.
#
# WHAT THIS SCRIPT CHECKS. The same authors administered the full 11-adjective
# English NVS as a trait measure in Study 2 ('Study 2 NAS.sav', N = 353,
# 1-7 scale). Those four adjectives split there into a clearly LOW-endorsement
# pair (Resentful 2.252, Ignored 2.629) and a clearly HIGH-endorsement pair
# (Misunderstood 3.105, Underappreciated 3.334). If the shipped mapping is right,
# the live Study 5 person means must show the same block split: NVS3 and NVS4
# both above NVS1 and NVS2. That is a falsifiable prediction -- it fails for 20
# of the 24 possible item->adjective permutations.
#
# WHAT IT DOES NOT ESTABLISH, and this is why the recorded status is PARTIAL:
#   * it does not separate NVS1 from NVS2 (Ignored vs Resentful): their person
#     means differ by 0.45 points on a 0-100 slider, n.s.;
#   * it does not separate NVS3 from NVS4 (Misunderstood vs Underappreciated).
#     Their means differ significantly, but in the OPPOSITE rank order to
#     Study 2's, so the contrast is evidence for the block split only, not for
#     the assignment within the block.
#   * a 24-permutation match of the 4x4 correlation matrix against Study 2's is
#     also computed below and is NON-discriminative (reported as a negative
#     result). This instrument is dominated by a general factor.
# Within-pair order therefore rests on the three documents above, not on data.

suppressMessages(library(irw))

TABLE <- "nas_rogoza_2024_study5_nvs"
ITEMS <- c("NVS1", "NVS2", "NVS3", "NVS4")
ADJ   <- c("Ignored", "Resentful", "Misunderstood", "Underappreciated")

# Study 2 anchors, computed from OSF u93eq 'Codebooks, Data and Scripts/Study 2/
# Study 2 NAS.sav' columns NVS2 / NVS7 / NVS10 / NVS5 (= Ignored / Resentful /
# Misunderstood / Underappreciated, per the Study 2 Codebook's 42-adjective list).
S2_MEAN <- c(Ignored = 2.629, Resentful = 2.252,
             Misunderstood = 3.105, Underappreciated = 3.334)
S2_COR <- matrix(c(1.000, 0.559, 0.555, 0.572,
                   0.559, 1.000, 0.491, 0.492,
                   0.555, 0.491, 1.000, 0.585,
                   0.572, 0.492, 0.585, 1.000), 4, 4,
                 dimnames = list(ADJ, ADJ))

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]

# person x item matrix of person means (Study 5 is a 30-day daily-diary design)
pm <- tapply(d$resp, list(as.character(d$id), d$item), mean)
pm <- pm[, ITEMS, drop = FALSE]
pm <- pm[stats::complete.cases(pm), , drop = FALSE]

cat(sprintf("live table: %s   %d rows, %d persons\n\n", TABLE, nrow(d), nrow(pm)))

cat("Study 2 anchor (English trait NVS, 1-7) vs Study 5 live person means (0-100)\n")
cat(sprintf("%-6s %-17s %10s %12s %8s\n",
            "item", "shipped adjective", "S2 mean", "S5 mean", "block"))
blk <- ifelse(S2_MEAN[ADJ] > 2.9, "HIGH", "LOW")
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %-17s %10.3f %12.3f %8s\n",
                ITEMS[i], ADJ[i], S2_MEAN[ADJ[i]], mean(pm[, ITEMS[i]]), blk[i]))

cat("\nBlock-split contrasts (paired t over persons; prediction: all four > 0)\n")
pairs <- list(c("NVS3","NVS1"), c("NVS3","NVS2"), c("NVS4","NVS1"), c("NVS4","NVS2"))
ok <- TRUE
for (p in pairs) {
    tt <- stats::t.test(pm[, p[1]], pm[, p[2]], paired = TRUE)
    cat(sprintf("  %s - %s = %+7.2f   t = %6.2f   p = %.2g\n",
                p[1], p[2], mean(pm[, p[1]] - pm[, p[2]]),
                tt$statistic, tt$p.value))
    if (!(mean(pm[, p[1]] - pm[, p[2]]) > 0 && tt$p.value < 1e-3)) ok <- FALSE
}

cat("\nContrasts that do NOT resolve (reported, not used in the verdict)\n")
for (p in list(c("NVS1","NVS2"), c("NVS3","NVS4"))) {
    tt <- stats::t.test(pm[, p[1]], pm[, p[2]], paired = TRUE)
    cat(sprintf("  %s - %s = %+7.2f   t = %6.2f   p = %.2g\n",
                p[1], p[2], mean(pm[, p[1]] - pm[, p[2]]),
                tt$statistic, tt$p.value))
}
cat("  Study 2 ranks Underappreciated (3.334) ABOVE Misunderstood (3.105);\n")
cat("  Study 5 ranks NVS3 above NVS4, i.e. the reverse. Different sample,\n")
cat("  language, timeframe and response format -- so the within-block order is\n")
cat("  left to the codebooks, and is recorded as unverified.\n")

# --- negative result: correlation-structure permutation matching ---
C5 <- stats::cor(pm)
iu <- upper.tri(C5)
perms <- list(); k <- 0
idx <- 1:4
for (a in idx) for (b in setdiff(idx,a)) for (cc in setdiff(idx,c(a,b))) {
    e <- setdiff(idx, c(a,b,cc)); k <- k + 1; perms[[k]] <- c(a,b,cc,e)
}
# metric: agreement of the 6 off-diagonal correlations with Study 2's, as a
# Pearson r (a mean-absolute-difference metric is permutation-invariant here,
# because every Study 5 r exceeds every Study 2 r, so all 24 tie exactly).
sc <- sapply(perms, function(p) -stats::cor(C5[p,p][iu], S2_COR[iu]))
o <- order(sc)
id_rank <- which(sapply(perms[o], function(p) all(p == 1:4)))
cat(sprintf("\nCorrelation-permutation match vs Study 2 (24 perms, criterion = r between\n  the two sets of 6 off-diagonal correlations): identity ranks %d of 24\n",
            id_rank))
cat(sprintf("  best r = %+.3f (perm %s); identity r = %+.3f -> NON-DISCRIMINATIVE\n",
            -sc[o[1]], paste(perms[[o[1]]], collapse = ""), -sc[o[id_rank]]))
cat(sprintf("  Study 5 between-person r range %.3f-%.3f -- a spread of %.3f across all\n",
            min(C5[iu]), max(C5[iu]), max(C5[iu]) - min(C5[iu])))
cat("  six correlations, comparable to their own sampling error at n = 317, so the\n")
cat("  ranking above is noise and is NOT read as evidence against the mapping. This\n")
cat("  is the underpowered case SKILL.md Step 5b route 5 warns about: a single\n")
cat("  dominant factor leaves the four items near-exchangeable.\n")

cat("\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
