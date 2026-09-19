# Verification for gilbert_meta_69 (#1945, batch_203).
#
# This is the Haryana arm of Banerjee et al. Its own file, haryana_analysis.dta,
# names the variables and labels them with the QUESTION NUMBER only ("Written
# Math ..."), not the task. The task wording is bridged from the study's own
# UTK/BH dictionary by question number, and that bridge is what needs testing.
#
# Route 1: the question-number sets must correspond exactly.
# Route 2: task families must cluster in difficulty. Items sharing one task
#   description are the same task, so their proportion-correct should be more
#   alike than chance. If the bridge attached the wrong descriptions, that
#   clustering would disappear. Tested against a permutation null.
set.seed(203)
dic <- read.csv(file.path(".cache/gilbert_meta_73", "b203_hary_math.csv"), stringsAsFactors = FALSE)
dic$ask <- trimws(gsub("\\s+", " ", dic$ask))
d <- as.data.frame(readRDS(file.path(Sys.getenv("CLAUDE_JOB_DIR"), "tmp", "b203_gilbert_meta_69.rds")))
d$item <- as.character(d$item)

cat("=== Route 1: question-number correspondence ===\n")
same <- setequal(unique(d$item), dic$code)
cat(sprintf("  dictionary %d codes, live %d, identical: %s\n", nrow(dic),
            length(unique(d$item)), same))
cat(sprintf("  every code present at both waves: %s\n",
            all(sapply(dic$code, function(c) length(unique(d$wave[d$item == c])) == 2))))
cat("  (so wave availability has no discriminating power on this table)\n")

cat("\n=== Route 2: do task families cluster in difficulty? ===\n")
p <- sapply(dic$code, function(c) mean(d$resp[d$item == c] == 1, na.rm = TRUE))
fam <- dic$ask
sizes <- table(fam)
multi <- names(sizes)[sizes > 1]
stat <- function(g) {
    v <- c()
    for (f in multi) { idx <- which(g == f); if (length(idx) > 1) v <- c(v, var(p[idx])) }
    mean(v)
}
obs  <- stat(fam)
null <- replicate(4000, stat(sample(fam)))
pv   <- (1 + sum(null <= obs)) / (1 + length(null))
cat(sprintf("  %d task families, %d of them with more than one item\n",
            length(sizes), length(multi)))
cat(sprintf("  mean within-family variance of p-correct: observed %.5f\n", obs))
cat(sprintf("  same-sized random groupings (4000): mean %.5f, min %.5f\n",
            mean(null), min(null)))
cat(sprintf("  permutation p = %.4f  (lower observed variance = tighter clustering)\n", pv))
r2 <- pv < 0.05
cat(sprintf("  -> %s\n", if (r2) "families cluster far more tightly than chance" else "no clustering detected"))

cat("\n=== per-family difficulty, for a human read ===\n")
for (f in names(sort(sapply(names(sizes), function(f) mean(p[fam == f]))))) {
    idx <- which(fam == f)
    cat(sprintf("  %-52s n=%d  p-correct %.3f\n", substr(f, 1, 52), length(idx), mean(p[idx])))
}

cat("\n=== What this does NOT establish ===\n")
cat("  Which item within a task family is which -- family members share one\n")
cat("  description, so they are interchangeable here. Nor does it prove Haryana\n")
cat("  used the identical printed form; no Haryana test instrument is deposited,\n")
cat("  and the bridge rests on the question numbering matching exactly. PARTIAL.\n")
cat("\nVERDICT:", if (same && r2) "PASS" else "FAIL", "\n")
