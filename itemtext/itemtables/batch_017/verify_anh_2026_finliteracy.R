# verify_anh_2026_finliteracy.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: the eight rows of PLOS ONE 10.1371/journal.pone.0340002
# Table 3 headed "Financial literacy (FL) [40]" carry the wording of item codes
# FL1..FL8 in the live IRW table, in that order.
#
# WHY IT IS FALSIFIABLE: Table 3 publishes an outer loading per FL item.
# Loadings are a per-item quantity, so if two FL items' texts were swapped the
# published loading order would no longer track the order of the same items'
# discrimination computed from the response data. This script recomputes
# corrected item-total correlations from the study's own S1 data file and
# compares their ordering to the published loadings. It also reproduces the
# published Cronbach's alpha (.904), which is what pins WHICH eight of the 51
# S1 columns constitute the FL block -- i.e. the block boundary between the
# preceding FW block and the following DT block.
#
# QUOTA NOTE: this script does NOT call irw_fetch(). The live table is checked
# only through irw::irw_table_sets() (server-side aggregates), and the item-level
# statistics come from the S1 CSV, which data/anh_2026_finwellbeing.py melts
# verbatim into the live table (no filtering beyond dropping missing resp).

suppressMessages(library(irw))

TABLE <- "anh_2026_finliteracy"
ITEMS <- paste0("FL", 1:8)

# PLOS ONE 10.1371/journal.pone.0340002 Table 3, "Financial literacy (FL)" block.
PUB_LOADING <- c(0.739, 0.724, 0.750, 0.800, 0.767, 0.810, 0.788, 0.800)
PUB_ALPHA   <- 0.904
names(PUB_LOADING) <- ITEMS

S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0340002.s001")
CACHE <- ".cache/anh_2026_finliteracy/s001.csv"
path <- if (file.exists(CACHE)) CACHE else S1
d <- read.csv(path, stringsAsFactors = FALSE)
X <- d[, ITEMS]

# --- 1. Tie the S1 file to the live table (sets + per-item counts, no export) ---
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(pi$n, pi$item)[ITEMS]
s1_n   <- sapply(X, function(v) sum(!is.na(v)))
cat("-- S1 columns vs live per-item n --\n")
print(data.frame(item = ITEMS, s1_n = as.integer(s1_n), live_n = as.integer(live_n)))
tie_ok <- identical(sort(s$items), sort(ITEMS)) && all(s1_n == live_n) &&
          identical(sort(as.numeric(s$resp)), sort(as.numeric(unique(unlist(X)))))
cat("S1<->live tie (item set, per-item n, resp set): ", tie_ok, "\n\n", sep = "")

# --- 2. Block boundary: does this set of 8 columns reproduce the published alpha? ---
k <- length(ITEMS); tot <- rowSums(X)
alpha <- k/(k-1) * (1 - sum(apply(X, 2, var)) / var(tot))
cat(sprintf("Cronbach's alpha over FL1..FL8: observed %.4f vs published %.3f (diff %.4f)\n\n",
            alpha, PUB_ALPHA, alpha - PUB_ALPHA))

# --- 3. Mapping: published loading order vs observed discrimination order ---
itc <- sapply(ITEMS, function(i) cor(X[[i]], tot - X[[i]]))
cat("-- published outer loading vs corrected item-total correlation --\n")
print(data.frame(item = ITEMS,
                 pub_loading = PUB_LOADING,
                 corrected_itc = round(itc, 3),
                 rank_pub = rank(PUB_LOADING),
                 rank_itc = rank(itc), row.names = NULL))
pear <- cor(PUB_LOADING, itc)
spea <- cor(PUB_LOADING, itc, method = "spearman")
cat(sprintf("\nPearson  r(published loading, observed ITC) = %.3f over 8 items\n", pear))
cat(sprintf("Spearman r                                  = %.3f\n", spea))

# --- What this does NOT establish -------------------------------------------
cat("\nNOTE: FL4 and FL8 share a published loading of 0.800, so this route cannot\n",
    "separate those two items from each other. What does separate them -- and every\n",
    "other pair -- is the exemption recorded in provenance: Table 3 prints the literal\n",
    "code 'FL1'..'FL8' beside each item, and those codes ARE the S1 CSV column headers,\n",
    "which data/anh_2026_finwellbeing.py melts unchanged into the live `item` column.\n",
    "The statistics below are corroboration of a label match, not a substitute for one.\n",
    "This route says nothing about option_text: the 1='strongly disagree' /\n",
    "5='strongly agree' anchors come from the paper's Methods 3.3 and are not testable\n",
    "here, since the data are stored raw and no reverse-keyed FL item exists.\n", sep = "")

pass <- tie_ok && abs(alpha - PUB_ALPHA) < 0.01 && pear > 0.85
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
