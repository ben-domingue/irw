# verify_perfectionismlit_2021_prepost.R -- Step 5b, route 1 (per-item descriptives).
#
# Claim: Q1..Q5 (source columns PreQn/PostQn with the Pre/Post prefix stripped by
# data/perfectionismlit_2021_prepost.py) are the five questions of Table 1/Table 2
# of Hill, Fenwick & Lightfoot (2021), NACE "Evaluation Report: Perfectionism
# Literacy Lesson", in printed order. Table 2 prints n, Time 1 M/SD and Time 2 M/SD
# per question; wave 1 = pre (Time 1), wave 2 = post (Time 2).
# The falsifiable prediction: each published row matches exactly one live item on
# all five numbers, and that item is the one we assigned.

suppressMessages(library(irw))
TABLE <- "perfectionismlit_2021_prepost"

PUB <- data.frame(
  item = paste0("Q", 1:5),
  n1   = c(68, 67, 68, 68, 68),  # "Respondents" column (Time 1 completers)
  m1   = c(3.07, 2.63, 2.46, 3.06, 3.31),
  sd1  = c(0.97, 1.27, 1.04, 1.09, 1.03),
  m2   = c(4.44, 3.78, 3.82, 3.93, 4.10),
  sd2  = c(0.66, 0.93, 0.93, 0.83, 0.78))
TOL <- 0.005

d <- irw::irw_fetch(TABLE)
st <- function(w, f) tapply(d$resp[d$wave == w], d$item[d$wave == w], f)
LIVE <- data.frame(item = names(st(1, mean)),
  n1 = as.vector(st(1, length)), m1 = as.vector(st(1, mean)), sd1 = as.vector(st(1, sd)),
  m2 = as.vector(st(2, mean)),  sd2 = as.vector(st(2, sd)))

cat(sprintf("%-4s | %-28s | %-28s\n", "pub", "published n m1 sd1 m2 sd2", "live (assigned item)"))
ok <- TRUE
for (i in seq_len(nrow(PUB))) {
  p <- PUB[i, ]
  # which live items match this published row on every statistic?
  hit <- LIVE$item[abs(LIVE$m1 - p$m1) <= TOL & abs(LIVE$sd1 - p$sd1) <= TOL &
                   abs(LIVE$m2 - p$m2) <= TOL & abs(LIVE$sd2 - p$sd2) <= TOL &
                   LIVE$n1 == p$n1]
  l <- LIVE[LIVE$item == p$item, ]
  cat(sprintf("%-4s | %2d %.2f %.2f %.2f %.2f | %2d %.3f %.3f %.3f %.3f | matches: %s\n",
              p$item, p$n1, p$m1, p$sd1, p$m2, p$sd2,
              l$n1, l$m1, l$sd1, l$m2, l$sd2, paste(hit, collapse = ",")))
  if (!identical(hit, p$item)) ok <- FALSE
}
cat("\nEach published row must match exactly one live item, and it must be the assigned one.\n")
cat("Q1/Q4 nearly tie on Time 1 mean (3.07 vs 3.06) but separate on Time 1 SD (0.97 vs 1.09)\n",
    "and Time 2 mean (4.44 vs 3.93); Q2 is also pinned by its n=67 (the one missing response).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
