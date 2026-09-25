# verify_xiao_2024_hierarchical_plateau.R -- batch_413, Step 5b.
# Copied from references/verify_template.R.
#
# Claim: HP1..HP4 = Part II items 1..4 of the study's questionnaire (I)
# (S1 File Chinese / S2 File English, PLOS ONE 10.1371/journal.pone.0315916),
# and resp 1..5 = 非常不符合 (Strongly disagree) .. 非常符合 (Strongly agree).
#
# What this CAN check:
#  (P) the live item codes are the S1 Dataset xlsx column names HP1..HP4
#      (per-item resp counts identical, live vs deposit) -- i.e. no rename.
#  (D) the option axis: scale mean in the raw direction matches the published
#      M = 2.375 (n=286; reversed it would be 3.625), and the HP scale correlates
#      negatively with taking charge and work engagement as published
#      (r = -0.525, -0.477).
#  (K) no item is reverse-keyed: every corrected item-total r is positive.
# What this does NOT establish: WHICH item is which. The paper publishes no
# per-item statistics, all four items share one 1-5 range, one subscale, one
# polarity, and near-synonymous content. Item identity rests on the codes'
# numbering matching the questionnaire's numbering 1-4. Item order: NO_ROUTE.

suppressMessages(library(irw))
TABLE <- "xiao_2024_hierarchical_plateau"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0315916.s001"

d <- as.data.frame(irw::irw_fetch(TABLE))
tmp <- tempfile(fileext = ".xlsx")
download.file(SI, tmp, mode = "wb", quiet = TRUE)
x <- as.data.frame(readxl::read_excel(tmp))

ok <- TRUE
cat("(P) per-item resp counts, live vs deposit xlsx column of the same name\n")
for (it in paste0("HP", 1:4)) {
  live <- table(factor(d$resp[d$item == it], levels = 1:5))
  dep  <- table(factor(x[[it]], levels = 1:5))
  same <- all(live == dep)
  cat(sprintf("  %s live %s | xlsx %s  %s\n", it, paste(live, collapse = "/"),
              paste(dep, collapse = "/"), if (same) "match" else "MISMATCH"))
  ok <- ok && same
}

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
hp <- w[, paste0("resp.HP", 1:4)]
m <- mean(rowMeans(hp, na.rm = TRUE))
cat(sprintf("\n(D) HP scale mean, live n=%d: %.3f (published 2.375, n=286; reversed would be %.3f)\n",
            nrow(hp), m, 6 - m))
okD1 <- abs(m - 2.375) < 0.15
hpx <- rowMeans(x[, paste0("HP", 1:4)])
tc <- rowMeans(x[, paste0("TC", 1:4)], na.rm = TRUE)
we <- rowMeans(x[, paste0("WE", 1:9)], na.rm = TRUE)
r_tc <- cor(hpx, tc); r_we <- cor(hpx, we)
cat(sprintf("    corr(HP, taking charge) = %.3f (published -0.525); corr(HP, work engagement) = %.3f (published -0.477)\n",
            r_tc, r_we))
okD2 <- r_tc < -0.3 && r_we < -0.3
ok <- ok && okD1 && okD2

cat("\n(K) corrected item-total r (all must be positive: no reverse-keyed item)\n")
for (i in 1:4) {
  r <- cor(hp[[i]], rowSums(hp[, -i]), use = "complete.obs")
  cat(sprintf("  HP%d %.3f\n", i, r)); ok <- ok && r > 0
}
cat("\nNOT ESTABLISHED: which of HP1..HP4 carries which wording (no per-item statistics published).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
