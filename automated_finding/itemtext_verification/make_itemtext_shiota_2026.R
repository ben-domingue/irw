#!/usr/bin/env Rscript
## Item text for shiota_2026_dass21 (Zenodo 10.5281/zenodo.23890112, CC BY 4.0).
##
##   Rscript make_itemtext_shiota_2026.R <final.sav> <resp_csv> <out_dir>
##
## Cheap case (automated_finding Step 3.5). data/shiota_2026_support_seeking.py
## maps source columns dass<i>_w<w> -> item dass<i> (a number-preserving rename
## that drops the week suffix). Each stem is that column's own SPSS variable
## label; the anchors are its value labels, which the deposit writes as
## "<code>\n<label>" -- the leading code and newline are stripped. The script
## asserts that all four weekly copies of each item carry the identical
## variable and value labels before using week 1's.
## Read with haven because pyreadstat is not installed on this machine.
suppressMessages(library(haven))
args <- commandArgs(TRUE)
stopifnot(length(args) == 3)
sav <- args[1]; resp_csv <- args[2]; out_dir <- args[3]
tab <- "shiota_2026_dass21"

d <- read_sav(sav, n_max = 1)
vlab <- function(c) attr(d[[c]], "label")
vals <- function(c) attr(d[[c]], "labels")

rows <- list()
for (i in 1:21) {
  c1 <- sprintf("dass%d_w1", i)
  for (w in 2:4) {
    cw <- sprintf("dass%d_w%d", i, w)
    stopifnot(identical(vlab(cw), vlab(c1)), identical(vals(cw), vals(c1)))
  }
  v <- vals(c1)
  stopifnot(identical(unname(as.numeric(v)), c(1, 2, 3, 4)))
  opt <- trimws(sub("^[0-9]+\\s*\\n", "", names(v)))
  stopifnot(identical(opt, c("Not at all", "Rarely", "Sometimes", "Most of the time")))
  stem <- trimws(vlab(c1))
  for (k in seq_along(v)) {
    rows[[length(rows) + 1]] <- data.frame(
      table = tab, section_id = paste0(tab, "_1"), item = sprintf("dass%d", i),
      instrument = "Depression Anxiety Stress Scales, 21-item version (DASS-21), Lovibond & Lovibond (1995)",
      instructions = NA, section_prompt = NA, item_text = stem,
      correct_response = NA, option_text = opt[k], resp = as.integer(v[k]),
      stringsAsFactors = FALSE)
  }
}
out <- do.call(rbind, rows)

r <- read.csv(resp_csv, stringsAsFactors = FALSE)
stopifnot(setequal(unique(out$item), unique(r$item)),
          setequal(unique(out$resp), unique(r$resp)))
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
p <- file.path(out_dir, paste0(tab, "__items.csv"))
write.csv(out, p, row.names = FALSE, na = "NA")
cat(sprintf("%s: %d rows, %d items\n", basename(p), nrow(out), length(unique(out$item))))
