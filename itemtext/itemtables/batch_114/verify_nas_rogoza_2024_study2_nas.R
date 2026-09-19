# verify_nas_rogoza_2024_study2_nas.R -- Step 5b mapping evidence.
#
# CLAIM UNDER TEST: the 18 adjectives listed in the study's own Study 2 Codebook
# (OSF u93eq, "Codebooks, Data and Scripts/Study 2/Study 2 Codebook.docx") are in the
# same order as the NAS1..NAS18 columns of "Study 2 NAS.sav", hence as the live IRW
# `item` codes (data/nas_rogoza_2024.R melts the .sav columns unchanged, so the IRW
# item code IS the source column name -- but the .sav carries NO variable labels, so
# which adjective NAS7 holds is an ORDER inference and has to be checked).
#
# FALSIFIABLE PREDICTION: the paper's additional online Table 2 ("Oblimin-Rotated
# Factor Loadings of the Three Adjective Narcissism Scales", Supplementary materials
# (Study 1 and Study 2).docx, OSF u93eq) prints, per ADJECTIVE NAME, a triple of
# loadings on the Neurotic / Antagonistic / Agentic factors from a 3-factor principal
# axis oblimin EFA of all 42 adjectives (N = 353). All 18 NAS triples are distinct.
# Re-running that EFA with the LIVE IRW NAS responses in place of the .sav's NAS
# columns must reproduce, for each item code, the triple published for the adjective
# this extraction assigned to it -- and nearest-neighbour matching over the 18
# published triples must return the identity permutation. If item_text for any two
# NAS items were swapped, that assignment would break.
#
# If it were swapped the wrong way this script FAILS; that is the point.

suppressMessages({library(irw); library(haven); library(psych)})

TABLE <- "nas_rogoza_2024_study2_nas"
CACHE <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- tempdir()
SAV <- file.path(CACHE, "Study2_NAS.sav")
if (!file.exists(SAV)) download.file("https://osf.io/download/cpb7q/", SAV, quiet = TRUE, mode = "wb")

# --- the extraction under test: item code -> adjective (Study 2 Codebook order) ---
ADJ <- c(NAS1="Abusive", NAS2="Spiteful", NAS3="Scheming", NAS4="Humiliating",
         NAS5="Misusing", NAS6="Insidious", NAS7="Treacherous", NAS8="Nasty",
         NAS9="Devaluing", NAS10="Offending", NAS11="Oppressive", NAS12="Denouncing",
         NAS13="Exploitative", NAS14="Manipulative", NAS15="Depreciating",
         NAS16="Conceitful", NAS17="Condescending", NAS18="Selfish")

# --- published: additional online Table 2, NAS block (Neurotic, Antagonistic, Agentic)
PUB <- rbind(
  Abusive      = c( .02, .71,  .01), Spiteful    = c( .22, .60,  .03),
  Scheming     = c( .11, .60,  .06), Humiliating = c( .15, .69, -.03),
  Misusing     = c( .05, .77,  .03), Insidious   = c(-.05, .82, -.02),
  Treacherous  = c(-.09, .82,  .00), Nasty       = c( .04, .66,  .02),
  Devaluing    = c( .02, .75,  .05), Offending   = c(-.01, .74, -.03),
  Oppressive   = c(-.13, .84, -.02), Denouncing  = c(-.07, .81, -.04),
  Exploitative = c(-.15, .84,  .05), Manipulative= c( .17, .57,  .03),
  Depreciating = c( .06, .69, -.02), Conceitful  = c( .00, .64,  .07),
  Condescending= c( .29, .45,  .02), Selfish     = c( .42, .33, -.02))
colnames(PUB) <- c("Neurotic", "Antagonistic", "Agentic")

# --- live NAS responses, wide; NVS/NGS columns from the source .sav (not in this table)
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(as.numeric(w$id)), ]

sav <- as.data.frame(read_sav(SAV))
# data/nas_rogoza_2024.R sets df2$id <- seq(1, nrow(df2)) before pivoting, so live id i
# is .sav row i. Guard that before relying on it.
stopifnot(nrow(sav) == nrow(w), identical(as.numeric(w$id), as.numeric(seq_len(nrow(sav)))))

nas <- paste0("NAS", 1:18)
X <- cbind(
  as.data.frame(lapply(sav[paste0("NVS", 1:11)], as.numeric)),
  setNames(as.data.frame(lapply(w[nas], as.numeric)), nas),   # LIVE data
  as.data.frame(lapply(sav[paste0("NGS", 1:13)], as.numeric)))

fa3 <- fa(X, nfactors = 3, fm = "pa", rotate = "oblimin")
L <- unclass(fa3$loadings)

# label the three extracted factors by which block they own; fix sign to that block
blocks <- list(Neurotic = 1:11, Antagonistic = 12:29, Agentic = 30:42)
own <- sapply(blocks, function(ix) which.max(colMeans(abs(L[ix, , drop = FALSE]))))
stopifnot(length(unique(own)) == 3)
L <- L[, unlist(own), drop = FALSE]
colnames(L) <- names(blocks)
for (j in 1:3) if (mean(L[blocks[[j]], j]) < 0) L[, j] <- -L[, j]
OBS <- L[nas, , drop = FALSE]

cat(sprintf("%-6s %-14s %18s %18s %6s\n", "item", "assigned adj",
            "published (N/An/Ag)", "observed (N/An/Ag)", "dist"))
d3 <- numeric(18); best <- character(18)
for (i in 1:18) {
  a <- ADJ[[nas[i]]]
  dists <- sqrt(rowSums((PUB - matrix(OBS[i, ], nrow(PUB), 3, byrow = TRUE))^2))
  best[i] <- names(which.min(dists)); d3[i] <- dists[a]
  cat(sprintf("%-6s %-14s  %5.2f %5.2f %5.2f   %5.2f %5.2f %5.2f  %5.3f%s\n",
              nas[i], a, PUB[a, 1], PUB[a, 2], PUB[a, 3],
              OBS[i, 1], OBS[i, 2], OBS[i, 3], d3[i],
              if (best[i] == a) "" else paste0("  <-- nearest is ", best[i])))
}
ok_assign <- sum(best == unname(ADJ[nas]))
cat(sprintf("\nnearest-published-triple assignment recovers %d/18 item->adjective pairs\n", ok_assign))
cat(sprintf("largest euclidean deviation from the published triple: %.3f\n", max(d3)))
sep <- min(apply(PUB, 1, function(p) min(sqrt(rowSums((PUB - matrix(p, 18, 3, byrow=TRUE))^2))[-1])))
cat(sprintf("all 18 published triples are distinct (min pairwise separation %.3f)\n",
            min(as.matrix(dist(PUB))[lower.tri(diag(18))])))
cat("This distinguishes every NAS item from every other one: the assignment is\n",
    "nearest-neighbour over 18 mutually distinct published triples, not a class or block match.\n",
    "It does NOT check option_text<->resp; those anchors come from the codebook's own\n",
    "printed scale (1 = Not at all, 7 = Extremely) and carry no inference.\n", sep = "")

cat(if (ok_assign == 18 && max(d3) <= 0.05) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
