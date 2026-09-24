# verify_germann_2026_state_intervention.R -- Step 5b mapping check (copied from verify_template.R)
#
# Claim: statint1 = "The railways should be under public ownership." (VAA statement q12) and
# statint2 = "Private sector involvement in the NHS should be reduced." (VAA statement q18),
# both stored raw (1 = Completely disagree .. 5 = Completely agree). Table S2.20 of the SI
# lists railways first and NHS second; the authors' Study2_Appendix_TablesS2_18-S2_23.R builds
# the 2017 state-intervention scale as data2017[, c("q12","q18")] in that order.
#
# Route A (response-frequency matching): live per-item level counts vs all 30 VAA statements
#   in the deposit's Scaling2017.tab, raw and reversed (60 candidates). statint1 must match
#   only q12 and statint2 only q18. Ties each code to one VAA column, and pins direction.
# Route B (published scale statistics, SI Table S2.20): Hi = 0.53 / 0.53, H = 0.53,
#   alpha = 0.65, N = 73931 recomputed on live complete cases. Pins membership + direction.
# Route C (polarity): agreement with both statements (both left-leaning) should correlate
#   negatively with cov_lr (0 = Left .. 10 = Right).
#
# NOT established: which of q12/q18 is the railways statement vs the NHS statement. That rests
# on the authors' script order matching Table S2.20's order -- a convention confirmed
# independently on the sibling immigration/redistribution/environment scales, but not testable
# here: with two same-direction items, Hi are necessarily equal and no published per-item
# statistic separates them. Hence PARTIAL in the ledger even though this script PASSes.

suppressMessages(library(irw))
TABLE <- "germann_2026_state_intervention"
d <- as.data.frame(irw::irw_fetch(TABLE))
live <- lapply(split(d$resp, d$item), function(v) tabulate(v, 5))
cat("live statint1 counts 1..5:", live$statint1, "\n")
cat("live statint2 counts 1..5:", live$statint2, "\n\n")

tf <- tempfile(fileext = ".csv")
download.file("https://dataverse.harvard.edu/api/access/datafile/13400018?format=original",
              tf, quiet = TRUE, mode = "wb")
s <- read.csv(tf)
qs <- grep("^q[0-9]+(rev)?$", names(s), value = TRUE)
cand <- lapply(qs, function(q) tabulate(s[[q]][!is.na(s[[q]])], 5)); names(cand) <- qs

ok <- TRUE
for (it in c("statint1", "statint2")) {
  hits <- names(cand)[vapply(cand, function(x) identical(x, live[[it]]), logical(1))]
  want <- if (it == "statint1") "q12" else "q18"
  cat(sprintf("%s exact count match among %d candidates: %s (expected %s: %s)\n", it,
              length(cand), if (length(hits)) paste(hits, collapse = ",") else "NONE",
              want, paste(cand[[want]], collapse = " ")))
  if (!identical(hits, want)) ok <- FALSE
}

# Route B
x <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
cc <- na.omit(x[, c("resp.statint1", "resp.statint2")])
n <- nrow(cc)
a <- cc[[1]]; b <- cc[[2]]
covab <- cov(a, b)
# Loevinger H for two items: cov / max cov given marginals
covmax <- cov(sort(a), sort(b))
H <- covab / covmax
alpha <- 2 * (1 - (var(a) + var(b)) / var(a + b))
cat(sprintf("\nTable S2.20 published: Hi 0.53/0.53, H 0.53, alpha 0.65, N 73931\n"))
cat(sprintf("live complete cases:    H %.3f, alpha %.3f, N %d\n", H, alpha, n))
if (!(abs(H - 0.53) < 0.006 && abs(alpha - 0.65) < 0.006 && n == 73931)) ok <- FALSE

# Route C
w <- unique(d[, c("id", "cov_lr")])
for (it in c("statint1", "statint2")) {
  m <- merge(d[d$item == it, c("id", "resp")], w, by = "id")
  r <- cor(m$resp, as.numeric(m$cov_lr), use = "pair")
  cat(sprintf("cor(%s, cov_lr right) = %+.3f (expect < 0)\n", it, r))
  if (!(r < -0.1)) ok <- FALSE
}

cat("\nNot established: railways-vs-NHS assignment between q12 and q18 rests on the authors'\n",
    "script order = SI table order; no route here separates the two items' wording.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
