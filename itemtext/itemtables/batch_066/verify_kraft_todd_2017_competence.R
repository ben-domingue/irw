# verify_kraft_todd_2017_competence.R
#
# Claim under test (Step 5b): the five live items COMP1..COMP5 are the COMPETENCE
# block of Kraft-Todd et al. (2017)'s 9-item Fiske stereotype-content warmth/
# competence scale (S2 File order: Competent, Confident, Independent, Competitive,
# Intelligent), NOT the four-item warmth block (Tolerant, Warm, Sincere, Good
# natured) that sits directly beside it in the same source file and the same paper.
#
# Two falsifiable predictions, both from the paper (PLOS ONE 12(5): e0177758):
#   A. The composite of these five items must reproduce the paper's COMPETENCE
#      figures (M = 3.64 empathic / 3.21 unempathic, alpha = .71) and must NOT
#      reproduce its WARMTH figures (3.73 / 2.28, alpha = .92). A warmth/competence
#      swap fails this by a wide margin -- the two conditions differ by 0.43 on
#      competence and by 1.45 on warmth.
#   B. Within the block, position 4 in the S2 File list is "Competitive", the one
#      SCM competence trait that is not a virtue in a physician. It must be the
#      item with the lowest mean, the weakest correlation with its own block, and
#      the most "Does not apply" (-> missing) responses. That is a prediction about
#      WHICH code carries that text, and COMP4 is where we put it.

suppressMessages(library(irw))

TABLE <- "kraft_todd_2017_competence"
ITEMS <- paste0("COMP", 1:5)

PUB_COMP <- c(unemp = 3.21, emp = 3.64)   # paper, "Participant ratings of physician competence"
PUB_WARM <- c(unemp = 2.28, emp = 3.73)   # paper, "Participant ratings of physician warmth"
PUB_ALPHA_COMP <- 0.71
PUB_ALPHA_WARM <- 0.92
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

wide <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
                timevar = "item", direction = "wide")
colnames(wide) <- sub("^resp\\.", "", colnames(wide))
M <- as.matrix(wide[, ITEMS])

## ---- A. block identity: composite by empathy condition -----------------------
comp <- rowMeans(M, na.rm = TRUE)
cond <- d$cov_condition_empathy[match(wide$id, d$id)]
obs <- c(unemp = mean(comp[cond == 0], na.rm = TRUE),
         emp   = mean(comp[cond == 1], na.rm = TRUE))

cat("A. Composite of COMP1..COMP5 by empathic-nonverbal condition\n")
cat(sprintf("%-24s %10s %10s %10s %8s\n", "condition", "obs", "pub COMP", "pub WARM", "d(COMP)"))
for (k in c("unemp", "emp"))
    cat(sprintf("%-24s %10.2f %10.2f %10.2f %8.3f\n",
                k, obs[k], PUB_COMP[k], PUB_WARM[k], obs[k] - PUB_COMP[k]))

cc <- M[complete.cases(M), , drop = FALSE]
k <- ncol(cc)
alpha <- k / (k - 1) * (1 - sum(apply(cc, 2, var)) / var(rowSums(cc)))
cat(sprintf("%-24s %10.2f %10.2f %10.2f\n", "Cronbach alpha", alpha, PUB_ALPHA_COMP, PUB_ALPHA_WARM))

okA <- max(abs(obs - PUB_COMP)) <= TOL && abs(alpha - PUB_ALPHA_COMP) < 0.05
cat(sprintf("  -> matches published COMPETENCE within %.2f: %s ; distance to WARMTH: %.2f\n\n",
            TOL, okA, max(abs(obs - PUB_WARM))))

## ---- B. within-block: COMP4 must be the "Competitive" item -------------------
means <- colMeans(M, na.rm = TRUE)
ns    <- colSums(!is.na(M))
R     <- cor(M, use = "pairwise.complete.obs")
diag(R) <- NA
rbar  <- colMeans(R, na.rm = TRUE)

cat("B. Per-item profile (shipped text alongside)\n")
txt <- c(COMP1 = "Competent", COMP2 = "Confident", COMP3 = "Independent",
         COMP4 = "Competitive", COMP5 = "Intelligent")
cat(sprintf("%-6s %-12s %8s %8s %10s\n", "item", "shipped", "mean", "n", "mean r"))
for (i in ITEMS)
    cat(sprintf("%-6s %-12s %8.3f %8d %10.3f\n", i, txt[i], means[i], ns[i], rbar[i]))

okB <- which.min(means) == 4 && which.min(ns) == 4 && which.min(rbar) == 4
cat(sprintf("  -> lowest mean / lowest n / weakest mean-r all land on COMP4: %s\n\n", okB))

cat("Does NOT establish: the order of Competent / Confident / Intelligent among\n",
    "COMP1, COMP2 and COMP5. Those three are high-mean, mutually correlated\n",
    "0.59-0.72, and nothing in the paper separates them; their assignment rests on\n",
    "the S2 File presentation order alone. Recorded as PARTIAL, not VERIFIED.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
