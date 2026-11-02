## One-off back-fill of itemtext_metadata.FK_grade under the per-item,
## English-only definition in ../fk_grade.R (ben-domingue/irw#3229).
##
## Scores every table and writes each old/new pair to
## logs/fk_grade_backfill_<date>.csv; hotfixes/fk_grade_apply.py then patches
## ONLY the FK_grade cells of itemtext_metadata.csv from that log, leaving every
## other byte of the file alone (it is unquoted CRLF, which write.csv would not
## reproduce). Unlike
## 08_itemtext_recompute.R it does not rebuild the file, so the language columns
## (#3224) and anything else added since survive.
##
##   cd metadata && Rscript hotfixes/fk_grade_per_item.R
##   python3 hotfixes/fk_grade_apply.py logs/fk_grade_backfill_<date>.csv
##
## A table whose item text cannot be fetched keeps its old value and is logged
## with status "fetch_failed"; re-running retries only those.
suppressPackageStartupMessages({ library(quanteda); library(quanteda.textstats) })
source("fk_grade.R")

path <- "itemtext_metadata.csv"
d <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
stopifnot(all(c("table", "FK_grade", "language") %in% names(d)))

log_path <- file.path("logs", sprintf("fk_grade_backfill_%s.csv", Sys.Date()))
done <- if (file.exists(log_path)) read.csv(log_path, stringsAsFactors = FALSE) else
  data.frame(table = character(), old = numeric(), new = numeric(), english = logical(),
             status = character())
todo <- setdiff(d$table, done$table[done$status == "ok"])
cat(length(todo), "of", nrow(d), "tables to score\n")

for (ii in seq_along(todo)) {
  tab <- todo[ii]
  row <- match(tab, d$table)
  items <- tryCatch(irw::irw_itemtext(tab), error = function(e) NULL)
  if (is.null(items) || !nrow(items)) {
    done <- rbind(done[done$table != tab, ], data.frame(table = tab, old = d$FK_grade[row],
                  new = NA_real_, english = NA, status = "fetch_failed"))
  } else {
    translated <- "item_text_translated" %in% names(items)
    z <- as.character(if (translated) items$item_text_translated else items$item_text)
    eng <- fk_text_is_english(translated, d$language[row])
    new <- if (eng) fk_grade(z) else NA_real_
    done <- rbind(done[done$table != tab, ], data.frame(table = tab, old = d$FK_grade[row],
                  new = new, english = eng, status = "ok"))
  }
  if (ii %% 50 == 0 || ii == length(todo)) {
    write.csv(done, log_path, row.names = FALSE)
    cat(sprintf("[%d/%d] %s\n", ii, length(todo), tab))
  }
}

ok <- done[done$status == "ok", ]
cat(sprintf("scored %d tables; %d fetch failures; %d not English (will be NA)\n",
            nrow(ok), sum(done$status == "fetch_failed"), sum(ok$english == FALSE)))
cat("now apply it: python3 hotfixes/fk_grade_apply.py", log_path, "\n")
