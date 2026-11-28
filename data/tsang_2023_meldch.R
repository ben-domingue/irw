# MELD-CH: Megastudy of Lexical Decision in Chinese, trial level. Two groups of
# readers, one of simplified and one of traditional Chinese, made visual lexical
# decisions on the same 12,578 Chinese words (1-4 characters), each group seeing
# them in its own script.
# Tsang, Y.-K., Huang, J., Wang, S., Wang, J., & Wong, A. W.-K. (2024).
# Comparing word recognition in simplified and traditional Chinese: A megastudy
# approach. Quarterly Journal of Experimental Psychology, 77(3), 593-610.
# doi:10.1177/17470218231176472
# Data: OSF https://osf.io/qzn32 (MELD-CH.xlsx). The OSF project sets no
# licence; Yiu-Kei Tsang granted IRW permission to share it on 2026-11-27 (the
# ask named CC BY 4.0; no other terms were set).
#
# Workbook sheets: `trial` (sub_id, script, item_id, order, RT, zRTp, zRTs, ERR,
# then word-level predictors), `participant` (sub, list, script, dictation,
# prorating, age, gender, mean RT, mean ERR), `item` (item, sim_word, tra_word,
# same, then per-script item means).
#
# Layout (person-first):
#   id   = `sub_id` (source participant number; 1xxxxx simplified group,
#          2xxxxx traditional group)
#   item = `item_id`, the source word number. The item is the word, not the
#          string shown: the two groups saw it in different scripts, and the
#          item sheet gives 31 traditional forms to two item_ids each (e.g.
#          乳製品 for both 奶制品 and 乳制品), so the string is not a unique key.
#   resp = 1 - `ERR` (1 = correct "word" decision)
#   rt   = `RT` / 1000, seconds. The source leaves RT empty on every error and
#          on 790 correct trials (outliers removed by the authors); kept empty.
#   trial_number = `order`, the trial's position in the session. It runs to
#          2,140 while a person has about 1,048 word trials: the workbook holds
#          word trials only, so the nonword trials are not in this table.
#   trial_list   = `list` (1-12), the word list the person was given
#   cov_script, cov_age, cov_gender, cov_dictation (dictation test score),
#   cov_proficiency_rating (`prorating`, self-rated proficiency); NA as given
#   itemcov_simplified, itemcov_traditional = the word as shown to each group;
#   itemcov_same_form = 1 when the two forms are identical (`same`)
# Not carried: zRTp/zRTs (derived), the word-level predictors in the trial
# sheet, and the per-person and per-item means.
#
# Usage: Rscript tsang_2023_meldch.R <MELD-CH.xlsx> <out_dir>
suppressMessages(library(readxl))

args <- commandArgs(trailingOnly = TRUE)
src <- if (length(args) >= 1) args[1] else "MELD-CH.xlsx"
out_dir <- if (length(args) >= 2) args[2] else "."

tr <- as.data.frame(read_excel(src, "trial", guess_max = 1e6))
pa <- as.data.frame(read_excel(src, "participant"))
it <- as.data.frame(read_excel(src, "item"))

stopifnot(nrow(tr) == 875308, !anyDuplicated(tr[, c("sub_id", "item_id")]),
          !anyDuplicated(pa$sub), !anyDuplicated(it$item),
          all(tr$sub_id %in% pa$sub), all(tr$item_id %in% it$item),
          all(tr$ERR %in% c(0, 1)), all(is.na(tr$RT[tr$ERR == 1])),
          sum(is.na(tr$RT) & tr$ERR == 0) == 790,
          all((it$sim_word == it$tra_word) == (it$same == 1)))
p <- pa[match(tr$sub_id, pa$sub), ]
stopifnot(all(p$script == tr$script))
w <- it[match(tr$item_id, it$item), ]

out <- data.frame(
  id = as.integer(tr$sub_id),
  item = as.integer(tr$item_id),
  resp = as.integer(1 - tr$ERR),
  rt = tr$RT / 1000,
  trial_number = as.integer(tr$order),
  trial_list = as.integer(p$list),
  cov_script = c(sim = "simplified", tra = "traditional")[tr$script],
  cov_age = p$age,
  cov_gender = p$gender,
  cov_dictation = p$dictation,
  cov_proficiency_rating = p$prorating,
  itemcov_simplified = w$sim_word,
  itemcov_traditional = w$tra_word,
  itemcov_same_form = as.integer(w$same),
  stringsAsFactors = FALSE
)
stopifnot(!anyNA(out$cov_script), !anyDuplicated(out[, c("id", "trial_number")]))
out <- out[order(out$id, out$trial_number), ]

name <- "tsang_2023_meldch"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
f <- file.path(out_dir, paste0(name, ".csv"))
write.csv(out, f, row.names = FALSE, na = "", fileEncoding = "UTF-8")
cat(sprintf("%s: rows=%d ids=%d items=%d resp_mean=%.3f rt_empty=%d rt=%.3f-%.3f\n",
            name, nrow(out), length(unique(out$id)), length(unique(out$item)),
            mean(out$resp), sum(is.na(out$rt)), min(out$rt, na.rm = TRUE),
            max(out$rt, na.rm = TRUE)))
# Then: irw-validate <out_dir>/tsang_2023_meldch.csv
