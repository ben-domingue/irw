# verify_fatima_2025_mslq.R -- Step 5b evidence, re-runnable.
#
# CLAIM: item code Q<n> (and Q<n>r for the eight reverse-worded items) carries
# item n of the paper's S1 Table ("MSLQ initial adaptation and amendments after
# content validation", PLOS ONE 10.1371/journal.pone.0319763.s001), i.e. the
# original 81-item MSLQ numbering of Pintrich et al. (1991).
#
# The falsifiable prediction: the canonical MSLQ item-number -> subscale
# assignment (15 subscales) is a block structure the data must show. If the
# numbering were shifted or permuted, the blocks dissolve. This script scores
# the shipped mapping against +-3 shifts and against a random-permutation null.
#
# A second, independent tie is checked first: S1 Table marks exactly items
# 33, 37, 40, 52, 57, 60, 77, 80 with (R) "reversed coded item", and the live
# data spells exactly those eight columns with an "r" suffix.

suppressMessages(library(irw))
TABLE <- "fatima_2025_mslq"

REV <- c(33, 37, 40, 52, 57, 60, 77, 80)          # (R)-marked items in S1 Table
code <- function(n) ifelse(n %in% REV, paste0("Q", n, "r"), paste0("Q", n))

# Canonical MSLQ (Pintrich et al. 1991) item numbers per subscale. Independently
# reproduced from this paper's own S2 Appendix (MSLQ-CL), whose 75 retained items
# are these minus the six reverse items 33/40/52/57/77/80 it dropped.
subs <- list(
  IntrinsicGoal = c(1, 16, 22, 24), ExtrinsicGoal = c(7, 11, 13, 30),
  TaskValue = c(4, 10, 17, 23, 26, 27), ControlBeliefs = c(2, 9, 18, 25),
  SelfEfficacy = c(5, 6, 12, 15, 20, 21, 29, 31), TestAnxiety = c(3, 8, 14, 19, 28),
  Rehearsal = c(39, 46, 59, 72), Elaboration = c(53, 62, 64, 67, 69, 81),
  Organisation = c(32, 42, 49, 63), CriticalThinking = c(38, 47, 51, 66, 71),
  Metacognitive = c(33, 36, 41, 44, 54, 55, 56, 57, 61, 76, 78, 79),
  TimeStudyEnv = c(35, 43, 52, 65, 70, 73, 77, 80), EffortReg = c(37, 48, 60, 74),
  PeerLearning = c(34, 45, 50), HelpSeeking = c(40, 58, 68, 75))

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w)); w$id <- NULL

# --- check 1: the (R) markers ---------------------------------------------
live_r <- sort(colnames(w)[grepl("r$", colnames(w))])
cat("S1 Table (R)-marked items :", paste(sort(code(REV)), collapse = " "), "\n")
cat("live columns with r suffix:", paste(live_r, collapse = " "), "\n")
marker_ok <- identical(live_r, sort(code(REV)))
cat("marker match:", marker_ok, "\n\n")

# --- check 2: subscale block structure ------------------------------------
R <- cor(w, use = "pairwise.complete.obs")
revc <- code(REV)
keep <- setdiff(colnames(w), revc)   # the 8 reverse items are near-zero
                                     # correlated with everything in this
                                     # sample, so they carry no block signal
score <- function(shift) {
  hit <- 0; tot <- 0
  for (s in names(subs)) {
    ns <- ((subs[[s]] - 1 + shift) %% 81) + 1
    its <- intersect(setdiff(code(ns), revc), keep)
    if (length(its) < 2) next
    for (i in its) {
      own <- mean(R[i, setdiff(its, i)]); oth <- mean(R[i, setdiff(keep, its)])
      hit <- hit + (own > oth); tot <- tot + 1
    }
  }
  c(hit, tot)
}
cat("items correlating higher with own canonical subscale than with the rest:\n")
res <- list()
for (s in -3:3) {
  r <- score(s); res[[as.character(s)]] <- r[1] / r[2]
  cat(sprintf("  numbering shift %+d : %2d/%d (%3.0f%%)%s\n",
              s, r[1], r[2], 100 * r[1] / r[2], if (s == 0) "   <- as shipped" else ""))
}
set.seed(1)
perm <- replicate(200, {
  p <- sample(1:81); hit <- 0; tot <- 0
  for (s in names(subs)) {
    its <- intersect(setdiff(code(p[subs[[s]]]), revc), keep)
    if (length(its) < 2) next
    for (i in its) {
      own <- mean(R[i, setdiff(its, i)]); oth <- mean(R[i, setdiff(keep, its)])
      hit <- hit + (own > oth); tot <- tot + 1
    }
  }
  hit / tot
})
cat(sprintf("  random permutations (200): mean %3.0f%%, max %3.0f%%\n",
            100 * mean(perm), 100 * max(perm)))

shipped <- res[["0"]]
rivals  <- max(unlist(res[as.character(setdiff(-3:3, 0))]))
cat(sprintf("\nshipped %.0f%% vs best rival shift %.0f%% vs permutation max %.0f%%\n",
            100 * shipped, 100 * rivals, 100 * max(perm)))

cat("Note: this route pins each item's SUBSCALE, not its order within a subscale,\n",
    "and it says nothing about the 8 reverse items (excluded above). Those eight are\n",
    "pinned instead by the (R)/r-suffix match in check 1, and item-level identity\n",
    "rests on S1 Table's own numbering 1-81 matching columns Q1-Q81.\n", sep = "")

ok <- marker_ok && shipped >= 0.95 && shipped > rivals && shipped > max(perm)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
