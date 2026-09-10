# verify_pellerin2020_gq6.R -- batch_131, 2026-09-10
#
# WHAT IS BEING VERIFIED
# data/pellerin2020_covid_resources.py melts the literal column list
# [f"GQ_{i}" for i in range(1,7)] out of the study's OSF file
# data.PsyR_lockdown2020.csv, so the IRW item code IS the source column name
# (code-derivation pattern 1). But that CSV is a bare header row with NO variable
# or value labels, so the code is tied to nothing textual. The wording ships from
# the GQ-6's own published form (McCullough, Emmons & Tsang 2002, Appendix A):
#   1  "I have so much in life to be thankful for."
#   2  "If I had to list everything that I felt grateful for, it would be a very long list."
#   3  "When I look at the world, I don't see much to be grateful for."        (reverse)
#   4  "I am grateful to a wide variety of people."
#   5  "As I get older I find myself more able to appreciate the people, events, and
#      situations that have been part of my life history."
#   6  "Long amounts of time can go by before I feel grateful to something or someone."  (reverse)
# The mapping under test is therefore the number-to-number tie GQ_k <-> GQ-6 item k.
# It is an ORDER INFERENCE (mapping_basis = paper_order); nothing states it.
#
# CHECK (A) -- WHICH TWO COLUMNS ARE THE REVERSE-KEYED PAIR.  DECISIVE.
# The OSF file carries the authors' own derived scale score, Grat.world
# ("gratitude toward the world"). If GQ_k is GQ-6 item k, that score must be the
# 6-item mean with exactly items 3 and 6 reversed. All 2^6 = 64 possible reversal
# subsets are tried; only one can reproduce a derived column exactly, and the
# prediction is that it is {3,6}. Chance = 1/64.
#
# CHECK (B) -- WHICH OF THE PAIR IS ITEM 6, AND WHICH BLOCK IS ITEMS 1-2.
# Run on the LIVE IRW table. Item 6 is the GQ-6's documented weak item: its
# loading is the lowest in every published validation (Chile adults .079,
# PMC4815209 Table 1; Germany 0.29, PMC7586006; Brazil .52), and it is the item
# removed to form the GQ-5. Items 1 and 2 are the near-synonymous top-loading
# pair (.838 / .812 in the Chilean adult EFA). Prediction on the keyed live data:
# the weakest-loading item is the one at position 6, and the two strongest are the
# ones at positions 1 and 2.
#
# WHAT THIS DOES NOT ESTABLISH
# It does not separate GQ_1 from GQ_2, nor GQ_4 from GQ_5. Both checks act on
# blocks: (A) fixes {3,6} as a set and (B) fixes item 6 within it and {1,2} as a
# set. No published per-item statistic orders items 1 vs 2 or 4 vs 5 reproducibly
# (the Chilean EFA puts item 5 above item 4, the live data puts them the other
# way round), so those two within-block orderings rest on the columns being
# numbered in the instrument's own order -- which every checkable point is
# consistent with and none contradicts, but which is not itself tested here.
# Hence the recorded status is PARTIAL, not VERIFIED.

options(digits = 12)
suppressMessages(library(irw))

TABLE <- "pellerin2020_gq6"
G     <- paste0("GQ_", 1:6)
okA <- NA; okB <- NA

# ---- (A) reverse-key subset, against the study's own OSF deposit -------------
cat("(A) which reversal subset reproduces the deposit's own Grat.world column?\n")
resA <- try({
    raw <- read.csv("https://osf.io/download/dc6me/", stringsAsFactors = FALSE)
    ok  <- complete.cases(raw[, G]) & !is.na(raw$Grat.world) & raw$Wave == 0
    gw  <- raw$Grat.world[ok]
    g   <- as.matrix(raw[ok, G])
    cat(sprintf("    wave-0 respondents with a complete GQ_1..GQ_6 triple-check: n = %d\n", sum(ok)))
    dev <- c()
    for (k in 0:6) {
        combos <- if (k == 0) list(integer(0)) else combn(6, k, simplify = FALSE)
        for (cmb in combos) {
            m <- g
            for (i in cmb) m[, i] <- 7 - m[, i]
            lbl <- if (length(cmb)) paste(cmb, collapse = ",") else "(none)"
            dev[lbl] <- max(abs(gw - rowMeans(m)))
        }
    }
    dev <- sort(dev)
    cat("    max |Grat.world - mean(items, named subset reversed)| , 5 best of 64:\n")
    for (i in 1:5) cat(sprintf("      reverse {%-9s}  %.4g\n", names(dev)[i], dev[i]))
    okA <<- (names(dev)[1] == "3,6" && dev[1] < 1e-9 && dev[2] > 1e-6)
    cat(sprintf("    -> unique exact subset is {%s}; predicted {3,6}: %s\n",
                names(dev)[1], if (isTRUE(okA)) "HOLDS" else "VIOLATED"))
    invisible(NULL)
}, silent = TRUE)
if (inherits(resA, "try-error"))
    cat("    (OSF deposit unreachable -- check (A) skipped)\n")

# ---- (B) loading ordering, against the LIVE IRW table -----------------------
cat("\n(B) keyed item-rest correlations and 1st-PC loadings, LIVE IRW data\n")
cat("    published GQ-6 loadings, Chilean adult EFA (PMC4815209 Tab.1):\n")
cat("      i1 .838  i2 .812  i3 .303  i4 .701  i5 .749  i6 .079   <- i6 lowest, {i1,i2} highest\n")
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "wave", "item", "resp")],
             idvar = c("id", "wave"), timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
m <- w[, G]
m <- m[complete.cases(m), ]
cat(sprintf("    live person-waves with all six items: n = %d\n", nrow(m)))
k <- m
k$GQ_3 <- 8 - k$GQ_3
k$GQ_6 <- 8 - k$GQ_6
tot <- rowSums(k)
irest <- sapply(G, function(g) cor(k[[g]], tot - k[[g]]))
ld <- svd(scale(k))$v[, 1]
if (sum(ld) < 0) ld <- -ld
ld <- ld / sqrt(sum(ld^2)) * 1  # direction only; report the raw item-rest too
load <- sapply(G, function(g) cor(k[[g]], as.matrix(scale(k)) %*% ld))
cat(sprintf("\n    %-6s %8s %10s %12s\n", "item", "mean", "item-rest", "1st-PC r"))
for (g in G) cat(sprintf("    %-6s %8.3f %10.3f %12.3f\n", g, mean(m[[g]]), irest[g], load[g]))

# sign pattern: only the two reverse items may correlate negatively with the rest
R <- cor(m)
neg <- names(which(sapply(G, function(g) mean(R[g, setdiff(G, g)]) < 0)))
cat(sprintf("\n    items with a negative mean correlation to the others: %s\n",
            paste(neg, collapse = ", ")))
weakest  <- names(which.min(load))
strong2  <- names(sort(load, decreasing = TRUE))[1:2]
cat(sprintf("    weakest-loading item: %s (predicted GQ_6)\n", weakest))
cat(sprintf("    two strongest-loading items: %s (predicted GQ_1, GQ_2)\n",
            paste(sort(strong2), collapse = ", ")))
okB <- identical(sort(neg), c("GQ_3", "GQ_6")) &&
       weakest == "GQ_6" &&
       identical(sort(strong2), c("GQ_1", "GQ_2"))

cat("\nNot established by either check: GQ_1 vs GQ_2, and GQ_4 vs GQ_5.\n")
cat("Both checks act on blocks; the within-block order rests on the deposit's\n")
cat("columns being numbered in the instrument's own order. Status = PARTIAL.\n\n")

pass <- isTRUE(okA) && isTRUE(okB)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
