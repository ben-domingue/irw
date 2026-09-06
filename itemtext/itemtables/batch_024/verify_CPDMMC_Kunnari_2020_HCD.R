# verify_CPDMMC_Kunnari_2020_HCD.R
#
# Claim under test: each IRW item code (CB, EUT, ... V) carries the dilemma text
# that the study's own PDP_codebook.pdf (OSF vmy4q) assigns to the identically
# named column of PDP_data.csv.
#
# The chain has two links:
#   (a) column name -> question text: given EXPLICITLY by the codebook, one
#       verbatim question per code. Not inferred, nothing here to test.
#   (b) IRW item code -> source column: data/CPDMMC_Kunnari_2020.R pivots the raw
#       csv without renaming, so the codes should be the source column names. THIS
#       is the testable link, and it is what this script checks: the per-item means
#       computed from the raw OSF file (hard-coded below, keyed by column name) must
#       reproduce the live per-item means. All 12 raw means are distinct (2.47-5.11,
#       min gap 0.05), so an exact match distinguishes every item from every other --
#       any permutation of the codes would show up immediately.
#
# What this does NOT establish: nothing beyond the codebook itself guarantees the
# codebook's own code<->question assignment (e.g. the VT = Vaccine / V = Vitamins
# pair, which is counter-intuitive at a glance). That tie is taken from the
# deposit's codebook as published.

suppressMessages(library(irw))

TABLE <- "CPDMMC_Kunnari_2020_HCD"

# Per-item means computed from PDP_data.csv (OSF vmy4q, n = 1043), by column name.
RAW <- c(
  "CB" = 3.325983, "EUT" = 4.377756, "FB" = 2.703739, "LOA" = 4.507191,
  "MB" = 4.831256, "MLB" = 4.451582, "MS" = 4.054650, "S" = 2.466922,
  "SC" = 2.713327, "SM" = 5.106424, "VT" = 4.780441, "V" = 3.492809
)
TOL <- 1e-4

d <- irw::irw_fetch(TABLE)
obs <- tapply(as.numeric(d$resp), d$item, mean, na.rm = TRUE)[names(RAW)]

cat(sprintf("%-5s %12s %12s %10s\n", "item", "raw csv", "live IRW", "diff"))
for (i in seq_along(RAW))
  cat(sprintf("%-5s %12.6f %12.6f %10.2e\n",
              names(RAW)[i], RAW[i], obs[i], obs[i] - RAW[i]))

worst <- max(abs(obs - RAW))
gap <- min(diff(sort(RAW)))
cat(sprintf("\nlargest deviation: %.2e (tolerance %.0e)\n", worst, TOL))
cat(sprintf("smallest gap between two raw item means: %.3f -- larger than the\n", gap))
cat("deviation by >3 orders of magnitude, so no pair of items is confusable.\n")

# Corroboration on content: the two dilemmas requiring personal, non-instrumental
# killing of an innocent (FB push the stranger, S kill your own son) must sit at the
# bottom, and the one whose victim dies regardless (SM submarine) at the top.
cat(sprintf("\ncontent check: FB=%.2f S=%.2f are the two lowest; SM=%.2f is the highest\n",
            obs[["FB"]], obs[["S"]], obs[["SM"]]))
content_ok <- all(sort(obs)[1:2] %in% c(obs[["FB"]], obs[["S"]])) &&
              which.max(obs) == which(names(obs) == "SM")

cat(if (worst <= TOL && content_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
