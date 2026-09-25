# Step 5b verification for lunacortes_2019_self_congruity.
# (Copied from references/verify_template.R.)
#
# THE MAPPING CLAIM, in two links.
#
#  LINK A (code -> data column). self_cong1..self_cong4 are a mechanical
#  lowercase/'-'->'_' rename of the S1 File XLSX headers "Self-Cong1".."Self-Cong4"
#  (data/lunacortes_2019_vsn_scales.py melts BY NAME, no positional step).
#  Prediction: each live item is cell-for-cell identical to its namesake column.
#
#  LINK B (column -> wording). PLOS Table 1 prints the four Self-congruity
#  [SELFCON] items as an UNNUMBERED bullet list; bullet order is taken as the
#  SELFCON1..SELFCON4 numbering of Table 2. Table 2 publishes loadings
#  SELFCON1 0.73, SELFCON2 0.72, SELFCON3 0.95, SELFCON4 0.95 and alpha 0.724.
#  Falsifiable prediction: {self_cong3, self_cong4} are the two strongest
#  indicators in the live data and {self_cong1, self_cong2} the two weakest,
#  on BOTH a 1-factor loading and corrected item-total r. The 4-item alpha
#  matching 0.724 confirms block identity only.
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN each pair. Published loadings are
# tied (0.95/0.95) or near-tied (0.73/0.72), so 1<->2 and 3<->4 swaps are
# undetectable; those rest on Table 1 bullet order alone. PARTIAL, not VERIFIED.
# A random assignment would pass the pair test with probability 1/6.
#
# COST NOTE: irw_fetch() is used deliberately (1,776 rows; locally cached by
# irw >= 1.3), because link A is a cell-for-cell comparison.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "lunacortes_2019_self_congruity"
ITEMS <- paste0("self_cong", 1:4)
SRC   <- paste0("Self-Cong", 1:4)
PUB_LOAD  <- c(self_cong1 = 0.73, self_cong2 = 0.72, self_cong3 = 0.95, self_cong4 = 0.95)  # PLOS t002
PUB_ALPHA <- 0.724
STRONG <- c("self_cong3", "self_cong4")

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

cat("== LINK A: live column vs its namesake S1 File column ==\n")
okA <- TRUE
for (i in seq_along(ITEMS)) {
    a <- as.numeric(w[[ITEMS[i]]]); b <- as.numeric(raw[[SRC[i]]])
    same <- length(a) == length(b) && all(a == b)
    okA <- okA && same
    cat(sprintf("%-10s vs '%s'  n=%d  identical=%s\n", ITEMS[i], SRC[i],
                sum(!is.na(a)), ifelse(same, "YES", "NO")))
}

X <- as.data.frame(sapply(ITEMS, function(i) as.numeric(w[[i]])))
alpha <- function(m) { m <- as.matrix(m); k <- ncol(m)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
a4 <- alpha(X)
lam <- factanal(X, 1)$loadings[, 1]
itc <- sapply(ITEMS, function(i) cor(X[[i]], rowSums(X[, setdiff(ITEMS, i)])))

cat(sprintf("\n== LINK B ==\n4-item alpha = %.4f (published %.3f)\n", a4, PUB_ALPHA))
cat(sprintf("%-10s %9s %9s %11s %7s %7s\n", "item", "pub_load", "obs_load",
            "item-total", "mean", "sd"))
for (i in ITEMS)
    cat(sprintf("%-10s %9.2f %9.3f %11.4f %7.3f %7.3f\n", i, PUB_LOAD[i], lam[i],
                itc[i], mean(X[[i]]), sd(X[[i]])))

top2 <- function(v) sort(names(sort(v, decreasing = TRUE))[1:2])
okAlpha <- abs(a4 - PUB_ALPHA) < 0.005
okB <- identical(top2(lam), STRONG) && identical(top2(itc), STRONG)
cat(sprintf("\nA  live == source columns, 4/4: %s\n", ifelse(okA, "YES", "NO")))
cat(sprintf("   4-item alpha within 0.005 of 0.724 (block identity only): %s\n",
            ifelse(okAlpha, "YES", "NO")))
cat(sprintf("B  top-2 indicators are {self_cong3, self_cong4} on loading (%s) and item-total (%s): %s\n",
            paste(top2(lam), collapse = ","), paste(top2(itc), collapse = ","),
            ifelse(okB, "YES", "NO")))
cat("Does NOT establish: order within {1,2} or within {3,4}; that rests on\n",
    "Table 1 bullet order. PARTIAL, not VERIFIED.\n", sep = "")

cat(if (okA && okAlpha && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
