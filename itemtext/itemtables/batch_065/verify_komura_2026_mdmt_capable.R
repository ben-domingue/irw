# verify_komura_2026_mdmt_capable.R
#
# Claim under test: the four columns mdmt_capable_1..4 carry the four items
# listed under "Capable:" in the study's S2 File
# (10.1371/journal.pone.0340449.s002, "User Instructions for Frontend Interface
# (translated in English)", section 7 "Questionnaire Screens" -> "Trust
# Evaluation (MDMT)"), in the order that file numbers them:
#   1. Capable   2. Skilled   3. Competent   4. Meticulous
# which is also the canonical order of the MDMT Capable subscale
# ("capable, skilled, competent, meticulous", MDMT v1 2019-04-01, Ullman &
# Malle), and that resp is stored raw with 0 = "not at all", 7 = "very much so".
#
# Two falsifiable predictions, both computed from the LIVE IRW tables:
#
# A. SUBSCALE IDENTITY AND DIRECTION (route 3). The paper's Table 2 prints the
#    Capability mean (SD) per AI-strategy condition. If these four items are the
#    Capable block, are stored raw, and are keyed with the positive pole at
#    resp = 7, the per-condition mean of the four must reproduce it. (Published
#    Random n = 46 -- paper Table 1 -- so the six rows whose cov_aitype is
#    "unknown" belong to the Random condition; 40 + 6 = 46.)
#
# B. ITEM 4 IS "METICULOUS" (routes 7 + 8, marker item). Capable/Skilled/
#    Competent are near-synonyms for general competence; "Meticulous" is about
#    thoroughness and care, a conscientiousness facet. So mdmt_capable_4, and
#    no other item, must (i) have the LOWEST corrected item-total correlation
#    with the rest of the Capable block, and (ii) be the item most strongly
#    tied to the GQS Perceived Intelligence item that is itself about
#    conscientiousness rather than ability -- gqs_perceived_intelligence_4,
#    "Irresponsible <-> Responsible" -- once the shared competence factor is
#    partialled out (partial r controlling the other three Capable items).
#
# What this does NOT establish, stated up front: nothing here separates
# mdmt_capable_1, _2 and _3 ("Capable", "Skilled", "Competent") from one
# another. Their order rests on the S2 File's explicit within-block numbering
# agreeing with the canonical MDMT subscale order, not on any statistic. Hence
# PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "komura_2026_mdmt_capable"
PI    <- "komura_2026_gqs_perceived_intelligence"

# Paper Table 2, "Capability" row: Vertical, Horizontal, Random.
PUB_MEAN <- c(vertical = 4.81, horizontal = 4.00, random = 4.22)
PUB_SD   <- c(vertical = 1.26, horizontal = 1.52, random = 1.31)
PUB_N    <- c(vertical = 52,   horizontal = 50,   random = 46)   # paper Table 1
TOL      <- 0.02

d <- as.data.frame(irw::irw_fetch(TABLE))
d$cond <- ifelse(d$cov_aitype == "unknown", "random", d$cov_aitype)

items <- paste0("mdmt_capable_", 1:4)
ids   <- sort(unique(d$id))
M <- sapply(items, function(i) d$resp[match(ids, ifelse(d$item == i, d$id, NA))])
rownames(M) <- ids
cond <- d$cond[match(ids, d$id)]
sub  <- rowMeans(M)

cat("=== A. Capable subscale mean (SD) [n] by condition, live vs paper Table 2 ===\n")
cat(sprintf("%-11s %16s %18s %8s %8s\n", "condition", "published", "observed",
            "d(mean)", "d(sd)"))
okA <- TRUE
for (cn in names(PUB_MEAN)) {
    s <- sub[cond == cn]; om <- mean(s); os <- sd(s)
    cat(sprintf("%-11s %7.2f (%.2f) [%2d] %9.4f (%.4f) [%2d] %8.4f %8.4f\n",
                cn, PUB_MEAN[cn], PUB_SD[cn], PUB_N[cn], om, os, length(s),
                om - PUB_MEAN[cn], os - PUB_SD[cn]))
    if (abs(om - PUB_MEAN[cn]) > TOL || abs(os - PUB_SD[cn]) > TOL ||
        length(s) != PUB_N[cn]) okA <- FALSE
}
cat(sprintf("A: %s\n\n", if (okA) "PASS" else "FAIL"))

cat("=== B. Item 4 as the 'Meticulous' item ===\n")
mu  <- colMeans(M)
cit <- sapply(items, function(i)
    cor(M[, i], rowMeans(M[, setdiff(items, i), drop = FALSE])))

p <- as.data.frame(irw::irw_fetch(PI))
P4 <- p$resp[match(ids, ifelse(p$item == "gqs_perceived_intelligence_4", p$id, NA))]

pcor <- function(x, y, Z) cor(resid(lm(x ~ Z)), resid(lm(y ~ Z)))
pr <- sapply(seq_along(items), function(j)
    pcor(M[, j], P4, M[, setdiff(seq_along(items), j)]))
names(pr) <- items

cat(sprintf("%-16s %7s %7s %10s\n", "item", "mean", "cITC", "partial_r"))
for (i in items)
    cat(sprintf("%-16s %7.4f %7.4f %+10.3f\n", i, mu[i], cit[i], pr[i]))
cat("  (partial_r = r with gqs_perceived_intelligence_4 'Irresponsible <-> Responsible',\n",
    "   controlling for the other three Capable items)\n", sep = "")

i4  <- "mdmt_capable_4"; oth <- setdiff(items, i4)
b1 <- cit[i4] == min(cit) && min(cit[oth]) - cit[i4] > 0.10
b2 <- pr[i4]  == max(pr)  && pr[i4] - max(pr[oth]) > 0.20
cat(sprintf("\n  B(i)  item 4 lowest corrected item-total, by >0.10: %s\n", b1))
cat(sprintf("  B(ii) item 4 highest partial r with PI4, by >0.20:  %s\n", b2))
okB <- b1 && b2
cat(sprintf("B: %s\n\n", if (okB) "PASS" else "FAIL"))

cat("NOT ESTABLISHED: nothing here separates mdmt_capable_1, _2 and _3\n",
    "('Capable', 'Skilled', 'Competent') from one another; their order rests on\n",
    "the S2 File's within-block numbering matching the canonical MDMT subscale\n",
    "order. This route pins the subscale, the scoring direction, and item 4 only.\n",
    sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
