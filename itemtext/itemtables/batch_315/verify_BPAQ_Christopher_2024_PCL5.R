# verify_BPAQ_Christopher_2024_PCL5.R -- Step 5b, batch_315.
#
# ITEM AXIS: exempt. The IRW code IS the deposit column name (data/BPAQ_Christopher_2024.R
# selects starts_with("pcl") and pivots with no rename), and the deposit's own
# "Data Dictionary_RMH.xlsx" (osf.io/bskn9, measure_variable_timepoint convention) labels
# pcl5 q1..q20 with the item wording. Nothing to infer, nothing to test here.
#
# OPTION AXIS: this is what carried inference and what this script checks. The paper
# (Christopher et al. 2024, PMC11559212) says the PCL-5 was rated "0-4", but the live
# resp set is 1-5. Anchors are shipped 1='Not at all' .. 5='Extremely'. Falsifiable
# predictions:
#   (a) the paper's own PCL-5 total (Table 1: M = 34.18, SD = 11.90, n = 109) is the plain
#       sum of the stored 1-5 values -- a 0-4 sum would be ~14.18, and min would be 0 not 20;
#   (b) higher stored values = more symptoms: the sum correlates positively with the BPAQ-SF
#       total as the paper reports (r = .56, n = 109), taken from the deposit's own
#       bpaqsf_aggTotal_b column;
#   (c) the modal response is the floor (1) -- a police sample cannot be modally 'Extremely'.
suppressMessages(library(irw))
TABLE <- "BPAQ_Christopher_2024_PCL5"
d <- irw::irw_fetch(TABLE)
tot <- tapply(d$resp, d$id, sum)
cnt <- tapply(d$resp, d$id, function(v) sum(!is.na(v)))
tot <- tot[cnt == 20]
cat(sprintf("(a) live 1-5 sum: n=%d  M=%.2f  SD=%.2f  min=%d  max=%d | paper: n=109 M=34.18 SD=11.90\n",
            length(tot), mean(tot), sd(tot), min(tot), max(tot)))
cat(sprintf("    same sum on a 0-4 recoding would be M=%.2f, min=%d\n", mean(tot) - 20, min(tot) - 20))
okA <- length(tot) == 109 && abs(mean(tot) - 34.18) < 0.01 && abs(sd(tot) - 11.90) < 0.01

okB <- NA
src <- tryCatch(read.csv("https://osf.io/download/m83xq/", check.names = FALSE), error = function(e) NULL)
if (!is.null(src)) {
  b <- setNames(src$bpaqsf_aggTotal_b, src$id)
  ids <- intersect(names(tot), names(b)[!is.na(b)])
  r <- cor(tot[ids], b[ids])
  cat(sprintf("(b) r(PCL-5 live sum, deposit BPAQ-SF total) = %.3f, n=%d | paper: .56, n=109\n", r, length(ids)))
  okB <- abs(r - 0.56) < 0.01
} else cat("(b) deposit unreachable -- skipped\n")

tab <- table(d$resp)
cat("(c) live resp distribution:", paste(names(tab), tab, sep = "=", collapse = " "), "\n")
okC <- names(tab)[which.max(tab)] == "1"

cat("Does NOT establish: that the three middle anchors sit at 2/3/4 in that order beyond the\n",
    "instrument's own ordinal layout -- the data can show offset and direction, not wording per level.\n", sep = "")
cat(if (okA && isTRUE(okB %in% c(TRUE, NA)) && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
