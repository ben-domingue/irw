# 17_coverage.R
#
# Per-table coverage matrix over the LIVE corpus (the monthly data-QC audit,
# 2026-10-15). For every table Redivis actually lists, one row saying which of
# the things a table should have it does have: a metadata row, a citation, a
# licence, a site page, tags (per column), a build script, column docs, a
# source codebook link, shipped item text. It is a WORK QUEUE, not a
# scorecard -- status.json already quotes percentages, and percentages did not
# stop the item-text issues page from accruing a 137-table backlog nobody saw.
#
# One denominator. Every other check here uses its own: 11_status.R counts
# metadata.csv rows, 12_stragglers.R and audit_tables.R count live tables, and
# audit_tables.R only reports a table missing from TWO or more catalogues. This
# stage uses the live listing for everything, and reports single-source misses.
#
# Report-only. It writes two tracked files and prints a summary; it fixes
# nothing, files nothing, and never exits non-zero on a finding. It is wired
# as an ADVISORY stage purely so run_pipeline.sh brackets its stdout and the
# workflow lifts it into the pull-request body.
#
#   coverage_matrix.csv   one row per live table, key (table, source):
#                         TRUE / FALSE / blank = not applicable to this source
#   coverage_report.md    counts per dimension, item-text status, worst rows
#
# Definitions (each column of the matrix):
#   withdrawn        a `kind=whole` row in itemtext/withdrawals.csv for a DATA
#                    dataset (not irw_text*). Kept in the matrix, excluded from
#                    every gap count: a withdrawn table is supposed to lack things.
#   metadata_row     in metadata.csv / comps_ / nominal_ / simsyn_ / conj_metadata.csv
#   biblio_row       in the source's biblio CSV
#   citation         that row's BibTex is non-blank
#   licence          that row's Derived_License is non-blank
#   page             metadata_row & licence & !withdrawn -- the rule the site
#                    applies (datapages/irw landing/page_rules.R, page_tables()),
#                    re-derived here because the site repo is not on the runner.
#                    Derived, not observed: v1 does not read the live sitemap.
#   tag_row          in tags.csv (core) / nominal_tags.csv (nom). comp and sim
#                    have no tag sheet by design (Rpkg/inst/developer/tags.md): blank.
#   tag_<column>     that tag column is filled, for the five columns whose blank
#                    is a gap: age range, sample, measurement tool, item format,
#                    primary language(s). `construct type` is blanked at assembly
#                    on purpose, `child age` is conditional, and `construct name`
#                    is a description not a category (#1837, 2026-09-02) -- none
#                    of those three is a gap. construct name's fill is reported
#                    as info (`has_construct_name`).
#   script           in table_scripts.csv (stage 13)
#   column_docs      share of the table's columns with documented=true in
#                    column_docs.csv (stage 14); a gap when < 1. Core only.
#   codebook_link    a codebook_links_checked.csv row whose outcome starts
#                    `hit:` (stage 15 / find_codebook_links.py)
#   data_note        in data_notes.csv -- INFO ONLY, never a gap: most tables
#                    legitimately carry no caveat.
#   itemtext_shipped in itemtext_metadata.csv and not withdrawn from irw_text*
#   itemtext_status  one string, first match wins:
#                      withdrawn   -- an irw_text* withdrawal (kind=whole)
#                      shipped     -- itemtext_shipped
#                      done_not_shipped -- queue_state says done, nothing shipped:
#                                     the silent-backlog shape, reported on its own
#                      blocked / excluded / failed -- queue_state.csv status
#                      unassessed  -- in none of the above
#                    Item-text ISSUES (DUE / ORPHAN against the public issues
#                    page) are the daily itemtext-issues.yml's job, not this one.
#   n_gaps           count of FALSE among metadata_row, biblio_row, citation,
#                    licence, page, tag_row, the five tag columns, script,
#                    column_docs < 1, codebook_link. Blank (n/a) does not count.
#                    Item text is not in n_gaps: most tables have none to ship.
#
# "Codebook" is deliberately three columns (script, column_docs, codebook_link)
# rather than one, so the monthly reader can decide which of them counts.
#
# A dimension is blank for a whole source when its input file has no row for any
# of that source's live tables -- that is how "the catalogue does not cover this
# source" (column docs for comp) is told apart from "every table is missing it".
#
# Usage (from metadata/, like the other numbered stages):
#   Rscript 17_coverage.R
#   Rscript 17_coverage.R --live-from live.csv   # offline: columns table,source
#   Rscript 17_coverage.R --top 40               # rows shown in the report/stdout
#
# Monthly review: read coverage_report.md once a month and turn its worst rows
# into work (automated_finding/TODO.md). Nothing here does that for you.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
})

## Token file, as audit_tables.R / run_pipeline.sh: an exported var wins, a
## missing file is not fatal (redivis falls back to cached OAuth credentials).
if (identical(Sys.getenv("REDIVIS_API_TOKEN"), "")) {
  token_file <- path.expand(Sys.getenv("REDIVIS_TOKEN_FILE", "~/.redivis_api_token"))
  if (file.exists(token_file)) {
    Sys.setenv(REDIVIS_API_TOKEN = trimws(readLines(token_file, n = 1, warn = FALSE)))
  }
}

args <- commandArgs(trailingOnly = TRUE)
arg <- function(flag, default) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
dir_path  <- arg("--dir", ".")
live_from <- arg("--live-from", NA_character_)
top_n     <- as.integer(arg("--top", "20"))

script_path <- grep("--file=", commandArgs(FALSE), value = TRUE)
here <- if (length(script_path)) dirname(normalizePath(sub("--file=", "", script_path[1]))) else getwd()
repo_root <- normalizePath(file.path(here, ".."))
itemtext_dir <- file.path(repo_root, "itemtext")

key <- function(x) tolower(trimws(as.character(x)))
filled <- function(x) !is.na(x) & trimws(as.character(x)) != ""
read_csv_or_null <- function(path) {
  if (!file.exists(path)) { message("  ! missing: ", path); return(NULL) }
  suppressMessages(read_csv(path, show_col_types = FALSE, col_types = cols(.default = "c"),
                            na = character()))
}
in_file <- function(k, tbl) if (is.null(tbl)) rep(NA, length(k)) else k %in% key(tbl$table)

## ---- 1. the live listing: the denominator ---------------------------------
SOURCES <- c("core", "comp", "nom", "sim", "conj")
## Non-core sources are each one Redivis dataset; core and conj tables carry
## their shard in metadata.csv (core) or nowhere (conj: #2934 split, no shard
## column), so `dataset` below is informative, not a key.
SOURCE_DATASET <- c(comp = "irw_competitions", nom = "irw_nominal",
                    sim = "irw_simsyn", conj = "irw_conjoint")

live <- if (!is.na(live_from)) {
  l <- read_csv_or_null(live_from)
  if (is.null(l)) stop("--live-from file not found: ", live_from)
  if (!"source" %in% names(l)) l$source <- "core"
  data.frame(table = key(l$table), source = l$source, stringsAsFactors = FALSE)
} else {
  bind_rows(lapply(SOURCES, function(s) {
    out <- tryCatch(irw::irw_list_tables(source = s), error = function(e) {
      message("  ! irw_list_tables(source='", s, "') failed: ", conditionMessage(e)); NULL
    })
    if (is.null(out) || nrow(out) == 0) return(NULL)
    data.frame(table = key(out$name), source = s, stringsAsFactors = FALSE)
  }))
}
live <- live[!duplicated(paste(live$table, live$source)), , drop = FALSE]
if (nrow(live) == 0) stop("no live tables listed; refusing to write an empty matrix.")

## ---- 2. inputs ----------------------------------------------------------
md_files  <- c(core = "metadata.csv", comp = "comps_metadata.csv", nom = "nominal_metadata.csv",
               sim = "simsyn_metadata.csv", conj = "conj_metadata.csv")
bib_files <- c(core = "biblio.csv", comp = "comps_biblio.csv", nom = "nominal_biblio.csv",
               sim = "simsyn_biblio.csv", conj = "conj_biblio.csv")
tag_files <- c(core = "tags.csv", nom = "nominal_tags.csv")
md  <- lapply(md_files,  function(f) read_csv_or_null(file.path(dir_path, f)))
bib <- lapply(bib_files, function(f) read_csv_or_null(file.path(dir_path, f)))
tg  <- lapply(tag_files, function(f) read_csv_or_null(file.path(dir_path, f)))

scripts  <- read_csv_or_null(file.path(dir_path, "table_scripts.csv"))
coldocs  <- read_csv_or_null(file.path(dir_path, "column_docs.csv"))
cblinks  <- read_csv_or_null(file.path(dir_path, "codebook_links_checked.csv"))
notes    <- read_csv_or_null(file.path(dir_path, "data_notes.csv"))
itemtext <- read_csv_or_null(file.path(dir_path, "itemtext_metadata.csv"))
queue    <- read_csv_or_null(file.path(itemtext_dir, "extraction_batches", "queue_state.csv"))
wd       <- read_csv_or_null(file.path(itemtext_dir, "withdrawals.csv"))

TAG_GAP_COLS <- c("age range", "sample", "measurement tool", "item format", "primary language(s)")
tag_col_name <- function(cn) paste0("tag_", gsub("[^a-z]+", "_", gsub("\\(s\\)", "", cn)))

## ---- 3. per-source matrices ---------------------------------------------
build <- function(src) {
  rows <- live[live$source == src, , drop = FALSE]
  if (nrow(rows) == 0) return(NULL)
  k <- rows$table
  m <- data.frame(table = k, source = src, stringsAsFactors = FALSE)

  ## dataset: core from metadata.csv; others fixed
  if (src == "core" && !is.null(md$core) && "dataset" %in% names(md$core)) {
    ds <- setNames(md$core$dataset, key(md$core$table))
    m$dataset <- unname(ds[k])
  } else {
    m$dataset <- SOURCE_DATASET[[src]]
  }

  ## withdrawn: whole-table withdrawal from a DATA dataset
  wd_data <- if (is.null(wd)) NULL else wd[wd$kind == "whole" & !grepl("^irw_text", wd$dataset), , drop = FALSE]
  wd_text <- if (is.null(wd)) NULL else wd[wd$kind == "whole" &  grepl("^irw_text", wd$dataset), , drop = FALSE]
  m$withdrawn <- if (is.null(wd_data)) FALSE else k %in% key(wd_data$table)

  m$metadata_row <- in_file(k, md[[src]])
  b <- bib[[src]]
  m$biblio_row <- in_file(k, b)
  if (!is.null(b)) {
    bk <- key(b$table)
    pick <- function(col) if (col %in% names(b)) filled(b[[col]])[match(k, bk)] else rep(NA, length(k))
    m$citation <- ifelse(m$biblio_row, pick("BibTex"), FALSE)
    m$licence  <- ifelse(m$biblio_row, pick("Derived_License"), FALSE)
  } else {
    m$citation <- NA; m$licence <- NA
  }
  m$page <- m$metadata_row %in% TRUE & m$licence %in% TRUE & !m$withdrawn

  t <- tg[[src]]
  if (!is.null(t)) {
    tk <- key(t$table)
    m$tag_row <- k %in% tk
    for (cn in TAG_GAP_COLS) {
      v <- if (cn %in% names(t)) filled(t[[cn]])[match(k, tk)] else rep(NA, length(k))
      m[[tag_col_name(cn)]] <- ifelse(m$tag_row, v, FALSE)
    }
    v <- if ("construct name" %in% names(t)) filled(t[["construct name"]])[match(k, tk)] else rep(NA, length(k))
    m$has_construct_name <- ifelse(m$tag_row, v, FALSE)
  } else {
    m$tag_row <- NA
    for (cn in TAG_GAP_COLS) m[[tag_col_name(cn)]] <- NA
    m$has_construct_name <- NA
  }

  m$script <- in_file(k, scripts)

  if (!is.null(coldocs) && all(c("table", "documented") %in% names(coldocs))) {
    cd <- coldocs %>% mutate(tk = key(table), doc = tolower(documented) == "true") %>%
      group_by(tk) %>% summarise(frac = round(mean(doc), 3), .groups = "drop")
    m$column_docs <- cd$frac[match(k, cd$tk)]
  } else m$column_docs <- NA_real_

  if (!is.null(cblinks) && all(c("table", "outcome") %in% names(cblinks))) {
    hit <- unique(key(cblinks$table[grepl("^hit:", cblinks$outcome)]))
    checked <- unique(key(cblinks$table))
    m$codebook_link <- ifelse(k %in% checked, k %in% hit, FALSE)
  } else m$codebook_link <- NA

  m$data_note <- in_file(k, notes)

  shipped <- in_file(k, itemtext)
  text_wd <- if (is.null(wd_text)) rep(FALSE, length(k)) else k %in% key(wd_text$table)
  m$itemtext_shipped <- shipped %in% TRUE & !text_wd
  qs <- if (is.null(queue)) rep(NA_character_, length(k)) else queue$status[match(k, key(queue$table))]
  m$itemtext_status <- ifelse(text_wd, "withdrawn",
                       ifelse(m$itemtext_shipped, "shipped",
                       ifelse(qs %in% "done", "done_not_shipped",
                       ifelse(qs %in% c("blocked", "excluded", "failed"), qs, "unassessed"))))

  ## source-level n/a: an input with no row for any of this source's tables
  ## is a catalogue that does not cover the source, not a source missing it all
  for (cn in c("script", "column_docs", "codebook_link", "data_note")) {
    v <- m[[cn]]
    none <- if (is.numeric(v)) all(is.na(v)) else !any(v %in% TRUE)
    if (none) m[[cn]] <- if (is.numeric(v)) NA_real_ else NA
  }
  m
}
mat <- bind_rows(Filter(Negate(is.null), lapply(SOURCES, build)))

## ---- 4. gaps --------------------------------------------------------------
GAP_COLS <- c("metadata_row", "biblio_row", "citation", "licence", "page", "tag_row",
              tag_col_name(TAG_GAP_COLS), "script", "codebook_link")
gap_flag <- function(cn) {
  v <- mat[[cn]]
  if (cn == "column_docs") !is.na(v) & v < 1 else (v %in% FALSE)
}
gap_cols_all <- c(GAP_COLS, "column_docs")
gaps <- sapply(gap_cols_all, gap_flag)
if (is.null(dim(gaps))) gaps <- matrix(gaps, nrow = nrow(mat), dimnames = list(NULL, gap_cols_all))
mat$n_gaps <- as.integer(rowSums(gaps))
mat$n_gaps[mat$withdrawn] <- 0L

mat <- mat[order(mat$source, mat$table), , drop = FALSE]
out_cols <- c("table", "source", "dataset", "withdrawn", "metadata_row", "biblio_row", "citation",
              "licence", "page", "tag_row", tag_col_name(TAG_GAP_COLS), "has_construct_name",
              "script", "column_docs", "codebook_link", "data_note",
              "itemtext_shipped", "itemtext_status", "n_gaps")
write_csv(mat[, out_cols], file.path(dir_path, "coverage_matrix.csv"), na = "")

## ---- 5. report ----------------------------------------------------------
active <- mat[!mat$withdrawn, , drop = FALSE]
dim_row <- function(cn) {
  v <- active[[cn]]
  if (cn == "column_docs") { app <- !is.na(v); ok <- app & v >= 1 }
  else { app <- !is.na(v); ok <- v %in% TRUE }
  data.frame(dimension = cn, applicable = sum(app), covered = sum(ok), missing = sum(app) - sum(ok),
             pct = if (sum(app)) round(100 * sum(ok) / sum(app), 1) else NA_real_)
}
dims <- bind_rows(lapply(c(gap_cols_all, "data_note", "has_construct_name", "itemtext_shipped"), dim_row))
## The assembled tags.csv fills every column of every row it carries, so the
## per-column lines repeat tag_row exactly. They stay in the matrix (a partial
## row would show there) and are dropped from the report while they add nothing.
tag_dims <- tag_col_name(TAG_GAP_COLS)
same_as_row <- dims$covered[match(tag_dims, dims$dimension)] == dims$covered[dims$dimension == "tag_row"]
dims <- dims[!(dims$dimension %in% tag_dims[same_as_row %in% TRUE]), , drop = FALSE]
status_counts <- active %>% count(itemtext_status, name = "n") %>% arrange(desc(n))
by_source <- active %>% group_by(source) %>%
  summarise(live = n(), no_metadata = sum(metadata_row %in% FALSE), no_licence = sum(licence %in% FALSE),
            no_page = sum(page %in% FALSE), untagged = sum(tag_row %in% FALSE),
            no_script = sum(script %in% FALSE), .groups = "drop")
by_shard <- active %>% filter(source == "core") %>%
  mutate(dataset = ifelse(is.na(dataset) | dataset == "", "(no metadata row)", dataset)) %>%
  group_by(dataset) %>%
  summarise(live = n(), no_page = sum(page %in% FALSE), untagged = sum(tag_row %in% FALSE),
            text_shipped = sum(itemtext_shipped), .groups = "drop")
## Tables with no metadata row are last week's arrivals waiting for stage 01's
## throttle (and stage 12's business once they persist). They would otherwise
## head this list every run with 13 gaps each and bury everything else.
arrivals <- active %>% filter(metadata_row %in% FALSE)
worst <- active %>% filter(n_gaps > 0, !(metadata_row %in% FALSE)) %>%
  arrange(desc(n_gaps), source, table) %>% head(top_n)
missing_of <- function(i) {
  r <- worst[i, ]
  miss <- gap_cols_all[vapply(gap_cols_all, function(cn) {
    v <- r[[cn]]; if (cn == "column_docs") !is.na(v) && v < 1 else isTRUE(v == FALSE) }, logical(1))]
  paste(miss, collapse = " ")
}

fmt_tbl <- function(df) {
  df[] <- lapply(df, function(x) ifelse(is.na(x), "", as.character(x)))
  c(paste0("| ", paste(names(df), collapse = " | "), " |"),
    paste0("|", paste(rep("---", ncol(df)), collapse = "|"), "|"),
    apply(df, 1, function(r) paste0("| ", paste(r, collapse = " | "), " |")))
}
md_out <- c(
  paste0("# Coverage audit -- ", Sys.Date()),
  "",
  paste0("Denominator: **", nrow(mat), " live tables** (", nrow(active), " after excluding ",
         sum(mat$withdrawn), " withdrawn). Definitions in the header of `metadata/17_coverage.R`;",
         " per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically."),
  "",
  "## Per dimension (active tables)", "", fmt_tbl(dims), "",
  "## Item-text status", "",
  "Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.",
  "", fmt_tbl(status_counts), "",
  "## Per source", "", fmt_tbl(by_source), "",
  "## Core, per shard", "", fmt_tbl(by_shard), "",
  paste0("## Worst ", nrow(worst), " tables (by n_gaps)"), "",
  paste0("Excludes the ", nrow(arrivals), " live tables with no metadata row yet (stage 01's",
         " rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`."),
  "",
  if (nrow(worst)) fmt_tbl(data.frame(table = worst$table, source = worst$source, n_gaps = worst$n_gaps,
                                       missing = vapply(seq_len(nrow(worst)), missing_of, character(1)),
                                       stringsAsFactors = FALSE)) else "_none_",
  "")
writeLines(md_out, file.path(dir_path, "coverage_report.md"))

## ---- 6. stdout (bracketed into the PR body by run_pipeline.sh) ----------
cat(sprintf("Coverage audit: %d live tables, %d active (%d withdrawn)\n",
            nrow(mat), nrow(active), sum(mat$withdrawn)))
cat(sprintf("  %-20s %6s %8s %8s %6s\n", "dimension", "applic", "covered", "missing", "pct"))
for (i in seq_len(nrow(dims))) cat(sprintf("  %-20s %6d %8d %8d %6s\n", dims$dimension[i],
    dims$applicable[i], dims$covered[i], dims$missing[i], ifelse(is.na(dims$pct[i]), "", dims$pct[i])))
cat("  item text:", paste(sprintf("%s=%d", status_counts$itemtext_status, status_counts$n), collapse = ", "), "\n")
cat(sprintf("  no metadata row yet (arrivals, see stage 12): %d\n", nrow(arrivals)))
cat(sprintf("  tables with >= 3 gaps: %d; worst %d (arrivals excluded) in coverage_report.md\n",
            sum(active$n_gaps >= 3 & !(active$metadata_row %in% FALSE)), nrow(worst)))
for (i in seq_len(min(nrow(worst), 10))) cat(sprintf("    %-50s %d  %s\n", worst$table[i], worst$n_gaps[i], missing_of(i)))
quit(save = "no", status = 0)
