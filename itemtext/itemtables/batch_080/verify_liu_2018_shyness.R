# verify_liu_2018_shyness.R -- Step 5b evidence, re-runnable.
#
# mapping_basis is data_labels, so the item_text<->item axis is exempt at the
# source: every header cell of the PLOS deposit (journal.pone.0194559.s002,
# .xlsx) carries an Excel CELL COMMENT giving that column's item sentence
# (xl/comments1.xml, cells M1..Y1 for Shyness01..Shyness13), and
# data/liu_2018_shyness_battery.py melts that explicit by-name column list with
# var_name = "item", so the IRW item code IS the commented column name.
# This script exists anyway because the OTHER axis -- option_text <-> resp --
# carried a real inference: the four reverse-worded RCBS items are stored
# ALREADY REVERSE-CODED, so their shipped anchors run 1 = "very characteristic
# or true" .. 5 = "very uncharacteristic or untrue" while the other nine run the
# paper's stated 1 = "very uncharacteristic or untrue" .. 5 = "very
# characteristic or true".
#
# Three checks, all on LIVE IRW data (the S2 workbook is used only for the SEM
# parcel columns, which IRW does not carry):
#   A. Cronbach's alpha of the 13 items AS STORED vs the paper's published .91,
#      and the same alpha with 3/6/9/12 un-reversed.
#   B. corrected item-total correlations -- all 13 must be positive if the
#      reverse items are already reversed.
#   C. parcel reconstruction: the workbook's own shyness_1/2/3 columns (whose
#      Excel comments define them as means of named Shyness columns) are
#      reproduced from the LIVE items, tying live codes to deposit columns
#      end-to-end rather than assuming the tie.
#
# What this does NOT establish: nothing about the item wording itself beyond the
# reverse/forward split -- that comes from the cell comments, not from here.

suppressMessages(library(irw))

TABLE <- "liu_2018_shyness"
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0194559.s002")
PUBLISHED_ALPHA <- 0.91   # Liu et al. 2018, Measures: "In the current study,
                          # the internal consistency was .91."
TOL <- 0.01

items <- sprintf("Shyness%02d", 1:13)
rev_items <- sprintf("Shyness%02d", c(3, 6, 9, 12))

d <- irw::irw_fetch(TABLE)
W <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(W) <- sub("^resp\\.", "", names(W))
W <- W[order(W$id), ]
X <- W[, items]
cat(sprintf("live table: %d respondents x %d items\n", nrow(X), ncol(X)))

alpha <- function(M) {
    M <- M[complete.cases(M), , drop = FALSE]
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}

# --- A. alpha as stored vs un-reversed ---------------------------------------
Xun <- X
Xun[, rev_items] <- 6 - Xun[, rev_items]
a_stored <- alpha(X); a_un <- alpha(Xun)
cat("\nA. Cronbach's alpha of the 13 items\n")
cat(sprintf("   as stored in IRW        : %.4f   (published %.2f, |diff| %.4f)\n",
            a_stored, PUBLISHED_ALPHA, abs(a_stored - PUBLISHED_ALPHA)))
cat(sprintf("   with 3/6/9/12 un-reversed: %.4f\n", a_un))
okA <- abs(a_stored - PUBLISHED_ALPHA) <= TOL && a_stored - a_un > 0.3

# --- B. corrected item-total correlations ------------------------------------
cat("\nB. corrected item-total correlations (stored vs un-reversed)\n")
tot <- rowSums(X)
itc <- sapply(items, function(i) cor(X[[i]], tot - X[[i]]))
totu <- rowSums(Xun)
itcu <- sapply(items, function(i) cor(Xun[[i]], totu - Xun[[i]]))
for (i in items)
    cat(sprintf("   %-10s %s  stored %+.3f   un-reversed %+.3f\n",
                i, if (i %in% rev_items) "[rev]" else "     ", itc[i], itcu[i]))
okB <- all(itc > 0) && all(itcu[rev_items] < 0)
cat(sprintf("   all 13 positive as stored: %s ; all four reverse items negative when un-reversed: %s\n",
            all(itc > 0), all(itcu[rev_items] < 0)))

# --- C. parcel reconstruction from live items --------------------------------
tf <- tempfile(fileext = ".xlsx")
download.file(S2, tf, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tf))
raw <- raw[order(raw$Serial_number), ]
stopifnot(identical(as.integer(raw$Serial_number), as.integer(W$id)))
parcels <- list(shyness_1 = c(1, 2, 4, 5, 7),
                shyness_2 = c(3, 6, 9, 12),
                shyness_3 = c(8, 10, 11, 13))
cat("\nC. authors' SEM parcels (S2 workbook) vs means of the LIVE items\n")
worstC <- 0
for (p in names(parcels)) {
    cc <- sprintf("Shyness%02d", parcels[[p]])
    dev <- max(abs(rowMeans(X[, cc]) - raw[[p]]))
    worstC <- max(worstC, dev)
    cat(sprintf("   %-10s = mean(%s)   max|deviation| over %d rows = %.2e\n",
                p, paste(cc, collapse = ", "), nrow(X), dev))
}
okC <- worstC < 1e-9

cat("\nNote: A and B establish that the four reverse-worded items are stored already\n")
cat("reversed (hence their reversed anchors); C ties the live item codes to the\n")
cat("deposit columns the cell comments are attached to. The wording itself comes\n")
cat("from those comments and is not tested here.\n")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
