# verify_makovi_2021_symbolic_racism.R -- Step 5b, re-runnable evidence (automated_finding, PMC sweep 2026-10-04).
#
# CLAIM: rscale_k in makovi_2021_symbolic_racism is the k-th question of the
# "Symbolic Racism Scale" block in the article's SI survey (MOESM1, Survey First
# Data Collection), so item_text for rscale_k is that question's stem.
# mapping_basis paper_order: the deposit's column names are positional.
#
# Two routes, both falsifiable:
#  (1) Option-label signature. The raw CSV (MOESM2) stores each answer as its
#      option label. The survey prints a distinctive option set for questions
#      4 (responsible), 6 (pushing), 7 (racial tension), 11 (change) and, through
#      a typo, 10 ("Neither agree not disagree"); 1,2,3,5,8,9 share the
#      Strongly agree..Strongly disagree set. Each column's observed label set
#      must equal the set printed for its claimed question.
#  (2) Polarity. With resp coded so a higher value is more agreement / more
#      responsibility / "too fast" / more tension / more positive change, the
#      survey wording predicts items 1,2,4,5,6,7,10,11 are pro-symbolic-racism
#      (correlate POSITIVELY with being TurkPrime-classified conservative) and
#      3,8,9 are the reverse-worded items (NEGATIVE). The authors' composite
#      rscore is printed for information only: its weights reverse items 3 and 9
#      but NOT item 8 (an apparent scoring slip in the authors' composite), while
#      item 8's own correlation with ideology is clearly negative (r ~ -0.50),
#      exactly as its reverse wording predicts, so the column-to-question tie
#      holds and only the authors' composite is off.
# NOT established: the order WITHIN {1,2,5} and within {3,8,9} (same option set,
# same polarity) -- hence PARTIAL, not VERIFIED.
#
# Data: raw MOESM2 from the Europe PMC supplementaryFiles zip, plus the staged
# response CSV (not on Redivis yet). Run from the repo root (irw/src) or automated_finding/.

TABLE <- "makovi_2021_symbolic_racism"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)

zf <- tempfile(fileext = ".zip")
download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8589981/supplementaryFiles",
              zf, quiet = TRUE, mode = "wb")
raw <- read.csv(unz(zf, "41598_2021_329_MOESM2_ESM.csv"), check.names = FALSE)

A5 <- c("Strongly agree", "Agree", "Neither agree nor disagree", "Disagree", "Strongly disagree")
PRINTED <- list(
  A5, A5, A5,
  c("Very responsible", "Somewhat responsible", "A little responsible", "Not at all responsible"),
  A5,
  c("Pushing way too fast", "Pushing a bit fast", "Pushing at the right pace", "Pushing a bit slow", "Pushing way to slowly"),
  c("All of the racial tension", "Most of the racial tension", "About half of the racial tension",
    "A little of the racial tension", "None of the racial tension"),
  A5, A5,
  c("Strongly agree", "Agree", "Neither agree not disagree", "Disagree", "Strongly disagree"),
  c("A lot of positive change", "A little positive change", "No change", "A little negative change",
    "A lot of negative change"))
ok <- TRUE
cat("(1) option-label signature: observed label set == printed set of question k\n")
for (k in 1:11) {
  obs <- sort(unique(raw[[paste0("rscale_", k)]]))
  hit <- setequal(obs, PRINTED[[k]])
  # which printed questions could this column be, by label set alone?
  could <- which(vapply(PRINTED, function(p) setequal(obs, p), logical(1)))
  ok <- ok && hit
  cat(sprintf("  rscale_%-3d matches q%-3d %-5s candidates by labels: %s\n", k, k, hit,
              paste(could, collapse = ",")))
}

cat("\n(2) polarity: r(item, conservative); the authors' rscore weight shown for information\n")
FORWARD <- c(1, 2, 4, 5, 6, 7, 10, 11); REVERSE <- c(3, 8, 9)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cons <- as.numeric(d$cov_ideology_turkprime[match(w$id, d$id)] == "conservative")
rs <- raw$rscore[match(w$id, raw[[1]])]
X <- as.matrix(w[, paste0("rscale_", 1:11)])
beta <- coef(lm(rs ~ X))[-1]
for (k in 1:11) {
  r <- cor(X[, k], cons)
  exp_sign <- if (k %in% REVERSE) -1 else 1
  hit <- sign(r) == exp_sign
  ok <- ok && hit
  cat(sprintf("  rscale_%-3d expected %-8s r=%+.3f  rscore weight=%+.4f %s\n", k,
              if (exp_sign > 0) "forward" else "reverse", r, beta[k], if (hit) "" else "<-- MISMATCH"))
}
cat("Labels pin q4, q6, q7, q10, q11 uniquely; polarity splits the shared-label items into\n",
    "{1,2,5} forward and {3,8,9} reverse. Order within those two triples is not tested.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
