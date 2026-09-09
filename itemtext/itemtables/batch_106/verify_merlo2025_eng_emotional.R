# verify_merlo2025_eng_emotional.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (three parts):
#
#  (A) item axis. merlo2025_eng_emotional's item codes ENG_EMO_01..ENG_EMO_09 are the
#      literal column names of the figshare deposit's Final-dataset.csv
#      (data/merlo2025_engagement.py melts them by name -- core-model derivation
#      pattern 1), and the deposit's own data dictionary Final-dataset-grid.csv
#      (VARIABLE;ITEM) maps each of those names to its administered Italian wording.
#      This script checks the one link that could silently be wrong: that live item
#      ENG_EMO_nn really carries deposit column ENG_EMO_nn's responses. Per-item means
#      are compared EXACTLY (tol 1e-9). The 9 deposit means are pairwise distinct --
#      closest pair ENG_EMO_03 4.46291 vs ENG_EMO_07 4.47324, gap 0.01033 -- so any
#      permutation of the 9 codes breaks the test for every permuted item.
#
#  (B) reverse-scoring. The shipped option_text for ENG_EMO_09 ("Penso che studiare sia
#      noioso" / "I think studying is boring") runs 1 = Totally agree ... 7 = Completely
#      disagree, i.e. OPPOSITE the other eight items, because the deposit stores this
#      item ALREADY REVERSED. Mameli & Passini (2017, TPM 24(4):527-541), the scale's
#      own validation paper, state the affective subscale has "nine items, one of which
#      is reverse scored" and name it as "I think learning is boring" (reverse). If it
#      were stored raw it would correlate NEGATIVELY with the eight positively worded
#      items; the test is that all eight correlations are positive and that Cronbach's
#      alpha computed on the columns AS STORED beats alpha with item 09 flipped, and
#      lands on the published .87.
#
#  (C) scale direction (option axis, ends only). Merlo et al. (2026) sec. 3.2.6 states
#      the affective subscale runs "completely disagree (1) to totally agree (7)"; the
#      instrument's validation paper says the same in other words ("1 = strongly
#      disagree to 7 = strongly agree"). Route 8 corroboration: under that direction the
#      least endorsed item must be the one about wanting to go to school and the most
#      endorsed the one about interest in learning, for a sample of 1065 adolescents
#      (mean age 15.95). Under the reversed reading the ordering would say Italian
#      teenagers most strongly look forward to school mornings and are least interested
#      in learning.
#
# WHAT THIS DOES NOT ESTABLISH: nothing here checks the WORDS. That the Italian
# wording in the deposit dictionary is what was on screen, and that the English in the
# *_translated columns is a faithful translation, are outside any numeric route. (C)
# pins only the two ENDS of the 7-point scale -- the five interior points are shipped
# with option_text blank precisely because no anchor exists for them.

suppressMessages(library(irw))

TABLE <- "merlo2025_eng_emotional"
TOL   <- 1e-9
GRID  <- "https://ndownloader.figshare.com/files/58188718"  # Final-dataset-grid.csv
DATA  <- "https://ndownloader.figshare.com/files/58188073"  # Final-dataset.csv

raw  <- read.csv2(DATA, fileEncoding = "UTF-8-BOM", check.names = FALSE)
grid <- read.csv2(GRID, fileEncoding = "UTF-8-BOM", check.names = FALSE)

cols <- grep("^ENG_EMO_", names(raw), value = TRUE)
dep  <- sapply(cols, function(c) mean(as.numeric(raw[[c]]), na.rm = TRUE))

d    <- irw::irw_fetch(TABLE)          # 9 items x 1065 respondents; a trivial export
live <- tapply(as.numeric(d$resp), d$item, mean)[cols]

wording <- setNames(
    trimws(sub("^.*questo semestre\\s+", "", gsub("[[:space:]]+", " ", trimws(grid$ITEM)))),
    trimws(grid$VARIABLE))[cols]

cat("--- (A) item axis: deposit column mean vs live item mean ---\n")
cat(sprintf("%-11s %-46s %10s %10s %12s\n", "item", "dictionary wording", "deposit", "live", "diff"))
for (i in seq_along(cols))
    cat(sprintf("%-11s %-46s %10.6f %10.6f %12.2e\n",
                cols[i], substr(wording[i], 1, 46), dep[i], live[i], live[i] - dep[i]))
worst <- max(abs(live - dep))
gaps  <- as.matrix(dist(dep)); diag(gaps) <- NA
cat(sprintf("\nlargest |live - deposit| : %.2e (tolerance %.0e)\n", worst, TOL))
cat(sprintf("closest pair of deposit means: %.5f -- any code permutation moves an item\n",
            min(gaps, na.rm = TRUE)))
okA <- worst <= TOL

cat("\n--- (B) ENG_EMO_09 is stored already reverse-scored ---\n")
X <- raw[cols]; X <- X[stats::complete.cases(X), ]
X[] <- lapply(X, as.numeric)
alpha <- function(M) {
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}
cm <- cor(X)
r9 <- cm["ENG_EMO_09", setdiff(cols, "ENG_EMO_09")]
cat("wording of ENG_EMO_09: ", wording[["ENG_EMO_09"]], "\n", sep = "")
cat("r(ENG_EMO_09, each of the other 8): ", paste(sprintf("%.2f", r9), collapse = " "), "\n", sep = "")
cat(sprintf("  all eight positive? %s  (range %.3f to %.3f)\n",
            all(r9 > 0), min(r9), max(r9)))
Y <- X; Y$ENG_EMO_09 <- 8 - Y$ENG_EMO_09
cat(sprintf("Cronbach alpha as stored          : %.4f\n", alpha(X)))
cat(sprintf("Cronbach alpha with 09 flipped    : %.4f\n", alpha(Y)))
cat(sprintf("published alpha (Mameli & Passini 2017, affective, n=1210): %.2f\n", 0.87))
okB <- all(r9 > 0) && alpha(X) > alpha(Y)

cat("\n--- (C) scale direction, ends only ---\n")
o <- order(live)
cat("least endorsed : ", sprintf("%s %.2f (%s)", cols[o[1]], live[o[1]], wording[o[1]]), "\n", sep = "")
cat("most endorsed  : ", sprintf("%s %.2f (%s)", cols[o[9]], live[o[9]], wording[o[9]]), "\n", sep = "")
cat("(1 = completely disagree ... 7 = totally agree makes this a sample of adolescents\n",
    " who are interested in learning but do not look forward to going to school; the\n",
    " reversed reading inverts both statements.)\n", sep = "")
okC <- cols[o[1]] == "ENG_EMO_05" && cols[o[9]] == "ENG_EMO_08"

cat("\n", if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n", sep = "")
