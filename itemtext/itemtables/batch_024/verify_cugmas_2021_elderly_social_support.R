# verify_cugmas_2021_elderly_social_support.R
#
# CLAIM UNDER TEST: each IRW item code (partner, child, grandchild,
# other_relative, friend, neighbour, other) carries the relationship-category
# wording of the SAME column in the study's S1 Data SPSS file -- whose variable
# labels read "Number of alters: partner", "... child", etc.
#
# The falsifiable prediction: the count distribution of every source column must
# reproduce the live IRW table's counts for the item code it was mapped to,
# cell for cell, AND the seven distributions must be mutually distinct so that a
# permutation of any two item codes would break the match. Both are printed.
#
# Live data is read with a SERVER-SIDE GROUP BY (redivis query), not irw_fetch(),
# so this costs no export quota.

suppressMessages({library(haven); library(redivis)})

TABLE <- "cugmas_2021_elderly_social_support"
LIVE  <- "datapages.item_response_warehouse_3:5xaj:v4_0.cugmas_2021_elderly_social_support:dsy4"
URL   <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0247993.s001")
ITEMS <- c("partner","child","grandchild","other_relative","friend","neighbour","other")

tmp <- tempfile(fileext = ".sav")
download.file(URL, tmp, quiet = TRUE, mode = "wb",
              headers = c("User-Agent" = "IRW-itemtext/1.0"))
sav <- haven::read_sav(tmp)

cat("-- S1 Data SPSS variable labels for the seven mapped columns --\n")
for (v in ITEMS)
    cat(sprintf("  %-15s %s\n", v, attr(sav[[v]], "label")))

src <- do.call(rbind, lapply(ITEMS, function(v) {
    x <- as.numeric(sav[[v]]); x <- x[!is.na(x)]
    data.frame(item = v, resp = as.integer(names(table(x))),
               n_src = as.integer(table(x)), stringsAsFactors = FALSE)
}))

live <- redivis$query(sprintf(
    "SELECT item, CAST(resp AS INT64) resp, COUNT(*) n_live FROM `%s` GROUP BY 1,2", LIVE))$to_data_frame()

m <- merge(src, live, by = c("item","resp"), all = TRUE)
m$n_src[is.na(m$n_src)] <- 0L; m$n_live[is.na(m$n_live)] <- 0L
m <- m[order(match(m$item, ITEMS), m$resp), ]

cat("\n-- source column counts vs live IRW counts, per item x resp cell --\n")
cat(sprintf("%-15s %5s %8s %8s\n", "item", "resp", "source", "live"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-15s %5d %8d %8d%s\n", m$item[i], m$resp[i], m$n_src[i], m$n_live[i],
                if (m$n_src[i] != m$n_live[i]) "   <-- MISMATCH" else ""))

cells_ok <- all(m$n_src == m$n_live)
cat(sprintf("\ncells compared: %d | mismatched: %d\n", nrow(m), sum(m$n_src != m$n_live)))

# Distinctness: could any two item codes be swapped without breaking the match?
sig <- lapply(ITEMS, function(v) {
    s <- m[m$item == v, c("resp","n_src")]
    setNames(s$n_src, s$resp)
})
names(sig) <- ITEMS
allresp <- sort(unique(m$resp))
mat <- sapply(sig, function(s) { v <- setNames(rep(0L, length(allresp)), allresp)
                                 v[names(s)] <- s; v })
dupes <- sum(duplicated(t(mat)))
cat(sprintf("distinct count-vectors among the %d items: %d (duplicates: %d)\n",
            length(ITEMS), length(ITEMS) - dupes, dupes))

cat("Note: this pins which SOURCE COLUMN each live item code was built from, and the\n",
    "column's own SPSS label names its relationship type -- so the item<->text tie is\n",
    "settled at the source. It does NOT check the Slovenian wording shipped in item_text,\n",
    "which was transcribed from the S1 Questionnaire's relationship-category list; nor\n",
    "does it check option_text, which is empty because resp is an unlabelled alter count.\n", sep = "")

cat(if (cells_ok && dupes == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
