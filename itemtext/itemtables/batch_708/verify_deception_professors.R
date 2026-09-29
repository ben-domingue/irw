# verify_deception_professors.R -- Step 5b mapping check for deception_professors (batch_708)
#
# CODE DERIVATION: script-generated integer (core model section 3, pattern 4).
# data/deception_professors.R pivots the retained .sav columns long and assigns
# item = row_number() over unique(item) -- i.e. the integer is the column's
# position after the script's select()/mutate() steps. So the claim to verify is
# the integer -> .sav variable mapping, and the check is to RE-RUN the script's
# logic over the OSF .sav and reproduce the live table item by item.
#
# Evidence that would break under a swap: for every item, the full frequency
# table of resp (every level, every count) from the re-run must equal the live
# table's, AND no two items may share a distribution (otherwise a swap between
# them would be invisible). Both are checked below.
#
# Source: OSF f3kzr (CC BY 4.0), DeceptionBan_ProfSurvey_OSF.sav
#   https://osf.io/download/74pgd/  sha256 a816b503c111a06b1a24b95f35ea797cdc87e6526bb9da172b4e4c25aff29d7a

suppressMessages({ library(irw); library(haven); library(dplyr); library(tidyr) })

TABLE <- "deception_professors"
sav <- file.path(tempdir(), "DeceptionBan_ProfSurvey_OSF.sav")
local <- "itemtext/.cache/deception_professors/DeceptionBan_ProfSurvey_OSF.sav"
for (p in c(local, sub("^itemtext/", "", local))) if (file.exists(p)) { file.copy(p, sav, overwrite = TRUE); break }
if (!file.exists(sav)) download.file("https://osf.io/download/74pgd/", sav, mode = "wb", quiet = TRUE)

# ---- re-run data/deception_professors.R (labelled::remove_labels -> haven::zap_labels) ----
df <- read_sav(sav); names(df) <- tolower(names(df))
df <- df |> rename(id = subid) |>
  select(-psych_reviewer, -numb_psychrevier, -numb_psycheditor, -eco_reviewer, -numb_ecoreview,
         -numb_ecoedit, -gensci_reviewer, -numb_genscireview, -numb_gensciedit, -you_use_decept,
         -you_rejected_bc_decept, -sex, -age, -hispanic, -race, -position, -instituteion_type,
         -region, -department, -you_behave_eco) |>
  mutate(decept_rigorous = if_else(decept_rigorous == 2, 0, decept_rigorous),
         reason_less_rigorous = case_when(necessary_or_more_rigorous == 1 ~ 1, immoral == 1 ~ 2,
           misinterprets_deception == 1 ~ 3, depends_on_method == 1 ~ 4, hurts_future_studies == 1 ~ 5,
           subjects_notdeceived == 1 ~ 6, its_lazy_unnecessary == 1 ~ 7, other == 1 ~ 8),
         you_worry_rigor = if_else(you_worry_rigor == 2, 0, you_worry_rigor),
         reason_no_deception = case_when(not_relevant == 1 ~ 1, not_necessary == 1 ~ 2,
           iam_economist == 1 ~ 3, lose_trust_pool == 1 ~ 4, need_trust_study == 1 ~ 5,
           difficult_publish == 1 ~ 6, unethical == 1 ~ 7, other2 == 1 ~ 8)) |>
  select(-necessary_or_more_rigorous, -immoral, -misinterprets_deception, -depends_on_method,
         -hurts_future_studies, -subjects_notdeceived, -its_lazy_unnecessary, -blank, -other,
         -not_relevant, -not_necessary, -iam_economist, -lose_trust_pool, -need_trust_study,
         -difficult_publish, -unethical, -blank2, -other2) |>
  mutate(across(-id, ~ as.numeric(zap_labels(.x)))) |>
  pivot_longer(!id, names_to = "var", values_to = "resp")
map <- data.frame(var = unique(df$var)); map$item <- seq_len(nrow(map))
df <- left_join(df, map, by = "var")

# The mapping the shipped item text assumes (item -> .sav variable)
CLAIM <- c("decept_percent_psych", "decept_percent_eco", "decept_percent_socsci", "decept_rigorous",
           "orthogonal_to_rigor", "psych_considerdecept", "eco_considerdecept", "gensci_considerdecept",
           "eco_poolbans", "eco_journalbans", "psych_poolbans", "psych_journalban", "gensci_journalban",
           "banharmful_eco", "banharmful_psych", "banharmful_gensci", "you_percent_decept",
           "you_worry_rigor", "you_limit_decept", "reason_less_rigorous", "reason_no_deception")
ok_map <- identical(map$var, CLAIM)
cat("re-run mapping equals shipped mapping:", ok_map, "\n\n")

live <- irw::irw_fetch(TABLE)
live$item <- as.integer(as.character(live$item))
cat(sprintf("rows: re-run %d, live %d\n\n", nrow(df), nrow(live)))

sig <- function(x) { x <- x[!is.na(x)]; t <- table(x); paste(names(t), t, sep = ":", collapse = " ") }
cat(sprintf("%-4s %-22s %5s %5s %11s %11s %s\n", "item", "variable", "n_rr", "n_lv", "mean_rerun", "mean_live", "freq_equal"))
all_eq <- TRUE; sigs <- character(21)
for (i in 1:21) {
  a <- df$resp[df$item == i]; b <- live$resp[live$item == i]
  eq <- sig(a) == sig(b); all_eq <- all_eq && eq; sigs[i] <- sig(b)
  cat(sprintf("%-4d %-22s %5d %5d %11.5f %11.5f %s\n", i, map$var[i], sum(!is.na(a)), sum(!is.na(b)),
              mean(a, na.rm = TRUE), mean(b, na.rm = TRUE), eq))
}
n_distinct_sig <- length(unique(sigs))
cat(sprintf("\nitems whose full resp frequency table matches re-run exactly: %d/21\n",
            sum(sapply(1:21, function(i) sig(df$resp[df$item == i]) == sig(live$resp[live$item == i])))))
cat(sprintf("distinct live per-item distributions: %d/21 (21 = every item distinguishable from every other)\n",
            n_distinct_sig))
cat("Note: this proves integer -> .sav variable. The variable -> wording tie is the .sav's own\n",
    "variable/value labels (and the codebook), read directly; it is not re-tested here.\n", sep = "")

cat(if (ok_map && all_eq && n_distinct_sig == 21) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
