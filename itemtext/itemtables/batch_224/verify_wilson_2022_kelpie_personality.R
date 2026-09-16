# verify_wilson_2022_kelpie_personality.R
#
# Claim under test (Step 5b, route 1): each IRW item code carries the trait the
# S2 header names and the S1 form's grid row prints, and resp 1..5 runs
# 'very low' -> 'very high'.
#
# Falsifiable prediction: PLOS ONE 17(4):e0267266 Table 2 publishes n, Mean and
# SD for all 18 traits. If any two items' text were swapped, the live per-item
# triples would no longer line up with the published ones under the shipped
# item_text. If the 1-5 coding were reversed, every mean would read 6 - published.

suppressMessages(library(irw))

TABLE <- "wilson_2022_kelpie_personality"

# PLOS ONE 17(4): e0267266, Table 2 (doi:10.1371/journal.pone.0267266.t002).
# Keyed by the live item code the shipped item_text assigns to each printed trait.
PUB <- data.frame(
  item = c("Confidence_stock","Calmness_stock","Intelligence_stock","Trainability_stock",
           "Boldness_stock","Patience_stock","Timidness_stock","Persistence_stock",
           "Hyperactivity_stock","Initiative_stock","Excitability_stock","Obedience_stock",
           "Nervousness_stock","Impulsiveness_stock","Sociability","Friendliness",
           "Stamina","Overall_ability"),
  trait = c("Confidence","Calmness","Intelligence","Trainability","Boldness","Patience",
            "Timidness","Persistence","Hyperactivity","Initiative","Excitability","Obedience",
            "Nervousness","Impulsiveness","Sociability","Friendliness","Stamina",
            "Overall ability"),
  n    = c(228,228,228,227,227,227,228,228,228,226,227,228,226,225,225,223,224,184),
  mean = c(4.14,3.63,4.12,3.90,3.81,3.49,2.01,3.98,2.78,3.85,3.17,3.74,1.98,2.58,4.04,4.33,3.99,3.85),
  sd   = c(0.86,1.07,0.83,0.88,0.95,0.99,0.93,0.92,1.24,0.89,1.14,0.91,0.95,1.13,0.98,0.84,0.83,0.84),
  stringsAsFactors = FALSE)

TOL_MEAN <- 0.005; TOL_SD <- 0.005

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

obs_n    <- tapply(d$resp, d$item, function(v) sum(!is.na(v)))
obs_mean <- tapply(d$resp, d$item, function(v) mean(v, na.rm = TRUE))
obs_sd   <- tapply(d$resp, d$item, function(v) sd(v,   na.rm = TRUE))

cat(sprintf("%-20s %-16s %14s %14s\n", "item", "trait(shipped)", "published n/M/SD", "live n/M/SD"))
bad <- 0
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]
  ln <- obs_n[[it]]; lm <- obs_mean[[it]]; ls <- obs_sd[[it]]
  ok <- !is.na(lm) && ln == PUB$n[i] &&
        abs(lm - PUB$mean[i]) <= TOL_MEAN && abs(ls - PUB$sd[i]) <= TOL_SD
  if (!ok) bad <- bad + 1
  cat(sprintf("%-20s %-16s %5d/%4.2f/%4.2f %5d/%5.2f/%5.2f %s\n",
              it, PUB$trait[i], PUB$n[i], PUB$mean[i], PUB$sd[i], ln, lm, ls,
              if (ok) "" else "  <-- MISMATCH"))
}

# Uniqueness: the route only verifies the mapping if the published triples
# separate every item from every other.
key <- paste(PUB$n, sprintf("%.2f", PUB$mean), sprintf("%.2f", PUB$sd))
dups <- sum(duplicated(key))
cat(sprintf("\nitems matched within tolerance: %d/%d; non-unique published (n,M,SD) triples: %d\n",
            nrow(PUB) - bad, nrow(PUB), dups))

# Direction of the 1-5 coding (the option_text axis).
rev_gap <- max(abs((6 - obs_mean[PUB$item]) - PUB$mean))
fwd_gap <- max(abs(obs_mean[PUB$item] - PUB$mean))
cat(sprintf("max |live - published| as shipped: %.3f ; if resp were reversed: %.3f\n",
            fwd_gap, rev_gap))

cat("Note: this does NOT test the interior anchors low/average/high individually,\n",
    "nor which form section an item sat in (Stamina's with-stock placement rests on\n",
    "S1 File image7 and the paper's text, not on these numbers).\n", sep = "")

cat(if (bad == 0 && dups == 0 && fwd_gap < rev_gap) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
