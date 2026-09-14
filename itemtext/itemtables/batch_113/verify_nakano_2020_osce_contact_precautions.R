# verify_nakano_2020_osce_contact_precautions.R
#
# CLAIM UNDER TEST: item_text for ContPrec_1..ContPrec_15 is the checklist item
# printed with that same number in Table 1 of Nagoshi et al. (2019),
# J Educ Eval Health Prof 16:31 (doi:10.3352/jeehp.2019.16.31).
#
# FALSIFIABLE PREDICTION: the paper publishes per-item % correct for
#   (a) cohort 2 pretest, OSCE 1  = the IRW table's wave 1 (n=144), Table 1 "Pretest"
#   (b) cohort 2 posttest, OSCE 2 (n=144), Table 1 "Posttest"
#   (c) cohort 1 OSCE (n=125), Table 2 "Cohort 1"
# IRW wave 2 pools (b) and (c) (269 records), so the prediction for wave 2 is the
# n-weighted mean of the two published columns. If any two items' texts were
# swapped, these per-item proportions would swap with them.
#
# Items 2 and 9 sit at 1.000 in every published column and at 1.00 in the live
# data, so this route CANNOT distinguish them from each other. Everything else is
# separated: notably ContPrec_1 vs ContPrec_10 tie in both wave-1 (.903) and
# posttest (.965) columns but split sharply in cohort 1 (.97 vs .78), which the
# pooled wave-2 comparison exercises.

suppressMessages(library(irw))
TABLE <- "nakano_2020_osce_contact_precautions"

pre  <- c(0.903,1.000,0.986,0.826,0.972,0.889,0.708,0.868,1.000,0.903,0.507,0.792,0.993,0.868,0.486)  # Table 1 pretest,  n=144
post <- c(0.965,1.000,1.000,0.993,1.000,0.951,0.924,0.938,1.000,0.965,0.924,0.951,1.000,0.951,0.750)  # Table 1 posttest, n=144
coh1 <- c(0.97, 1.00, 0.97, 0.95, 0.96, 0.97, 0.81, 0.94, 1.00, 0.78, 0.79, 0.90, 0.98, 0.86, NA)      # Table 2 cohort 1, n=125 (item 15 not reported)
items <- paste0("ContPrec_", 1:15)

d <- irw::irw_fetch(TABLE)
w1 <- d[d$wave == 1, ]; w2 <- d[d$wave == 2, ]
m1 <- tapply(w1$resp, w1$item, mean)[items]
m2 <- tapply(w2$resp, w2$item, mean)[items]
n1 <- tapply(w1$resp, w1$item, length)[items]
n2 <- tapply(w2$resp, w2$item, length)[items]

pool <- (125 * coh1 + 144 * post) / 269   # predicted wave-2 pooled proportion

cat(sprintf("wave 1 n = %s ; wave 2 n = %s\n\n", paste(unique(n1), collapse=","), paste(unique(n2), collapse=",")))
cat(sprintf("%-12s %9s %9s %7s | %9s %9s %7s\n",
            "item", "pub_pre", "obs_w1", "diff", "pub_pool", "obs_w2", "diff"))
ok <- TRUE
for (i in seq_along(items)) {
  d1 <- m1[i] - pre[i]
  d2 <- if (is.na(pool[i])) NA_real_ else m2[i] - pool[i]
  cat(sprintf("%-12s %9.3f %9.3f %7.3f | %9s %9.3f %7s\n", items[i], pre[i], m1[i], d1,
              ifelse(is.na(pool[i]), "  --", sprintf("%9.3f", pool[i])), m2[i],
              ifelse(is.na(d2), "  --", sprintf("%7.3f", d2))))
  if (abs(d1) > 0.005) ok <- FALSE
  if (!is.na(d2) && abs(d2) > 0.010) ok <- FALSE
}

cat("\nTie-break check, ContPrec_1 vs ContPrec_10 (identical in both n=144 columns):\n")
cat(sprintf("  predicted pooled  1 = %.3f, 10 = %.3f\n", pool[1], pool[10]))
cat(sprintf("  observed  wave 2  1 = %.3f, 10 = %.3f\n", m2[1], m2[10]))
sep <- abs(m2[1] - m2[10]) > 0.05 && (m2[1] > m2[10]) == (pool[1] > pool[10])
cat(sprintf("  separated in the predicted direction: %s\n", sep))
if (!sep) ok <- FALSE

cat("\nNOT ESTABLISHED by this route: ContPrec_2 and ContPrec_9 are at 1.000 in every\n")
cat("published column and at 1.00 in the live data, so a swap between those two\n")
cat("items would be invisible here. Their mapping rests on the paper's item\n")
cat("numbering matching the source file's ContPrec1..15 column numbering.\n")

cat(if (ok) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")
