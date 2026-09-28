# verify_estrella_2023_hakim5.R -- item axis for estrella_2023_hakim5 (batch_ingest_0927).
#
# data/estrella_2023_hypermobility.py renames inclusion_hakim5_<i> -> hakim5_<i>
# (number-preserving). Route 9: each source column's 0/1 counts reproduce the
# table's counts for its own code. Five binary items can tie, so the check also
# reports whether each source column matches ONLY its own code.
TABLE <- "estrella_2023_hakim5"
here <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))))
src <- file.path(here, "..", "..", ".cache", "estrella_2023", "data.csv")
if (!file.exists(src)) download.file("https://osf.io/download/xenyq/", src, mode = "wb", quiet = TRUE)
s <- read.csv(src, colClasses = "character")
rd <- Sys.getenv("IRW_RESP_DIR")
d <- if (nzchar(rd)) read.csv(file.path(rd, paste0(TABLE, ".csv"))) else irw::irw_fetch(TABLE)
codes <- paste0("hakim5_", 1:5); cols <- paste0("inclusion_hakim5_", 1:5)
cnt <- function(x) c(sum(x == 0, na.rm = TRUE), sum(x == 1, na.rm = TRUE))
tab_live <- sapply(codes, function(i) cnt(d$resp[d$item == i]))
tab_src <- sapply(cols, function(c) cnt(suppressWarnings(as.integer(trimws(s[[c]])))))
hit <- lapply(1:5, function(k) which(apply(tab_live, 2, function(x) all(x == tab_src[, k]))))
for (k in 1:5) cat(sprintf("  %-18s no/yes %-12s -> %s\n", cols[k], paste(tab_src[, k], collapse = "/"),
                           paste(codes[hit[[k]]], collapse = ",")))
ok <- all(lengths(hit) == 1) && all(unlist(hit) == 1:5)
cat("every source column matches exactly one code, its own:", ok, "\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
