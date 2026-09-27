# verify_robie_2022_cab.R -- item axis for robie_2022_cab (batch_ingest_0927).
#
# data/robie_2022_response_order.py assigns codes POSITIONALLY: source Q126..Q150
# -> cab_1..cab_25 by enumerate(). Two checks:
#   1. header diff: the shipped item_text of cab_k equals the merge.sav variable
#      label of Q(125+k), for all 25;
#   2. route 9: each source column's response counts (1-6) reproduce the table's
#      counts for the code it was assigned, and no other code's counts.
# Response data: $IRW_RESP_DIR/<table>.csv while the table is only in a draft;
# irw_fetch() once released. Source: itemtext/.cache/robie_2022_cab/merge.sav
# (OSF ck5xm, https://osf.io/download/dfvme/).
suppressMessages({library(haven)})
TABLE <- "robie_2022_cab"
here <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))))
it <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
sav <- file.path(here, "..", "..", ".cache", TABLE, "merge.sav")
if (!file.exists(sav)) download.file("https://osf.io/download/dfvme/", sav, mode = "wb", quiet = TRUE)
s <- read_sav(sav)
rd <- Sys.getenv("IRW_RESP_DIR")
d <- if (nzchar(rd)) read.csv(file.path(rd, paste0(TABLE, ".csv"))) else irw::irw_fetch(TABLE)

ok <- TRUE
cat("1. header diff (shipped item_text vs .sav label at the assigned position)\n")
nmatch <- 0
for (k in 1:25) {
    src <- paste0("Q", 125 + k)
    lab <- attr(s[[src]], "label")
    txt <- unique(it$item_text[it$item == paste0("cab_", k)])
    m <- length(txt) == 1 && identical(txt, lab)
    nmatch <- nmatch + m
    if (!m) cat("  MISMATCH", src, "cab_", k, "\n")
}
cat(sprintf("  %d/25 identical\n", nmatch)); ok <- ok && nmatch == 25

cat("2. response counts, source column vs table code (levels 1-6)\n")
tab_live <- sapply(paste0("cab_", 1:25), function(i) tabulate(d$resp[d$item == i], 6))
tab_src <- sapply(paste0("Q", 126:150), function(c) tabulate(as.integer(s[[c]]), 6))
hit <- sapply(1:25, function(k) which(apply(tab_live, 2, function(x) all(x == tab_src[, k]))))
for (k in 1:25) cat(sprintf("  Q%d  %-28s -> %s\n", 125 + k,
                            paste(tab_src[, k], collapse = "/"), paste0("cab_", hit[[k]], collapse = ",")))
uniq <- all(lengths(hit) == 1) && all(unlist(hit) == 1:25)
cat(sprintf("  every source column matches exactly one code, its own: %s\n", uniq))
ok <- ok && uniq
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
