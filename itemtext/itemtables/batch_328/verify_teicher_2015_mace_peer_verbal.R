# verify_teicher_2015_mace_peer_verbal.R -- copied from references/verify_template.R
#
# Claim: item codes peer_swore / Peer_hurtful / Peer_Rumors / Peer_Excluded / Peer_afraid
# (S9 File column names, used verbatim by data/teicher_2015_mace_items.py) carry the MACE-X
# wording of items 39 / 40 / 41 / 42 / 43 (= 52-item MACE items 26-30), and resp 1 = "Yes".
#
# Route 1: Teicher & Parigger (2015) PLOS ONE Table 6 (image, doi:10.1371/journal.pone.0117423.t006,
# n = 1050 per item) prints "% Yes" against each item's abbreviated wording:
# 59.3 / 65.0 / 48.3 / 46.9 / 21.9. The live table has the same n (1050 per item), so each
# live %resp==1 must round to its OWN published value (|diff| <= 0.05 + float slack), and be
# nearest to it. The smallest published gap (Rumors 48.3 vs Excluded 46.9) is 1.4 points,
# ~25x the rounding tolerance, so any permutation of the five fails.

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_peer_verbal"

PUBLISHED <- c(
    peer_swore    = 59.3,  # (26) Swore, called you names/insults more than few times per year
    Peer_hurtful  = 65.0,  # (27) Said hurtful things made you feel humiliated more than few times per year
    Peer_Rumors   = 48.3,  # (28) Said things behind you back, spread rumors
    Peer_Excluded = 46.9,  # (29) Excluded you from activities / groups
    Peer_afraid   = 21.9   # (30) Acted in way that made you afraid you might be hurt
)
TOL <- 0.06  # published values rounded to 0.1, identical n (1050): rounding only

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]
n_obs <- tapply(d$resp, d$item, length)
pct <- 100 * tapply(d$resp == 1, d$item, mean)

ok <- TRUE
cat(sprintf("%-15s %6s %10s %10s %8s  %s\n", "item", "n", "published", "observed", "diff", "nearest published"))
for (it in names(PUBLISHED)) {
    nearest <- names(PUBLISHED)[which.min(abs(PUBLISHED - pct[[it]]))]
    dev <- pct[[it]] - PUBLISHED[[it]]
    cat(sprintf("%-15s %6d %10.1f %10.2f %8.2f  %s\n", it, n_obs[[it]], PUBLISHED[[it]], pct[[it]], dev, nearest))
    if (abs(dev) > TOL || nearest != it) ok <- FALSE
}
cat(sprintf("\nsmallest gap between published values: %.1f points (tolerance %.2f)\n", min(dist(PUBLISHED)), TOL))
swap_dev <- c(abs(pct[["Peer_Rumors"]] - PUBLISHED[["Peer_Excluded"]]), abs(pct[["Peer_Excluded"]] - PUBLISHED[["Peer_Rumors"]]))
cat(sprintf("if Peer_Rumors/Peer_Excluded texts were swapped, deviations would be %.2f and %.2f\n", swap_dev[1], swap_dev[2]))
swap2 <- c(abs(pct[["peer_swore"]] - PUBLISHED[["Peer_hurtful"]]), abs(pct[["Peer_hurtful"]] - PUBLISHED[["peer_swore"]]))
cat(sprintf("if peer_swore/Peer_hurtful texts were swapped, deviations would be %.2f and %.2f\n", swap2[1], swap2[2]))
flip <- 100 - pct
cat(sprintf("if resp were flipped, %%Yes would read %s (published %s)\n",
            paste(sprintf("%.1f", flip[names(PUBLISHED)]), collapse = "/"), paste(PUBLISHED, collapse = "/")))
if (any(abs(flip[names(PUBLISHED)] - PUBLISHED) <= TOL)) ok <- FALSE
cat(sprintf("resp values present: %s\n", paste(sort(unique(d$resp)), collapse = ", ")))

cat("Every item's observed %Yes must round to its own Table 6 value and be nearest to it; the smallest\n",
    "published gap (1.4, Rumors vs Excluded) is ~25x the rounding tolerance, so this distinguishes all 5\n",
    "items and fixes resp=1 as 'Yes'. NOT established by this script: the online administration's\n",
    "rendering of the section prompt (only the formatted .docx is published).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
