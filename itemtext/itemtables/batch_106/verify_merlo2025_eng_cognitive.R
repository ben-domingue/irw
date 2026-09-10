# verify_merlo2025_eng_cognitive.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (two axes):
#
#  (A) ITEM AXIS. merlo2025_eng_cognitive's item codes ENG_COGN_01..ENG_COGN_12 are the
#      literal column names of the figshare deposit's Final-dataset.csv --
#      data/merlo2025_engagement.py melts them BY NAME with no rename (core-model
#      derivation pattern 1) -- and the deposit's own data dictionary,
#      Final-dataset-grid.csv (VARIABLE;ITEM), gives each of those names its administered
#      Italian wording.  mapping_basis is therefore data_labels and Step 5b is exempt;
#      this script checks the one link that could still be silently wrong -- that live
#      item ENG_COGN_nn really carries deposit column ENG_COGN_nn's responses.  Per-item
#      means are compared exactly (tol 1e-9), and the 12 deposit means are pairwise
#      distinct, so ANY permutation of the codes breaks the test for every permuted item.
#
#  (B) OPTION AXIS / SCALE DIRECTION.  The shipped anchors are 1 = Never .. 7 = Always
#      (Merlo et al. 2026, Formazione & insegnamento 24(2):114-129 sec. 3.2.6: "from
#      never (1) to always (7) in cognitive subscale"; Mameli & Passini 2017 TPM
#      24(4):527-541 p.533: "a 7-point Likert scale of frequency was used (from
#      1 = never to 7 = always)").  The deposit publishes no value labels, so the
#      direction is checked against the paper's own published composite: Table 1 gives
#      ENG_C M = 4.229, SD = 1.316, Median = 4.22, Skew = -0.317, Kurt = -0.169.  That
#      composite is reproduced here from the LIVE data.  Its item set is not the full 12:
#      a search over all subsets found exactly one that reproduces the published figures,
#      the 9 items left after dropping ENG_COGN_04, _05 and _11 (the paper reports
#      dropping "C5, C11" plus agentic items in its CFA trimming; the reconstruction says
#      C4 went too).  Under the reversed reading (resp' = 8 - resp) the same composite
#      would be 3.771 with skew +0.318, so this pins the direction decisively.
#
# WHAT THIS DOES NOT ESTABLISH:
#   * Nothing here checks the WORDS.  That ENG_COGN_08's wording really is "Quando studio
#     cerco di fare dei collegamenti", and that the English in the *_translated columns is
#     a faithful translation of the administered Italian, are outside any numeric route.
#   * (B) pins the two ENDS of the response scale and the membership of the 9 composite
#     items.  It says nothing about the five interior scale points -- which is why
#     option_text for resp 2..6 is shipped blank rather than guessed.

suppressMessages(library(irw))

TABLE <- "merlo2025_eng_cognitive"
TOL   <- 1e-9
DATA  <- "https://ndownloader.figshare.com/files/58188073"   # Final-dataset.csv
ITEMS <- sprintf("ENG_COGN_%02d", 1:12)

# Merlo et al. (2026) Table 1, row ENG_C.
PUB <- c(mean = 4.229, sd = 1.316, median = 4.22, skew = -0.317, kurt = -0.169)
COMPOSITE <- setdiff(ITEMS, c("ENG_COGN_04", "ENG_COGN_05", "ENG_COGN_11"))

g1 <- function(x) { n <- length(x); m <- mean(x); s <- sd(x)
                    sqrt(n*(n-1))/(n-2) * (sum((x-m)^3)/n) / (sum((x-m)^2)/n)^1.5 }
g2 <- function(x) { n <- length(x); m <- mean(x)
                    b2 <- (sum((x-m)^4)/n) / (sum((x-m)^2)/n)^2
                    ((n+1)*(b2-3) + 6) * (n-1)/((n-2)*(n-3)) }

raw <- read.csv2(DATA, fileEncoding = "UTF-8-BOM", check.names = FALSE)
dep <- sapply(ITEMS, function(c) mean(as.numeric(raw[[c]]), na.rm = TRUE))

d <- irw::irw_fetch(TABLE)               # 12,780 rows; a trivial export
live <- tapply(as.numeric(d$resp), d$item, mean)[ITEMS]

cat("--- (A) item axis: deposit column mean vs live item mean ---\n")
cat(sprintf("%-12s %11s %11s %12s\n", "item", "deposit", "live", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-12s %11.6f %11.6f %12.2e\n", ITEMS[i], dep[i], live[i], live[i]-dep[i]))
worst <- max(abs(live - dep))
gaps  <- as.matrix(dist(dep)); diag(gaps) <- NA
mg    <- which(gaps == min(gaps, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("\nlargest |live - deposit| : %.2e (tolerance %.0e)\n", worst, TOL))
cat(sprintf("closest pair of deposit means: %s %.6f vs %s %.6f (gap %.5f)\n",
            ITEMS[mg[1]], dep[mg[1]], ITEMS[mg[2]], dep[mg[2]], min(gaps, na.rm = TRUE)))
cat("=> all 12 means are distinct, so any code permutation moves at least two items.\n")
okA <- worst <= TOL

cat("\n--- (B) option axis: published ENG_C composite, rebuilt from LIVE data ---\n")
sub_d <- d[d$item %in% COMPOSITE, c("id", "item", "resp")]
sub_d$id   <- as.character(sub_d$id)
sub_d$resp <- as.numeric(sub_d$resp)
w <- tapply(sub_d$resp, list(sub_d$id, sub_d$item), function(z) z[1])
stopifnot(!anyNA(w), ncol(w) == length(COMPOSITE))
m   <- rowMeans(w)
rev <- rowMeans(8 - w)
obs <- c(mean = mean(m), sd = sd(m), median = median(m), skew = g1(m), kurt = g2(m))
rv  <- c(mean = mean(rev), sd = sd(rev), median = median(rev), skew = g1(rev), kurt = g2(rev))
cat(sprintf("composite = mean of %d items: %s\n", length(COMPOSITE),
            paste(sub("ENG_COGN_", "", COMPOSITE), collapse = ",")))
cat(sprintf("n respondents: %d\n", nrow(w)))
cat(sprintf("%-8s %11s %11s %11s\n", "stat", "published", "live 1..7", "live rev"))
for (k in names(PUB))
    cat(sprintf("%-8s %11.3f %11.3f %11.3f\n", k, PUB[k], obs[k], rv[k]))
dir_ok <- abs(obs["mean"] - PUB["mean"]) < 0.01 && abs(obs["skew"] - PUB["skew"]) < 0.01 &&
          abs(obs["sd"] - PUB["sd"]) < 0.01
cat(sprintf("\n=> shipped direction off by %.4f on the mean and %.4f on the skew;\n",
            obs["mean"] - PUB["mean"], obs["skew"] - PUB["skew"]))
cat(sprintf("   the reversed reading would be off by %.4f and %.4f.\n",
            rv["mean"] - PUB["mean"], rv["skew"] - PUB["skew"]))

cat("\nNote: this establishes the item<->column link and the 1 = Never / 7 = Always\n")
cat("direction. It establishes NOTHING about the item wording itself, about the IRW-\n")
cat("produced English translation, or about the five unlabelled interior scale points.\n")

cat(if (okA && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
