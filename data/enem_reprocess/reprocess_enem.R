# Reprocess ENEM year -> IRW tables restricted to MAIN (standard regular-booklet)
# items only. Year-parameterized; used for the full 2013-2025 redo (FarmShare).
#
# Definitions (locked 2026-07-13):
#  - main items = STANDARD regular booklets (plain colors); exclude accessibility
#    variants, reaplicacao, digital  -> clean 45 for CH/CN/MT, density ~1.0.
#  - LC keeps BOTH languages via TP_LINGUA (sparse by design, issue #723).
#  - sample 1,000,000 from REGULAR-application examinees (seed 5150).
#
# Inputs (env, with sensible defaults):
#   ENEM_YEAR      (required)          e.g. 2023
#   ENEM_DATA_DIR  dir with DADOS csvs (auto: ENEM/extracted_<year>/DADOS)
#   ENEM_CODES     prova_codes.csv     (auto: ENEM/output/regular/enem_<year>_prova_codes.csv)
#   ENEM_OUT_DIR   output dir          (auto: ENEM/output/regular)
#   ENEM_DRY_N     if set, read only N microdata rows and skip the 1M subsample
#
# Layout is auto-detected: "single" (MICRODADOS_ENEM_<year>.csv) or
# "split" (PARTICIPANTES_<year>.csv + RESULTADOS_<year>.csv).

suppressWarnings(suppressMessages({library(tidyverse); library(vroom)}))

year   <- Sys.getenv("ENEM_YEAR", unset = commandArgs(trailingOnly = TRUE)[1])
if (is.na(year) || year == "") stop("Set ENEM_YEAR or pass year as arg")
root   <- Sys.getenv("IRW_ROOT", unset = "C:/Users/mmmaz/OneDrive/Stanford/IRW")
setwd(root)
data_dir <- Sys.getenv("ENEM_DATA_DIR", unset = sprintf("ENEM/extracted_%s/DADOS", year))
codes_f  <- Sys.getenv("ENEM_CODES",    unset = sprintf("ENEM/output/regular/enem_%s_prova_codes.csv", year))
out_dir  <- Sys.getenv("ENEM_OUT_DIR",  unset = "ENEM/output/regular")
DRY_N    <- Sys.getenv("ENEM_DRY_N", unset = "")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
nmax <- if (nzchar(DRY_N)) as.integer(DRY_N) else Inf

# ---- booklet codes (from identify_regular_items.py) ----
codes <- read.csv(codes_f)
standard_prova_codes <- codes$CO_PROVA[codes$is_standard %in% c(TRUE, "True", "true")]
regular_prova_codes  <- codes$CO_PROVA[codes$application == "regular"]
stopifnot(length(standard_prova_codes) > 0, length(regular_prova_codes) > 0)

# ---- load microdata (auto-detect layout) ----
single <- file.path(data_dir, sprintf("MICRODADOS_ENEM_%s.csv", year))
partic <- file.path(data_dir, sprintf("PARTICIPANTES_%s.csv", year))
resul  <- file.path(data_dir, sprintf("RESULTADOS_%s.csv", year))
if (file.exists(single)) {
  microdata <- vroom(single, delim = ";",
                     col_select = list(id = NU_INSCRICAO, tp_lingua = TP_LINGUA,
                                       starts_with("CO_PROVA"), starts_with("TX_RESPOSTAS")),
                     n_max = nmax, show_col_types = FALSE) |> drop_na()
} else if (file.exists(partic) && file.exists(resul)) {
  p <- vroom(partic, delim = ";", col_select = list(id = NU_INSCRICAO),
             n_max = nmax, show_col_types = FALSE)
  r <- vroom(resul, delim = ";",
             col_select = list(tp_lingua = TP_LINGUA, starts_with("CO_PROVA"),
                               starts_with("TX_RESPOSTAS")),
             n_max = nmax, show_col_types = FALSE)
  stopifnot(nrow(p) == nrow(r))
  microdata <- bind_cols(p, r) |> drop_na()
} else stop(sprintf("No microdata found in %s", data_dir))

# ---- regular examinees, then 1M subsample ----
regular_ids <- microdata$id[microdata$CO_PROVA_CH %in% regular_prova_codes]
cat(sprintf("[%s] regular examinees: %d of %d (%.3f)\n",
            year, length(regular_ids), nrow(microdata), length(regular_ids)/nrow(microdata)))
if (!nzchar(DRY_N)) {
  set.seed(5150)
  keep_ids <- sample(regular_ids, size = min(1e6, length(regular_ids)), replace = FALSE)
} else keep_ids <- regular_ids
microdata <- microdata |> filter(id %in% keep_ids)

# ---- items + standard item set ----
items <- vroom(file.path(data_dir, sprintf("ITENS_PROVA_%s.csv", year)), delim = ";",
               col_select = list(subj = SG_AREA, item = CO_ITEM, position = CO_POSICAO,
                                 booklet = CO_PROVA, key = TX_GABARITO, item_lingua = TP_LINGUA),
               show_col_types = FALSE)
standard_items <- items |> filter(booklet %in% standard_prova_codes) |> distinct(subj, item)
std_set <- function(area) standard_items$item[standard_items$subj == area]

booklets <- microdata |>
  select(id, starts_with("CO_PROVA")) |>
  pivot_longer(starts_with("CO_PROVA"), names_to = "subj",
               values_to = "booklet", names_prefix = "CO_PROVA_")

# area position ranges (standard ENEM layout; verify for pre-2017 years)
AREAS <- list(LC = c(1,45), CH = c(46,90), CN = c(91,135), MT = c(136,180))

process_area <- function(area) {
  rng <- AREAS[[area]]; txcol <- paste0("TX_RESPOSTAS_", area)
  df <- microdata |>
    select(id, all_of(txcol)) |>
    separate(!!txcol, into = paste0("raw_", area, "_", rng[1]:rng[2]), sep = 1:(rng[2]-rng[1])) |>
    pivot_longer(starts_with("raw"), names_to = c("type","subj","position"), names_sep = "_") |>
    pivot_wider(id_cols = c(id, subj, position), names_from = "type", values_from = "value") |>
    mutate(position = as.numeric(position)) |>
    left_join(booklets, by = c("id","subj"))
  if (area == "LC") {
    df <- df |>
      left_join(microdata |> select(id, tp_lingua), by = "id") |>
      left_join(items |> filter(subj == "LC") |> select(booklet, position, item, key, item_lingua),
                by = c("booklet","position"), relationship = "many-to-many") |>
      filter(is.na(item_lingua) | item_lingua == tp_lingua)
  } else {
    df <- df |>
      left_join(items |> select(subj, booklet, position, item, key),
                by = c("subj","booklet","position"))
  }
  df |> mutate(resp = if_else(raw == key, 1, 0)) |>
    filter(item %in% std_set(area)) |>
    select(id, item, resp, position, booklet)
}

qc <- function(df, name) {
  n <- nrow(df); ids <- n_distinct(df$id); its <- n_distinct(df$item)
  cat(sprintf("%-22s rows=%d ids=%d items=%d rpp=%.1f density=%.3f resp=%s\n",
              name, n, ids, its, n/ids, n/(ids*its), paste(range(df$resp, na.rm=TRUE), collapse="-")))
}

for (area in names(AREAS)) {
  suf <- tolower(area)
  df <- process_area(area)
  qc(df, sprintf("enem_%s_1mil_%s", year, suf))
  if (!nzchar(DRY_N)) {
    save(df, file = file.path(out_dir, sprintf("enem_%s_1mil_%s.Rdata", year, suf)))
    write.csv(df, file.path(out_dir, sprintf("enem_%s_1mil_%s.csv", year, suf)), row.names = FALSE)
  }
}
cat("DONE_REPROCESS\n")
