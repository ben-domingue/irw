##Paired tax-change choice experiment (UK) from
##Barnes, L., de Romémont, J., & Lauderdale, B. E. (2024). Public preferences over changes to
##the composition of government tax revenue. British Journal of Political Science, 54(4),
##1457-1467. https://doi.org/10.1017/S0007123424000127
##Replication data: Harvard Dataverse doi:10.7910/DVN/FXPEFT, CC0 1.0. Files read:
##P_lse_tax_experiment_Sept21_client_with_timing.sav ("original format" download; YouGov
##export, 9,713 respondents) and survey_prompts_final.csv (the 56 prompt texts the survey
##drew from, one row per lever x direction x size). Read as text/image only:
##tax-experiment-replication.Rmd (the authors' analysis and paper source), codebook.html,
##screenshot_without_arguments_shiny.jpg (an example screen).
##Usage: Rscript barnes_2024.R <dir holding the .sav and the prompts csv> <output dir>
##
##YouGov, nationally representative UK adults, 4-14 October 2021. One task per respondent:
##two proposed tax changes side by side (Option A = profile 1, Option B = profile 2, as on the
##screen). exp3a_csv_row_seen / exp3bexp3b give the row of survey_prompts_final.csv shown as
##A / B (the authors' Rmd merges them the same way). Randomized: the two tax levers (never
##the same lever twice, checked), and at task level the direction (qsplit_revenueDirection:
##increase / cut, same for A and B, checked), the revenue size (qsplit_revenueSize: £1
##billion / £10 billion, same for A and B; £10 billion only for the 'big five' taxes, so the
##size restricts which levers can appear: restriction) and an argument arm (qsplit_arguments:
##pro arguments for both, con arguments for both, or none).
##Attributes, as displayed (assembled from the prompts file following the screenshot):
##  attr_headline     leverChange1 + commNameCh, e.g. "An increase in the higher rate of
##                    income tax." (identifies lever x direction)
##  attr_description  taxDescription + complementSQ + leverSQ (how the tax works, status quo)
##  attr_change       statementOfChange + " would <increase|cut> tax revenue by <size> per
##                    year." (the screenshot shows "would increase tax revenue by £1 billion per
##                    year."; the cut wording follows the authors' appendix table code, Rmd
##                    L1155-1156)
##  attr_argument     the lever's `pro` or `con` text in the pro / con arms, "(not shown)" in
##                    the no-argument arm. The sentence that framed the argument on screen is
##                    not in the deposit: the stored text is the inserted fragment only.
##Task-level columns: trial_direction, trial_revenue_size, trial_arguments (answer text of
##the qsplit variables), trial_page_time_sec (page_p_exp3_timing).
##Outcome choice: "If the government was only going to make one of these changes, which
##would you prefer?" Option A / Option B / "I think both of these changes are equally good or
##bad." / "Don't know". OPT-OUT: the last two (2,911 and 1,709 respondents) are tasks with
##choice = 0 on both profiles; 2,565 chose A and 2,528 chose B (the paper's counts).
##Covariates (answer text of the .sav value labels): cov_age (years, `age` as stored),
##cov_gender (profile_gender Male/Female -> male/female), cov_education
##(profile_education_level text; "Prefer not to say" -> NA, "Don't know" kept),
##cov_education_age, cov_region (profile_GOR), cov_household_income (profile_gross_household),
##cov_marital_status, cov_social_grade, cov_work_status, cov_eu_ref_vote (pastvote_EURef),
##cov_voted_ge_2019, cov_vote_ge_2019 (pastvote_ge_2019: vote choice, not party ID),
##cov_survey_weight (W8, the YouGov weight the paper uses), cov_duration_sec (endtime -
##starttime, whole survey). Dropped: timestamps, YouGov weighting-cell variables
##(bpcagegeneduc_w8, socgrade4_w8, threeway_attention_w8, pvbyregion_w8, EURef_w8). ID is a
##1..9713 row key, kept as id. N = 9,713, as in the paper.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "P_lse_tax_experiment_Sept21_client_with_timing.sav")))
p <- as.data.table(read.csv(file.path(raw, "survey_prompts_final.csv"), encoding = "UTF-8", stringsAsFactors = FALSE))
stopifnot(nrow(s) == 9713, all(p$X == seq_len(nrow(p))), uniqueN(s$ID) == 9713)
lab <- function(x) { v <- as.character(as_factor(x, levels = "labels")); v[v %in% c("Skipped", "Not Asked")] <- NA; v }
s[, `:=`(ra = as.integer(exp3a_csv_row_seen), rb = as.integer(exp3bexp3b))]
s[, `:=`(dir = lab(qsplit_revenueDirection), size = lab(qsplit_revenueSize), args = lab(qsplit_arguments), ans = lab(q1_exp3))]
stopifnot(!anyNA(s[, .(ra, rb, dir, size, args, ans)]), p$lever[s$ra] != p$lever[s$rb],
          p$revenueDirection[s$ra] == s$dir, p$revenueDirection[s$rb] == s$dir,
          p$revenueSize[s$ra] == s$size, p$revenueSize[s$rb] == s$size)
prof <- function(r, k) {
  q <- p[r]
  data.table(id = as.integer(s$ID), task = 1L, profile = k,
             choice = as.integer(s$ans == c("Option A", "Option B")[k]),
             attr_headline = paste(trimws(q$leverChange1), trimws(q$commNameCh)),
             attr_description = paste(trimws(q$taxDescription), trimws(q$complementSQ), trimws(q$leverSQ)),
             attr_change = paste0(trimws(q$statementOfChange), " would ", q$revenueDirection, " tax revenue by ",
                                  q$revenueSize, " per year."),
             attr_argument = fifelse(s$args == "the pro arguments for both A and B", trimws(q$pro),
                             fifelse(s$args == "the con arguments for both A and B", trimws(q$con), "(not shown)")))
}
d <- rbind(prof(s$ra, 1L), prof(s$rb, 2L))
tk <- s[, .(id = as.integer(ID), trial_direction = dir, trial_revenue_size = size, trial_arguments = args,
            trial_page_time_sec = as.numeric(page_p_exp3_timing))]
edu <- lab(s$profile_education_level); edu[edu == "Prefer not to say"] <- NA
g <- lab(s$profile_gender); stopifnot(all(g %in% c("Male", "Female")))
cv <- s[, .(id = as.integer(ID), cov_age = as.integer(zap_labels(age)), cov_gender = tolower(g), cov_education = edu,
            cov_education_age = lab(profile_education_age), cov_region = lab(profile_GOR),
            cov_household_income = lab(profile_gross_household), cov_marital_status = lab(profile_marital_stat),
            cov_social_grade = lab(profile_socialgrade_cie), cov_work_status = lab(profile_work_stat),
            cov_eu_ref_vote = lab(pastvote_EURef), cov_voted_ge_2019 = lab(voted_ge_2019),
            cov_vote_ge_2019 = lab(pastvote_ge_2019), cov_survey_weight = as.numeric(W8),
            cov_duration_sec = as.numeric(difftime(endtime, starttime, units = "secs")))]
stopifnot(!anyNA(cv$cov_age), all(cv$cov_age >= 18))
d <- merge(merge(d, tk, by = "id"), cv, by = "id")
stopifnot(d[, sum(choice), id][, all(V1 <= 1)], d[, sum(choice)] == 2565 + 2528)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnes_2024_tax_levers.csv"))
