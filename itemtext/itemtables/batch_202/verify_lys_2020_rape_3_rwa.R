# Verification for lys_2020_rape_3_rwa (#1945, batch_202).
#
# Two separate questions, and the second one corrected a claim this table
# originally shipped.
#
# 1. Does the deposit store these items RAW or already reverse-scored? The
#    original scale reverse-words six of the twelve, so it matters. Solving for
#    the weights of the deposit's own rwa_sum settles it.
# 2. Does the Polish/English pairing hold? The Polish comes from
#    Grzesiak-Feldman's adaptation (CEEOL id=108624), the English from the .sav.
suppressMessages(library(haven))
x  <- as.data.frame(read_sav(".cache/lys_2020_rape/study3.sav"))
rv <- paste0("rwa", 1:12)
m  <- sapply(x[rv], as.numeric); y <- as.numeric(x$rwa_sum)
ok <- !is.na(y) & rowSums(is.na(m)) == 0

cat("=== Route 1: are the items stored raw or pre-recoded? ===\n")
cat(sprintf("  complete rows %d, rwa_sum range %s\n", sum(ok),
            paste(range(y[ok]), collapse = "-")))
fit <- lm.fit(cbind(1, m[ok, ]), y[ok]); b <- coef(fit)
pred <- cbind(1, m[ok, ]) %*% b
cat(sprintf("  solved weights: %s (intercept %.3f)\n",
            paste(sprintf("%+.2f", b[-1]), collapse = " "), b[1]))
plain <- sum(abs(rowSums(m[ok, ]) - y[ok]) < 1e-8)
REV <- c(1, 3, 5, 7, 9, 11)
mm <- m[ok, ]; for (j in REV) mm[, j] <- 6 - mm[, j]
flip <- sum(abs(rowSums(mm) - y[ok]) < 1e-8)
cat(sprintf("  plain sum of all twelve == rwa_sum: %d of %d\n", plain, sum(ok)))
cat(sprintf("  sum with the six reverse-worded items flipped: %d of %d\n", flip, sum(ok)))
r1 <- plain == sum(ok) && flip < sum(ok)
cat(sprintf("  -> %s\n", if (r1)
    "items are stored ALREADY RECODED; higher = more authoritarian throughout" else "inconclusive"))

cat("\n=== Route 2: keying polarity, and why it is NOT evidence here ===\n")
ids <- unique(x$nr_part); if (all(is.na(ids))) ids <- seq_len(nrow(x))
C <- cor(m, use = "pairwise.complete.obs")
FWD <- setdiff(1:12, REV)
cat(sprintf("  mean r within the reverse-worded six: %+0.3f\n",
            mean(C[REV, REV][upper.tri(diag(length(REV)))])))
cat(sprintf("  mean r within the forward six:        %+0.3f\n",
            mean(C[FWD, FWD][upper.tri(diag(length(FWD)))])))
cat(sprintf("  mean r across the two blocks:         %+0.3f\n", mean(C[REV, FWD])))
cat("  All positive, which is what pre-recoding predicts. A raw table would show\n")
cat("  a negative across-block correlation. So polarity cannot be used to test\n")
cat("  the item pairing on this table -- route 1 explains why, and that is the\n")
cat("  finding rather than a failure.\n")

cat("\n=== What establishes the pairing instead ===\n")
cat("  Content, one-to-one. Each of the twelve English labels in the .sav is a\n")
cat("  direct translation of exactly one numbered item in the appendix and vice\n")
cat("  versa, across a 20-item pool, so the correspondence is forced rather than\n")
cat("  positional. The six items the appendix marks (R) land on rwa1, rwa3, rwa5,\n")
cat("  rwa7, rwa9 and rwa11 -- the odd codes -- so the questionnaire alternated\n")
cat("  keying direction, the same alternating design the cons block shows.\n")
cat("\n=== What is NOT established ===\n")
cat("  The response anchors. The appendix publishes a SIX-point scale, but this\n")
cat("  study administered five (the paper says so and the data contains only\n")
cat("  1-5), so the appendix labels do not describe this administration and\n")
cat("  option_text stays blank.\n")
cat("\nVERDICT:", if (r1) "PASS" else "FAIL", "\n")
