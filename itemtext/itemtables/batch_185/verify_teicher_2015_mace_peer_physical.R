# verify_teicher_2015_mace_peer_physical.R -- copied from references/verify_template.R
#
# Claim: item codes Peer_threat_money / Peer_forced / Peer_pushed / Peer_hit / Peer_hit_med
# (S9 File column names, used verbatim by data/teicher_2015_mace_items.py) carry the MACE-X
# wording of items 44 / 45 / 46 / 47 / 48 (= 52-item MACE items 31-35), and resp 1 = "Yes".
#
# Route 1: Teicher & Parigger (2015) PLOS ONE Table 7 (image, doi:10.1371/journal.pone.0117423.t007,
# "Rasch analysis of peer physical bullying", n = 1050 per item) prints "% Yes" against each item's
# wording: 6.3 / 11.0 / 32.7 / 11.5 / 3.3. The live table has the same n (1050 per item), so each
# live %resp==1 must round to its OWN published value (|diff| <= 0.05 + float slack).
# Forced (11.0) and hit (11.5) are only 0.5 points apart, which is 10x the rounding tolerance, so a
# swap of those two would miss by ~0.5 and fail. Route 8 (semantic nesting) is printed as an
# independent tie-break for that pair: the severe "medical attention" item should nest inside "hit
# ... left marks", and "hit" inside "pushed ... kicked", far more than inside "forced ... to do things".

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_peer_physical"

PUBLISHED <- c(
    Peer_threat_money = 6.3,   # (31) Threatened you in order to take money or possessions
    Peer_forced       = 11.0,  # (32) Forced you to do things you did not want to
    Peer_pushed       = 32.7,  # (33) Intentionally pushed, shoved, punched, kicked you etc.
    Peer_hit          = 11.5,  # (34) Hit you so hard it left marks for more than a few minutes
    Peer_hit_med      = 3.3    # (35) Hit or harmed you so severely as to need medical attention
)
TOL <- 0.06  # published values are rounded to 0.1 and n is identical (1050), so rounding only

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]
n_obs <- tapply(d$resp, d$item, length)
pct <- 100 * tapply(d$resp == 1, d$item, mean)

ok <- TRUE
cat(sprintf("%-18s %6s %10s %10s %8s  %s\n", "item", "n", "published", "observed", "diff", "nearest published"))
for (it in names(PUBLISHED)) {
    nearest <- names(PUBLISHED)[which.min(abs(PUBLISHED - pct[[it]]))]
    dev <- pct[[it]] - PUBLISHED[[it]]
    cat(sprintf("%-18s %6d %10.1f %10.2f %8.2f  %s\n", it, n_obs[[it]], PUBLISHED[[it]], pct[[it]], dev, nearest))
    if (abs(dev) > TOL || nearest != it) ok <- FALSE
}
cat(sprintf("\nsmallest gap between published values: %.1f points (tolerance %.2f)\n", min(dist(PUBLISHED)), TOL))
swap_dev <- c(abs(pct[["Peer_forced"]] - PUBLISHED[["Peer_hit"]]), abs(pct[["Peer_hit"]] - PUBLISHED[["Peer_forced"]]))
cat(sprintf("if Peer_forced/Peer_hit texts were swapped, deviations would be %.2f and %.2f\n", swap_dev[1], swap_dev[2]))
cat(sprintf("if resp were flipped, Peer_threat_money would read %.1f %% Yes\n", 100 - pct[["Peer_threat_money"]]))

# Route 8 tie-break: conditional endorsement (nesting) from the live person-level data
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cond <- function(a, b) { m <- which(w[[a]] == 1 & !is.na(w[[b]])); c(n = length(m), k = sum(w[[b]][m] == 1)) }
show <- function(a, b) { x <- cond(a, b); cat(sprintf("  P(%s=1 | %s=1) = %d/%d = %.2f\n", b, a, x[["k"]], x[["n"]], x[["k"]] / x[["n"]])); x[["k"]] / x[["n"]] }
cat("\nnesting (route 8):\n")
p_hit_given_med    <- show("Peer_hit_med", "Peer_hit")
p_forced_given_med <- show("Peer_hit_med", "Peer_forced")
p_push_given_hit   <- show("Peer_hit", "Peer_pushed")
p_push_given_forced<- show("Peer_forced", "Peer_pushed")
if (!(p_hit_given_med > p_forced_given_med && p_push_given_hit > p_push_given_forced)) ok <- FALSE

cat(sprintf("resp values present: %s\n", paste(sort(unique(d$resp)), collapse = ", ")))
cat("Every item's observed %Yes must round to its own Table 7 value and be nearest to it; the smallest\n",
    "published gap (0.5, forced vs hit) is ~10x the rounding tolerance, and the nesting pattern breaks that\n",
    "tie independently. Together these distinguish all 5 items and fix resp=1 as 'Yes'. NOT established:\n",
    "the online administration's rendering of the section prompt (only the formatted .docx is published).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
