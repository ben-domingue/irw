# verify_turner_2022_sr_belief_change.R
#
# WHAT IS BEING VERIFIED.  The live item codes are the source .sav's own column
# names (Q3_SRchange ... Q40_SRchange -- data/turner_2022_abcs.py melts them
# unchanged), but the item TEXT is published in the PLOS S2 File against a
# separate 1..24 renumbering of the EFA item pool, with no Q-number anywhere in
# it.  The 24 S2 numbers are ordered by factor loading within factor, so items
# 16-24 are the nine S-R change items in this table.  The shipped mapping from
# S2 number -> Q-code is therefore RECONSTRUCTED, and this script is the check.
#
# THE FALSIFIABLE PREDICTION.  S2 publishes, for every one of the 24 items, its
# loading on the retained factor AND its cross-loading on the other factor.  Re-
# running the paper's first-iteration EFA on its own S1 Data (.sav) reproduces
# both columns per Q-code, so the assignment of S2 numbers to Q-codes is the
# permutation that minimises the discrepancy.  All 9! = 362880 permutations are
# searched; the winner must be the shipped mapping.
#
# A second, independent check: the S2 texts split cleanly into "other people must
# change" and "the situation must change / I must leave it" statements, and under
# the shipped mapping every PEOPLE item is less endorsed than every SITUATION
# item (a perfect 4/5 split; p = 1/choose(9,4) = .0079 by chance).
#
# WHAT IT DOES NOT ESTABLISH: S2 items 17 and 18 publish loadings .693/.690 and
# cross-loadings .036/.037 -- indistinguishable at the printed precision.  The
# loading search prefers 17=Q34_SRchange, 18=Q35_Srchange over the swap by only
# 6% of total cost, so that ONE pair is separated by the semantic/means argument
# above, not by the published statistics.  Hence status PARTIAL, not VERIFIED.

suppressMessages({library(irw); library(haven); library(psych)})

TABLE <- "turner_2022_sr_belief_change"
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?id=10.1371/journal.pone.0269928.s006&type=supplementary")

# Shipped mapping: S2 File item number -> live IRW item code.
SHIPPED <- c("16"="Q40_SRchange", "17"="Q34_SRchange", "18"="Q35_Srchange",
             "19"="Q24_SRchange", "20"="Q22_SRchange", "21"="Q3_SRchange",
             "22"="Q13_SRchange", "23"="Q32_SRchange", "24"="Q15_SRchange")

# Published S2 File loadings (factor 2 = S-R change) and cross-loadings
# (factor 1 = C-M generation), items 16-24.  Item 20's cross-loading is printed
# as "0.71" in the DOCX, an evident typo for 0.071 -- see note at the end.
PUB_F  <- c(.727, .693, .690, .686, .678, .627, .618, .585, .582)
PUB_X  <- c(-.058, .036, .037, -.089, .071, .038, -.081, -.002, -.064)
# "other people must change" (PEOPLE) vs "the situation must change" (SITUATION)
CLS <- c("PEOPLE","SITUATION","PEOPLE","SITUATION","SITUATION",
         "PEOPLE","SITUATION","PEOPLE","SITUATION")

## ---- 1. source data: re-run the paper's first-iteration EFA ----------------
cache <- file.path(".cache", TABLE, "s006.sav")
if (!file.exists(cache)) {
    cache <- tempfile(fileext = ".sav")
    utils::download.file(SAV_URL, cache, quiet = TRUE,
                         headers = c("User-Agent" = "Mozilla/5.0"))
}
d <- haven::read_sav(cache)
pool <- grep("gen$|change$", names(d), ignore.case = TRUE, value = TRUE)
stopifnot(length(pool) == 24)
X <- as.data.frame(lapply(d[pool], as.numeric))

ev <- eigen(cor(X))$values
cat(sprintf("EFA sanity: eigenvalues %.2f / %.2f (paper: 6.20 / 3.95); %% variance %.2f / %.2f (paper: 25.69 / 16.46)\n",
            ev[1], ev[2], 100*ev[1]/24, 100*ev[2]/24))

f <- psych::fa(X, nfactors = 2, fm = "pa", rotate = "oblimin")
L <- unclass(f$loadings)
sr <- grep("srchange$", rownames(L), ignore.case = TRUE)
stopifnot(length(sr) == 9)
k <- which.max(colMeans(abs(L[sr, ])))          # the S-R change factor
obs_f <- L[sr, k]; obs_x <- L[sr, -k]
codes <- rownames(L)[sr]
sav_mean <- vapply(codes, function(v) mean(X[[v]]), numeric(1))

## ---- 2. exhaustive assignment search --------------------------------------
perms <- function(v) if (length(v) == 1) matrix(v) else
    do.call(rbind, lapply(seq_along(v), function(i) cbind(v[i], perms(v[-i]))))
P <- perms(1:9)
cost <- apply(P, 1, function(p) sum((obs_f[p]-PUB_F)^2 + (obs_x[p]-PUB_X)^2))
o <- order(cost)
best <- codes[P[o[1], ]]

cat("\n-- published S2 values vs EFA replication, under the best assignment --\n")
cat(sprintf("%-4s %-14s %8s %8s %8s | %8s %8s %8s | %-9s %6s\n",
            "S2", "item", "pub_f", "obs_f", "d_f", "pub_x", "obs_x", "d_x", "class", "mean"))
for (i in 1:9)
    cat(sprintf("%-4d %-14s %8.3f %8.4f %8.4f | %8.3f %8.4f %8.4f | %-9s %6.3f\n",
                15+i, best[i], PUB_F[i], obs_f[P[o[1], i]], obs_f[P[o[1], i]]-PUB_F[i],
                PUB_X[i], obs_x[P[o[1], i]], obs_x[P[o[1], i]]-PUB_X[i],
                CLS[i], sav_mean[P[o[1], i]]))

cat(sprintf("\nbest cost %.6f ; runner-up %.6f (ratio %.3f), differing only at S2 items %s\n",
            cost[o[1]], cost[o[2]], cost[o[2]]/cost[o[1]],
            paste((16:24)[P[o[1], ] != P[o[2], ]], collapse = " & ")))

ok_assign <- identical(best, unname(SHIPPED[as.character(16:24)]))
cat("best assignment == shipped mapping:", ok_assign, "\n")

## ---- 3. semantic class separation of endorsement --------------------------
m <- sav_mean[P[o[1], ]]
sep <- max(m[CLS == "PEOPLE"]) < min(m[CLS == "SITUATION"])
cat(sprintf("class separation: max(PEOPLE mean) %.3f < min(SITUATION mean) %.3f -> %s (p = %.4f by chance)\n",
            max(m[CLS == "PEOPLE"]), min(m[CLS == "SITUATION"]), sep, 1/choose(9, 4)))

## ---- 4. the join axis: live IRW item means == .sav column means -----------
# 2,250 rows; this is what confirms the melt did not permute the codes.
live <- irw::irw_fetch(TABLE)
lm_ <- tapply(live$resp, live$item, mean)[codes]
cat("\n-- live IRW per-item mean vs source .sav column mean --\n")
for (i in seq_along(codes))
    cat(sprintf("%-14s live %.4f  sav %.4f  diff %.2e\n",
                codes[i], lm_[i], sav_mean[i], lm_[i]-sav_mean[i]))
ok_join <- max(abs(lm_ - sav_mean)) < 1e-9
cat("live means reproduce .sav column means:", ok_join, "\n")

cat("\nNOTE: S2 prints item 20's cross-loading as 0.71; the replication gives 0.070 for\n",
    "Q22_SRchange, so it is read here as a typo for 0.071. Reading it literally would\n",
    "make item 20 unmatchable by any Q-code (no cross-loading exceeds 0.18).\n", sep = "")
cat("NOTE: this route does NOT separate S2 items 17 and 18 (see header); that pair rests\n",
    "on the semantic class check in step 3, which is why the recorded status is PARTIAL.\n", sep = "")

cat(if (ok_assign && sep && ok_join) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
