## Harrison, L., Yang, F., Franconeri, S., & Chang, R. (2014). Ranking
## visualizations of correlation using Weber's law. IEEE Transactions on
## Visualization and Computer Graphics (InfoVis), 20(12), 1943-1952.
## doi:10.1109/TVCG.2014.2346979
## Data: https://github.com/TuftsVALT/ranking-correlation, data/all_judgments.csv.
## Licence: CC BY 4.0 for the data (data/LICENSE, added 2026-11-25), granted by
## Lane Harrison by email 2026-11-25; copy in irw/licenseinfo/emails/.
## Psychophysics collection.
##
## Task: JND staircases for correlation. Two charts of the same type, one at a
## fixed correlation (rbase) and one at a varied correlation (rv); the observer
## picks the more correlated one. Nine chart types x positive/negative
## correlation, between people (one chart type and direction per person); each
## person runs 4 staircases (2 rbase values x approach from above/below),
## 24-50 judgements each. Step 0.01 down after correct, 0.03 up after wrong.
## Each trial drew a fresh random dataset at the target r, so a stimulus is
## defined by its parameters. 1,693 MTurk observers.
##
## The source README notes these judgement-level data were not used in the
## paper (which analysed the per-staircase JND, data/master.csv).
##
## rv is on the depositors' scale: the chart showed r = rv (positive
## condition) or -rv (negative condition). rv < 0 means the staircase from
## below crossed zero, so the comparison chart showed the opposite sign; rv is
## clamped at 1 at the top. Floating-point noise in rv is rounded to 0.01.
##
## Layout:
##   item = chart_direction_rbase_rv in hundredths, e.g. scatterplot_neg_b60_v67;
##     a negative rv is written with "n" (donut_neg_b30_vn14 is rv = -0.14)
##   resp = gotItRight (1 = picked the more correlated chart)
##   trial_staircase = rbase_approach (e.g. 0.60_above); trial_number =
##     judgement index within that staircase (0-49, from the source)
##   itemcov_chart, itemcov_direction, itemcov_rbase, itemcov_rv,
##   itemcov_delta = rv - rbase
## No covariates. The depositors' random 8-character ids are remapped to
## integers. The per-staircase jnd column is dropped (derived from the rows).
##
## Usage: Rscript harrison_2014_correlation_jnd.R <all_judgments.csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw <- if (length(args) >= 1) args[1] else "all_judgments.csv"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- read.csv(raw, stringsAsFactors = FALSE)
stopifnot(nrow(x) == 275976, length(unique(x$participant)) == 1693,
          all(x$gotItRight %in% c("true", "false")),
          all(x$approach %in% c("above", "below")),
          all(x$rdirection %in% c("positive", "negative")),
          all(abs(x$rv * 100 - round(x$rv * 100)) < 1e-6),
          !anyDuplicated(x[, c("participant", "rbase", "approach", "index")]))
x$rv <- round(x$rv, 2) + 0  # + 0 clears -0
rv100 <- as.integer(round(x$rv * 100))
dir <- ifelse(x$rdirection == "positive", "pos", "neg")
ids <- unique(x$participant)
d <- data.frame(
  id = match(x$participant, ids),
  item = sprintf("%s_%s_b%02d_v%s%02d", x$vis, dir, as.integer(round(x$rbase * 100)),
                 ifelse(rv100 < 0, "n", ""), abs(rv100)),
  resp = as.integer(x$gotItRight == "true"),
  trial_staircase = sprintf("%.2f_%s", x$rbase, x$approach),
  trial_number = as.integer(x$index),
  itemcov_chart = x$vis,
  itemcov_direction = x$rdirection,
  itemcov_rbase = x$rbase,
  itemcov_rv = x$rv,
  itemcov_delta = (rv100 - as.integer(round(x$rbase * 100))) / 100,
  stringsAsFactors = FALSE)
d <- d[order(d$id, d$trial_staircase, d$trial_number), ]
table <- "harrison_2014_correlation_jnd"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
## check: item and resp line up with the staircase rule (|delta| steps down
## 0.01 after a correct judgement, up 0.03 after a wrong one; the remainder
## are clamps at r = 1 and at the smallest delta)
k <- paste(d$id, d$trial_staircase)
nx <- c(k[-1] == k[-length(k)], FALSE)
step <- round(c(abs(d$itemcov_delta)[-1], NA) - abs(d$itemcov_delta), 2)
cat(sprintf("step rule followed: correct %.3f, wrong %.3f\n",
            mean(step[nx & d$resp == 1] == -0.01), mean(step[nx & d$resp == 0] == 0.03)))
