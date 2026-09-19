# verify_motion.R -- Step 5b evidence for `motion` (batch_110), re-runnable.
#
# CLAIM UNDER TEST: the live item code "<block> <stim>" means block <block> of the
# session and a random-dot stimulus at <stim>% motion coherence, which is what the
# shipped item_text says. Two independent things have to hold.
#
# (A) CODE -> SOURCE CELL. data/motion_discrimination.R builds item as
#     paste(block, stim) over the deposit file
#     github.com/yeatmanlab/Parametric_public Analysis/Clean_Motion_Data.csv
#     (blocks 1-6 only). Re-running that over the deposit gives a per-item
#     fingerprint -- accuracy and mean RT -- which is hard-coded below. If the live
#     item codes were permuted relative to the source cells, the fingerprints would
#     not line up. Note the fingerprint must be BOTH numbers: items "1 24" and
#     "6 24" have identical accuracy (0.867925), and only mean RT separates them.
#
# (B) stim -> COHERENCE PERCENT. Established by the study's own task code
#     (Motion/Exp/RunMotionDisc.m: coherence_vector = [0.06 0.12 0.24 0.48],
#     end_pts = [1]) and by O'Brien & Yeatman 2021 (Dev Sci 24:e13039,
#     "Stimuli were presented at five coherence levels: 6%, 12%, 24%, 48%, and
#     100%"). The falsifiable data prediction is psychophysical: accuracy rises and
#     RT falls monotonically over 6 -> 12 -> 24 -> 48 within EVERY block, with the
#     100% condition sitting BELOW 48% (the paper reports exactly this anomaly:
#     "many subjects ... found 100% coherence difficult ... Performance typically
#     declined for 100% coherence stimuli compared to 48% coherence").
#
# WHAT THIS DOES NOT ESTABLISH: nothing about which calendar session each block
# number was, and nothing about response-option wording beyond resp==1 meaning a
# correct direction judgement (the source `response` column is scored accuracy:
# result.response = keyResponse == config.dir/180 in RunMotionDisc.m).

suppressMessages(library(irw))

TABLE <- "motion"

ITEMS <- c("1 6","1 12","1 24","1 48","1 100","2 6","2 12","2 24","2 48","2 100",
           "3 6","3 12","3 24","3 48","3 100","4 6","4 12","4 24","4 48","4 100",
           "5 6","5 12","5 24","5 48","5 100","6 6","6 12","6 24","6 48","6 100")
SRC_ACC <- c(0.621698,0.705660,0.867925,0.889623,0.796226,0.651887,0.770755,0.862264,0.882075,0.779245,
             0.657547,0.772642,0.856604,0.896226,0.812264,0.698113,0.815094,0.920755,0.928302,0.805660,
             0.635849,0.783962,0.887736,0.904717,0.816038,0.662264,0.782075,0.867925,0.881132,0.811321)
SRC_RT  <- c(2.621268,2.353461,1.815228,1.515268,1.720544,2.286898,1.862769,1.456696,1.402610,1.454392,
             2.127816,1.732896,1.445027,1.293868,1.445169,1.750718,1.489021,1.287737,1.205144,1.378676,
             1.836778,1.548420,1.313114,1.223190,1.373306,1.961502,1.640372,1.403525,1.223958,1.385927)

d <- irw::irw_fetch(TABLE)
acc <- tapply(d$resp, d$item, mean)[ITEMS]
rt  <- tapply(d$rt,   d$item, mean)[ITEMS]

cat("== (A) live vs. re-run of data/motion_discrimination.R over the deposit CSV ==\n")
cat(sprintf("%-8s %9s %9s %9s %9s %9s %9s\n",
            "item","src_acc","live_acc","d_acc","src_rt","live_rt","d_rt"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-8s %9.6f %9.6f %9.6f %9.6f %9.6f %9.6f\n",
              ITEMS[i], SRC_ACC[i], acc[i], acc[i]-SRC_ACC[i],
              SRC_RT[i], rt[i], rt[i]-SRC_RT[i]))
wa <- max(abs(acc - SRC_ACC)); wr <- max(abs(rt - SRC_RT))
cat(sprintf("\nlargest deviation: accuracy %.2e (tol 5e-6), mean RT %.2e (tol 5e-6)\n", wa, wr))

# The fingerprint has to be item-SPECIFIC, not merely reproduced: for each live
# item, its own source row must be the nearest of all 30.
z <- function(x) (x - mean(x)) / sd(x)
D <- outer(z(as.numeric(acc)), z(SRC_ACC), "-")^2 + outer(z(as.numeric(rt)), z(SRC_RT), "-")^2
nearest <- apply(D, 1, which.min)
uniq <- all(nearest == seq_along(ITEMS))
cat(sprintf("nearest-source match is self for %d/%d live items\n", sum(nearest == seq_along(ITEMS)), length(ITEMS)))
tie <- which(ITEMS %in% c("1 24","6 24"))
cat(sprintf("  accuracy-tied pair 1 24 / 6 24: acc %.6f vs %.6f (identical), mean RT %.4f vs %.4f (separates them)\n",
            acc[tie[1]], acc[tie[2]], rt[tie[1]], rt[tie[2]]))

cat("\n== (B) psychophysical signature of the coherence labels, per block ==\n")
cat(sprintf("%-6s %8s %8s %8s %8s %8s  %s\n","block","6%","12%","24%","48%","100%","6<12<24<48 & 100<48"))
ok_mono <- TRUE
for (b in 1:6) {
  a <- sapply(c(6,12,24,48,100), function(s) acc[[paste(b, s)]])
  mono <- all(diff(a[1:4]) > 0) && a[5] < a[4]
  ok_mono <- ok_mono && mono
  cat(sprintf("%-6d %8.3f %8.3f %8.3f %8.3f %8.3f  %s\n", b, a[1],a[2],a[3],a[4],a[5],
              if (mono) "yes" else "NO"))
}
cat(sprintf("%-6s %8s %8s %8s %8s %8s\n","RT:","","","","",""))
ok_rt <- TRUE
for (b in 1:6) {
  r <- sapply(c(6,12,24,48,100), function(s) rt[[paste(b, s)]])
  m <- all(diff(r[1:4]) < 0); ok_rt <- ok_rt && m
  cat(sprintf("%-6d %8.3f %8.3f %8.3f %8.3f %8.3f  %s\n", b, r[1],r[2],r[3],r[4],r[5],
              if (m) "falls 6->48" else "NO"))
}

pass <- wa <= 5e-6 && wr <= 5e-6 && uniq && ok_mono && ok_rt
cat(if (pass) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")
