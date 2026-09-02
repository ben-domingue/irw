suppressMessages(library(irw))
options(irw.itemtext_disclaimer = FALSE)
# Paths default beside this script rather than into a /tmp scratch directory that
# does not survive the session, which is what made the round 1 check un-rerunnable (#1811).
# works under Rscript (--file=) and under source() alike
.a   <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
here <- if (length(.a)) dirname(normalizePath(sub("^--file=", "", .a[1]))) else getwd()
targets <- Sys.getenv("ITBF_TARGETS", file.path(here, "targets.csv"))
tg  <- read.csv(targets, stringsAsFactors=FALSE)
out <- Sys.getenv("ITBF_SRC", file.path(here, "published"))
dir.create(out, showWarnings=FALSE, recursive=TRUE)
for (i in seq_len(nrow(tg))) {
  tb <- tg$table[i]
  f  <- file.path(out, paste0(tb, ".csv"))
  if (file.exists(f)) next
  x <- try(irw_itemtext(tb), silent=TRUE)
  if (inherits(x, "try-error")) {
    cat(sprintf("%d/%d ERR %s\n", i, nrow(tg), tb))
    writeLines(as.character(x), file.path(out, paste0(tb, ".ERR")))
  } else {
    write.csv(x, f, row.names=FALSE, fileEncoding="UTF-8")
    cat(sprintf("%d/%d ok  %s (%d)\n", i, nrow(tg), tb, nrow(x)))
  }
}
cat("DONE\n")
