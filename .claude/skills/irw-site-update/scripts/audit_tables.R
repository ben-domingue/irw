#!/usr/bin/env Rscript
## Cross-table consistency audit for the IRW metadata/tags/biblio pipeline.
##
## Generalizes metadata/04_tables.R's presence-matrix idea (its `x`/`zz`
## objects) from core-only to all four Redivis sources (core/comp/nom/sim),
## using irw::irw_list_tables(source=...) as ground truth instead of raw
## Redivis calls -- same accessor the tags/itemtext skills already depend on.
##
## Produces a FRESH report every run (nothing persisted/tracked across runs
## -- Ben triages the current list by hand each time, so there is no queue
## file here unlike tags/tags_queue_staging.csv or
## automated_finding/license_blocked_candidates.csv).
##
## REQUIRES workflow 1 (scripts/run_pipeline.sh) to have already been run in
## this same directory (Ben, 2026-07-27): this script reads the local
## metadata/biblio/tags CSVs as-is, it does NOT fetch or regenerate them from
## Redivis itself -- only irw::irw_list_tables() (ground truth for what's
## live) is fetched remotely. Running the audit against a stale or missing
## local CSV will misreport those tables as absent everywhere.
##
## Usage (run from metadata/, same convention as the numbered pipeline scripts):
##   cd metadata
##   ../.claude/skills/irw-site-update/scripts/run_pipeline.sh   # generate fresh CSVs first
##   Rscript ../.claude/skills/irw-site-update/scripts/audit_tables.R
## Optional: --dir <path>          (defaults to cwd, i.e. metadata/)
##           --out <path>          (markdown report; default table_audit_report.md)
##           --skip-dict           (skip the four Google Sheet dictionary pulls -- faster, less complete)
##
## Bucket A reproduces `zz` from metadata/04_tables.R exactly (confirmed with
## Ben, 2026-07-28, after a first attempt at generalizing it -- present in
## ANY fewer than all sources -- turned out far noisier than what `zz` ever
## showed: 805 "incomplete" rows, most of it uninformative). `zz`'s actual
## rule, from the source:
##   n<-rowSums(x[,-1],na.rm=TRUE); z<-x[n<4,]              # missing >=2 of 5
##   tmp<-z[,-6]; nn<-rowSums(is.na(tmp)); zz<-z[nn<4,]      # drop tag-only rows
## i.e. (a) missing at least 2 of the applicable sources -- not just 1 -- and
## (b) drop rows where the ONLY source present is tags_csv (Ben: "I
## definitely don't want tag only"). Both are applied below, generalized
## from `zz`'s core-only 5-column shape to all four sources' own column
## counts. Output is the same wide 1/blank-per-source shape `zz` had --
## `present_in`/`missing_from` string columns are gone.
##
## Near-duplicate/inconsistent-name detection (edit distance across the full
## table universe) is deliberately NOT implemented yet -- an earlier attempt
## was almost entirely false positives (subscale/batch-suffix variants like
## algner2022_cse vs algner2022_oss, not real naming inconsistencies). Ben,
## 2026-07-27: hold off until there are real incomplete-coverage examples to
## look at together before designing that detector.

## Load REDIVIS_API_TOKEN from a dedicated file rather than relying on it
## being set in ~/.Renviron (2026-07-28: that also leaks into Ben's plain
## interactive `R` sessions and triggers the redivis package's "deprecated
## and highly discouraged" interactive-token warning -- see run_pipeline.sh
## for the matching fix on that entry point). Bare token value only, no
## `REDIVIS_API_TOKEN=` prefix. An already-set env var wins; a missing file
## is not fatal -- redivis falls back to cached OAuth credentials at
## ~/.redivis/r_credentials.
if (identical(Sys.getenv("REDIVIS_API_TOKEN"), "")) {
  token_file <- path.expand(Sys.getenv("REDIVIS_TOKEN_FILE", "~/.redivis_api_token"))
  if (file.exists(token_file)) {
    Sys.setenv(REDIVIS_API_TOKEN = trimws(readLines(token_file, n = 1, warn = FALSE)))
  }
}

suppressMessages({
  library(irw)
  library(dplyr)
  library(readr)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
dir_path   <- get_arg("--dir", ".")
out_path   <- get_arg("--out", file.path(dir_path, "table_audit_report.md"))
skip_dict  <- "--skip-dict" %in% args

sources <- c("core", "comp", "nom", "sim")

metadata_csvs <- c(core = "metadata.csv", comp = "comps_metadata.csv",
                    nom  = "nominal_metadata.csv", sim  = "simsyn_metadata.csv")
biblio_csvs   <- c(core = "biblio.csv", comp = "comps_biblio.csv",
                    nom  = "nominal_biblio.csv", sim  = "simsyn_biblio.csv")
tags_csv_path <- "tags.csv"  # single flat sheet; no per-source equivalent for comp/nom/sim

## Same four dictionary sheets 02_biblio.R already reads per source.
dict_urls <- c(
  core = "https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315",
  comp = "https://docs.google.com/spreadsheets/d/1WZZYyVC2cmw8CUJM69qP0F_ZlQjQfdkCZbdsG-8mUrs/edit?gid=1337607315#gid=1337607315",
  nom  = "https://docs.google.com/spreadsheets/d/12tM4vADKcUm5LGOGRwQ5_HKkdYa3mZUaKbFUqgs2U_w/edit?gid=1337607315#gid=1337607315",
  sim  = "https://docs.google.com/spreadsheets/d/1_2SR1_miAqUy0HWFQqo5vrBVrIN4V1FU6RfavBc7WdA/edit?gid=1337607315#gid=1337607315"
)

lc <- function(x) tolower(trimws(as.character(x)))

get_live <- function(src) {
  out <- tryCatch(irw::irw_list_tables(source = src), error = function(e) {
    message("  ! irw_list_tables(source='", src, "') failed: ", conditionMessage(e))
    NULL
  })
  if (is.null(out)) return(character(0))
  lc(out$name)
}

get_dict <- function(src) {
  if (skip_dict) return(NULL)
  tab <- tryCatch(gsheet::gsheet2tbl(dict_urls[[src]]), error = function(e) {
    message("  ! dictionary sheet fetch failed for '", src, "': ", conditionMessage(e))
    NULL
  })
  if (is.null(tab) || !"table" %in% names(tab)) return(NULL)
  if ("Public Reshare?" %in% names(tab)) tab <- tab[tab$`Public Reshare?` == "Public", ]
  lc(tab$table)
}

read_table_col <- function(path) {
  full <- file.path(dir_path, path)
  if (!file.exists(full)) return(character(0))
  df <- suppressMessages(readr::read_csv(full, show_col_types = FALSE))
  if (!"table" %in% names(df)) return(character(0))
  lc(df$table)
}

message("Fetching live Redivis table lists (irw::irw_list_tables) ...")
live  <- setNames(lapply(sources, get_live), sources)
message("Fetching dictionary sheets ...")
dict  <- setNames(lapply(sources, get_dict), sources)
meta  <- setNames(lapply(sources, function(s) read_table_col(metadata_csvs[[s]])), sources)
bib   <- setNames(lapply(sources, function(s) read_table_col(biblio_csvs[[s]])), sources)
tags  <- read_table_col(tags_csv_path)

## ---- build one presence matrix per source ---------------------------------
build_matrix <- function(src) {
  cols <- list(redivis = live[[src]], metadata_csv = meta[[src]], biblio_csv = bib[[src]])
  if (!is.null(dict[[src]])) cols$dictionary_sheet <- dict[[src]]
  if (src == "core") cols$tags_csv <- tags

  all_tables <- unique(unlist(cols))
  if (length(all_tables) == 0) return(NULL)

  m <- data.frame(table = all_tables, stringsAsFactors = FALSE)
  for (nm in names(cols)) m[[nm]] <- m$table %in% cols[[nm]]
  m$category <- src
  m
}
mats <- Filter(Negate(is.null), lapply(sources, build_matrix))

## ---- bucket A: incomplete coverage -- reproduces `zz` exactly -------------
## missing >= 2 of the applicable sources, tag-only rows dropped. Sorted
## worst-first (fewest sources present) so triage starts where `zz` always
## put the most-obviously-broken rows.
DISPLAY_COLS <- c("redivis", "dictionary_sheet", "biblio_csv", "metadata_csv", "tags_csv")

incomplete_list <- lapply(mats, function(m) {
  ind_cols <- setdiff(names(m), c("table", "category"))
  n_present <- rowSums(m[, ind_cols, drop = FALSE])
  n_total   <- length(ind_cols)
  keep <- n_present <= n_total - 2   # zz: n<4 of 5 == missing at least 2
  if ("tags_csv" %in% ind_cols) {    # zz: nn<4 -- drop "only tags_csv present" rows
    other_cols <- setdiff(ind_cols, "tags_csv")
    tag_only <- m$tags_csv & !apply(m[, other_cols, drop = FALSE], 1, any)
    keep <- keep & !tag_only
  }
  if (!any(keep)) return(NULL)
  out <- m[keep, c("table", "category", ind_cols)]
  out$n_present <- n_present[keep]
  out$n_total <- n_total
  out
})
incomplete <- dplyr::bind_rows(Filter(Negate(is.null), incomplete_list))
if (nrow(incomplete) == 0) incomplete <- NULL
if (!is.null(incomplete)) {
  incomplete <- incomplete[order(incomplete$n_present, incomplete$category, incomplete$table), ]
  ## fixed column order regardless of which sources each category has
  for (cn in DISPLAY_COLS) if (!cn %in% names(incomplete)) incomplete[[cn]] <- NA
  incomplete <- incomplete[, c("table", "category", DISPLAY_COLS, "n_present", "n_total")]
}

## ---- bucket B: urgent -- live in Redivis, absent from every local CSV -----
urgent <- if (!is.null(incomplete)) {
  incomplete[incomplete$n_present == 1 & incomplete$redivis %in% TRUE, ]
} else NULL

## Bucket C (near-duplicate/inconsistent names) intentionally omitted for
## now -- see header note. Revisit once bucket A has been triaged for real
## and there are concrete examples of what an inconsistency actually looks
## like in this table-naming scheme.

## ---- write outputs ----------------------------------------------------
## CSV: wide 1/blank-per-source shape, matching zz. TRUE->1, FALSE/NA->blank
## (blank distinguishes "absent" from "not applicable to this category",
## same visual meaning zz's NA had).
to_csv_cell <- function(x) ifelse(is.na(x), "", ifelse(x, "1", ""))
csv_out <- sub("\\.md$", "_incomplete.csv", out_path)
if (!is.null(incomplete)) {
  csv_df <- incomplete
  for (cn in DISPLAY_COLS) csv_df[[cn]] <- to_csv_cell(incomplete[[cn]])
  write_csv(csv_df, csv_out)
} else {
  file.create(csv_out)
}

## Fixed-width plain text: the actual ask (Ben, 2026-07-28) -- "visually
## organized as columns in raw text", i.e. readable as an aligned grid
## without opening a spreadsheet, same as zz printed to the R console.
txt_out <- sub("\\.md$", "_incomplete.txt", out_path)
if (!is.null(incomplete)) {
  txt_cols <- c("table", "category", DISPLAY_COLS)
  disp <- incomplete[, txt_cols]
  for (cn in DISPLAY_COLS) disp[[cn]] <- to_csv_cell(incomplete[[cn]])
  widths <- vapply(txt_cols, function(cn) max(nchar(cn), nchar(disp[[cn]]), na.rm = TRUE), integer(1))
  pad_row <- function(vals) paste(mapply(function(v, w) formatC(v, width = -w), vals, widths), collapse = " | ")
  lines <- c(
    pad_row(txt_cols),
    paste(vapply(widths, function(w) strrep("-", w), character(1)), collapse = "-+-"),
    apply(disp, 1, pad_row)
  )
  writeLines(lines, txt_out)
} else {
  file.create(txt_out)
}

md <- c(
  paste0("# IRW table-name consistency audit -- ", Sys.Date()),
  "",
  "Ground truth: `irw::irw_list_tables(source = c(\"core\",\"comp\",\"nom\",\"sim\"))`. ",
  if (skip_dict) "Dictionary sheets skipped (--skip-dict)." else "Dictionary sheets included (Public rows only).",
  "",
  "## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)",
  "",
  paste0("Full list, aligned columns: `", basename(txt_out), "`. Same data as CSV: `",
         basename(csv_out), "` (", if (is.null(incomplete)) 0 else nrow(incomplete), " rows). ",
         "Nothing here is auto-fixed -- triage by hand."),
  ""
)
if (!is.null(incomplete)) {
  head_n <- min(30, nrow(incomplete))
  md <- c(md, paste0("| ", paste(c("table", "category", DISPLAY_COLS), collapse = " | "), " |"),
          paste0("|", strrep("---|", 2 + length(DISPLAY_COLS))))
  for (i in seq_len(head_n)) {
    r <- incomplete[i, ]
    cells <- vapply(DISPLAY_COLS, function(cn) if (isTRUE(r[[cn]])) "1" else "", character(1))
    md <- c(md, paste0("| ", r$table, " | ", r$category, " | ", paste(cells, collapse = " | "), " |"))
  }
  if (nrow(incomplete) > head_n) md <- c(md, sprintf("_...and %d more, see the .txt or .csv._", nrow(incomplete) - head_n))
} else {
  md <- c(md, "_None -- every table is present everywhere it should be._")
}

md <- c(md, "", "## B. Urgent -- live in Redivis, not in any local CSV yet", "")
if (!is.null(urgent) && nrow(urgent)) {
  md <- c(md, "| table | category |", "|---|---|")
  for (i in seq_len(nrow(urgent))) md <- c(md, sprintf("| %s | %s |", urgent$table[i], urgent$category[i]))
  md <- c(md, "", "_These probably just need the generate-CSVs workflow re-run (01/05/06/07 pick up new Redivis tables automatically)._")
} else {
  md <- c(md, "_None._")
}

md <- c(md, "", "## C. Near-duplicate / inconsistent names -- not implemented yet", "",
        "_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at",
        "together before designing this detector. See script header for what was tried",
        "and discarded._")

writeLines(md, out_path)
message("\nWrote:")
message("  ", out_path)
message("  ", csv_out)
message("  ", txt_out)
message(sprintf("\nSummary: %d incomplete, %d urgent.",
                 if (is.null(incomplete)) 0 else nrow(incomplete),
                 if (is.null(urgent)) 0 else nrow(urgent)))
