# verify_humor_styles.R -- Step 5b mapping check for `humor_styles`.
#
# CLAIM UNDER TEST: IRW item i (a bare integer 1..32) is column Qi of the
# openpsychometrics HSQ deposit (http://openpsychometrics.org/_rawdata/HSQ.zip),
# whose codebook.txt prints the verbatim statement for each Q-code. The IRW code
# is a script-generated integer -- data/humor_styles.R assigns it with
# row_number() over unique(item) after pivot_longer -- so nothing in the live
# table names its source column and the tie has to be re-derived.
#
# The falsifiable prediction: per-item n of non-missing responses and per-item
# mean, computed from the RAW deposit column Qi, must equal the live values for
# item i. The 32 (n, mean) signatures are all distinct, so ANY permutation of
# the mapping -- including a swap of two adjacent items -- breaks this.
#
# Raw values are hard-coded (computed from HSQ/data.csv, -1 treated as missing
# exactly as data/humor_styles.R does) so the script needs no network but Redivis.

suppressMessages(library(irw))

TABLE <- "humor_styles"

# Q1..Q32 of HSQ/data.csv: n non-missing, and mean of non-missing responses.
RAW_N <- c(1068, 1068, 1069, 1070, 1069, 1069, 1069, 1064, 1067, 1068, 1069, 1069,
           1069, 1067, 1064, 1066, 1058, 1065, 1067, 1065, 1063, 1064, 1063, 1064,
           1061, 1062, 1066, 1067, 1065, 1063, 1064, 1068)
RAW_MEAN <- c(2.033708, 3.354869, 3.086062, 2.837383, 3.608045, 4.161833, 3.285313,
              2.558271, 2.596064, 2.880150, 2.747428, 2.972872, 4.450889, 3.282099,
              3.401316, 3.119137, 1.950851, 2.769953, 3.259606, 2.112676, 4.398871,
              3.046992, 2.793039, 2.425752, 1.567389, 3.552731, 2.282364, 3.221181,
              2.339906, 3.983067, 2.792293, 2.849251)
TOL <- 1e-5

# Distinctness of the signature is what makes this a mapping test rather than a
# consistency check -- state it in numbers, don't assert it.
sig <- paste(RAW_N, sprintf("%.6f", RAW_MEAN))
cat(sprintf("distinct (n, mean) signatures among the 32 raw columns: %d/32\n\n",
            length(unique(sig))))

d <- irw::irw_fetch(TABLE)          # 34,272 rows -- a trivial export
d <- d[!is.na(d$resp), ]
live_n <- tapply(d$resp, as.character(d$item), length)
live_m <- tapply(d$resp, as.character(d$item), mean)

cat(sprintf("%-6s %-6s %8s %8s %12s %12s %10s\n",
            "item", "srccol", "raw_n", "live_n", "raw_mean", "live_mean", "diff"))
ok <- TRUE
for (i in 1:32) {
    k <- as.character(i)
    ln <- live_n[[k]]; lm <- live_m[[k]]
    dif <- lm - RAW_MEAN[i]
    cat(sprintf("%-6s %-6s %8d %8d %12.6f %12.6f %10.6f\n",
                k, paste0("Q", i), RAW_N[i], ln, RAW_MEAN[i], lm, dif))
    if (ln != RAW_N[i] || abs(dif) > TOL) ok <- FALSE
}

cat(sprintf("\nworst |mean| deviation: %.2e (tolerance %.0e)\n",
            max(abs(sapply(1:32, function(i) live_m[[as.character(i)]] - RAW_MEAN[i]))), TOL))

# What this does and does not establish.
cat("Establishes: every one of the 32 live item codes is tied to a unique raw\n",
    "deposit column, and hence to that column's codebook statement. No item is\n",
    "left interchangeable with another.\n",
    "Does not establish: that the codebook's Q-numbering matches the 2003 JRP\n",
    "article's published item order -- irrelevant here, since the wording ships\n",
    "from the codebook itself rather than from the article.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
