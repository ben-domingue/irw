# verify_jian-wen-low-sepsis-and-trauma-resuscitation-2024.R
#
# Claim: scenarioS_itemN = item No. N of "Case S" in the deposit's Supplement 1
# (Case 1 = severe community-acquired pneumonia / SEPSIS; Case 2 = major trauma),
# and Supplement 1's Bloom-domain flags say which items are "only cognitive".
#
# Falsifiable prediction: Low et al. 2024 (JEEHP 21:33, PMC11647267) Table 3 reports,
# per scenario and per arm, mean±SD of checklist points summed over BOTH raters for
# (a) all 31 items, (b) the "only cognitive" items, (c) the "not only cognitive" items,
# with maxima 62/42/20 (sepsis) and 62/40/22 (trauma). If scenario 1/2 were swapped,
# or if any item were assigned to the wrong domain set (i.e. the item numbering
# did not match the supplement's), the subscale sums would miss.
#
# Does NOT establish order WITHIN a domain set (e.g. that sepsis item 5 is not sepsis
# item 6, both only-cognitive). That tie rests on the shared item numbering 1..31.

suppressMessages(library(irw))
TABLE <- "jian-wen-low-sepsis-and-trauma-resuscitation-2024"

# Supplement 1: items with Psychomotor or Affective flagged (= "not only cognitive")
NOC <- list(scenario1 = c(2, 3, 4, 8, 9, 21, 23, 25, 28, 31),
            scenario2 = c(1, 6, 7, 9, 17, 18, 19, 20, 28, 29, 30))
# Published Table 3: mean, SD for VPS then IPS
PUB <- rbind(
  c("scenario1", "overall",      38.0, 4.4, 36.0, 6.1),
  c("scenario1", "only_cog",     27.8, 3.6, 26.7, 4.5),
  c("scenario1", "not_only_cog", 10.2, 2.0,  9.3, 2.1),
  c("scenario2", "overall",      36.2, 6.0, 37.2, 4.2),
  c("scenario2", "only_cog",     23.1, 4.0, 23.5, 3.6),
  c("scenario2", "not_only_cog", 13.1, 3.2, 13.7, 2.7))

d <- irw::irw_fetch(TABLE)
d$scen <- sub("_item.*", "", d$item)
d$num  <- as.integer(sub(".*_item", "", d$item))
# cov_intervention: 1 = VPS (n=19), 2 = IPS (n=21) -- paper's arm sizes
cat("arm sizes (ids):", tapply(d$id, d$cov_intervention, function(x) length(unique(x))), "\n\n")

cat(sprintf("%-10s %-13s %-4s %8s %8s %8s %8s\n", "scenario", "subset", "arm", "pubM", "obsM", "pubSD", "obsSD"))
worst_m <- 0; worst_sd <- 0
for (i in seq_len(nrow(PUB))) {
  s <- PUB[i, 1]; sub <- PUB[i, 2]
  x <- d[d$scen == s, ]
  noc <- x$num %in% NOC[[s]]
  if (sub == "only_cog") x <- x[!noc, ]
  if (sub == "not_only_cog") x <- x[noc, ]
  for (a in 1:2) {
    tot <- tapply(x$resp[x$cov_intervention == a], x$id[x$cov_intervention == a], sum)
    pm <- as.numeric(PUB[i, 1 + 2 * a]); ps <- as.numeric(PUB[i, 2 + 2 * a])
    cat(sprintf("%-10s %-13s %-4s %8.1f %8.2f %8.1f %8.2f\n", s, sub, c("VPS", "IPS")[a],
                pm, mean(tot), ps, sd(tot)))
    worst_m <- max(worst_m, abs(mean(tot) - pm))
    # Overall-row SDs are invariant to the item mapping (a 31-item sum does not care
    # which item is which), so only subscale SDs are gated. Published trauma/VPS
    # overall SD 6.0 vs 5.69 observed is a paper-side discrepancy: the deposit's own
    # 'Outcome simulation scenario 2 raw total score' column also gives 5.69.
    if (sub != "overall") worst_sd <- max(worst_sd, abs(sd(tot) - ps))
  }
}
# Swap test: the sepsis/trauma overall arm means are what pin scenario<->case.
cat(sprintf("\nlargest |mean diff| %.3f, largest subscale |SD diff| %.3f (tolerance 0.06 = rounding)\n", worst_m, worst_sd))
cat("Not established: order within a domain set; relies on item numbering 1..31 shared by data headers and Supplement 1.\n")
cat(if (worst_m <= 0.06 && worst_sd <= 0.06) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
