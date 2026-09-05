# verify_experimental_iq.R
#
# experimental_iq is BLOCKED: no item text was shipped (the 25 items are figural
# matrices distributed only as PNG images, see notes_experimental_iq.csv). There is
# therefore no item_text<->item mapping to verify in the usual sense.
#
# What this script DOES verify, so the finding is re-runnable and so a future round
# that gains a way to carry image stimuli does not have to redo it: that the IRW
# integer item codes 1..25 are exactly the raw file's columns Q1..Q25 in order.
# data/experimental_iq.R assigns them with row_number() over unique(item) after a
# pivot_longer of the lowercased columns, i.e. a script-generated integer
# (SKILL core model s3, pattern 4) -- so it is re-derived here rather than reasoned
# about, per the rule for that pattern.
#
# The falsifiable prediction: re-running that derivation over the released
# openpsychometrics IQ1 data.csv must reproduce, for every one of the 25 items,
# the live per-item n and the live per-item number of resp==1. Any shift or
# permutation of the column->code assignment breaks it, because the 25 items have
# very different difficulties.

suppressMessages({library(irw); library(dplyr); library(tidyr); library(readr)})

TABLE <- "experimental_iq"
RAW   <- "http://openpsychometrics.org/_rawdata/IQ1.zip"

# --- re-derive from the released raw file, exactly as data/experimental_iq.R does
tmp <- tempfile(fileext = ".zip"); dir.create(td <- tempfile())
download.file(RAW, tmp, quiet = TRUE); unzip(tmp, exdir = td)
raw <- suppressMessages(read_delim(file.path(td, "IQ1", "data.csv"),
                                   show_col_types = FALSE))
names(raw) <- tolower(names(raw))

df <- raw |>
  select(-gender, -score) |>
  mutate(age = if_else(age > 99, NA, age), id = row_number()) |>
  mutate_all(~ replace(., . == 0, NA)) |>
  pivot_longer(cols = -c(id, age), names_to = "item", values_to = "resp")

items <- data.frame(src = unique(df$item), item_id = seq_along(unique(df$item)))
df <- df |>
  left_join(items, by = c("item" = "src")) |>
  mutate(resp = case_when(resp == 10 ~ 1, resp >= 1 & resp <= 7 ~ 0, is.na(resp) ~ NA_real_))

rederived <- df |> filter(!is.na(resp)) |>
  group_by(item_id, src = item) |>
  summarise(n = n(), ncorrect = sum(resp == 1), .groups = "drop") |>
  arrange(item_id)

# --- live IRW table (small: 25 items x ~400 respondents)
live <- irw::irw_fetch(TABLE)
livesum <- live |> filter(!is.na(resp)) |>
  group_by(item = as.integer(as.character(item))) |>
  summarise(n = n(), ncorrect = sum(resp == 1), .groups = "drop") |>
  arrange(item)

cat(sprintf("%-5s %-6s %8s %8s %10s %10s\n",
            "item", "srccol", "n_raw", "n_live", "corr_raw", "corr_live"))
ok <- TRUE
for (i in seq_len(nrow(rederived))) {
  r <- rederived[i, ]; l <- livesum[livesum$item == r$item_id, ]
  match_i <- nrow(l) == 1 && l$n == r$n && l$ncorrect == r$ncorrect
  ok <- ok && match_i
  cat(sprintf("%-5d %-6s %8d %8d %10d %10d%s\n", r$item_id, r$src, r$n,
              if (nrow(l)) l$n else NA_integer_, r$ncorrect,
              if (nrow(l)) l$ncorrect else NA_integer_,
              if (match_i) "" else "   <-- MISMATCH"))
}
cat(sprintf("\nspread of per-item proportion correct (raw): %.3f to %.3f\n",
            min(rederived$ncorrect / rederived$n), max(rederived$ncorrect / rederived$n)))
cat("The difficulties are spread widely, so a shifted or permuted column->code\n",
    "assignment would break at least one cell above.\n", sep = "")
cat("This does NOT establish any item_text mapping: no item text exists for this\n",
    "table. The instrument's 25 items are matrix images (questions/N/q.png) with\n",
    "eight picture options and no wording anywhere in the source release.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
