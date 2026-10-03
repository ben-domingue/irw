# verify_political_psychology.R -- Step 5b check for batch_730.
#
# The IRW item codes 1..37 are SCRIPT-GENERATED INTEGERS: data/political_psychology.R
# pivots yllanon.csv long and assigns row_number() over unique(item), i.e. column order
# after dropping 12 non-item columns. This was the unverified step that got the previous
# item text withdrawn (irw#1594). The check here:
#   1. re-runs the processing script's logic over the raw OSF file (osf.io/3pwvb,
#      "Data and Codebook/yllanon.csv") to get the integer -> variable-name crosswalk;
#   2. compares, per integer, the rerun's n, mean and item x resp counts with the live
#      table -- a shifted or permuted crosswalk would break these immediately, since the
#      37 variables have distinct distributions;
#   3. checks each shipped item_text contains a distinguishing phrase from the codebook
#      entry (codebook1.html, keyed by variable name) of the variable its integer maps to.
suppressMessages({library(dplyr); library(tidyr); library(readr)})

TABLE <- "political_psychology"
fa <- grep("^--file=", commandArgs(FALSE), value = TRUE)
here <- if (length(fa)) dirname(normalizePath(sub("^--file=", "", fa[1]))) else "itemtables/batch_730"
items_csv <- file.path(here, "political_psychology__items.csv")

raw_path <- file.path(tempdir(), "yllanon.csv")
download.file("https://osf.io/download/782ez/", raw_path, quiet = TRUE, mode = "wb")
df <- read_csv(raw_path, show_col_types = FALSE)
names(df) <- tolower(names(df))
na89 <- c("def","crime","terror","poor","health","econ","unemploy","blkaid","adopt","imm","vaccines",
          "guns","friends_1","friends_2","friends_3","friends_4","friends_5","climate","ideo","partyid",
          "quarantine","sickleave")
df <- df |>
  select(-enddate,-wave,-check,-gender,-ethnic,-edu,-inc,-state,-relig,-age,-responseid,-`duration (in seconds)`,-startdate) |>
  mutate(voting = case_when(voting == "trump" ~ 1, voting == "clinton" ~ 2, voting == "other" ~ 3),
         across(all_of(na89), ~ if_else(.x %in% c(8, 9), NA, .x)),
         abort = if_else(abort %in% c(5, 6), NA, abort),
         djt = if_else(djt %in% c(5, 6), NA, djt),
         across(c(beh_att_1, beh_att_2, beh_att_3), ~ if_else(.x == 8, NA, .x)),
         beh_identity = if_else(beh_identity == 9, NA, beh_identity),
         votereport = if_else(votereport %in% c(3, 6), NA, votereport),
         votereport = if_else(votereport %in% c(4, 5), 3, votereport))
vars <- setdiff(names(df), "id")               # column order = the script's item order
cw <- data.frame(item = seq_along(vars), var = vars)
long <- df |> pivot_longer(all_of(vars), names_to = "var", values_to = "resp") |>
  filter(!is.na(resp)) |> left_join(cw, by = "var")

live <- irw::irw_fetch(TABLE) |> filter(!is.na(resp)) |> mutate(item = as.integer(item))
a <- long |> group_by(item, var) |> summarise(n = n(), mean = mean(resp), .groups = "drop")
b <- live |> group_by(item) |> summarise(ln = n(), lmean = mean(resp))
m <- left_join(a, b, by = "item")
cat(sprintf("%-4s %-13s %7s %7s %9s %9s\n", "item", "var", "n_raw", "n_live", "mean_raw", "mean_live"))
for (i in seq_len(nrow(m)))
  cat(sprintf("%-4d %-13s %7d %7d %9.5f %9.5f\n", m$item[i], m$var[i], m$n[i], m$ln[i], m$mean[i], m$lmean[i]))

# Known, explained residual: the live table also drops beh_identity == 8 ("I would vote for
# another party, namely:") -- 35 rows -- which the committed script does not. Exclude that
# one level on the raw side and require everything else to match cell for cell.
cells_raw  <- long |> filter(!(var == "beh_identity" & resp == 8)) |> count(item, resp, name = "n_raw")
cells_live <- live |> count(item, resp, name = "n_live")
cj <- full_join(cells_raw, cells_live, by = c("item", "resp"))
n_bad <- sum(is.na(cj$n_raw) | is.na(cj$n_live) | cj$n_raw != cj$n_live)
cat(sprintf("\nitem x resp cells: %d compared, %d mismatched (beh_identity resp=8, n=%d, excluded as noted)\n",
            nrow(cj), n_bad, sum(long$var == "beh_identity" & long$resp == 8)))
m2 <- m |> filter(var != "beh_identity")
cat(sprintf("per-item n identical for %d/36 non-beh_identity items; max |mean diff| %.2e\n",
            sum(m2$n == m2$ln), max(abs(m2$mean - m2$lmean))))

# Text side: codebook phrase for each variable must appear in the shipped item_text of its integer.
key <- c(def="defense", crime="crime", terror="terrorism", poor="aid to the poor", health="healthcare",
         econ="stimulate the economy", abort="abortion", unemploy="unemployed", blkaid="blacks",
         adopt="adopting", imm="immigration", vaccines="vaccinate", guns="buy a gun", djt="Donald Trump",
         interest="interested are you in politics", friends_1="Liberals", friends_2="Conservatives",
         friends_3="Moderates", friends_4="Republicans", friends_5="Democrats", tense="tense",
         death="fear of death", ewry="worse off financially", values="values in our country",
         ideo="liberal, conservative, moderate", partyid="Republican, a Democrat, an Independent",
         votereport="2016 presidential election", voting="Prolific", climate="climate change",
         beh_att_1="aid to the poor", beh_att_2="stimulate the economy", beh_att_3="healthcare",
         beh_identity="next Presidential election", virusthreat="coronavirus (COVID-19)?",
         quarantine="prohibit travel", sickleave="sick leave", fourth="4th of July")
it <- read.csv(items_csv, stringsAsFactors = FALSE) |> distinct(item, item_text)
txt_ok <- vapply(seq_len(nrow(cw)), function(i) {
  t <- it$item_text[it$item == cw$item[i]]
  length(t) == 1 && grepl(key[[cw$var[i]]], t, fixed = TRUE)
}, logical(1))
cat(sprintf("item_text carries its variable's codebook phrase: %d/%d\n", sum(txt_ok), nrow(cw)))
if (any(!txt_ok)) print(cw[!txt_ok, ])

ok <- nrow(cw) == 37 && n_bad == 0 && all(m2$n == m2$ln) && max(abs(m2$mean - m2$lmean)) < 1e-9 && all(txt_ok)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
