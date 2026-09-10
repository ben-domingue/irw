# verify_nas_rogoza_2024_study2_nvs.R -- Step 5b mapping evidence.
#
# CLAIM UNDER TEST: the first 11 adjectives listed in the study's own Study 2 Codebook
# (OSF u93eq, "Codebooks, Data and Scripts/Study 2/Study 2 Codebook.docx") are, in that
# order, the NVS1..NVS11 columns of "Study 2 NAS.sav", hence the live IRW `item` codes
# (data/nas_rogoza_2024.R melts the .sav columns unchanged, so the IRW item code IS the
# source column name -- but the .sav carries NO variable labels and NO value labels, so
# which adjective NVS7 holds is an ORDER inference and has to be checked against data).
#
# FALSIFIABLE PREDICTION: the paper's additional online Table 2 ("Oblimin-Rotated Factor
# Loadings of the Three Adjective Narcissism Scales", Supplementary materials (Study 1 and
# Study 2).docx, OSF u93eq, https://osf.io/download/ed6up/) prints, per ADJECTIVE NAME, a
# triple of loadings on the Neurotic / Antagonistic / Agentic factors from a 3-factor
# principal-axis oblimin EFA of all 42 adjectives (N = 353). Re-running that EFA with the
# LIVE IRW NVS responses in place of the .sav's NVS columns must reproduce, for each item
# code, the triple published for the adjective this extraction assigned to it -- and
# nearest-neighbour matching over the published triples must return the identity
# permutation. If item_text for any two NVS items were swapped, that would break.
#
# NOTE ON POWER: the NVS block's published triples are far less separated than the NAS
# block's (several neurotic adjectives load ~.65-.68 / ~.00 / ~.00). The script therefore
# matches against ALL 42 published triples, and reports both the within-NVS minimum
# pairwise separation and the largest observed deviation, so the reader can see whether
# the route actually resolves every item or only the well-separated ones.

suppressMessages({library(irw); library(haven); library(psych)})

TABLE <- "nas_rogoza_2024_study2_nvs"
CACHE <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
if (!dir.exists(CACHE)) { CACHE <- tempdir() }
SAV <- file.path(CACHE, "Study2_NAS.sav")
if (!file.exists(SAV)) download.file("https://osf.io/download/cpb7q/", SAV, quiet = TRUE, mode = "wb")

# --- the extraction under test: item code -> adjective (Study 2 Codebook order) ---
ADJ <- c(NVS1="Ashamed", NVS2="Ignored", NVS3="Self-absorbed", NVS4="Fragile",
         NVS5="Underappreciated", NVS6="Envious", NVS7="Resentful", NVS8="Insecure",
         NVS9="Irritable", NVS10="Misunderstood", NVS11="Vengeful")

# --- published: additional online Table 2, all 42 adjectives, in codebook order ---
PUB <- rbind(
  Ashamed        = c( .61,  .13,  .00), Ignored      = c( .79, -.06, -.01),
  `Self-absorbed`= c( .27,  .25,  .05), Fragile      = c( .66, -.08, -.02),
  Underappreciated=c( .65, -.01,  .00), Envious      = c( .75,  .02,  .03),
  Resentful      = c( .72,  .12,  .00), Insecure     = c( .87, -.13, -.10),
  Irritable      = c( .68,  .09, -.07), Misunderstood= c( .66,  .06,  .02),
  Vengeful       = c( .27,  .41,  .05),
  Abusive        = c( .02,  .71,  .01), Spiteful     = c( .22,  .60,  .03),
  Scheming       = c( .11,  .60,  .06), Humiliating  = c( .15,  .69, -.03),
  Misusing       = c( .05,  .77,  .03), Insidious    = c(-.05,  .82, -.02),
  Treacherous    = c(-.09,  .82,  .00), Nasty        = c( .04,  .66,  .02),
  Devaluing      = c( .02,  .75,  .05), Offending    = c(-.01,  .74, -.03),
  Oppressive     = c(-.13,  .84, -.02), Denouncing   = c(-.07,  .81, -.04),
  Exploitative   = c(-.15,  .84,  .05), Manipulative = c( .17,  .57,  .03),
  Depreciating   = c( .06,  .69, -.02), Conceitful   = c( .00,  .64,  .07),
  Condescending  = c( .29,  .45,  .02), Selfish      = c( .42,  .33, -.02),
  Perfect        = c(-.13,  .06,  .67), Superior     = c( .02,  .00,  .70),
  Heroic         = c( .01,  .02,  .72), Omnipotent   = c(-.08,  .29,  .52),
  Authoritative  = c( .00,  .14,  .54), Glorious     = c( .00, -.03,  .74),
  Prestigous     = c(-.04, -.04,  .87), Acclaimed    = c( .001,-.09,  .85),
  Prominent      = c( .00, -.08,  .90), `High-status`= c(-.04, -.09,  .89),
  Dominant       = c( .02, -.01,  .73), Envied       = c( .09,  .08,  .64),
  Powerful       = c( .04, -.05,  .84))
colnames(PUB) <- c("Neurotic", "Antagonistic", "Agentic")
stopifnot(nrow(PUB) == 42)

# --- live NVS responses, wide; NAS/NGS columns from the source .sav (not in this table)
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(as.numeric(w$id)), ]

sav <- as.data.frame(read_sav(SAV))
# data/nas_rogoza_2024.R sets df2$id <- seq(1, nrow(df2)) before pivoting, so live id i
# is .sav row i. Guard that before relying on it.
stopifnot(nrow(sav) == nrow(w), identical(as.numeric(w$id), as.numeric(seq_len(nrow(sav)))))

nvs <- paste0("NVS", 1:11)
X <- cbind(
  setNames(as.data.frame(lapply(w[nvs], as.numeric)), nvs),   # LIVE data
  as.data.frame(lapply(sav[paste0("NAS", 1:18)], as.numeric)),
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
OBS <- L[nvs, , drop = FALSE]

cat(sprintf("%-6s %-16s %18s %18s %6s\n", "item", "assigned adj",
            "published (N/An/Ag)", "observed (N/An/Ag)", "dist"))
d3 <- numeric(11); best <- character(11)
for (i in 1:11) {
  a <- ADJ[[nvs[i]]]
  dists <- sqrt(rowSums((PUB - matrix(OBS[i, ], nrow(PUB), 3, byrow = TRUE))^2))
  best[i] <- names(which.min(dists)); d3[i] <- dists[a]
  cat(sprintf("%-6s %-16s  %5.2f %5.2f %5.2f   %5.2f %5.2f %5.2f  %5.3f%s\n",
              nvs[i], a, PUB[a, 1], PUB[a, 2], PUB[a, 3],
              OBS[i, 1], OBS[i, 2], OBS[i, 3], d3[i],
              if (best[i] == a) "" else paste0("  <-- nearest is ", best[i])))
}
ok_assign <- sum(best == unname(ADJ[nvs]))
cat(sprintf("\nnearest-published-triple assignment (over all 42 published triples) recovers %d/11 item->adjective pairs\n", ok_assign))
cat(sprintf("largest euclidean deviation from the published triple: %.3f\n", max(d3)))
Pn <- PUB[unname(ADJ[nvs]), , drop = FALSE]
sep_nvs <- min(as.matrix(dist(Pn))[lower.tri(diag(11))])
cat(sprintf("minimum pairwise separation among the 11 NVS published triples: %.3f\n", sep_nvs))
cat(sprintf("separation/deviation margin: %.2fx\n", sep_nvs / max(d3)))
cat("Scope: this checks item_text<->item only. It does NOT check option_text<->resp;\n",
    "those anchors come from the codebook's own printed scale (1 = Not at all,\n",
    "7 = Extremely) and carry no inference.\n", sep = "")

cat(if (ok_assign == 11 && max(d3) < sep_nvs / 2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
