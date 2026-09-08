# Verification for kfcovid_Li2020 (#1945, batch_202).
#
# The live item codes are bare integers 1-12, which normally demands caution.
# Here they are not opaque: data/kfcovid_Li2020/"knowledge and fear of covid_
# knowledge scale.do" reshapes `Q1 Q2 ... Q12 -> Q` and renames the reshape
# index to `item`, so the integer IS the Q number, and the deposit workbook's
# Codebook sheet keys Q1..Q12 to their statements. That is the basis.
#
# This script corroborates it against the response data, which the source makes
# possible: the workbook's Survey 1 sheet publishes % Correct per item, so the
# proportion of resp == 1 must reproduce it item by item.
P <- ".cache/kfcovid_Li2020/kfcovid_pctcorrect.csv"
pub <- read.csv(P)
d <- as.data.frame(readRDS(file.path(Sys.getenv("CLAUDE_JOB_DIR"), "tmp",
                                     "b202_kfcovid_Li2020.rds")))
d$item <- as.numeric(as.character(d$item))
obs <- tapply(d$resp, d$item, function(z) mean(z == 1, na.rm = TRUE))
obs <- unname(obs[order(as.numeric(names(obs)))])

cat("=== published % correct vs observed proportion of resp == 1 ===\n")
cat(sprintf("%-5s %12s %12s %11s\n", "item", "published", "observed", "diff"))
for (k in 1:12)
    cat(sprintf("%-5d %12.6f %12.6f %11.2e\n", k, pub$pct_correct[k], obs[k],
                abs(pub$pct_correct[k] - obs[k])))
exact <- max(abs(pub$pct_correct - obs)) < 1e-9
cat(sprintf("\nmax absolute difference: %.3e -> %s\n", max(abs(pub$pct_correct - obs)),
            if (exact) "exact on all 12" else "MISMATCH"))

# What the route does NOT do. Four items share 0.990909 and two share 0.972727,
# so the percentages alone leave those groups interchangeable: 4! * 2! = 48 of
# the 479,001,600 possible orderings reproduce all twelve values. The individual
# assignment therefore rests on the Codebook keying and the .do reshape, both of
# which name the item explicitly, and not on this route.
tie <- table(round(pub$pct_correct, 6))
n_perm <- prod(factorial(as.integer(tie)))
cat(sprintf("orderings consistent with the percentages alone: %d of %s\n",
            n_perm, format(factorial(12), big.mark = ",", scientific = FALSE)))
cat("tied groups:\n")
for (v in names(tie)[tie > 1])
    cat(sprintf("  %s -> items %s\n", v,
                paste(which(round(pub$pct_correct, 6) == as.numeric(v)), collapse = ", ")))

cat("\nVERDICT:", if (exact) "PASS" else "FAIL", "\n")
