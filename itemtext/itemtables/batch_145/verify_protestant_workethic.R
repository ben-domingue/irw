#!/usr/bin/env Rscript
# verify_protestant_workethic.R -- Step 5b mapping verification.
#
# WHAT IS VERIFIED: that IRW item code i (a bare integer 1..45 invented by
# data/protestant_workethic.R via row_number() over unique(item) after
# pivot_longer) refers to the source column this extraction assigned it
# (1-19 = PWE Q1A..Q19A, 20-29 = TIPI1..TIPI10, 30-45 = VCL1..VCL16).
#
# HOW: re-run the published processing script over the original deposit
# (openpsychometrics.org/_rawdata/PWE_data.zip) and compare, per item code,
# the n and the mean of `resp` against the LIVE irw table. This is the
# core-model-3 "script-generated integer -> re-run the script" route; it
# reproduces the derivation rather than inferring it. Route 2 (per-item
# response range) is reported alongside as a coarse cross-check.
#
# NOT verified here: nothing about the mapping. (Item *set* equality is
# validate_items.R's job and is deliberately not re-done as "evidence".)

suppressPackageStartupMessages({
  library(irw); library(dplyr); library(tidyr); library(readr); library(stringr)
})

cache <- file.path(tempdir(), "pwe")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
zipf <- file.path(cache, "PWE_data.zip")
if (!file.exists(zipf))
  download.file("http://openpsychometrics.org/_rawdata/PWE_data.zip", zipf, quiet = TRUE)
unzip(zipf, exdir = cache)
raw <- file.path(cache, "PWE_data", "data.csv")

## ---- re-run data/protestant_workethic.R verbatim in its mapping-relevant part
df <- read_delim(raw, show_col_types = FALSE)
names(df) <- tolower(names(df))
df <- df |>
  select(-country, -introelapse, -testelapse, -surveyelapse, -education, -urban,
         -gender, -engnat, -age, -screenw, -screenh, -hand, -religion,
         -orientation, -race, -voted, -married, -familysize, -major,
         -ends_with('i')) |>
  mutate(id = row_number(),
         across(starts_with('tipi') | ends_with('a'), ~ if_else(. == 0, NA, .)))
times <- df |> select(id, ends_with('e')) |>
  pivot_longer(cols = -id, names_to = 'item', values_to = 'rt') |>
  mutate(rt = rt / 1000, item = str_replace(item, 'e', 'a'))
df <- df |> select(-ends_with('e')) |>
  pivot_longer(cols = -id, names_to = 'item', values_to = 'resp') |>
  left_join(times, by = c('id', 'item'))
map <- data.frame(srcname = unique(df$item), stringsAsFactors = FALSE)
map$item <- seq_len(nrow(map))

## the assignment this extraction shipped
expected <- c(paste0("q", 1:19, "a"), paste0("tipi", 1:10), paste0("vcl", 1:16))
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
live <- irw_fetch("protestant_workethic")
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

## is the (n, mean) signature actually item-distinguishing?
sig <- paste(cmp$n_live, format(cmp$mean_live, digits = 15))
cat("distinct (n, mean) signatures among the 45 live items:", length(unique(sig)), "/", nrow(cmp), "\n")

pass <- code_ok && all(cmp$n_ok) && all(cmp$rng_ok) &&
        max(cmp$d_mean) < 1e-10 && length(unique(sig)) == nrow(cmp)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
