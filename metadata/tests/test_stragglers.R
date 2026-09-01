##Tests for 12_stragglers.R (issue #1765, sub-action 2.5b).
##
##Runs entirely offline via --live-from, so nothing here touches Redivis.
##Run it from the metadata/ directory:
##
##    Rscript tests/test_stragglers.R
##
##THE TEST THAT MATTERS is no_missing_tables(). The script spends most of its
##life with nothing missing -- that is the healthy state -- and the first real
##run against the live catalog failed there, because `last_seen = today` is a
##length-1 scalar that cannot recycle to zero rows. A straggler detector that
##crashes whenever there are no stragglers is worse than none: it would have
##been switched off before it ever fired.

failures <- 0L
check <- function(cond, what) {
    if (isTRUE(cond)) cat("  ok   -", what, "\n")
    else { cat("  FAIL -", what, "\n"); failures <<- failures + 1L }
}

tmp <- tempfile(); dir.create(tmp)
on.exit(unlink(tmp, recursive = TRUE), add = TRUE)
SCRIPT <- normalizePath("12_stragglers.R")

##A metadata.csv large enough to clear --min-live, plus a live list on top.
setup <- function(described, live) {
    d <- file.path(tmp, basename(tempfile())); dir.create(d)
    writeLines(c("table", described), file.path(d, "metadata.csv"))
    writeLines(live, file.path(d, "live.txt"))
    d
}
run <- function(d, ...) {
    out <- suppressWarnings(system2(
        "Rscript", c(SCRIPT, "--dir", d, "--watch", file.path(d, "watch.tsv"),
                     "--live-from", file.path(d, "live.txt"), ...),
        stdout = TRUE, stderr = TRUE))
    list(out = paste(out, collapse = "\n"),
         status = attr(out, "status") %||% 0L)
}
`%||%` <- function(a, b) if (is.null(a)) b else a
watch_rows <- function(d) {
    f <- file.path(d, "watch.tsv")
    if (!file.exists(f)) return(NULL)
    read.delim(f, colClasses = "character")
}

BULK <- paste0("described_", seq_len(1200))

cat("\nthe healthy state\n")
d <- setup(BULK, BULK)
r <- run(d)
check(r$status == 0L, "no missing tables: exits 0")
check(grepl("no stragglers", r$out), "no missing tables: reports no stragglers")
check(!is.null(watch_rows(d)) && nrow(watch_rows(d)) == 0L,
      "no missing tables: writes an empty watch file rather than crashing")

cat("\naccumulation and the threshold\n")
d <- setup(BULK, c(BULK, "stuck_one", "stuck_two"))
r1 <- run(d); r2 <- run(d)
check(r1$status == 0L && r2$status == 0L,
      "a table missing for 2 runs is not yet reported (that is the throttle)")
r3 <- run(d)
check(r3$status == 1L, "a table missing for a 3rd run exits non-zero")
check(grepl("stuck_one", r3$out) && grepl("stuck_two", r3$out),
      "stragglers are named, not counted")
check(grepl("first seen", r3$out), "each straggler reports how long it has waited")
check(nrow(watch_rows(d)) == 2L, "the watch file carries both tables")

cat("\nresolution\n")
writeLines(c("table", BULK, "stuck_one"), file.path(d, "metadata.csv"))
r <- run(d)
check(grepl("1 resolved", r$out), "a table that gains a metadata row is counted as resolved")
w <- watch_rows(d)
check(nrow(w) == 1L && w$table == "stuck_two",
      "a resolved table is dropped from the watch, silently")

cat("\nguards\n")
d2 <- setup(BULK, c(BULK, "STUCK_ONE"))
writeLines(c("table", BULK, "stuck_one"), file.path(d2, "metadata.csv"))
r <- run(d2)
check(grepl("0 awaiting metadata", r$out),
      "a live table matching its metadata row only by case is not a straggler")

before <- watch_rows(d)
writeLines(head(BULK, 5), file.path(d, "live.txt"))
r <- run(d)
check(r$status != 0L && grepl("Refusing to update", r$out),
      "a truncated live catalog is refused, not believed")
check(identical(watch_rows(d), before),
      "a truncated live catalog leaves the watch file untouched")

cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all tests passed\n")
