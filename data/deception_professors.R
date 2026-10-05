# deception_professors
#
# Source: OSF f3kzr, DeceptionBan_ProfSurvey_OSF.sav (file 74pgd): a survey of
# psychology and economics professors on deception in experiments.
#
# Rebuilt 2026-10-05 (irw#2846). Before, items were numbered 1-21 by column
# position; they now keep the source's variable names (lower case):
#   1 decept_percent_psych, 2 decept_percent_eco, 3 decept_percent_socsci
#   (0-100); 4 decept_rigorous; 6-8 psych/eco/gensci_considerdecept (1-5);
#   9-16 eco_poolbans, eco_journalbans, psych_poolbans, psych_journalban,
#   gensci_journalban, banharmful_eco, banharmful_psych, banharmful_gensci
#   (1-7); 17 you_percent_decept (0-100); 18 you_worry_rigor;
#   19 you_limit_decept.
# Old item 5 (orthogonal_to_rigor, always 1) was not an item: it is one of the
# coded categories of the open answer to "are deception studies inherently
# less rigorous? Please elaborate". Old items 20/21 folded those coded
# categories (and the ones for "why don't you use deception?") into one 1-8
# code, keeping only the first category ticked and missing
# orthogonal_to_rigor entirely. Each category is now its own 0/1 item,
# reason_less_rigorous_<category> / reason_no_deception_<category>, for the
# respondents whose answer was coded (not "blank"); 1 = the answer was coded
# into that category. Rows with no response are dropped (they had been
# shipped as resp "NA", #2029).
# Demographics (sex, age band, race, ...) are not shipped, as before.
library(dplyr)
library(tidyr)
library(haven)

df <- read_sav("DeceptionBan_ProfSurvey_OSF.sav")
names(df) <- tolower(names(df))
df <- zap_labels(df)
df <- rename(df, id = subid)

items <- c("decept_percent_psych", "decept_percent_eco", "decept_percent_socsci",
           "decept_rigorous",
           "psych_considerdecept", "eco_considerdecept", "gensci_considerdecept",
           "eco_poolbans", "eco_journalbans", "psych_poolbans", "psych_journalban",
           "gensci_journalban", "banharmful_eco", "banharmful_psych",
           "banharmful_gensci",
           "you_percent_decept", "you_worry_rigor", "you_limit_decept")

main <- df |>
  # yes/no items to 0/1 (0 == no, 1 == yes)
  mutate(decept_rigorous = if_else(decept_rigorous == 2, 0, decept_rigorous),
         you_worry_rigor = if_else(you_worry_rigor == 2, 0, you_worry_rigor)) |>
  select(id, all_of(items)) |>
  pivot_longer(-id, names_to = "item", values_to = "resp")

# coded open answers: one 0/1 item per category, for coded (non-blank) answers
coded <- function(cats, prefix) {
  d <- df[, c("id", cats)]
  d[cats] <- lapply(d[cats], function(x) as.numeric(!is.na(x) & x == 1))
  d <- d[rowSums(d[cats]) > 0, ]   # "blank" (no answer given) alone -> no rows
  d |>
    pivot_longer(-id, names_to = "item", values_to = "resp") |>
    mutate(item = paste0(prefix, sub("other2$", "other", item)))
}
less_rigorous <- coded(c("orthogonal_to_rigor", "necessary_or_more_rigorous",
                         "immoral", "misinterprets_deception", "depends_on_method",
                         "hurts_future_studies", "subjects_notdeceived",
                         "its_lazy_unnecessary", "other"),
                       "reason_less_rigorous_")
no_deception <- coded(c("not_relevant", "not_necessary", "iam_economist",
                        "lose_trust_pool", "need_trust_study", "difficult_publish",
                        "unethical", "other2"),
                      "reason_no_deception_")

out <- bind_rows(main, less_rigorous, no_deception) |>
  filter(!is.na(resp)) |>
  arrange(id, item) |>
  as.data.frame()

print(c(rows = nrow(out), ids = length(unique(out$id)), items = length(unique(out$item))))
write.csv(out, "deception_professors.csv", row.names = FALSE)
