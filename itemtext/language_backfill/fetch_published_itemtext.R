suppressMessages(library(irw))
options(irw.itemtext_disclaimer = FALSE)
tg  <- read.csv("/tmp/claude-1000/itbf/targets.csv", stringsAsFactors=FALSE)
out <- "/tmp/claude-1000/itbf/text"
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
