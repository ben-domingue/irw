# verify_germann_2026_environment.R -- Step 5b mapping check (copied from verify_template.R)
#
# Claim: env1 = "The government should allow ... fracking." (VAA statement q17, stored
# REVERSED, i.e. env1 = 6 - q17), and env2 = "The UK should continue to meet the EU's green
# energy targets." (VAA statement q26, stored raw). Table S2.22 of the supplement lists the
# two statements in that order; the authors' Study2_Appendix_TablesS2_18-S2_23.R builds the
# 2017 environment scale as data2017[, c("q17rev","q26")] in the same order.
#
# Route 1 (response-frequency matching): live per-item level counts are compared against
#   every one of the 30 VAA statements in the deposit's Scaling2017.tab, raw and reversed
#   (60 candidates). The mapping holds only if env1 matches q17rev and env2 matches q26
#   uniquely and exactly.
# Route 2 (keying polarity, content-based): agreement with "allow fracking" should track the
#   political right; agreement with "meet EU green targets" should track the left. With
#   cov_lr (0 = Left .. 10 = Right), raw agreement is recovered from the stored codes.

suppressMessages(library(irw))
TABLE <- "germann_2026_environment"

d <- as.data.frame(irw::irw_fetch(TABLE))
live <- lapply(split(d$resp, d$item), function(v) tabulate(v, 5))
cat("live env1 counts 1..5:", live$env1, "\n")
cat("live env2 counts 1..5:", live$env2, "\n\n")

# Scaling2017.tab (Harvard Dataverse doi:10.7910/DVN/ALYGQS, file id 13400018)
tf <- tempfile(fileext = ".csv")
download.file("https://dataverse.harvard.edu/api/access/datafile/13400018?format=original",
              tf, quiet = TRUE, mode = "wb")
s <- read.csv(tf)
qs <- grep("^q[0-9]+(rev)?$", names(s), value = TRUE)
cand <- lapply(qs, function(q) tabulate(s[[q]][!is.na(s[[q]])], 5)); names(cand) <- qs

ok <- TRUE
for (it in c("env1", "env2")) {
  hits <- names(cand)[vapply(cand, function(x) identical(x, live[[it]]), logical(1))]
  cat(sprintf("%s exact count match among %d candidates: %s\n", it, length(cand),
              if (length(hits)) paste(hits, collapse = ",") else "NONE"))
  want <- if (it == "env1") "q17rev" else "q26"
  cat(sprintf("   expected %s: counts %s\n", want, paste(cand[[want]], collapse = " ")))
  if (!identical(hits, want)) ok <- FALSE
}

# Route 2
w <- unique(d[, c("id", "cov_lr")])
agree <- function(it) {  # raw agreement 1 = completely disagree .. 5 = completely agree
  x <- d[d$item == it, c("id", "resp")]
  if (it == "env1") x$resp <- 6 - x$resp
  m <- merge(x, w, by = "id"); cor(m$resp, as.numeric(m$cov_lr), use = "pair")
}
r1 <- agree("env1"); r2 <- agree("env2")
cat(sprintf("\ncor(agreement with fracking statement [6-env1], cov_lr right) = %+.3f (expect > 0)\n", r1))
cat(sprintf("cor(agreement with EU green targets [env2], cov_lr right)     = %+.3f (expect < 0)\n", r2))
if (!(r1 > 0.2 && r2 < -0.2)) ok <- FALSE

x <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
cat(sprintf("cor(env1, env2) as stored = %+.3f (both pro-environment oriented, expect > 0)\n",
            cor(x$resp.env1, x$resp.env2, use = "pair")))

cat("\nNot established by these routes: nothing further -- with two items in opposite\n",
    "polarity classes and unique count matches, each item is distinguished from the other.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
