# verify_chuemchit_2024_nonpartner_violence.R
#
# CLAIM UNDER TEST: each of the five item codes carries the violence TYPE its
# item_text names (npeco12=economic, nppsy12=psychological, npcyb12=cyber
# bullying, npphy12=physical, npsex12=sexual), and resp=1 means "experienced".
#
# FALSIFIABLE PREDICTION: Chuemchit et al. 2024 (PLOS ONE 10.1371/journal.pone.0300388)
# report, in the Results text describing Table 4, the proportion of the 494 women
# who experienced each type of NON-intimate-partner violence in the past 12 months:
#   "Psychological violence was the most common type (11.4% for IPV and 14.4% for
#    N-IPV), followed by economic violence (7.7% for IPV and 7.3% for N-IPV) and
#    sexual violence (6.9% for IPV and 3.4% for N-IPV). The proportion of
#    cyberbullying was 6.4% for IPV and 2.2% for N-IPV, and that of physical
#    violence was 5.9% for IPV and 0.8% for N-IPV".
# All five published values are distinct, so mean(resp==1) per item distinguishes
# EVERY item from EVERY other item and also fixes the coding direction.
#
# What this does NOT test: which underlying S1-File questionnaire questions
# (Q126-Q191) were composited into each binary indicator -- the study publishes no
# composite key -- nor the administered (Khmer/Lao/Myanmar) wording.

suppressMessages(library(irw))

TABLE <- "chuemchit_2024_nonpartner_violence"

PUBLISHED <- c(npeco12 = 7.3, nppsy12 = 14.4, npcyb12 = 2.2,
               npphy12 = 0.8, npsex12 = 3.4)   # % N-IPV, past 12 months
TOL <- 0.05  # percentage points; published to 1 d.p.

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs <- 100 * tapply(d$resp, d$item, mean)[names(PUBLISHED)]
n   <- tapply(d$resp, d$item, length)[names(PUBLISHED)]

cat(sprintf("%-9s %5s %11s %10s %8s\n", "item", "n", "published_%", "observed_%", "diff"))
ok <- TRUE
for (i in names(PUBLISHED)) {
  df <- obs[[i]] - PUBLISHED[[i]]
  if (!is.finite(df) || abs(df) > TOL) ok <- FALSE
  cat(sprintf("%-9s %5d %11.1f %10.2f %8.2f\n", i, n[[i]], PUBLISHED[[i]], obs[[i]], df))
}

# The five published values are mutually distinct, so a permutation of the
# item->type mapping would be detected. Show the minimum published gap.
gaps <- as.matrix(dist(PUBLISHED))
diag(gaps) <- NA
cat(sprintf("\nsmallest gap between any two published values: %.1f pp (tolerance %.2f pp)\n",
            min(gaps, na.rm = TRUE), TOL))
cat(sprintf("distinguishing power: %s\n",
            if (min(gaps, na.rm = TRUE) > 2 * TOL) "every item separable from every other"
            else "NOT all items separable"))

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
