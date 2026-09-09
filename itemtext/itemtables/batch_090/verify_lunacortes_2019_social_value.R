# Step 5b verification for lunacortes_2019_social_value.
#
# THE MAPPING CLAIM, in two links.
#
#  LINK A (code -> data column). The IRW codes social_val1/2/3 are a mechanical
#  lowercase/dash rename of the S1 File XLSX headers "Social-Val1".."Social-Val3"
#  (data/lunacortes_2019_vsn_scales.py: rename_map lowercases and maps "-"->"_",
#  then melts BY NAME -- no positional step). Falsifiable prediction: each live
#  item's values are cell-for-cell identical to its namesake source column.
#
#  LINK B (paper's PSV numbering -> data column). PLOS Table 1 prints the three
#  Perceived Social Value items as an UNLABELLED bullet list, and Table 2 reports
#  loadings for PSV1 and PSV2 ONLY, because section 3.4 says PSV3 "presented
#  factor loadings lower than the rest of the items" and was removed on the
#  Lagrange test. So the paper's two-indicator PSV factor is a NAMED SUBSET of
#  the three data columns, and its published Cronbach's alpha = 0.822 (Table 2)
#  is a fingerprint that identifies WHICH two. Falsifiable predictions:
#     (b1) alpha of the pair {social_val1, social_val2} reproduces 0.822, and
#          neither other pair does;
#     (b2) social_val3 is the weakest indicator (lowest corrected item-total r),
#          the signature of the item the paper dropped.
#  Content corroboration (route 8): bullet 3, "makes a good impression on other
#  people", is the semantic odd one out -- it is about others' impression rather
#  than the respondent's own social standing (bullets 1 and 2: "helps me to feel
#  acceptable", "improves the way I am perceived") -- and so is the easiest to
#  endorse, predicting the highest mean and smallest SD.
#
# WHAT THIS DOES NOT ESTABLISH: it pins social_val3 = PSV3 = bullet 3 outright,
# but it does NOT separate social_val1 from social_val2. The paper's published
# loadings for those two are 0.83 and 0.84 with an IDENTICAL robust t of 24.100,
# a gap far too small to key on. Hence PARTIAL, not VERIFIED.
#
# COST NOTE: irw_fetch() is used deliberately. This table is 1,332 rows, so the
# export is negligible against the 200GB/30-day account cap, and a cell-for-cell
# comparison against the source columns (link A) cannot be done from the
# server-side set/aggregate route.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "lunacortes_2019_social_value"
ITEMS <- c("social_val1", "social_val2", "social_val3")
SRC   <- c("Social-Val1", "Social-Val2", "Social-Val3")
PUB_ALPHA <- 0.822           # PLOS ONE t002, Perceived Social Value factor
PUB_LOAD  <- c(PSV1 = 0.83, PSV2 = 0.84)   # PSV3 absent: removed from the CFA

URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0217758.s001")

cache_dir <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(cache_dir)) cache_dir <- file.path(".cache", TABLE)
dir.create(cache_dir, recursive = TRUE, showWarnings = FALSE)
p <- file.path(cache_dir, "s001.xlsx")
if (!file.exists(p)) utils::download.file(URL, p, mode = "wb", quiet = TRUE)
raw <- as.data.frame(readxl::read_excel(p, sheet = "Hoja1"))
stopifnot(all(SRC %in% names(raw)))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(as.numeric(as.character(w$id))), ]
raw <- raw[order(as.numeric(raw$Number)), ]

## ---- LINK A: cell-for-cell live vs source column ------------------------
cat("== LINK A: live column vs its namesake S1 File column ==\n")
okA <- TRUE
for (i in seq_along(ITEMS)) {
    a <- as.numeric(w[[ITEMS[i]]]); b <- as.numeric(raw[[SRC[i]]])
    same <- length(a) == length(b) && all(a == b)
    okA <- okA && same
    cat(sprintf("%-12s n_live=%d n_src=%d identical=%s\n",
                ITEMS[i], sum(!is.na(a)), sum(!is.na(b)), ifelse(same, "YES", "NO")))
}

## ---- LINK B: which two columns are the paper's PSV1/PSV2 ----------------
alpha <- function(m) {
    m <- as.matrix(m); k <- ncol(m)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}
X <- as.data.frame(sapply(ITEMS, function(i) as.numeric(w[[i]])))
cat("\n== LINK B1: Cronbach's alpha of each retainable PAIR vs published 0.822 ==\n")
prs <- combn(ITEMS, 2, simplify = FALSE)
avals <- sapply(prs, function(pr) alpha(X[, pr]))
for (j in seq_along(prs))
    cat(sprintf("  {%-11s,%-11s} alpha = %.4f   |diff| = %.4f\n",
                prs[[j]][1], prs[[j]][2], avals[j], abs(avals[j] - PUB_ALPHA)))
best <- prs[[which.min(abs(avals - PUB_ALPHA))]]
cat(sprintf("  alpha of all three items = %.4f\n", alpha(X)))
okB1 <- identical(best, c("social_val1", "social_val2")) &&
        abs(min(abs(avals - PUB_ALPHA))) < 0.005 &&
        sort(abs(avals - PUB_ALPHA))[2] > 0.1

cat("\n== LINK B2: corrected item-total r (weakest = the dropped PSV3) ==\n")
itc <- sapply(ITEMS, function(i) cor(X[[i]], rowSums(X[, setdiff(ITEMS, i)])))
mn  <- colMeans(X); sdv <- apply(X, 2, sd)
cat(sprintf("%-12s %10s %8s %8s\n", "item", "item-total", "mean", "sd"))
for (i in ITEMS) cat(sprintf("%-12s %10.4f %8.3f %8.3f\n", i, itc[i], mn[i], sdv[i]))
okB2 <- names(which.min(itc)) == "social_val3"
okB3 <- names(which.max(mn)) == "social_val3" && names(which.min(sdv)) == "social_val3"

cat(sprintf("\nA  live == source columns, 3/3: %s\n", ifelse(okA, "YES", "NO")))
cat(sprintf("B1 {social_val1,social_val2} is the pair matching alpha 0.822: %s\n",
            ifelse(okB1, "YES", "NO")))
cat(sprintf("B2 social_val3 is the weakest indicator (the removed PSV3): %s\n",
            ifelse(okB2, "YES", "NO")))
cat(sprintf("B3 social_val3 highest mean and smallest SD (easiest to endorse): %s\n",
            ifelse(okB3, "YES", "NO")))
cat("Published loadings PSV1 0.83 / PSV2 0.84 share an identical robust t of\n",
    "24.100, so they do NOT separate social_val1 from social_val2. This script\n",
    "pins bullet 3 only; the 1-vs-2 assignment rests on Table 1 bullet order.\n",
    "PARTIAL, not VERIFIED.\n", sep = "")

cat(if (okA && okB1 && okB2 && okB3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
