library(tidyverse)
library(vroom)

year <- 2025
standard_prova_codes <- c(1447, 1448, 1449, 1450, 1459, 1460, 1461, 1462, 1471, 1472, 1473, 1474, 1483, 1484, 1485, 1486, 1583, 1584, 1585, 1586, 1595, 1596, 1597, 1598, 1607, 1608, 1609, 1610, 1619, 1620, 1621, 1622)
regular_prova_codes  <- c(1447, 1448, 1449, 1450, 1451, 1452, 1454, 1459, 1460, 1461, 1462, 1463, 1464, 1466, 1471, 1472, 1473, 1474, 1475, 1476, 1478, 1483, 1484, 1485, 1486, 1487, 1488, 1490, 1495, 1496, 1497, 1498, 1583, 1584, 1585, 1586, 1587, 1595, 1596, 1597, 1598, 1599, 1607, 1608, 1609, 1610, 1611, 1619, 1620, 1621, 1622, 1623, 1631, 1632, 1633, 1634)

# INEP response codes: A-E, "." blank, "*" double mark
ALPHABET <- c("A", "B", "C", "D", "E", ".", "*")

# some years ship PARTICIPANTES + RESULTADOS instead of one MICRODADOS file
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

# regular examinees, then 1M subsample
regular_ids <- microdata$id[microdata$CO_PROVA_CH %in% regular_prova_codes]
cat(sprintf("[%s] regular examinees: %d of %d (%.3f)\n",
            year, length(regular_ids), nrow(microdata), length(regular_ids)/nrow(microdata)))
set.seed(5150)
keep_ids <- sample(regular_ids, size = min(1e6, length(regular_ids)), replace = FALSE)
microdata <- microdata |> filter(id %in% keep_ids)

# items + standard item set
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

# area order within the 180-item booklet varies by year
AREAS <- lapply(split(items$position, items$subj), function(p) c(min(p), max(p)))[c("LC","CH","CN","MT")]
for (area in c("CH","CN","MT")) {
  rng <- AREAS[[area]]
  if (diff(rng) != 44) stop(sprintf("area %s position range is not a contiguous 45-wide block: %d-%d", area, rng[1], rng[2]))
}
if (!diff(AREAS$LC) %in% c(44, 49)) stop(sprintf("area LC position range is neither 45- nor 50-wide: %d-%d", AREAS$LC[1], AREAS$LC[2]))

process_area <- function(area) {
  rng <- AREAS[[area]]; txcol <- paste0("TX_RESPOSTAS_", area)
  npos  <- rng[2] - rng[1] + 1

  # a few records per year are not the year's string length; the dominant
  # length sets the layout and the rest are dropped
  len_tab <- table(nchar(microdata[[txcol]]))
  width   <- as.integer(names(len_tab)[which.max(len_tab)])
  md      <- microdata[nchar(microdata[[txcol]]) == width, ]
  n_off   <- nrow(microdata) - nrow(md)
  if (n_off > 0) {
    cat(sprintf("  %s: dropped %d of %d examinees whose %s is not %d characters\n",
                area, n_off, nrow(microdata), txcol, width))
    if (n_off / nrow(microdata) > 0.01)
      stop(sprintf("%s %s: %.4f of records are off-length -- layout is not uniform",
                   year, area, n_off / nrow(microdata)))
  }

  # where the LC string is 5 wider than the position span it holds both
  # language blocks: slots 1-5 are TP_LINGUA 0, slots 6-10 TP_LINGUA 1, slots
  # 11-50 the shared questions. The block not sat is padded with "9".
  if (area == "LC" && width == npos + 5) {
    df <- md |>
      select(id, tp_lingua, all_of(txcol)) |>
      separate(!!txcol, into = paste0("slot_", 1:width), sep = 1:(width - 1)) |>
      pivot_longer(starts_with("slot_"), names_to = "slot", names_prefix = "slot_",
                   values_to = "raw") |>
      mutate(slot = as.integer(slot)) |>
      filter(slot > 10 | (slot <= 5 & tp_lingua == 0) | (slot >= 6 & tp_lingua == 1)) |>
      mutate(position = if_else(slot <= 10, rng[1] + ((slot - 1) %% 5),
                                            rng[1] + 5 + (slot - 11)),
             subj = area) |>
      select(id, subj, position, raw) |>
      left_join(booklets, by = c("id","subj"))
    # padding must not survive the mapping
    if (any(df$raw == "9"))
      stop(sprintf("%s %s: '9' padding survived the language-block mapping", year, area))
  } else {
  df <- md |>
    select(id, all_of(txcol)) |>
    separate(!!txcol, into = paste0("raw_", area, "_", rng[1]:rng[2]), sep = 1:(rng[2]-rng[1])) |>
    pivot_longer(starts_with("raw"), names_to = c("type","subj","position"), names_sep = "_") |>
    pivot_wider(id_cols = c(id, subj, position), names_from = "type", values_from = "value") |>
    mutate(position = as.numeric(position)) |>
    left_join(booklets, by = c("id","subj"))
  }
  if (area == "LC") {
    df <- df |>
      left_join(md |> select(id, tp_lingua), by = "id") |>
      left_join(items |> filter(subj == "LC") |> select(booklet, position, item, key, item_lingua),
                by = c("booklet","position"), relationship = "many-to-many") |>
      filter(is.na(item_lingua) | item_lingua == tp_lingua)
  } else {
    df <- df |>
      left_join(items |> select(subj, booklet, position, item, key),
                by = c("subj","booklet","position"))
  }
  out <- df |> mutate(resp = if_else(raw == key, 1, 0)) |>
    filter(item %in% std_set(area)) |>
    select(id, item, resp, resp_raw = raw, position, booklet)

  stopifnot(!any(is.na(out$resp_raw)))
  tb  <- table(out$resp_raw)
  bad <- setdiff(names(tb), ALPHABET)
  if (length(bad) > 0)
    stop(sprintf("%s %s: unexpected raw codes: %s", year, area,
                 paste(sprintf("%s(n=%d)", bad, tb[bad]), collapse = " ")))
  cat(sprintf("  %s raw: %s\n", area,
              paste(sprintf("%s=%.4f", names(tb), tb / sum(tb)), collapse = " ")))
  out
}

for (area in names(AREAS)) {
  suf <- tolower(area)
  df <- process_area(area)
  dups <- sum(duplicated(df[, c("id", "item")]))
  if (dups > 0) stop(sprintf("enem_%d_1mil_%s: %d duplicate id+item rows -- booklet/position join produced ambiguous matches; investigate before trusting output", year, suf, dups))
  save(df, file = sprintf("enem_%d_1mil_%s.Rdata", year, suf))
  write.csv(df, sprintf("enem_%d_1mil_%s.csv", year, suf), row.names = FALSE)
}

