# verify_xiao_2024_taking_charge.R -- batch_413, Step 5b.
#
# Claim: TC1..TC4 are Part III items 1..4 of questionnaire (II) (S1 File Chinese /
# S2 File English), and resp 1..5 runs 非常不频繁 (Very Infrequently) .. 非常频繁 (Very frequently).
#
# What this CAN test:
#  (P) the live TC items are the deposit's TC1..TC4 columns (per-item resp counts match
#      the S1 Dataset xlsx cell for cell) -- plumbing, stated for completeness only.
#  (D) option direction: TC scale mean vs the paper's Table 2 (M 3.790, SD 0.992,
#      r with hierarchical plateau -0.525, r with work engagement +0.447, N=286). A reversed
#      resp axis would flip both correlation signs and put the mean near 2.2.
# What this CANNOT test: which TC item is which. The paper publishes no per-item
# statistics, the four items share one 1-5 range and one polarity, and there are no
# subscales. Item identity rests on the questionnaire numbering 1-4 matching the
# deposit's TC1-TC4 column suffixes (and on Parker & Collins' published order, which is
# the same). Status: NO_ROUTE for item identity.

suppressMessages(library(irw))
TABLE <- "xiao_2024_taking_charge"
d <- irw::irw_fetch(TABLE)

tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0315916.s001",
              tf, mode = "wb", quiet = TRUE)
x <- as.data.frame(readxl::read_excel(tf))

ok <- TRUE
cat("(P) per-item resp counts, live vs deposit column\n")
for (it in paste0("TC", 1:4)) {
  live <- as.integer(table(factor(d$resp[d$item == it], levels = 1:5)))
  dep  <- as.integer(table(factor(x[[it]], levels = 1:5)))
  cat(sprintf("  %s live %-22s deposit %s\n", it, paste(live, collapse = "/"), paste(dep, collapse = "/")))
  if (!identical(live, dep)) ok <- FALSE
}

tc <- rowMeans(x[, paste0("TC", 1:4)])
hp <- rowMeans(x[, paste0("HP", 1:4)])
we <- rowMeans(x[, paste0("WE", 1:9)])
r_hp <- cor(tc, hp); r_we <- cor(tc, we)
cat(sprintf("\n(D) TC scale: mean %.3f SD %.3f (paper 3.790 / 0.992, N=286; deposit N=%d)\n",
            mean(tc), sd(tc), nrow(x)))
cat(sprintf("    r(TC,HP) %.3f (paper -0.525); r(TC,WE) %.3f (paper +0.447)\n", r_hp, r_we))
if (abs(mean(tc) - 3.790) > 0.1 || r_hp > -0.4 || r_we < 0.3) ok <- FALSE

cat("\nNOT ESTABLISHED: which item is which -- no per-item statistics are published;",
    "item identity is NO_ROUTE and rests on questionnaire numbering 1-4 = TC1-TC4.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
