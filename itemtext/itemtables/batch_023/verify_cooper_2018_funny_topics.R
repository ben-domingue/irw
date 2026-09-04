# verify_cooper_2018_funny_topics.R
#
# CLAIM UNDER TEST: each live item code (e.g. `funny.muslims`) carries the joke
# subject that the shipped item_text names (e.g. "jokes about Muslims").
#
# FALSIFIABLE PREDICTION: S1 Table of Cooper et al. 2018 (PLoS ONE 13(8):
# e0201258) publishes, per joke subject *named in English*, a logistic
# regression of "found funny" on gender -- an intercept (female reference) and a
# male coefficient. With the paper's own N (1004 female, 606 male) those two
# numbers imply a pooled endorsement proportion for each NAMED SUBJECT. The live
# table's per-item mean is the observed pooled proportion for each ITEM CODE.
# If any item_text were attached to the wrong code, the two vectors would stop
# lining up. This is independent of the item codes' own wording.
#
# Run: Rscript verify_cooper_2018_funny_topics.R

suppressMessages(library(irw))

TABLE <- "cooper_2018_funny_topics"
N_F <- 1004; N_M <- 606          # Cooper et al. 2018, gender counts of the S3 File

# S1 Table: subject -> c(intercept, male coefficient). Keyed here by the item
# code whose shipped item_text names that subject.
B <- rbind(
  funny.science           = c( 2.11,  0.05), funny.college      = c( 1.77, -0.16),
  funny.tv                = c( 1.31, -0.36), funny.food.puns    = c( 0.94, -0.55),
  funny.relationships     = c( 0.43,  0.20), funny.cute.animals = c( 0.34, -0.29),
  funny.dogs              = c( 0.34, -0.33), funny.cats         = c( 0.21, -0.22),
  funny.students          = c(-0.03,  0.22), funny.sports       = c(-0.18,  0.67),
  funny.donald.trump      = c(-0.28,  0.30), funny.politics     = c(-0.38,  0.87),
  funny.sex               = c(-0.44,  0.50), funny.farts        = c(-0.77,  0.20),
  funny.old.people        = c(-1.32,  0.80), funny.hillaryclinton = c(-1.40, 0.99),
  funny.republicans       = c(-1.60,  0.91), funny.genitalia    = c(-1.61,  0.97),
  funny.divorce           = c(-1.67,  0.82), funny.seanspicer   = c(-1.77,  0.96),
  funny.democrats         = c(-1.93,  1.24), funny.mormons      = c(-2.28,  1.20),
  funny.christians        = c(-2.38,  1.30), funny.women        = c(-2.43,  1.56),
  funny.weight            = c(-2.47,  1.56), funny.catholics    = c(-2.64,  1.41),
  funny.mexicans          = c(-2.79,  1.54), funny.immigration  = c(-2.97,  1.78),
  funny.jewish            = c(-3.04,  1.76), funny.african.americans = c(-3.06, 1.71),
  funny.gaypeople         = c(-3.18,  1.83), funny.transgender  = c(-3.29,  1.89),
  funny.muslims           = c(-3.32,  1.96), funny.disabilities = c(-3.59,  1.99))

sig  <- function(x) 1 / (1 + exp(-x))
pred <- (N_F * sig(B[, 1]) + N_M * sig(B[, 1] + B[, 2])) / (N_F + N_M)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs <- tapply(d$resp, d$item, mean)[rownames(B)]

cat(sprintf("%-24s %10s %10s %8s\n", "item", "predicted", "observed", "diff"))
for (i in seq_along(obs))
  cat(sprintf("%-24s %10.3f %10.3f %+8.3f\n",
              names(obs)[i], pred[i], obs[i], obs[i] - pred[i]))
worst <- max(abs(obs - pred))
cat(sprintf("\nlargest deviation: %.4f (tolerance 0.02)\n", worst))

# The decisive part: is the shipped (identity) assignment the BEST of all 34!
# permutations of item_text onto item codes? Hungarian algorithm on |obs-pred|.
C <- abs(outer(as.numeric(obs), as.numeric(pred), "-"))
best <- as.integer(clue::solve_LSAP(C))
mis  <- which(best != seq_along(best))
cat(sprintf("optimal assignment over all 34! permutations: %d item(s) reassigned\n",
            length(mis)))
if (length(mis)) cat("  reassigned:", paste(names(obs)[mis], "->", names(obs)[best[mis]],
                                            collapse = "; "), "\n")
cat(sprintf("identity total cost %.4f vs optimal %.4f\n",
            sum(diag(C)), sum(C[cbind(seq_along(best), best)])))

cat("\nNote: nearest-neighbour matching alone leaves 8 items ambiguous (the\n",
    "cluster near 0.10: gaypeople/muslims/transgender/african.americans, and\n",
    "the dogs/cute.animals tie at 0.34 logit). It is the GLOBAL assignment that\n",
    "separates them. This route says nothing about the option_text labels\n",
    "('Selected'/'Not selected'), which are described in provenance.\n", sep = "")

cat(if (worst <= 0.02 && length(mis) == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
