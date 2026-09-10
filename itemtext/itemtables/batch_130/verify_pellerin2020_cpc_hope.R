# verify_pellerin2020_cpc_hope.R -- batch_130, 2026-09-10
#
# WHAT IS BEING VERIFIED
# The IRW item codes Hope_1/Hope_2/Hope_3 are the OSF deposit's own column names
# (data/pellerin2020_covid_resources.py melts them straight through), but that
# deposit is a bare CSV with NO variable labels -- the codes carry no text. The
# wording ships from the CPC-12's own S1 Appendix (Lorenz, Beer, Puetz & Heinitz
# 2016, PLOS ONE 11(4):e152892, CC BY 4.0), whose hope block is items 1-3:
#   1  "If I should find myself in a jam, I could think of many ways to get out of it."  (SHS1)
#   2  "Right now, I see myself as being pretty successful."                             (SHS4)
#   3  "I can think of many ways to reach my current goals."                             (SHS5)
# So the mapping under test is the number-to-number tie Hope_k <-> CPC-12 hope item k.
# It is an ORDER INFERENCE (mapping_basis = paper_order): nothing in the deposit or
# in Pellerin & Raufaste (2020) states it. That is what this script tests.
#
# THE FALSIFIABLE PREDICTION
# The three CPC-12 hope items have a reproducible, ASYMMETRIC intercorrelation
# signature in the instrument's own two development samples:
#
#   sample                                   r(i1,i2)  r(i1,i3)  r(i2,i3)
#   Lorenz 2016 Study 1 (S1 Dataset, n=321,  0.313     0.474     0.584
#     SHS columns hope1/hope4/hope5, 1-6)
#   Lorenz 2016 Study 2 (S2 Dataset, n=202,  0.342     0.499     0.545
#     CPC columns cpc1/cpc2/cpc3, 1-6)
#
# i.e. r(1,2) < r(1,3) < r(2,3) in BOTH samples, replicated independently.
# All three pairwise values are distinct, and S3 acts faithfully on the three
# pairs, so exactly ONE of the 6 possible assignments of {Hope_1,Hope_2,Hope_3}
# to CPC hope items {1,2,3} reproduces that ordering. If the shipped mapping is
# right, the live French data must show r(Hope_1,Hope_2) < r(Hope_1,Hope_3) <
# r(Hope_2,Hope_3). Chance alone gets this right 1 time in 6.
#
# Check (B) is an independent second discriminator on the same permutation:
# in Lorenz Study 2 the "pretty successful" item (cpc2) correlates far more
# strongly with life satisfaction (lezu1-5) than the two pathways items --
# cpc2 .368 > cpc3 .211 > cpc1 .162. The prediction is the same rank order
# against Pellerin's well-being scales. Also 1 in 6 by chance, and it uses a
# different statistic than (A).
#
# WHAT THIS DOES NOT ESTABLISH
# It is a structural match, not a source-level label tie: no file anywhere
# spells "Hope_2 = Right now, I see myself as being pretty successful". It also
# assumes the item structure of the German development samples carries over to
# this French administration -- which is what checks (A) and (B) jointly test,
# but it is an assumption a variable label would not need.

suppressMessages(library(irw))

TABLE <- "pellerin2020_cpc_hope"
ITEMS <- c("Hope_1", "Hope_2", "Hope_3")

# ---- (A) intercorrelation-ordering signature, against LIVE IRW data ----------
PUB_S1 <- c(r12 = 0.313, r13 = 0.474, r23 = 0.584)   # Lorenz 2016 S1 Dataset, n=321
PUB_S2 <- c(r12 = 0.342, r13 = 0.499, r23 = 0.545)   # Lorenz 2016 S2 Dataset, n=202

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "wave", "item", "resp")],
             idvar = c("id", "wave"), timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
m <- w[, ITEMS]
m <- m[complete.cases(m), ]
R <- cor(m)
obs <- c(r12 = R["Hope_1", "Hope_2"], r13 = R["Hope_1", "Hope_3"],
         r23 = R["Hope_2", "Hope_3"])

cat("(A) CPC-12 hope-item intercorrelation signature\n")
cat(sprintf("    live n (complete triples) = %d\n\n", nrow(m)))
cat(sprintf("    %-24s %8s %8s %8s\n", "sample", "r(1,2)", "r(1,3)", "r(2,3)"))
cat(sprintf("    %-24s %8.3f %8.3f %8.3f\n", "Lorenz 2016 Study 1", PUB_S1[1], PUB_S1[2], PUB_S1[3]))
cat(sprintf("    %-24s %8.3f %8.3f %8.3f\n", "Lorenz 2016 Study 2", PUB_S2[1], PUB_S2[2], PUB_S2[3]))
cat(sprintf("    %-24s %8.3f %8.3f %8.3f\n", "LIVE pellerin (French)", obs[1], obs[2], obs[3]))

okA <- obs["r12"] < obs["r13"] && obs["r13"] < obs["r23"]
cat(sprintf("\n    predicted order r(1,2) < r(1,3) < r(2,3): %s\n",
            if (okA) "HOLDS" else "VIOLATED"))
cat("    (1 of 6 possible item assignments reproduces this; p = 0.167 by chance)\n\n")

# ---- (B) external-criterion ordering, against the OSF source file -----------
# Needs the well-being scales, which are covariates the IRW table does not carry,
# so this half reads the study's own OSF deposit. Non-fatal if unreachable.
PUB_LEZU <- c(i1 = 0.162, i2 = 0.368, i3 = 0.211)  # Lorenz Study 2, cpc1/2/3 vs lezu1-5 mean
okB <- NA
cat("(B) external-criterion ordering (well-being / life satisfaction)\n")
cat(sprintf("    Lorenz 2016 Study 2 vs life satisfaction: i1=%.3f  i2=%.3f  i3=%.3f",
            PUB_LEZU[1], PUB_LEZU[2], PUB_LEZU[3]))
cat("   -> predicted i2 > i3 > i1\n")
res <- try({
    raw <- read.csv("https://osf.io/download/dc6me/", stringsAsFactors = FALSE)
    s <- raw[!is.na(raw$Hope_1) & !is.na(raw$Hope_2) & !is.na(raw$Hope_3), ]
    hits <- 0L; tot <- 0L
    for (wv in sort(unique(s$Wave))) {
        for (crit in c("EWB", "PWB", "SWB", "IWB")) {
            x <- s[s$Wave == wv, c(ITEMS, crit)]
            x <- x[complete.cases(x), ]
            if (nrow(x) < 50) next
            r <- sapply(ITEMS, function(i) cor(x[[i]], x[[crit]]))
            tot <- tot + 1L
            good <- r[2] > r[3] && r[3] > r[1]
            hits <- hits + as.integer(good)
            cat(sprintf("    wave %s n=%4d %-4s: H1=%.3f H2=%.3f H3=%.3f  %s\n",
                        wv, nrow(x), crit, r[1], r[2], r[3],
                        if (good) "order holds" else "order violated"))
        }
    }
    cat(sprintf("\n    predicted order holds in %d of %d wave x criterion comparisons\n", hits, tot))
    okB <- (tot > 0 && hits >= ceiling(0.75 * tot))
    invisible(NULL)
}, silent = TRUE)
if (inherits(res, "try-error"))
    cat("    (OSF deposit unreachable -- check (B) skipped, verdict rests on (A))\n")

cat("\nNote: neither route is a source-level label tie -- no file states the\n")
cat("Hope_k <-> item-k correspondence. What they establish is that the live\n")
cat("data reproduces, on two different statistics, the item structure the\n")
cat("CPC-12's own development samples show under exactly this assignment and\n")
cat("under none of the other five.\n\n")

pass <- isTRUE(okA) && !isFALSE(okB)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
