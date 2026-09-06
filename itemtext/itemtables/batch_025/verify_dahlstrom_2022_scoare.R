# verify_dahlstrom_2022_scoare.R -- Step 5b mapping check.
#
# CLAIM: the IRW item codes are the S1 Dataset column names with the B/N
# (Before/Now) suffix stripped, and each two/three-letter code maps to a named
# row of the S1 File survey grid, with the 3rd letter W = "Scientific writing"
# and S = "Speaking or presenting".
#
# FALSIFIABLE PREDICTION: Dahlstrom et al. (2022) PLoS ONE 17(1):e0262418
# Tables 5 and 6 publish pre-test mean/SD, post-test mean/SD and n for 14 of the
# 20 items. wave=0 is "before", wave=1 is "now". If any two item texts were
# swapped -- in particular if W and S were swapped -- the assignment would break.
#
# The test is nearest-neighbour, not just tolerance: each published row must be
# closest to the item this extraction assigned it to, out of all 20 live items.

suppressMessages(library(irw))
TABLE <- "dahlstrom_2022_scoare"
TOL <- 0.02   # paper rounds to 2 dp

# item, pre mean, pre sd, post mean, post sd, published n, source row
P <- read.csv(text = "item,pre_m,pre_sd,post_m,post_sd,n,label
KB,1.13,0.83,2.27,0.63,158,T5 How linguistic biases influence perceptions of others
KR,1.06,0.82,2.32,0.58,158,T5 Research on the impact of SC on training outcomes
KEW,1.33,0.67,2.53,0.52,91,T5 Various strategies to encourage engagement in WRITING
KES,1.52,0.69,2.54,0.50,90,T5 Various strategies to encourage engagement in SPEAKING
KAW,1.12,0.70,2.31,0.59,91,T5 How to avoid unproductive strategies in WRITING
KAS,1.32,0.81,2.30,0.59,90,T5 How to avoid unproductive strategies in SPEAKING
SFW,1.85,0.61,2.61,0.53,92,T6 Providing feedback about their WRITING
SFS,2.18,0.66,2.63,0.49,92,T6 Providing feedback about their SPEAKING
SDW,1.53,0.76,2.45,0.54,92,T6 Diagnosing trainees' needs in WRITING
SDS,1.93,0.78,2.52,0.57,91,T6 Diagnosing trainees' needs in SPEAKING
STW,1.34,0.75,2.54,0.52,92,T6 Applying new/various techniques in WRITING
STS,1.54,0.76,2.57,0.50,92,T6 Applying new/various techniques in SPEAKING
SMW,1.45,0.65,2.45,0.54,92,T6 Motivating trainees to engage in WRITING
SMS,1.69,0.71,2.49,0.52,91,T6 Motivating trainees to engage in SPEAKING",
  stringsAsFactors = FALSE)

d <- irw::irw_fetch(TABLE)
agg <- function(w) {
  s <- d[d$wave == w, ]
  data.frame(item = sort(unique(s$item)),
             m  = as.numeric(tapply(s$resp, s$item, mean)[sort(unique(s$item))]),
             sd = as.numeric(tapply(s$resp, s$item, sd)[sort(unique(s$item))]),
             n  = as.numeric(tapply(s$resp, s$item, length)[sort(unique(s$item))]),
             stringsAsFactors = FALSE)
}
a0 <- agg(0); a1 <- agg(1)
live <- merge(a0, a1, by = "item", suffixes = c("_pre", "_post"))

cat(sprintf("%-4s %-58s %s\n", "item", "published row (Table 5/6)",
            "pre M/SD (n)  ->  live pre M/SD (n) | post pub -> live"))
worst <- 0; bad <- character(0)
for (i in seq_len(nrow(P))) {
  r <- P[i, ]; L <- live[live$item == r$item, ]
  dev <- max(abs(c(L$m_pre - r$pre_m, L$sd_pre - r$pre_sd,
                   L$m_post - r$post_m, L$sd_post - r$post_sd)))
  worst <- max(worst, dev)
  cat(sprintf("%-4s %-58s %.2f/%.2f (%d) -> %.2f/%.2f (%d) | %.2f/%.2f -> %.2f/%.2f  maxdev %.3f\n",
              r$item, substr(r$label, 1, 58), r$pre_m, r$pre_sd, r$n,
              L$m_pre, L$sd_pre, L$n_pre, r$post_m, r$post_sd, L$m_post, L$sd_post, dev))
  if (dev > TOL) bad <- c(bad, r$item)
  if (L$n_pre != r$n && abs(L$n_pre - r$n) > 1)
    bad <- c(bad, paste0(r$item, "(n)"))
}

# Uniqueness: is each published profile CLOSEST to the item we assigned it to?
cat("\n-- nearest-neighbour assignment over all 20 live items --\n")
mis <- character(0)
for (i in seq_len(nrow(P))) {
  r <- P[i, ]
  dist <- sqrt((live$m_pre - r$pre_m)^2 + (live$sd_pre - r$pre_sd)^2 +
               (live$m_post - r$post_m)^2 + (live$sd_post - r$post_sd)^2)
  nn <- live$item[which.min(dist)]
  second <- sort(dist)[2]
  cat(sprintf("%-4s -> nearest live item %-4s (d=%.3f; runner-up d=%.3f) %s\n",
              r$item, nn, min(dist), second, if (nn == r$item) "OK" else "MISMATCH"))
  if (nn != r$item) mis <- c(mis, r$item)
}

cat(sprintf("\nlargest per-statistic deviation: %.3f (tolerance %.2f)\n", worst, TOL))
cat("W = scientific writing, S = speaking or presenting is decided here: e.g. SFW\n",
    "matches the published WRITING row (1.85/.61) and SFS the SPEAKING row (2.18/.66);\n",
    "swapping them would raise the deviation to ~0.33.\n", sep = "")
cat("NOT established by this route: the 6 Year-1 unsplit items (SF, SD, ST, SM,\n",
    "KE, KA) have no published per-item statistics. Their text rests on sharing a\n",
    "code prefix with the verified split siblings, not on the data.\n", sep = "")

cat(if (length(bad) == 0 && length(mis) == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
