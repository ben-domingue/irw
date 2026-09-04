# verify_dd_rotation.R -- Step 5b mapping check for dd_rotation.
#
# CLAIM UNDER TEST: the live IRW item codes "1".."10" are column X[i] / T[i] of
# diffIRT::rotation, and the rotation angle shipped as item_text for item i is
# the angle diffIRT's rotation.Rd lists for "item i".
#
# Route A (re-run the processing script, core model section 3). data/diffIRT_dat.R
# assigns item <- 1:ncol(rt) over rotation[,1:10] / rotation[,11:20] and drops rows
# with missing rt. Re-running that over the CRAN source (diffIRT 1.5,
# data/rotation.rda) yields a per-item n, mean response time and proportion correct
# for each source column; these are hard-coded below and compared to the live table.
# An exact match column-by-column pins EVERY item to EVERY other item, because the
# ten columns' rt means are all distinct (2.32 .. 3.84, min gap 0.054 s).
#
# Route B (semantic coherence, route 8) checks the OTHER half -- that Rd "item i"
# is column X[i] -- via the mental-rotation effect: larger angular disparity should
# mean slower and less accurate responses. This separates the 50-degree class from
# the rest; it does NOT separate 100 from 150 (see printed output).

suppressMessages(library(irw))

TABLE <- "dd_rotation"

# Recomputed from CRAN diffIRT 1.5 data/rotation.rda, columns X[1..10] / T[1..10],
# restricted to rows with non-missing rt (exactly what data/diffIRT_dat.R keeps).
SRC_N   <- c(120, 118, 119, 114, 119, 119, 119, 120, 118, 112)
SRC_RT  <- c(3.1572750000, 2.8714915254, 3.3652184874, 3.7890877193, 2.5216302521,
             2.6639159664, 3.0800924370, 2.3246083333, 2.9623898305, 3.8430089286)
SRC_ACC <- c(0.8500000000, 0.9237288136, 0.8655462185, 0.7719298246, 0.9327731092,
             0.8907563025, 0.9075630252, 0.9666666667, 0.8813559322, 0.8571428571)
# Angles as shipped in item_text, from diffIRT's rotation.Rd \format block.
ANGLE   <- c(150, 50, 100, 150, 50, 100, 150, 50, 150, 100)

d <- irw::irw_fetch(TABLE)          # 1,178 rows -- negligible against the export cap
d$resp <- as.numeric(d$resp)
d$rt   <- as.numeric(d$rt)
k <- as.character(1:10)
obs_n   <- as.numeric(tapply(d$resp, d$item, length)[k])
obs_rt  <- as.numeric(tapply(d$rt,   d$item, mean)[k])
obs_acc <- as.numeric(tapply(d$resp, d$item, mean)[k])

cat("Route A -- re-run of data/diffIRT_dat.R over CRAN diffIRT 1.5 rotation.rda\n")
cat(sprintf("%-5s %5s %5s %12s %12s %10s %10s %10s\n",
            "item", "n_src", "n_live", "rt_src", "rt_live", "acc_src", "acc_live", "angle"))
for (i in 1:10)
  cat(sprintf("%-5s %5d %5d %12.7f %12.7f %10.6f %10.6f %10d\n",
              k[i], SRC_N[i], obs_n[i], SRC_RT[i], obs_rt[i],
              SRC_ACC[i], obs_acc[i], ANGLE[i]))

d_n   <- max(abs(SRC_N   - obs_n))
d_rt  <- max(abs(SRC_RT  - obs_rt))
d_acc <- max(abs(SRC_ACC - obs_acc))
cat(sprintf("\nmax |diff|: n=%g  mean_rt=%.3e  acc=%.3e\n", d_n, d_rt, d_acc))
gaps <- min(diff(sort(SRC_RT)))
cat(sprintf("smallest gap between any two source rt means: %.4f s -- so the match is item-distinguishing\n", gaps))

cat("\nRoute B -- mental-rotation effect against the shipped angles\n")
for (a in c(50, 100, 150))
  cat(sprintf("  %3d deg (items %s): mean rt = %.3f s, prop correct = %.3f\n",
              a, paste(k[ANGLE == a], collapse = ","),
              mean(obs_rt[ANGLE == a]), mean(obs_acc[ANGLE == a])))
cat(sprintf("  Spearman rho(angle, item mean rt)  = %+.3f\n",
            suppressWarnings(cor(ANGLE, obs_rt,  method = "spearman"))))
cat(sprintf("  Spearman rho(angle, item accuracy) = %+.3f\n",
            suppressWarnings(cor(ANGLE, obs_acc, method = "spearman"))))
cat("  Accuracy falls monotonically across the three angle classes; rt separates 50 deg\n",
    "  from the rest but 100 and 150 overlap. Route B therefore corroborates the angle\n",
    "  assignment at CLASS level only -- it does not fix which 150-degree item is which,\n",
    "  and no data route can, since the Rd is the only statement of per-item angle.\n", sep = "")

ok <- (d_n == 0) && (d_rt < 1e-9) && (d_acc < 1e-9) &&
      all(diff(c(mean(obs_acc[ANGLE == 150]), mean(obs_acc[ANGLE == 100]),
                 mean(obs_acc[ANGLE == 50]))) > 0)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
