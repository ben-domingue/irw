#!/usr/bin/env Rscript
# verify_nature_relatedness.R -- Step 5b mapping verification.
#
# WHAT IS VERIFIED: that IRW item code i (a bare integer 1..32 invented by
# data/nature_relatedness.R via row_number() over unique(item) after
# pivot_longer) refers to the source column this extraction assigned it
# (1-6 = NR-6 Q1A..Q6A, 7-16 = TIPI1..TIPI10, 17-32 = VCL1..VCL16).
#
# HOW: re-run the published processing script over the original deposit
# (openpsychometrics.org/_rawdata/NR6-data-14Nov2018.zip) and compare, per item
# code, n / mean / min / max of `resp` against the LIVE irw table. Core-model-3
# "script-generated integer -> re-run the script" route: it reproduces the
# derivation rather than inferring it. Route 2 (per-item response range) is
# printed alongside as a coarse structural cross-check.
#
# NOT verified here: whether codebook.txt's own Q-number -> wording listing is
# correct (taken on the deposit's authority; the NR-6 wording also matches
# Nisbet & Zelenski 2013 Appendix A text). Item *set* equality is
# validate_items.R's job and is deliberately not re-done here.

suppressPackageStartupMessages({
  library(irw); library(dplyr); library(tidyr); library(readr); library(stringr)
})

cache <- file.path(tempdir(), "nr6")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
zipf <- file.path(cache, "NR6-data-14Nov2018.zip")
if (!file.exists(zipf))
  download.file("http://openpsychometrics.org/_rawdata/NR6-data-14Nov2018.zip", zipf,
                quiet = TRUE, mode = "wb")
unzip(zipf, exdir = cache)
raw <- file.path(cache, "NR6-data-14Nov2018", "data-final.csv")

## ---- re-run data/nature_relatedness.R verbatim in its mapping-relevant part
df <- read_delim(raw, show_col_types = FALSE)
names(df) <- tolower(names(df))
df <- df |>
  select(-education, -urban, -gender, -engnat, -age, -screenw, -screenh, -hand,
         -religion, -orientation, -race, -voted, -married, -familysize, -major,
         -country, -introelapse, -testelapse, -surveyelapse, -ends_with('i')) |>
  mutate(id = row_number(),
         across(starts_with('tipi') | ends_with('a'), ~ if_else(. == 0, NA, .)))
times <- df |> select(id, ends_with('e')) |>
  pivot_longer(cols = -id, names_to = 'item', values_to = 'rt') |>
  mutate(item = str_replace(item, 'e', 'a'), rt = rt / 1000)
df <- df |> select(-ends_with('e')) |>
  pivot_longer(cols = -id, names_to = 'item', values_to = 'resp') |>
  left_join(times, by = c('id', 'item'))
map <- data.frame(srcname = unique(df$item), stringsAsFactors = FALSE)
map$item <- seq_len(nrow(map))

## the assignment this extraction shipped
expected <- c(paste0("q", 1:6, "a"), paste0("tipi", 1:10), paste0("vcl", 1:16))
cat("=== item code -> source column, from re-running the script ===\n")
print(data.frame(item = map$item, rerun = map$srcname, shipped_assumes = expected,
                 agree = map$srcname == expected))
code_ok <- identical(map$srcname, expected)
cat("code->column assignment reproduces shipped assignment:", code_ok, "\n\n")

loc <- df |> left_join(map, by = c("item" = "srcname")) |>
  rename(item_code = item.y) |> filter(!is.na(resp)) |>
  group_by(item_code) |>
  summarise(n_rerun = n(), mean_rerun = mean(resp),
            min_rerun = min(resp), max_rerun = max(resp), .groups = "drop")

## ---- live IRW table
live <- irw_fetch("nature_relatedness")
live$item <- as.numeric(live$item); live$resp <- as.numeric(live$resp)
liv <- live |> filter(!is.na(resp)) |> group_by(item) |>
  summarise(n_live = n(), mean_live = mean(resp),
            min_live = min(resp), max_live = max(resp), .groups = "drop")

cmp <- merge(loc, liv, by.x = "item_code", by.y = "item")
cmp$d_mean <- abs(cmp$mean_rerun - cmp$mean_live)
cmp$n_ok   <- cmp$n_rerun == cmp$n_live
cmp$rng_ok <- cmp$min_rerun == cmp$min_live & cmp$max_rerun == cmp$max_live

cat("=== per-item n / mean / range: re-run vs live ===\n")
print(data.frame(item = cmp$item_code,
                 n_rerun = cmp$n_rerun, n_live = cmp$n_live,
                 mean_rerun = round(cmp$mean_rerun, 6),
                 mean_live  = round(cmp$mean_live, 6),
                 d_mean = signif(cmp$d_mean, 3),
                 range_rerun = paste0(cmp$min_rerun, "-", cmp$max_rerun),
                 range_live  = paste0(cmp$min_live, "-", cmp$max_live)),
      row.names = FALSE)

cat("\nitems compared:", nrow(cmp), "\n")
cat("items with identical n:", sum(cmp$n_ok), "/", nrow(cmp), "\n")
cat("items with identical range:", sum(cmp$rng_ok), "/", nrow(cmp), "\n")
cat("max |mean difference|:", format(max(cmp$d_mean), scientific = TRUE), "\n")

sig <- paste(cmp$n_live, format(cmp$mean_live, digits = 15))
cat("distinct (n, mean) signatures among the live items:", length(unique(sig)), "/", nrow(cmp), "\n")

pass <- code_ok && nrow(cmp) == 32 && all(cmp$n_ok) && all(cmp$rng_ok) &&
        max(cmp$d_mean) < 1e-10 && length(unique(sig)) == nrow(cmp)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
