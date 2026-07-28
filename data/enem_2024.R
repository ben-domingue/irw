# ENEM 2024 -> IRW long format (id | item | resp | position | booklet),
# restricted to MAIN (standard regular-booklet) items only (issue #955):
# excludes reaplicacao, digital, and accessibility-substitute items so every
# area is a single unlinked instrument (density ~= 1.0 for CH/CN/MT).
# LC intentionally keeps BOTH languages via TP_LINGUA (sparse by design, #723).
# 1,000,000 examinees sampled from the REGULAR-application pool (seed 5150).
#
# standard_prova_codes / regular_prova_codes below were generated offline from
# this year's INEP dictionary (Dicionario_Microdados_Enem_2024.xlsx) by
# enem_reprocess/identify_regular_items.py -- see that directory for the full
# reprocessing writeup and the shared logic this script was derived from.

library(tidyverse)
library(vroom)

year <- 2024
standard_prova_codes <- c(1383, 1384, 1385, 1386, 1395, 1396, 1397, 1398, 1407, 1408, 1409, 1410, 1419, 1420, 1421, 1422)
regular_prova_codes  <- c(1383, 1384, 1385, 1386, 1387, 1388, 1390, 1395, 1396, 1397, 1398, 1399, 1400, 1402, 1407, 1408, 1409, 1410, 1411, 1412, 1414, 1419, 1420, 1421, 1422, 1423, 1424, 1426)

# ---- load microdata (layout varies by year; some ship split PARTICIPANTES/RESULTADOS) ----
find_ci <- function(dir, pattern) {
  hits <- list.files(dir, pattern = pattern, ignore.case = TRUE, full.names = TRUE)
  if (length(hits) > 0) hits[1] else file.path(dir, pattern)
}
data_dir <- "DADOS"
single <- find_ci(data_dir, sprintf("^MICRODADOS_ENEM_%s\\.csv$", year))
partic <- find_ci(data_dir, sprintf("^PARTICIPANTES_%s\\.csv$", year))
resul  <- find_ci(data_dir, sprintf("^RESULTADOS_%s\\.csv$", year))
if (file.exists(single)) {
  microdata <- vroom(single, delim = ";",
                     col_select = list(id = NU_INSCRICAO, tp_lingua = TP_LINGUA,
                                       starts_with("CO_PROVA"), starts_with("TX_RESPOSTAS")),
                     show_col_types = FALSE) |> drop_na()
} else if (file.exists(partic) && file.exists(resul)) {
  p <- vroom(partic, delim = ";", col_select = list(id = NU_INSCRICAO), show_col_types = FALSE)
  r <- vroom(resul, delim = ";",
             col_select = list(tp_lingua = TP_LINGUA, starts_with("CO_PROVA"),
                               starts_with("TX_RESPOSTAS")),
             show_col_types = FALSE)
  stopifnot(nrow(p) == nrow(r))
  microdata <- bind_cols(p, r) |> drop_na()
} else stop(sprintf("No microdata found in %s", data_dir))

# ---- regular examinees, then 1M subsample ----
regular_ids <- microdata$id[microdata$CO_PROVA_CH %in% regular_prova_codes]
cat(sprintf("[%s] regular examinees: %d of %d (%.3f)\n",
            year, length(regular_ids), nrow(microdata), length(regular_ids)/nrow(microdata)))
set.seed(5150)
keep_ids <- sample(regular_ids, size = min(1e6, length(regular_ids)), replace = FALSE)
microdata <- microdata |> filter(id %in% keep_ids)

# ---- items + standard item set ----
items <- vroom(find_ci(data_dir, sprintf("^ITENS_PROVA_%s\\.csv$", year)), delim = ";",
               col_select = list(subj = SG_AREA, item = CO_ITEM, position = CO_POSICAO,
                                 booklet = CO_PROVA, key = TX_GABARITO, item_lingua = TP_LINGUA),
               show_col_types = FALSE)
standard_items <- items |> filter(booklet %in% standard_prova_codes) |> distinct(subj, item)
std_set <- function(area) standard_items$item[standard_items$subj == area]

booklets <- microdata |>
  select(id, starts_with("CO_PROVA")) |>
  pivot_longer(starts_with("CO_PROVA"), names_to = "subj",
               values_to = "booklet", names_prefix = "CO_PROVA_")

# area position ranges: derived from this year's ITENS_PROVA (order of areas in the
# combined 180-item booklet varies by year, e.g. 2013 runs CH,CN,LC,MT while 2023 runs
# LC,CH,CN,MT; 2017 lays out LC as a genuine 50-wide block instead of reusing 45 slots).
AREAS <- lapply(split(items$position, items$subj), function(p) c(min(p), max(p)))[c("LC","CH","CN","MT")]
for (area in c("CH","CN","MT")) {
  rng <- AREAS[[area]]
  if (diff(rng) != 44) stop(sprintf("area %s position range is not a contiguous 45-wide block: %d-%d", area, rng[1], rng[2]))
}
if (!diff(AREAS$LC) %in% c(44, 49)) stop(sprintf("area LC position range is neither 45- nor 50-wide: %d-%d", AREAS$LC[1], AREAS$LC[2]))

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

for (area in names(AREAS)) {
  suf <- tolower(area)
  df <- process_area(area)
  dups <- sum(duplicated(df[, c("id", "item")]))
  if (dups > 0) stop(sprintf("enem_%d_1mil_%s: %d duplicate id+item rows -- booklet/position join produced ambiguous matches; investigate before trusting output", year, suf, dups))
  save(df, file = sprintf("enem_%d_1mil_%s.Rdata", year, suf))
  write.csv(df, sprintf("enem_%d_1mil_%s.csv", year, suf), row.names = FALSE)
}

