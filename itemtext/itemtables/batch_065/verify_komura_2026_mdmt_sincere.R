# verify_komura_2026_mdmt_sincere.R
#
# Claim under test: the four columns mdmt_sincere_1..4 carry the four trust
# words listed under "Sincere:" in the study's S2 File
# (10.1371/journal.pone.0340449.s002, "User Instructions for Frontend Interface
# (translated in English)", section 7 "Questionnaire Screens", "Trust
# Evaluation (MDMT)"), in the order that file numbers them:
#   1. Sincere
#   2. Genuine/authentic
#   3. Straightforward
#   4. Real/trustworthy
#
# Two falsifiable predictions, both computed from the LIVE IRW table:
#
# A. SUBSCALE IDENTITY, MEMBERSHIP AND DIRECTION (route 3). The paper's Table 2
#    prints mean (SD) per AI-strategy condition for each of the four MDMT trust
#    dimensions. If these four items are the SINCERITY block, are stored raw
#    (no reverse coding, high resp = more trust), and are exactly the four items
#    the paper averaged, their per-condition mean and SD must reproduce the
#    Sincerity row -- and must NOT reproduce the Reliability, Capability or
#    Ethicality rows, which is what distinguishes this block from the three
#    sibling blocks in the same workbook.
#    (Published Random n = 46 -- paper Table 1 -- so the six rows whose
#    cov_aitype is "unknown" belong to the Random condition; 40 + 6 = 46.)
#
# B. LIVE ITEM CODE == S3 WORKBOOK COLUMN (route 9 in count form). The four
#    columns of the S3 File (.s003 XLSX, the deposit the IRW table was built
#    from) have four DISTINCT resp-frequency vectors, hard-coded below from that
#    file. If data/komura_2026_godspeed.py's melt carried each column through
#    under its own name, each live item's frequency vector must match its
#    namesake column cell for cell. A permutation of the four codes at any point
#    between workbook and warehouse would break this immediately, because no two
#    of the four vectors are equal.
#
# What this does NOT establish, stated up front: A pins the block, its
# membership and its scoring direction, and B pins live code -> workbook column,
# but NEITHER separates the four synonyms from one another. Their order rests
# solely on the S2 File's own within-block numbering (1..4) matching the
# workbook's own column suffixes (_1.._4). The four words are near-synonyms
# rated by the same 148 people, so no statistical route can distinguish them:
# the paper publishes no per-item statistics and the items share one 0-7 scale.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "komura_2026_mdmt_sincere"
items <- paste0("mdmt_sincere_", 1:4)

# Paper Table 2 (t002), all four MDMT rows: Vertical, Horizontal, Random.
PUB <- rbind(
    Reliability = c(4.76, 4.08, 4.09),
    Capability  = c(4.81, 4.00, 4.22),
    Ethicality  = c(4.71, 4.21, 4.11),
    Sincerity   = c(4.92, 4.32, 4.31))
colnames(PUB) <- c("vertical", "horizontal", "random")
PUB_SD <- c(vertical = 1.08, horizontal = 1.27, random = 1.05)   # Sincerity row
PUB_N  <- c(vertical = 52,   horizontal = 50,   random = 46)     # paper Table 1
TOL_MEAN <- 0.02
TOL_SD   <- 0.02

# S3 File (.s003) column frequency vectors, counts of resp 1..7, read from the
# workbook with pandas. These are properties of the deposited file and fixed.
S3 <- rbind(
    mdmt_sincere_1 = c(0, 6, 22, 52, 26, 32, 10),
    mdmt_sincere_2 = c(1, 9, 22, 53, 36, 22,  5),
    mdmt_sincere_3 = c(1, 5, 13, 49, 34, 36, 10),
    mdmt_sincere_4 = c(3, 9, 20, 47, 34, 27,  8))
colnames(S3) <- 1:7

d <- as.data.frame(irw::irw_fetch(TABLE))
d$cond <- ifelse(d$cov_aitype == "unknown", "random", d$cov_aitype)
ids  <- sort(unique(d$id))
M    <- sapply(items, function(i) d$resp[match(ids, ifelse(d$item == i, d$id, NA))])
rownames(M) <- ids
cond <- d$cond[match(ids, d$id)]
subscale <- rowMeans(M)

cat("=== A. Subscale mean (SD) [n] by condition, live vs paper Table 2 ===\n")
cat(sprintf("%-11s %17s %19s %8s %8s\n",
            "condition", "published Sinc.", "observed", "d(mean)", "d(sd)"))
okA <- TRUE
for (cn in colnames(PUB)) {
    s  <- subscale[cond == cn]
    om <- mean(s); os <- sd(s)
    cat(sprintf("%-11s %8.2f (%.2f) [%2d] %8.3f (%.3f) [%2d] %8.3f %8.3f\n",
                cn, PUB["Sincerity", cn], PUB_SD[cn], PUB_N[cn],
                om, os, length(s), om - PUB["Sincerity", cn], os - PUB_SD[cn]))
    if (abs(om - PUB["Sincerity", cn]) > TOL_MEAN ||
        abs(os - PUB_SD[cn])           > TOL_SD   ||
        length(s) != PUB_N[cn]) okA <- FALSE
}
obs_prof <- sapply(colnames(PUB), function(cn) mean(subscale[cond == cn]))
cat("\n  distance of the observed condition profile from each published row:\n")
for (r in rownames(PUB))
    cat(sprintf("    %-12s max|diff| = %.3f\n", r, max(abs(obs_prof - PUB[r, ]))))
best <- rownames(PUB)[which.min(apply(PUB, 1, function(p) max(abs(obs_prof - p))))]
cat(sprintf("  closest published row: %s\n", best))
okA <- okA && identical(best, "Sincerity")
cat(sprintf("A: %s\n\n", if (okA) "PASS" else "FAIL"))

cat("=== B. Per-item resp frequencies, live vs S3 workbook column ===\n")
LIVE <- t(sapply(items, function(i)
    as.integer(table(factor(d$resp[d$item == i], levels = 1:7)))))
colnames(LIVE) <- 1:7
cat(sprintf("%-16s %-26s %-26s %s\n", "item", "S3 column (1..7)", "live (1..7)", "match"))
okB <- TRUE
for (i in items) {
    m <- identical(as.integer(S3[i, ]), as.integer(LIVE[i, ]))
    okB <- okB && m
    cat(sprintf("%-16s %-26s %-26s %s\n", i,
                paste(S3[i, ], collapse = " "), paste(LIVE[i, ], collapse = " "),
                if (m) "yes" else "NO"))
}
np <- sum(sapply(items, function(a) sapply(items, function(b)
        !identical(as.integer(S3[a, ]), as.integer(S3[b, ]))))) / 2
cat(sprintf("  distinct S3 vectors: all %d of the %d unordered pairs differ\n",
            np, choose(length(items), 2)))
okB <- okB && np == choose(length(items), 2)
cat(sprintf("B: %s\n\n", if (okB) "PASS" else "FAIL"))

cat("NOT ESTABLISHED: nothing above separates the four near-synonymous words\n",
    "(Sincere / Genuine-authentic / Straightforward / Real-trustworthy) from one\n",
    "another; that order comes from the S2 File's own numbering. PARTIAL.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
