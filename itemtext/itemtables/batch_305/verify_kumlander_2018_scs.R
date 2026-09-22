# Mapping verification for kumlander_2018_scs (Self-Compassion Scale, Finnish).
#
# THE CLAIM UNDER TEST: live item code scompN carries the wording the study's S1
# Table prints as SCS item N -- i.e. the study's numbering is Neff's canonical
# numbering, and no two items are swapped.
#
# THE FALSIFIABLE PREDICTION: S2 Table of the same paper (pone.0207706.s002.pdf)
# publishes fully standardized loadings for the preliminary two-factor model on
# WAVE 1 -- which is exactly the sample this IRW table holds (the processing
# script ships s006.sav alone). Those loadings are per-item and, within each
# factor, all distinct. Refit that model on the live data and every item must
# land on its own published value. Swap any two items' text and the pairing of
# code to loading breaks.
#
# Model: SC =~ the 13 positively-keyed items (Self-Kindness, Common Humanity,
# Mindfulness); SCold =~ the 13 reverse-keyed items (Self-Judgment, Isolation,
# Over-identification) -- the subscale assignment printed in S1 Table and
# independently carried by the .sav's "(neg)" variable labels.

suppressMessages({library(irw); library(lavaan)})

TABLE <- "kumlander_2018_scs"
TOL   <- 0.01

POS <- c(5, 12, 19, 23, 26, 3, 7, 10, 15, 9, 14, 17, 22)
NEG <- c(1, 8, 11, 16, 21, 4, 13, 18, 25, 2, 6, 20, 24)

# PLOS ONE 13(12):e0207706, S2 Table (W1), transcribed verbatim.
PUB <- c(scomp5=.651, scomp12=.639, scomp19=.707, scomp23=.594, scomp26=.656,
         scomp3=.536, scomp7=.452, scomp10=.526, scomp15=.707,
         scomp9=.448, scomp14=.619, scomp17=.614, scomp22=.612,
         scomp1=.678, scomp8=.739, scomp11=.593, scomp16=.710, scomp21=.733,
         scomp4=.643, scomp13=.656, scomp18=.618, scomp25=.676,
         scomp2=.730, scomp6=.681, scomp20=.568, scomp24=.486)
# S2 Table's residual variance for SCOMP19 is .631, and 1 - .607^2 = .632 while
# 1 - .707^2 = .500 -- so the printed .707 is a typo for .607 by the table's own
# arithmetic. Corrected here; it is the only exception allowed.
PUB_FIX <- PUB; PUB_FIX["scomp19"] <- .607

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w)); w$id <- NULL

mod <- paste0("SC =~ ",    paste0("scomp", POS, collapse = " + "), "\n",
              "SCold =~ ", paste0("scomp", NEG, collapse = " + "))
fit <- lavaan::cfa(mod, data = w, estimator = "MLR", missing = "fiml")
st  <- lavaan::standardizedSolution(fit); st <- st[st$op == "=~", ]

ord <- c(paste0("scomp", POS), paste0("scomp", NEG))
obs <- setNames(st$est.std[match(ord, st$rhs)], ord)

cat(sprintf("%-9s %10s %10s %8s\n", "item", "S2 Table", "refit", "diff"))
for (it in ord)
    cat(sprintf("%-9s %10.3f %10.3f %8.3f\n",
                it, PUB[it], obs[it], obs[it] - PUB_FIX[it]))

dev <- abs(obs - PUB_FIX[ord])
cat(sprintf("\nlargest deviation vs S2 Table (scomp19 corrected to .607): %.4f (tol %.2f)\n",
            max(dev), TOL))
cat(sprintf("deviation vs S2 Table AS PRINTED, scomp19: %.3f\n",
            obs["scomp19"] - PUB["scomp19"]))

# Uniqueness: a loading only identifies an item if no sibling shares it.
uniq <- all(!duplicated(round(obs[paste0("scomp", POS)], 3))) &&
        all(!duplicated(round(obs[paste0("scomp", NEG)], 3)))
cat(sprintf("within-factor loadings all distinct to 3 dp: %s\n", uniq))

cat("Note: this pins every one of the 26 items to its own published loading, so no\n",
    "pair of items can be swapped. It does NOT check the Finnish-vs-English pairing\n",
    "inside a row -- both languages come from the same S1 Table line, so that tie is\n",
    "the source's, not an inference of ours.\n", sep = "")

cat(if (max(dev) <= TOL && uniq) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
