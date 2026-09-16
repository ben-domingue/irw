# verify_wu2021_burnout.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST. wu2021_burnout's D1..D16 are section 四 (items 1-16) of the
# study's own supplementary questionnaire (Frontiers Data_Sheet_2.PDF), which is
# the 16-item Chinese Basic Empathy Scale -- NOT a burnout scale, despite the
# table name. Two things have to hold for the shipped file to be right:
#   (A) live item D<n> is the source column D<n>, and that column is questionnaire
#       item n of section 四;
#   (B) the 8 negatively-worded items are stored ALREADY REVERSE-RECODED, which is
#       why their shipped option_text runs 1=完全同意 .. 5=完全不同意.
#
# Nothing here re-checks item/resp sets; validate_items.R did that.

suppressMessages(library(irw))

TABLE <- "wu2021_burnout"
RAW_URL <- "https://ndownloader.figshare.com/files/30891994"   # figshare 16683931, CC BY 4.0
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       "wu2021_burnout__items.csv")
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- "itemtables/batch_229/wu2021_burnout__items.csv"

ok <- TRUE

## ---- source deposit -------------------------------------------------------
tf <- tempfile(fileext = ".csv")
download.file(RAW_URL, tf, quiet = TRUE, mode = "wb")
raw <- read.csv(tf, fileEncoding = "UTF-8", check.names = FALSE)
D <- paste0("D", 1:16)
for (cc in c(D, "认知移情", "情感移情"))
  raw[[cc]] <- suppressWarnings(as.numeric(raw[[cc]]))
X <- raw[stats::complete.cases(raw[, D]), D]     # listwise set, used for alpha/correlations
cat(sprintf("source deposit: %d rows, %d complete over D1..D16\n\n", nrow(raw), nrow(X)))

## ---- (A1) live item codes carry the same numbers as the source columns ----
d <- irw::irw_fetch(TABLE)
live  <- tapply(d$resp, d$item, mean)[D]
liven <- tapply(d$resp, d$item, length)[D]
srcm <- sapply(D, function(cc) mean(raw[[cc]], na.rm = TRUE))
srcn <- sapply(D, function(cc) sum(!is.na(raw[[cc]])))
cat("per-item mean and n, live IRW table vs source column of the same name:\n")
cat(sprintf("%-5s %9s %9s %10s %7s %7s\n", "item", "live", "source", "diff", "n_live", "n_src"))
for (i in seq_along(D))
  cat(sprintf("%-5s %9.4f %9.4f %10.2e %7d %7d\n",
              D[i], live[i], srcm[i], live[i] - srcm[i], liven[i], srcn[i]))
a1 <- max(abs(live - srcm)) < 1e-9 && all(liven == srcn)
cat(sprintf("max |diff| = %.2e, all n equal = %s  -> %s\n\n",
            max(abs(live - srcm)), all(liven == srcn), if (a1) "OK" else "FAIL"))
ok <- ok && a1

## ---- (A2) the deposit's own subscale columns pin each item's subscale -----
# The shipped item_text at positions 3,6,7,9,11,12,15,16 are the cognitive-empathy
# items of section 四 (BES-20 items 6,9,10,12,14,16,19,20); positions
# 1,2,4,5,8,10,13,14 are the affective items (BES-20 items 1,5,7,8,11,13,17,18).
COG <- c(3, 6, 7, 9, 11, 12, 15, 16)
AFF <- setdiff(1:16, COG)
sub <- raw[stats::complete.cases(raw[, c(D, "认知移情", "情感移情")]), ]
cogres <- max(abs(rowMeans(sub[, paste0("D", COG)]) - sub[["认知移情"]]))
affres <- max(abs(rowMeans(sub[, paste0("D", AFF)]) - sub[["情感移情"]]))
cat(sprintf("cognitive-empathy column == mean(D%s): max residual %.2e over %d rows\n",
            paste(COG, collapse = ","), cogres, nrow(sub)))
cat(sprintf("affective-empathy column == mean(D%s): max residual %.2e\n",
            paste(AFF, collapse = ","), affres))
# falsification: the same test for one swapped pair must fail
bad <- COG; bad[bad == 3] <- 1
badres <- max(abs(rowMeans(sub[, paste0("D", bad)]) - sub[["认知移情"]]))
cat(sprintf("  (control) swapping D3 for D1 in that set: max residual %.3f -- must be large\n", badres))
a2 <- cogres < 1e-9 && affres < 1e-9 && badres > 0.01
cat(sprintf("  -> %s\n\n", if (a2) "OK" else "FAIL"))
ok <- ok && a2

## ---- (B) storage direction, against the paper's published alpha -----------
PUBLISHED_ALPHA <- 0.827   # Wu & Qi 2021, "The Cronbach's alpha coefficient for
                           # the Basic Empathy Scale was 0.827"
alpha <- function(m) { k <- ncol(m); k/(k-1) * (1 - sum(apply(m, 2, var))/var(rowSums(m))) }
items <- read.csv(ITEMS_CSV, fileEncoding = "UTF-8")
# which items did the shipped file flip? resp==1 labelled 完全同意 ("completely agree")
flip <- sort(as.integer(sub("^D", "", unique(
  items$item[items$resp == 1 & items$option_text == "完全同意"]))))
cat("items whose shipped option_text runs agree->disagree: ", paste0("D", flip, collapse = " "), "\n")
Y <- X; for (i in flip) Y[[paste0("D", i)]] <- 6 - Y[[paste0("D", i)]]
a_stored <- alpha(as.matrix(X)); a_flipped <- alpha(as.matrix(Y))
cat(sprintf("Cronbach alpha, data AS STORED           : %.3f   (published %.3f)\n", a_stored, PUBLISHED_ALPHA))
cat(sprintf("Cronbach alpha, those items flipped back : %.3f\n", a_flipped))
cat("  antonym pairs (must be POSITIVE if the negative items are stored recoded):\n")
prs <- list(c(3, 7), c(11, 16), c(1, 2), c(5, 13))
pr_ok <- TRUE
for (p in prs) {
  r <- cor(X[[paste0("D", p[1])]], X[[paste0("D", p[2])]])
  cat(sprintf("    r(D%d,D%d) = %+.3f\n", p[1], p[2], r)); pr_ok <- pr_ok && r > 0
}
b <- identical(flip, c(1L, 3L, 4L, 5L, 10L, 14L, 15L, 16L)) &&
     abs(a_stored - PUBLISHED_ALPHA) < 0.005 && a_flipped < a_stored && pr_ok
cat(sprintf("  -> %s\n\n", if (b) "OK" else "FAIL"))
ok <- ok && b

cat("What this does NOT establish: the order of items WITHIN each of the four\n",
    "blocks (cognitive-positive 5, cognitive-reverse 3, affective-positive 3,\n",
    "affective-reverse 5). 5!*3!*3!*5! = 518,400 permutations of the shipped\n",
    "item_text survive every test above, so the verification status is PARTIAL.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
