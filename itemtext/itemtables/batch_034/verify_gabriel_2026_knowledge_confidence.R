# verify_gabriel_2026_knowledge_confidence.R
#
# CLAIM UNDER TEST -- two mappings, both from the S2 Dataset's own codebook:
#   (a) item conf_N carries the variable label of source column Q21_SQ00N#1,
#       i.e. knowledge statement N of Gabriel & Bitsch (2026) Table 2;
#   (b) resp 1..6 are the six German confidence anchors in ascending order,
#       "50% (da muss ich raten)" .. "100 % (das weiss ich sicher)".
#
# ROUTE 9 (response-frequency matching). The deposit's Data_label sheet stores
# the German ANCHOR STRINGS for the same 2022 respondents the IRW table stores
# as integers. So for every one of the 9 x 6 = 54 item x level cells, the count
# of respondents choosing anchor k on statement N must equal the live count of
# resp=k on item conf_N. A swapped pair of items, or any permuted/flipped level,
# breaks cells immediately. The 9 items' 6-cell count vectors are also mutually
# distinct, which is what makes the item axis identified rather than merely
# consistent.
#
# The live side is read with a server-side GROUP BY (no irw_fetch export).

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "gabriel_2026_knowledge_confidence"
CACHE <- file.path(dirname(normalizePath(sub("^--file=", "",
           commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1]))),
           "..", "..", ".cache", TABLE)
XLSX  <- file.path(CACHE, "S2.xlsx")
URL   <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0341457.s002&type=supplementary"

if (!file.exists(XLSX)) {
    dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
    download.file(URL, XLSX, mode = "wb", quiet = TRUE)
}

ANCHORS <- c("50% (da muss ich raten)", "60%", "70%", "80%", "90%",
             "100 % (das weiß ich sicher)")   # resp 1..6, in that order

lab <- readxl::read_excel(XLSX, sheet = "Data_label")

# source side: 9 x 6 count matrix
src <- matrix(0L, 9, 6, dimnames = list(paste0("conf_", 1:9), 1:6))
for (n in 1:9) {
    v <- lab[[sprintf("Q21_SQ00%d#1", n)]]
    v <- v[!is.na(v)]
    src[n, ] <- as.integer(sapply(ANCHORS, function(a) sum(v == a)))
}

# live side, server-side aggregate
tblref <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
q <- irw:::.irw_query_tibble(sprintf(
  "SELECT CAST(item AS STRING) AS item, TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n FROM `%s` WHERE resp IS NOT NULL GROUP BY 1,2",
  tblref$qualified_reference))
live <- matrix(0L, 9, 6, dimnames = dimnames(src))
for (i in seq_len(nrow(q))) live[q$item[i], as.character(as.integer(q$resp[i]))] <- as.integer(q$n[i])

cat("anchor order tested (resp 1..6):\n  ", paste(ANCHORS, collapse = " | "), "\n\n", sep = "")
cat(sprintf("%-8s %-29s %-29s\n", "item", "source label counts (1..6)", "live resp counts (1..6)"))
for (n in 1:9)
    cat(sprintf("%-8s %-29s %-29s %s\n", rownames(src)[n],
        paste(src[n, ], collapse = "/"), paste(live[n, ], collapse = "/"),
        if (all(src[n, ] == live[n, ])) "match" else "MISMATCH"))

cells_ok <- sum(src == live)
cat(sprintf("\ncells matching: %d of 54\n", cells_ok))

# identification: are the 9 count vectors distinct from one another?
vecs <- apply(src, 1, paste, collapse = "/")
cat(sprintf("distinct source count vectors across the 9 items: %d of 9\n", length(unique(vecs))))

# how badly a swap would show: worst off-diagonal comparison
best_wrong <- max(sapply(1:9, function(a) max(sapply(setdiff(1:9, a),
                  function(b) sum(src[a, ] == live[b, ])))))
cat(sprintf("best cell agreement any MIS-matched item pair achieves: %d of 6\n", best_wrong))

cat("\nWhat this does NOT establish: it verifies the code->column and the anchor\n",
    "ordering, not the German->English wording of item_text (the deposit and the\n",
    "paper publish only the authors' English for the statements; the administered\n",
    "German statement wording is not in either).\n", sep = "")

cat(if (cells_ok == 54 && length(unique(vecs)) == 9) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
