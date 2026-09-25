# Step 5b verification for lunacortes_2019_interperson_conn.
#
# THE MAPPING CLAIM, in two links.
#
#  LINK A (code -> data column). ic_1..ic_4 are a mechanical lowercase/space->_
#  rename of the S1 File XLSX headers "IC 1".."IC 4"
#  (data/lunacortes_2019_vsn_scales.py melts BY NAME, no positional step).
#  Prediction: each live item is cell-for-cell identical to its namesake column.
#
#  LINK B (column -> wording). PLOS Table 1 prints the four Interpersonal
#  Connections [IC] items as an UNNUMBERED bullet list; bullet order is taken as
#  the IC1..IC4 numbering Table 2 uses. Table 2 publishes loadings IC1 0.62,
#  IC2 0.87, IC3 0.90, IC4 0.86 and alpha 0.937. IC1 stands apart (0.24 below
#  the next), so the falsifiable prediction is that ic_1 is the WEAKEST
#  indicator in the live data (lowest 1-factor loading AND lowest corrected
#  item-total r). The 4-item alpha matching 0.937 confirms the block identity
#  (this is the IC scale) but not order within it.
#
# WHAT THIS DOES NOT ESTABLISH: ic_2, ic_3 and ic_4 are not separated. Their
# published loadings (0.87/0.90/0.86) are near-tied, and the observed 1-factor
# loadings (~0.909/0.907/0.893) are too; the observed ic_2 vs ic_3 order is even
# the reverse of the published one by a 0.002 margin, which a full-model robust
# CFA vs a 1-factor ML fit can easily produce. Their assignment rests on bullet
# order alone. Hence PARTIAL, not VERIFIED.
#
# COST NOTE: irw_fetch() is used deliberately (1,776 rows; locally cached by
# irw >= 1.3), because link A is a cell-for-cell comparison.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "lunacortes_2019_interperson_conn"
ITEMS <- paste0("ic_", 1:4)
SRC   <- paste0("IC ", 1:4)
PUB_LOAD  <- c(ic_1 = 0.62, ic_2 = 0.87, ic_3 = 0.90, ic_4 = 0.86)  # PLOS t002
PUB_ALPHA <- 0.937

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
    cat(sprintf("%-5s vs '%s'  n=%d  identical=%s\n", ITEMS[i], SRC[i],
                sum(!is.na(a)), ifelse(same, "YES", "NO")))
}

X <- as.data.frame(sapply(ITEMS, function(i) as.numeric(w[[i]])))
alpha <- function(m) { m <- as.matrix(m); k <- ncol(m)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
a4 <- alpha(X)
lam <- factanal(X, 1)$loadings[, 1]
itc <- sapply(ITEMS, function(i) cor(X[[i]], rowSums(X[, setdiff(ITEMS, i)])))

cat(sprintf("\n== LINK B ==\n4-item alpha = %.4f (published %.3f)\n", a4, PUB_ALPHA))
cat(sprintf("%-5s %9s %9s %11s %7s %7s\n", "item", "pub_load", "obs_load",
            "item-total", "mean", "sd"))
for (i in ITEMS)
    cat(sprintf("%-5s %9.2f %9.3f %11.4f %7.3f %7.3f\n", i, PUB_LOAD[i], lam[i],
                itc[i], mean(X[[i]]), sd(X[[i]])))

okAlpha <- abs(a4 - PUB_ALPHA) < 0.005
okB <- names(which.min(lam)) == "ic_1" && names(which.min(itc)) == "ic_1"
cat(sprintf("\nA  live == source columns, 4/4: %s\n", ifelse(okA, "YES", "NO")))
cat(sprintf("   4-item alpha reproduces 0.937 (block identity only): %s\n",
            ifelse(okAlpha, "YES", "NO")))
cat(sprintf("B  ic_1 is the weakest indicator (published IC1 0.62): %s\n",
            ifelse(okB, "YES", "NO")))
cat("Does NOT establish: the ic_2/ic_3/ic_4 assignment (published 0.87/0.90/0.86,\n",
    "observed near-tied); that rests on Table 1 bullet order. PARTIAL, not VERIFIED.\n",
    sep = "")

cat(if (okA && okAlpha && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
