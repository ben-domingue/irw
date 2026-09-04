# verify_cognitive_load_klimova_2023_mlq.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes MLQ{Control,Exp}{a..i} are the Meaning in Life Questionnaire
# (Steger, Frazier, Oishi & Kaler 2006) items 1..9 in alphabetical order (MLQ item
# 10 is absent from this table), and the 1-7 coding runs 1 = "Absolutely Untrue"
# ... 7 = "Absolutely True" (canonical MLQ direction), NOT the reversed direction
# printed in the study's AsPredicted pre-registration (#134579).
#
# Two falsifiable predictions follow from that mapping.
#
# P1  SUBSCALE / KEYING STRUCTURE.  MLQ Presence = items 1,4,5,6,9(reverse);
#     Search = items 2,3,7,8,10.  Under a->1 ... i->9 that makes
#       Presence-positive = {a,d,e,f}, Search = {b,c,g,h}, reverse item = {i}.
#     So the correlation matrix must show two positively cohering blocks, near-zero
#     correlation between them, and item i correlating NEGATIVELY with the
#     Presence block and roughly zero with the Search block.
#     The table holds two independent subsamples (Control n=83, Exp n=87) that saw
#     the same items, so the prediction is tested twice on disjoint respondents.
#
# P2  SCALE DIRECTION.  With 7 = "Absolutely True", undergraduates should sit above
#     the midpoint on Presence and Search and BELOW it on item 9 ("My life has no
#     clear purpose").  The pre-registration's stated direction predicts the mirror
#     image.  Steger et al. (2006) student norms: MLQ-P ~ 4.6, MLQ-S ~ 5.1 of 7.
#
# WHAT THIS DOES NOT ESTABLISH ----------------------------------------------
# It pins block membership, the reverse item, and the scale direction. It does NOT
# distinguish a/d/e/f from each other (MLQ 1/4/5/6) or b/c/g/h from each other
# (MLQ 2/3/7/8) -- those four-way orders rest on the alphabetical convention alone.
# Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "cognitive_load_klimova_2023_mlq"
PRES  <- c("a","d","e","f")   # MLQ 1,4,5,6
SRCH  <- c("b","c","g","h")   # MLQ 2,3,7,8
REV   <- "i"                  # MLQ 9, reverse worded

d <- irw::irw_fetch(TABLE)
ok <- TRUE

mean_off <- function(m) { diag(m) <- NA; mean(m, na.rm = TRUE) }

for (blk in c("MLQControl", "MLQExp")) {
    s <- as.data.frame(d)[grepl(paste0("^", blk), d$item), c("id", "item", "resp")]
    s$L <- sub(paste0("^", blk), "", s$item)
    w <- reshape(s[, c("id", "L", "resp")], idvar = "id", timevar = "L",
                 direction = "wide")
    m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
    cm <- cor(m, use = "pairwise.complete.obs")

    wP  <- mean_off(cm[PRES, PRES])
    wS  <- mean_off(cm[SRCH, SRCH])
    bPS <- mean(cm[PRES, SRCH])
    rP  <- mean(cm[REV, PRES])
    rS  <- mean(cm[REV, SRCH])

    cat(sprintf("\n=== %s  (n ids = %d) ===\n", blk, nrow(w)))
    cat(sprintf("  mean r within Presence-positive {a,d,e,f} : %+.3f   (predict > +0.35)\n", wP))
    cat(sprintf("  mean r within Search          {b,c,g,h} : %+.3f   (predict > +0.30)\n", wS))
    cat(sprintf("  mean r BETWEEN the two blocks          : %+.3f   (predict |r| < 0.20)\n", bPS))
    cat(sprintf("  mean r of reverse item i with Presence : %+.3f   (predict < -0.25)\n", rP))
    cat(sprintf("  mean r of reverse item i with Search   : %+.3f   (predict  > -0.25)\n", rS))
    p1 <- wP > 0.35 && wS > 0.30 && abs(bPS) < 0.20 && rP < -0.25 && rS > -0.25
    cat(sprintf("  P1 (structure) : %s\n", if (p1) "PASS" else "FAIL"))

    mP <- mean(colMeans(m[, PRES], na.rm = TRUE))
    mS <- mean(colMeans(m[, SRCH], na.rm = TRUE))
    mR <- mean(m[, REV], na.rm = TRUE)
    cat(sprintf("  Presence mean %.2f (Steger student norm ~4.6) | Search mean %.2f (~5.1) | item 9 mean %.2f\n",
                mP, mS, mR))
    p2 <- mP > 4 && mS > 4 && mR < 4
    cat(sprintf("  P2 (direction, 7 = Absolutely True) : %s\n", if (p2) "PASS" else "FAIL"))

    ok <- ok && p1 && p2
}

cat("\nNote: this route pins subscale membership, the reverse-keyed item and the\n",
    "scale direction. It does NOT separate a/d/e/f from one another, nor\n",
    "b/c/g/h from one another; that ordering rests on the alphabetical convention.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
