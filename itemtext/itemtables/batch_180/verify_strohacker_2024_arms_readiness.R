# verify_strohacker_2024_arms_readiness.R -- Step 5b mapping check (batch_180)
#
# Claim: each ARMS_* code carries the paper wording its name abbreviates
# (ARMS_PhysFresh = "I am physically fresh", ARMS_CantFocus = "I cannot focus today", ...).
# The codes are the S1 Data workbook's own column names (data/strohacker_2024_situational.py
# melts them unchanged), and each names its own content, so a permutation would be
# self-evident: that exemption is what distinguishes every item from every other.
#
# This script tests the two data predictions the shipped wording makes:
#  (A) POLARITY (route 6). The data are raw (no reverse-scoring in the processing script),
#      so the four fatigue-worded items (PhysTired, PhysSpent, MentalTired, CantFocus) must
#      correlate positively with each other and negatively with all six readiness-worded items.
#  (B) PAIR STRUCTURE (route 5, within-person). The workbook's descriptor row and the paper
#      assign the items to five two-item factors. Using person-mean-centred responses
#      (22 people, 5-50 sessions each), each item's same-sign partner with the highest
#      correlation should be its designated pair partner. Threat-challenge readiness
#      (HandleFeels/UnderControl) is expected to be weak: those items overlap with cognitive
#      readiness, so a near-tie there is reported, not failed on.
#
# What this does NOT establish: statistics alone cannot tell the two items within a pair
# apart (e.g. PhysSpent vs PhysTired), and do not separate the threat-challenge pair from
# ThinkClear. That identity rests on the self-describing codes.

suppressMessages(library(irw))
TABLE <- "strohacker_2024_arms_readiness"

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "wave", "item", "resp")]
w <- reshape(d, idvar = c("id", "wave"), timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.ARMS_", "", names(w))
X <- w[, setdiff(names(w), c("id", "wave"))]
cat(sprintf("live: %d rows, %d persons, %d session reports\n", nrow(d), length(unique(d$id)), nrow(w)))

fatigue   <- c("PhysTired", "PhysSpent", "MentalTired", "CantFocus")
readiness <- c("PhysFresh", "FeelFIt", "FocusWell", "ThinkClear", "HandleFeels", "UnderControl")

# (A) polarity, pooled correlations
R <- cor(X, use = "pairwise.complete.obs")
within_f <- R[fatigue, fatigue][upper.tri(R[fatigue, fatigue])]
within_r <- R[readiness, readiness][upper.tri(R[readiness, readiness])]
cross    <- R[fatigue, readiness]
cat(sprintf("\n(A) pooled r: fatigue-fatigue %.2f..%.2f; readiness-readiness %.2f..%.2f; fatigue-readiness %.2f..%.2f\n",
            min(within_f), max(within_f), min(within_r), max(within_r), min(cross), max(cross)))
okA <- all(within_f > 0) && all(within_r > 0) && all(cross < 0)
cat("(A) polarity pattern:", if (okA) "holds" else "BROKEN", "\n")

# (B) pair structure, within-person centred
Xc <- as.data.frame(lapply(X, function(v) v - ave(v, w$id, FUN = function(z) mean(z, na.rm = TRUE))))
Rc <- cor(Xc, use = "pairwise.complete.obs")
pairs <- list(c("PhysFresh", "FeelFIt"), c("PhysSpent", "PhysTired"), c("FocusWell", "ThinkClear"),
              c("MentalTired", "CantFocus"), c("HandleFeels", "UnderControl"))
partner <- setNames(character(0), character(0))
for (p in pairs) { partner[p[1]] <- p[2]; partner[p[2]] <- p[1] }
cat("\n(B) within-person: item | designated partner r | best other same-polarity item r\n")
hits <- 0; near <- 0
for (it in names(partner)) {
    cls <- if (it %in% fatigue) fatigue else readiness
    others <- setdiff(cls, c(it, partner[[it]]))
    r_own <- Rc[it, partner[[it]]]
    best <- others[which.max(Rc[it, others])]
    r_best <- Rc[it, best]
    tag <- if (r_own > r_best) { hits <- hits + 1; "ok" } else if (r_best - r_own <= 0.05) { near <- near + 1; "near-tie" } else "MISS"
    cat(sprintf("  %-12s %-12s %.2f | %-12s %.2f  %s\n", it, partner[[it]], r_own, best, r_best, tag))
}
cat(sprintf("(B) %d/10 items' strongest same-polarity partner is the designated one; %d near-ties (<=0.05)\n", hits, near))
okB <- (hits + near) == 10 && all(c("PhysFresh", "FeelFIt", "PhysSpent", "PhysTired", "FocusWell", "ThinkClear") %in%
                                   names(partner)[sapply(names(partner), function(it) {
                                       cls <- if (it %in% fatigue) fatigue else readiness
                                       others <- setdiff(cls, c(it, partner[[it]]))
                                       Rc[it, partner[[it]]] > max(Rc[it, others]) })])

cat("\nNote: neither route separates the two items within a pair, nor the threat-challenge pair from\n",
    "ThinkClear; item identity rests on the self-describing column names.\n", sep = "")
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
