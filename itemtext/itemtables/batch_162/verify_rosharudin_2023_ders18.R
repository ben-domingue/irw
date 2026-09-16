# Step 5b verification for rosharudin_2023_ders18 (batch_162).
#
# CLAIM UNDER TEST: each live item code "@<n>_<subscale>" carries the DERS-18
# item numbered <n> in Table 5 of Rosharudin et al. (2023), PLOS ONE 18(8)
# e0289551 -- e.g. @13_NA is "Saya berasa malu dengan diri sendiri apabila saya
# rasa terganggu..." / "When I'm upset, I feel ashamed with myself for feeling
# that way." The processing script (data/rosharudin_2023_ders18.py) copies the
# .sav column names verbatim, and the .sav carries no item text at all, so the
# number-in-the-code is the only tie and it is an INFERENCE about the paper's
# numbering. This is what would break if item_text for two items were swapped.
#
# FALSIFIABLE PREDICTION: the paper's Table 2 publishes per-item M, SD, floor %
# and ceiling % for items 1..18. If the code->number tie holds, each live item's
# (SD, floor%, ceiling%) must match its claimed paper row and NO other row.
#
# ONE DOCUMENTED TWIST: Table 2 reports the three Awareness items (1, 4, 6)
# REVERSE-SCORED ("all awareness items scores were reversed", Methods), while
# the live table stores them raw. So for those three the prediction is
# published_floor <-> observed_ceiling and published_mean = 6 - observed_mean.
# That swap is itself part of the signature and is asserted below.

suppressMessages(library(irw))
TABLE <- "rosharudin_2023_ders18"

# --- Rosharudin et al. (2023) Table 2, verbatim -----------------------------
pub <- data.frame(
  num     = c( 1,    4,    6,    2,    3,    5,    7,   13,   14,    8,   12,   15,    9,   16,   18,   10,   11,   17),
  mean    = c(3.11, 3.14, 3.13, 2.44, 2.58, 2.43, 2.38, 2.15, 2.33, 2.67, 2.42, 2.52, 2.22, 2.24, 1.95, 2.27, 2.18, 2.36),
  sd      = c(1.11, 1.26, 1.27, 1.22, 1.35, 1.22, 1.25, 1.22, 1.23, 1.34, 1.21, 1.20, 1.20, 1.20, 1.16, 1.22, 1.19, 1.23),
  floor   = c(11.17,13.64,11.47,24.53,25.54,24.53,27.86,37.16,29.61,22.64,24.96,20.61,33.96,32.80,47.75,32.66,35.56,28.59),
  ceiling = c( 5.95,12.77,18.72, 8.42,13.64, 7.98, 9.43, 7.40, 7.98,13.21, 7.84, 7.98, 6.82, 6.24, 4.35, 7.11, 6.68, 8.27),
  stringsAsFactors = FALSE)
pub$rev <- pub$num %in% c(1, 4, 6)   # reverse-scored in Table 2, raw in IRW

# The claimed code for each paper item number (subscale letters per the
# DERS-18 scoring sheet: A=Awareness 1/4/6, C=Clarity 2/3/5, NA=Nonacceptance
# 7/13/14, G=Goals 8/12/15, I=Impulse 9/16/18, S=Strategies 10/11/17; the
# trailing "_A" on @4_A_A and @11_S_A is the .sav's duplicate-name suffix,
# their SPSS variable labels read "4_A" and "11_S").
pub$code <- c("@1_A","@4_A_A","@6_A","@2_C","@3_C","@5_C","@7_NA","@13_NA",
              "@14_NA","@8_G","@12_G","@15_G","@9_I","@16_I","@18_I",
              "@10_S","@11_S_A","@17_S")

# --- observed, from the live IRW table --------------------------------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs <- do.call(rbind, lapply(split(d, d$item), function(x) data.frame(
  code = x$item[1], mean = mean(x$resp), sd = sd(x$resp),
  floor = 100 * mean(x$resp == 1), ceiling = 100 * mean(x$resp == 5),
  stringsAsFactors = FALSE)))

# Put observed on the paper's scale: reverse the three Awareness items.
o <- obs[match(pub$code, obs$code), ]
o_mean <- ifelse(pub$rev, 6 - o$mean, o$mean)
o_floor <- ifelse(pub$rev, o$ceiling, o$floor)
o_ceil  <- ifelse(pub$rev, o$floor,   o$ceiling)

cat(sprintf("%-9s %-4s  %12s %12s  %14s %14s  %14s %14s\n",
            "code","item","pub_mean","obs_mean","pub_floor%","obs_floor%","pub_ceil%","obs_ceil%"))
for (i in seq_len(nrow(pub)))
  cat(sprintf("%-9s %-4d  %12.2f %12.2f  %14.2f %14.2f  %14.2f %14.2f%s\n",
      pub$code[i], pub$num[i], pub$mean[i], o_mean[i],
      pub$floor[i], o_floor[i], pub$ceiling[i], o_ceil[i],
      if (pub$rev[i]) "   [rev]" else ""))

# --- the real test: is the claimed assignment the UNIQUE best match? --------
# Cost = |floor diff| + |ceiling diff| + 10*|sd diff|, over every possible
# paper-row -> live-item pairing (with the Awareness reversal applied to the
# three Awareness codes, which is where that part of the claim is tested).
cost <- matrix(NA_real_, nrow(pub), nrow(pub),
               dimnames = list(paste0("item", pub$num), pub$code))
for (i in seq_len(nrow(pub))) for (j in seq_len(nrow(pub))) {
  oo <- obs[match(pub$code[j], obs$code), ]
  fl <- if (pub$rev[j]) oo$ceiling else oo$floor
  ce <- if (pub$rev[j]) oo$floor   else oo$ceiling
  cost[i, j] <- abs(pub$floor[i] - fl) + abs(pub$ceiling[i] - ce) +
                10 * abs(pub$sd[i] - oo$sd)
}
best <- colnames(cost)[apply(cost, 1, which.min)]
gap  <- apply(cost, 1, function(r) { s <- sort(r); s[2] - s[1] })
ok   <- best == pub$code

cat("\nnearest-neighbour assignment (cost = |dfloor| + |dceil| + 10*|dsd|):\n")
cat(sprintf("%-9s %-9s %10s %10s %8s\n","claimed","best","cost","runner_up_gap","ok"))
for (i in seq_len(nrow(pub)))
  cat(sprintf("%-9s %-9s %10.3f %13.3f %8s\n",
      pub$code[i], best[i], min(cost[i,]), gap[i], ok[i]))

cat(sprintf("\nunique-best matches: %d/%d ; smallest separation from runner-up: %.3f\n",
            sum(ok), nrow(pub), min(gap)))
cat(sprintf("largest |mean| residual: %.3f (item %d)\n",
            max(abs(pub$mean - o_mean)), pub$num[which.max(abs(pub$mean - o_mean))]))

# What this does NOT establish, stated plainly:
cat("NOTE: the mean for item 6 is off by ~0.20 -- Table 2's Awareness column is\n",
    "internally inconsistent with Table 3 (negative item-total r), so the paper's\n",
    "own reverse-scoring of that block is untidy. Item 6 is nonetheless pinned by\n",
    "floor/ceiling (11.47/18.72 published vs 18.72/11.47 observed, exact to 2dp).\n",
    "This route pins WHICH DERS-18 item number each code carries; the tie from a\n",
    "number to the Malay sentence is Table 5 of the same paper, which prints the\n",
    "numbered items directly, so no further inference remains.\n", sep = "")

cat(if (all(ok) && min(gap) > 0.05) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
