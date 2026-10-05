# verify_makovi_2021_environmental_concern.R -- Step 5b, re-runnable evidence (automated_finding, PMC sweep 2026-10-04).
#
# CLAIM: escale_k in makovi_2021_environmental_concern is the k-th question of
# the "Environmental Concern Scale" block in the article's SI survey (MOESM1,
# Survey First Data Collection); air_polluted is the block's 8th question ("Air
# pollution is an issue in the area where you live"), tied by its name.
# mapping_basis paper_order (positional column names).
#
# Routes:
#  (1) Option-label signature from the raw CSV (MOESM2 stores labels): q1
#      concern, q2-3 willing, q4-5 dangerous, q6-7 and air_polluted 4-point agree.
#  (2) Polarity among the agree items: "Many environmental threats are
#      exaggerated" (q6) is the only reverse-worded item, so escale_6 must
#      correlate NEGATIVELY with escale_1 (concern) and with being
#      TurkPrime-liberal, and escale_7 POSITIVELY; and the authors' composite
#      escore must be reproduced as the rescaled mean of escale_1..7 with
#      escale_6 (and only escale_6) reversed.
# NOT established: escale_2 vs escale_3 (both "willing"), escale_4 vs escale_5
# (both "dangerous") -- hence PARTIAL.

TABLE <- "makovi_2021_environmental_concern"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
zf <- tempfile(fileext = ".zip")
download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8589981/supplementaryFiles",
              zf, quiet = TRUE, mode = "wb")
raw <- read.csv(unz(zf, "41598_2021_329_MOESM2_ESM.csv"), check.names = FALSE)

CON <- c("Not concerned at all", "Somewhat unconcerned", "Somewhat concerned", "Very concerned")
WIL <- c("Not at all willing", "Somewhat willing", "Mostly willing", "Very willing")
DAN <- c("Not at all dangerous", "Slightly dangerous", "Somewhat dangerous", "Very dangerous")
AG4 <- c("Strongly agree", "Agree", "Disagree", "Strongly disagree")
PRINTED <- list(CON, WIL, WIL, DAN, DAN, AG4, AG4, AG4)
COLS <- c(paste0("escale_", 1:7), "air_polluted")
ok <- TRUE
cat("(1) option-label signature\n")
for (k in 1:8) {
  obs <- sort(unique(raw[[COLS[k]]]))
  hit <- setequal(obs, PRINTED[[k]]); ok <- ok && hit
  could <- which(vapply(PRINTED, function(p) setequal(obs, p), logical(1)))
  cat(sprintf("  %-13s matches q%d %-5s candidates by labels: %s\n", COLS[k], k, hit,
              paste(could, collapse = ",")))
}
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
lib <- as.numeric(d$cov_ideology_turkprime[match(w$id, d$id)] == "liberal")
cat("\n(2) polarity of the agree items\n")
for (it in c("escale_6", "escale_7", "air_polluted")) {
  r1 <- cor(w[[it]], w$escale_1); r2 <- cor(w[[it]], lib)
  exp_sign <- if (it == "escale_6") -1 else 1
  hit <- sign(r1) == exp_sign && sign(r2) == exp_sign; ok <- ok && hit
  cat(sprintf("  %-13s expected %-8s r(escale_1)=%+.3f r(liberal)=%+.3f %s\n", it,
              if (exp_sign > 0) "forward" else "reverse", r1, r2, if (hit) "" else "<-- MISMATCH"))
}
X <- as.matrix(w[, paste0("escale_", 1:7)])
es <- raw$escore[match(w$id, raw[[1]])]
for (rev in 1:7) {
  Y <- X; Y[, rev] <- 5 - Y[, rev]
  dev <- max(abs((rowMeans(Y) - 1) / 3 - es))
  cat(sprintf("  escore reproduced with escale_%d reversed: max |dev| = %.4f\n", rev, dev))
  if (rev == 6) ok <- ok && dev < 0.01 else ok <- ok && dev > 0.05
}
cat("Labels pin q1 and separate {2,3}, {4,5}, {6,7,air_polluted}; polarity and the escore\n",
    "reconstruction pin escale_6 as the reverse-worded q6 and escale_7 as q7. Not tested: 2 vs 3, 4 vs 5.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
