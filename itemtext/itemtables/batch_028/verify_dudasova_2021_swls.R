# verify_dudasova_2021_swls.R -- Step 5b mapping check.
#
# CLAIM under test: LifeSat1..LifeSat5 correspond to SWLS items 1..5 in Diener,
# Emmons, Larsen & Griffin (1985) canonical order, and resp 1..7 runs
# "Strongly disagree" (1) .. "Strongly agree" (7).
#
# The mapping was NOT tied by any label: the study's S1 .sav (PLOS
# 10.1371/journal.pone.0247114.s001) carries no variable labels and no value
# labels at all, and the paper never describes the SWLS. So the assignment is
# reconstructed from the numeric suffix + canonical SWLS order, and it needs a
# falsifiable prediction.
#
# Two predictions, both from the SWLS literature (not from this paper):
#
#  (A) ITEM PROFILE. Across SWLS samples items 3 and 4 are the two highest-mean
#      items (3 highest), and item 5 -- "If I could live my life over, I would
#      change almost nothing" -- is the most dispersed and the weakest item, with
#      the lowest corrected item-total correlation. Diener et al. (1985) report
#      factor loadings .84 .77 .84 .72 .61 for items 1..5, i.e. item 3 top tier
#      and item 5 clearly lowest.
#
#  (B) SCALE DIRECTION. Higher resp must mean MORE satisfied. Tested against a
#      variable in the same .sav whose direction is documented by the paper's own
#      S1 Appendix: PsyCap1..12 on 1 = strongly disagree .. 6 = strongly agree.
#      Life satisfaction and psychological capital must correlate POSITIVELY.
#
# Data is fetched from the source .sav (identical to the live IRW table, which
# this script also spot-checks) rather than irw_fetch(), to avoid burning the
# account-wide Redivis export quota.
#
# WHAT THIS DOES NOT ESTABLISH: it separates item 3, item 4 and item 5 from the
# rest. It does NOT distinguish LifeSat1 from LifeSat2 -- their means differ by
# only 0.14 and their item-total correlations run the opposite way to Diener's
# published loadings. Status is therefore PARTIAL, not VERIFIED.

url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0247114.s001")
f <- file.path(tempdir(), "dudasova_s001.sav")
if (!file.exists(f)) download.file(url, f, mode = "wb", quiet = TRUE)
suppressMessages(library(haven))
d <- haven::read_sav(f)

sw <- paste0("LifeSat", 1:5)
pc <- paste0("PsyCap", 1:12)
X  <- as.data.frame(lapply(d[sw], as.numeric))
P  <- as.data.frame(lapply(d[pc], as.numeric))
X  <- X[complete.cases(X), , drop = FALSE]

cat(sprintf("N = %d, resp range %g..%g\n\n", nrow(X), min(X), max(X)))

tot <- rowSums(X)
m   <- sapply(X, mean); s <- sapply(X, sd)
itc <- sapply(sw, function(c) cor(X[[c]], tot - X[[c]]))
LOAD_1985 <- c(.84, .77, .84, .72, .61)

cat(sprintf("%-9s %6s %6s %8s %12s\n", "item", "mean", "sd", "item-tot", "Diener1985 L"))
for (i in 1:5)
  cat(sprintf("%-9s %6.2f %6.2f %8.3f %12.2f\n", sw[i], m[i], s[i], itc[i], LOAD_1985[i]))

# (A) three falsifiable orderings
a1 <- which.max(m) == 3L                       # item 3 highest mean
a2 <- order(m, decreasing = TRUE)[2] == 4L     # item 4 second highest mean
a3 <- which.min(itc) == 5L                     # item 5 weakest item-total
a4 <- which.max(s) == 5L                       # item 5 most dispersed
cat(sprintf("\n(A1) highest mean is item %d (predict 3): %s\n", which.max(m), a1))
cat(sprintf("(A2) 2nd highest mean is item %d (predict 4): %s\n", order(m, decreasing = TRUE)[2], a2))
cat(sprintf("(A3) lowest item-total is item %d (predict 5): %s\n", which.min(itc), a3))
cat(sprintf("(A4) largest SD is item %d (predict 5): %s\n", which.max(s), a4))
cat(sprintf("     rank corr(observed item-total, Diener 1985 loadings) = %.3f\n",
            cor(itc, LOAD_1985, method = "spearman")))

# (B) direction
sub <- complete.cases(cbind(d[sw], d[pc]))
r <- cor(rowMeans(as.data.frame(lapply(d[sub, sw], as.numeric))),
         rowMeans(as.data.frame(lapply(d[sub, pc], as.numeric))))
cat(sprintf("\n(B) corr(SWLS mean, PsyCap mean) = %+.3f  (PsyCap 1=strongly disagree..6=strongly agree,\n", r))
cat("    per this paper's S1 Appendix) -- must be POSITIVE if resp 7 = Strongly agree.\n")
b1 <- r > 0.2

cat("\nNOT established by this script: LifeSat1 vs LifeSat2 (means 4.52 vs 4.66)\n",
    "are not separated; that pair rests on the numeric suffix alone.\n", sep = "")

cat(if (a1 && a2 && a3 && a4 && b1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
