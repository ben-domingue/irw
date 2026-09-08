# verify_komura_2026_gqs_likeability.R
#
# Claim under test: the five columns gqs_likeability_1..5 carry the five
# semantic-differential anchor pairs listed under "Likeability:" in the study's
# S2 File (10.1371/journal.pone.0340449.s002, "User Instructions for Frontend
# Interface (translated in English)", section 7 "Questionnaire Screens"), in the
# order that file numbers them:
#   1. Unpleasant <-> Pleasant
#   2. Unkind     <-> Kind
#   3. Unpleasant <-> Pleasant
#   4. Awful      <-> Nice
#   5. Scary      <-> Not scary
#
# Two falsifiable predictions, both computed from the LIVE IRW tables:
#
# A. SUBSCALE IDENTITY AND DIRECTION (route 3). The paper's Table 3 prints the
#    Likeability mean (SD) per AI-strategy condition. If these five items are
#    the Likeability block, are all keyed with the positive pole at resp = 5,
#    and are stored raw, the per-condition mean of the five must reproduce it.
#    (The published Random n = 46 -- paper Table 1 -- so the six rows whose
#    cov_aitype is "unknown" are part of the Random condition; 40 + 6 = 46.)
#
# B. ITEM 5 IS THE FEAR ITEM (route 7, marker item + route 8). "Scary <-> Not
#    scary" is not part of the published Godspeed Likeability subscale, and it
#    is the only one of the five that is about fear rather than affection. So
#    gqs_likeability_5, and no other item, must (i) have the highest mean -- a
#    text brainstorming assistant is not frightening -- (ii) have the lowest
#    corrected item-total correlation with the rest of the Likeability block,
#    and (iii) be the item most strongly tied to the GQS Perceived Safety
#    block, with the sign pattern of an item scored 5 = "Not scary": positive
#    with perceived_safety_1 (Anxious <-> Calm) and negative with
#    perceived_safety_2 (Calm <-> Agitated, reversed) and _3 (Peaceful <->
#    Surprised, reversed).
#
# What this does NOT establish, stated up front: items 1 and 3 are given
# IDENTICAL English text by the source, so no route can separate them (and a
# swap between them is textually a no-op); and nothing here separates
# gqs_likeability_2 ("Unkind <-> Kind") from gqs_likeability_4 ("Awful <->
# Nice"), or either from items 1/3. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "komura_2026_gqs_likeability"
SAFE  <- "komura_2026_gqs_perceived_safety"

# Paper Table 3, Likeability row: Vertical, Horizontal, Random.
PUB_MEAN <- c(vertical = 3.57, horizontal = 3.43, random = 3.45)
PUB_SD   <- c(vertical = 0.69, horizontal = 0.64, random = 0.67)
PUB_N    <- c(vertical = 52,   horizontal = 50,   random = 46)   # paper Table 1
TOL_MEAN <- 0.02
TOL_SD   <- 0.02

d <- irw::irw_fetch(TABLE)
d$cond <- ifelse(d$cov_aitype == "unknown", "random", d$cov_aitype)

d <- as.data.frame(d)
items <- paste0("gqs_likeability_", 1:5)
ids <- sort(unique(d$id))
M <- sapply(items, function(i) d$resp[match(ids, ifelse(d$item == i, d$id, NA))])
rownames(M) <- ids
cond <- d$cond[match(ids, d$id)]
subscale <- rowMeans(M)

cat("=== A. Subscale mean (SD) [n] by condition, live vs paper Table 3 ===\n")
cat(sprintf("%-11s %16s %16s %8s %8s\n",
            "condition", "published", "observed", "d(mean)", "d(sd)"))
okA <- TRUE
for (cn in names(PUB_MEAN)) {
    s <- subscale[cond == cn]
    om <- mean(s); os <- sd(s)
    cat(sprintf("%-11s %7.2f (%.2f) [%2d] %7.3f (%.3f) [%2d] %8.3f %8.3f\n",
                cn, PUB_MEAN[cn], PUB_SD[cn], PUB_N[cn], om, os, length(s),
                om - PUB_MEAN[cn], os - PUB_SD[cn]))
    if (abs(om - PUB_MEAN[cn]) > TOL_MEAN || abs(os - PUB_SD[cn]) > TOL_SD ||
        length(s) != PUB_N[cn]) okA <- FALSE
}
cat(sprintf("A: %s\n\n", if (okA) "PASS" else "FAIL"))

cat("=== B. Item 5 as the fear item ===\n")
mu  <- colMeans(M)
cit <- sapply(items, function(i) cor(M[, i], rowMeans(M[, setdiff(items, i), drop = FALSE])))

ds <- irw::irw_fetch(SAFE)
ds <- as.data.frame(ds)
sitems <- paste0("gqs_perceived_safety_", 1:3)
S <- sapply(sitems, function(i) ds$resp[match(ids, ifelse(ds$item == i, ds$id, NA))])
rs <- t(sapply(items, function(i) cor(M[, i], S)))
colnames(rs) <- c("r_safety1(Anx-Calm)", "r_safety2(rev)", "r_safety3(rev)")

cat(sprintf("%-22s %7s %7s %9s %9s %9s\n", "item", "mean", "cITC",
            colnames(rs)[1], colnames(rs)[2], colnames(rs)[3]))
for (i in items)
    cat(sprintf("%-22s %7.3f %7.3f %9.3f %9.3f %9.3f\n",
                i, mu[i], cit[i], rs[i, 1], rs[i, 2], rs[i, 3]))

i5 <- "gqs_likeability_5"; oth <- setdiff(items, i5)
b1 <- mu[i5]  == max(mu)  && mu[i5]  - max(mu[oth])  > 0.3
b2 <- cit[i5] == min(cit) && min(cit[oth]) - cit[i5] > 0.1
b3 <- rs[i5, 1] == max(rs[, 1]) && rs[i5, 2] == min(rs[, 2]) && rs[i5, 3] == min(rs[, 3])
cat(sprintf("\n  B(i)  item 5 highest mean, by >0.3 over the next: %s\n", b1))
cat(sprintf("  B(ii) item 5 lowest corrected item-total, by >0.1: %s\n", b2))
cat(sprintf("  B(iii)item 5 extreme on all three safety items, +/-/-: %s\n", b3))
okB <- b1 && b2 && b3
cat(sprintf("B: %s\n\n", if (okB) "PASS" else "FAIL"))

cat("NOT ESTABLISHED: items 1 and 3 carry identical source text, so nothing can\n",
    "separate them; items 2 and 4 are not separated from each other or from 1/3.\n",
    "This route pins the subscale, the scoring direction, and item 5 only.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
