# ---------------------------------------------------------------------------
# Survey on cognitive/emotional responses to visual anthropomorphism
# in health media (Russian, n = 121).
#
# Nominal data standard (https://itemresponsewarehouse.org/nominal_standard.html):
# - Single-select questions -> resp = numeric code of the chosen option.
# - Multi-select ("choose all that apply") -> resp = selected (1) / not (0). Not mutually exclusive.
# - Likert -> ordinal numeric item; resp = 1-5, text = NA.
#
# All text is in Russian. 
# `item_text` = the question stem (Russian)
# ---------------------------------------------------------------------------

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
rm(list = ls())
library(tidyverse)

raw <- read_csv(
  "Survey data on cognitive and emotional responses to visual anthropomorphism in health media.csv",
  show_col_types = FALSE
)

# Keep the original Russian headers for item_text, then rename to short handles.
q_text <- names(raw) %>% str_replace_all("[\\r\\n]+", " ") %>% str_squish()
names(raw) <- c("timestamp", "age", "gender", "med_edu",
                "q04", "q05", "q06", "q07", "q08", "q09", "q10",
                "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18")
names(q_text) <- names(raw)

# Reformat Timestamp to Unix
df <- raw %>%
  mutate(
    id   = row_number(),
    date = as.numeric(as.POSIXct(timestamp, format = "%d.%m.%Y %H:%M:%S", tz = "UTC"))
  )

# Covariates
cov <- df %>%
  select(id, date,
         cov_age     = age,       # ordinal age bands
         cov_gender  = gender,    # Женский / Мужской
         cov_med_edu = med_edu)   # Да / Нет (medical education)

# --- helpers ----------------------------------------------------------------

# Likert: an already-numeric 1-5 rating -> one ordinal item. No nominal `text`.
make_likert <- function(data, col, item_id) {
  data %>%
    transmute(id,
              item        = item_id,
              item_family = NA_character_,
              resp        = as.numeric(.data[[col]]),
              text        = NA_character_) %>%
    filter(!is.na(resp))
}

# Single-select (nominal) -> ONE item. resp is a numeric code for the chosen
# option; `text` is the option itself (Russian). Respondents who skipped the question are dropped.
make_single <- function(data, col, item_id) {
  d <- data %>% select(id, raw = all_of(col)) %>% filter(!is.na(raw))
  codes <- d %>% count(raw) %>% arrange(desc(n), raw) %>%
    transmute(raw, resp = row_number())
  d %>% inner_join(codes, by = "raw") %>%
    transmute(id, item = item_id, item_family = NA_character_,
              resp = as.integer(resp), text = raw)
}

# Multi-select ("select all that apply") -> one 0/1 item per option
# (selected = 1), grouped by an item_family. `text` holds the option string.
make_multi <- function(data, col, fam, slug, atoms) {
  opts <- tibble(option = atoms,
                 item   = sprintf("%s_%02d", slug, seq_along(atoms)),
                 .k = 1L)
  data %>% select(id, raw = all_of(col)) %>% filter(!is.na(raw)) %>%
    mutate(.k = 1L) %>%
    inner_join(opts, by = ".k", relationship = "many-to-many") %>%
    transmute(id, item, item_family = fam,
              resp = as.integer(str_detect(raw, fixed(option))),
              text = option)
}

# Atoms for the two multi-select questions
atoms_q07 <- c(
  "Жутковатое чувство и дискомфорт (как будто в теле живет кто-то чужой)",
  "Заинтересованность (необычный образ сразу привлекает внимание и заставляет прочитать текст)",
  "Недоумение (слишком странный и нелепый рисунок для медицинской статьи)",
  "Отвращение (картинка кажется слишком неприятной / некрасивой)",
  "Смех (выглядит как забавный мультяшный монстрик)",
  "Сочувствие к человеку (глядя на картинку, почти физически ощущаешь, как больно наступать)"
)
atoms_q11 <- c(
  "Желание позаботиться о своем организме",
  "Умиление",
  "Никаких эмоций, это просто рисунок",
  "Отторжение / Дискомфорт",
  "Сочувствие / Жалость",
  "Тревогу за свое здоровье"
)

# --- build the long item table ----------------------------------------------
# Dropped:
# - q06 & q08 (100% missing)
# - q10 & q15 (free text -> not numeric resp)
items <- bind_rows(
  make_likert(df, "q04", "q04_trevozhnost_obraz"),                                 # anxiety 1-5
  make_single(df, "q05", "q05_opisanie"),                                          # which description fits
  make_multi (df, "q07", "q07_chuvstva_bolezn",  "q07_chuvstva_bolezn", atoms_q07),# feelings about image
  make_single(df, "q09", "q09_kto_upravlyaet"),                                    # who is in control
  make_multi (df, "q11", "q11_emocii_personazh", "q11_emocii_personazh", atoms_q11),# emotions re character
  make_single(df, "q12", "q12_vizual_nefropatii"),                                 # how disease shown
  make_single(df, "q13", "q13_vpechatlenie_organ"),                                # impression of organ
  make_single(df, "q14", "q14_nastroenie_chtenie"),                                # mood before reading
  make_single(df, "q16", "q16_effektivnyy_podhod"),                                # most effective approach
  make_likert(df, "q17", "q17_snizhenie_trevozhnosti"),                            # lowers anxiety 1-5
  make_single(df, "q18", "q18_illustr_zagolovok")                                  # illustration vs title
)

# --- assemble in IRW column order -------------------------------------------
# item_text = the question stem (Russian), matched from the source headers.
final <- items %>%
  left_join(cov, by = "id") %>%
  mutate(item_text = unname(q_text[str_extract(item, "^q\\d{2}")])) %>%
  select(id, item, resp, text, item_text,
         date, cov_age, cov_gender, cov_med_edu, item_family) %>%
  arrange(id, item)

write_csv(final, "anthropomorphism_health_Voropaeva_2026.csv")