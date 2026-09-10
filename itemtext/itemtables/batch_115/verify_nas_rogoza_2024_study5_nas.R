# verify_nas_rogoza_2024_study5_nas.R
#
# Step 5b re-runnable evidence for nas_rogoza_2024_study5_nas.
#
# THE CLAIM UNDER TEST. The IRW item codes NAS1..NAS4 are the column names of
# OSF u93eq's "Study 5 NAS.sav" (data/nas_rogoza_2024.R pivots them by name), but
# that .sav carries NO variable labels and NO value labels, so which Polish
# adjective each code holds is an ORDER inference off the study's own
# "Study 5 Codebook - Daily.docx", which prints under the heading NAS:
#     Znieważający / Lekceważący / Wyzyskujący / Bezczelny
# and which this extraction reads as NAS1/NAS2/NAS3/NAS4 in that order. The
# English glosses come from the study's own "NAS - questionnaire and
# translations/NAS.xlsx": Abusive / Depreciating / Exploitative / Nasty.
#
# The rival hypothesis this has to beat is NOT a random permutation -- it is the
# order the same four adjectives appear in on the FINAL 16-item NAS form
# (Abusive, Nasty, Exploitative, Depreciating; rows 1, 8, 13, 15 of NAS.xlsx,
# the four marked "used in the within-person protocol"). The daily codebook lists
# them in a different order, so exactly one of the two orders is right.
#
# TWO ROUTES, both anchored on Study 2 of the same paper, whose 18-item
# code->adjective mapping was VERIFIED item-by-item in batch_114 against the
# published EFA loadings of additional online Table 2 (18/18, worst euclidean
# deviation 0.021).
#
#   Route 8  (semantic coherence of the response distribution). Lekceważący
#            "dismissive/depreciating" is by far the mildest and most everyday
#            of the four adjectives, so it should be the most endorsed and the
#            least floored. Only one live code is separated on mean level.
#
#   Route 1  (cross-study nomological profile). In Study 2, Exploitative is the
#            one adjective of the four that tilts GRANDIOSE rather than
#            VULNERABLE: it is the only one whose correlation with the NGS
#            composite exceeds its correlation with the NVS composite. That is a
#            per-adjective signature, computed here on the LIVE IRW Study 5
#            tables (NAS joined to its NVS and NGS siblings on id + wave).
#
# WHAT THIS DOES NOT ESTABLISH, stated up front: nothing here separates NAS1
# from NAS4 (Znieważający/Abusive vs Bezczelny/Nasty). Their live means differ
# by 0.5 points on a 0-100 slider and in Study 2 the same two adjectives sit
# 0.08 apart on a 1-7 scale with d differing by 0.003. The status is PARTIAL.

suppressMessages(library(irw))

TABLE  <- "nas_rogoza_2024_study5_nas"
CODES  <- c("NAS1", "NAS2", "NAS3", "NAS4")
SHIPPED <- c(NAS1 = "Zniewazajacy/Abusive",     NAS2 = "Lekcewazacy/Depreciating",
             NAS3 = "Wyzyskujacy/Exploitative", NAS4 = "Bezczelny/Nasty")

## Study 2 anchors. Computed from OSF u93eq "Study 2 NAS.sav" (CC0 1.0, N = 353,
## https://osf.io/download/cpb7q/) using batch_114's verified mapping
## NAS1=Abusive, NAS8=Nasty, NAS13=Exploitative, NAS15=Depreciating.
## Hard-coded so this script needs only the live IRW data.
S2_MEAN <- c(Abusive = 1.331, Depreciating = 1.513, Exploitative = 1.518, Nasty = 1.411)
S2_D    <- c(Abusive = 0.144, Depreciating = 0.200, Exploitative = -0.073, Nasty = 0.141)
## (S2_D[a] = cor(a, mean of NVS1..NVS11) - cor(a, mean of NGS1..NGS13).)

nas <- irw::irw_fetch(TABLE)
nvs <- irw::irw_fetch("nas_rogoza_2024_study5_nvs")
ngs <- irw::irw_fetch("nas_rogoza_2024_study5_ngs")

wide <- function(d) {
    d <- as.data.frame(d)
    d$resp <- suppressWarnings(as.numeric(as.character(d$resp)))
    d <- d[!is.na(d$resp), c("id", "wave", "item", "resp")]
    key <- paste(d$id, d$wave, sep = "\r")
    codes <- sort(unique(d$item))
    w <- data.frame(key = sort(unique(key)), stringsAsFactors = FALSE)
    for (cd in codes) {
        s2 <- d[d$item == cd, ]
        w[[cd]] <- s2$resp[match(w$key, paste(s2$id, s2$wave, sep = "\r"))]
    }
    parts <- do.call(rbind, strsplit(w$key, "\r", fixed = TRUE))
    w$id <- parts[, 1]; w$wave <- parts[, 2]
    w
}
W  <- wide(nas)
NV <- wide(nvs); NG <- wide(ngs)
NV$NVSm <- rowMeans(NV[, grep("^NVS", names(NV))], na.rm = TRUE)
NG$NGSm <- rowMeans(NG[, grep("^NGS", names(NG))], na.rm = TRUE)
M <- merge(merge(W, NV[, c("id", "wave", "NVSm")], by = c("id", "wave")),
           NG[, c("id", "wave", "NGSm")], by = c("id", "wave"))

cat("live rows fetched: NAS ", nrow(nas), " | joined person-occasions: ", nrow(M), "\n\n", sep = "")

## ---- ROUTE 8 -------------------------------------------------------------
cat("=== Route 8: mean level and floor share, live IRW data ===\n")
mu   <- sapply(CODES, function(cc) mean(W[[cc]], na.rm = TRUE))
zero <- sapply(CODES, function(cc) 100 * mean(W[[cc]] == 0, na.rm = TRUE))
cat(sprintf("%-6s %-26s %8s %9s\n", "code", "shipped as", "mean", "% at 0"))
for (cc in CODES)
    cat(sprintf("%-6s %-26s %8.3f %8.2f%%\n", cc, SHIPPED[[cc]], mu[[cc]], zero[[cc]]))
top    <- CODES[which.max(mu)]
margin <- max(mu) - max(mu[CODES != top])
cat(sprintf("\nhighest mean: %s, ahead of the next by %.3f points on a 0-100 slider\n",
            top, margin))
cat(sprintf("least floored: %s (%.2f%% at 0, vs %.2f-%.2f%% for the rest)\n",
            CODES[which.min(zero)], min(zero), min(zero[CODES != CODES[which.min(zero)]]),
            max(zero)))
cat("prediction: the mildest adjective, Lekceważący/Depreciating, is NAS2.\n")
cat("rival (NAS.xlsx 16-item order) would put Nasty here and Depreciating at NAS4,\n",
    "  i.e. the mildest adjective would be the LEAST endorsed and most floored.\n", sep = "")
r8 <- identical(top, "NAS2") && identical(CODES[which.min(zero)], "NAS2") && margin > 2

## ---- ROUTE 1 -------------------------------------------------------------
cat("\n=== Route 1: cross-study nomological profile (Study 2 anchors) ===\n")
d5 <- sapply(CODES, function(cc)
    cor(M[[cc]], M$NVSm, use = "pairwise") - cor(M[[cc]], M$NGSm, use = "pairwise"))
cat(sprintf("%-6s %-26s %10s %14s\n", "code", "shipped as", "d(live)", "d(Study 2)"))
for (cc in CODES) {
    a <- sub(".*/", "", SHIPPED[[cc]])
    cat(sprintf("%-6s %-26s %10.3f %14.3f\n", cc, SHIPPED[[cc]], d5[[cc]], S2_D[[a]]))
}
cat(sprintf("\nminimum d: live %s (%.3f); Study 2 minimum is Exploitative (%.3f),\n",
            CODES[which.min(d5)], min(d5), min(S2_D)))
cat("  the only one of the four whose NGS correlation exceeds its NVS correlation.\n")
r1 <- identical(CODES[which.min(d5)], "NAS3")

## ---- all 24 permutations -------------------------------------------------
cat("\n=== Rank agreement over all 24 code->adjective assignments ===\n")
perm <- function(v) { if (length(v) == 1) return(list(v))
    do.call(base::c, lapply(seq_along(v), function(i)
        lapply(perm(v[-i]), function(r) base::c(v[i], r)))) }
ps <- perm(names(S2_D))
sc <- sapply(ps, function(p) suppressWarnings(
    cor(S2_D[p], d5[CODES], method = "spearman")))
o <- order(-sc)
for (k in seq_len(6))
    cat(sprintf("  rho=%5.2f  %s\n", sc[o[k]], paste(ps[[o[k]]], collapse = " ")))
shipped_perm <- c("Abusive", "Depreciating", "Exploitative", "Nasty")
rk <- which(sapply(ps[o], function(p) identical(p, shipped_perm)))
cat(sprintf("shipped assignment (%s) ranks %d of 24, rho=%.2f\n",
            paste(shipped_perm, collapse = " "), rk, sc[o[rk]]))
cat(sprintf("rival NAS.xlsx assignment (Abusive Nasty Exploitative Depreciating) rho=%.2f\n",
            cor(S2_D[c("Abusive", "Nasty", "Exploitative", "Depreciating")],
                d5[CODES], method = "spearman")))

cat("\nEstablished: NAS2 = Lekceważący/Depreciating (route 8) and NAS3 =",
    "Wyzyskujący/Exploitative (route 1).\n")
cat("NOT established: NAS1 vs NAS4 (Znieważający/Abusive vs Bezczelny/Nasty) --",
    "no signal\n  separates them in either study. Hence PARTIAL, not VERIFIED.\n")

cat(if (r8 && r1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
