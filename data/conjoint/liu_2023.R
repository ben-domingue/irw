##Public-program evaluation conjoint from
##Liu, Y., Lee, H., & Berry, F. (2023). How and when democratic values matter: Challenging
##the effectiveness-centric framework in program evaluation. Public Performance &
##Management Review, 46(4), 820-845. https://doi.org/10.1080/15309576.2023.2184839
##Replication data: Harvard Dataverse doi:10.7910/DVN/FJ82VU, CC0 1.0. Files read:
##Conjoint_LBB_PPMR.csv and Survey_LBB_PPMR.csv (Dataverse "original format" downloads
##of the two .tab files). No codebook ships with the deposit.
##Usage: Rscript liu_2023.R <dir holding the two .csv files> <output dir>
##
##liu_2023_program_evaluation: 1,154 US adults, 4 pairs of hypothetical school energy-saving
##  programs, 4 attributes (who decision-making involves; who implementation information
##  is available to; annual CO2 reduction; annual school savings). Each attribute had
##  two levels. Attribute order was randomized once per respondent and held across the
##  4 tasks; the row position (1-4) is kept as attrpos_* (from the survey file's F.1.k
##  columns). Level and attribute text are as displayed in the survey file.
##  Outcomes: choice = forced choice between the two programs (no opt-out; every task has
##  exactly one chosen profile); rating = 0-100 slider rating of each program (one
##  decimal; higher = more support; the authors code > 50 as "support"). The exact
##  question wording is not in the deposit and the article was not reachable.
##  The authors' analyses keep only the 885 respondents who passed the manipulation
##  check and the attention check; all 1,154 are kept here with those flags as covariates.
##  Respondents were randomized to a low-trust prime or a control text before the
##  conjoint: trial_low_trust_prime (1 = low-trust prime). The authors' plotting script
##  relabels "Diverse local communities" as "Local communities"; the displayed text is kept.
##Covariates (source codes): cov_trust = trust in US local government, 0-100, measured
##  after the prime; cov_manip_check = answer to the prime manipulation check (23/24),
##  cov_manip_check_pass and cov_attention_pass (1 = passed; source `at`, which the authors'
##  LLB_PPMR2023.R calls the "attention test"); cov_us (source "us", 0/1, meaning
##  undocumented); cov_gender female/male from the authors' dummies `female`/`male` (sex 1
##  -> male = 1, sex 2 -> female = 1, checked; LLB_PPMR2023.R reports survey$female as
##  "Female" in its descriptive table); cov_race (1 White, 2 Black, 3 Hispanic, 4 Asian, 5
##  other; from the authors' dummies); cov_age in years; cov_income (1-7) ordinal code and
##  cov_education_code (1-8; the main education question, but no source maps the codes, so
##  they stay codes); cov_ideology (1 very liberal ... 5 very conservative, 6 none/don't
##  know, inferred from the authors' ideo1/ideo2 recodes); cov_duration_sec = Qualtrics
##  total survey duration (source `duration`; the unit is not documented, but values run
##  50-14,227 with median 274, which only makes sense as seconds).
##Design: attribute levels' probabilities and any restrictions are not documented (each
##  attribute has two levels; shares within 1.05x; all level pairs occur). Profiles are the
##  Qualtrics conjoint table (F.<task>.<profile>.<row> fields). No task is designed as a
##  repeat (with 16 possible profiles, some pairs recur by chance). No survey weight.
##Dropped: Qualtrics RandomID, the observation counter, the authors' ideology recodes.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cj <- fread(file.path(raw, "Conjoint_LBB_PPMR.csv"))
sv <- fread(file.path(raw, "Survey_LBB_PPMR.csv"))
d <- cj[, .(id = as.integer(IndID), task = as.integer(PairID), profile = as.integer(Profile),
            choice = as.integer(choice), rating = as.numeric(rate),
            attr_decision_making_involves = Inclusiveness,
            attr_implementation_info_available_to = Openness,
            attr_co2_reduction = Environmental.indicator,
            attr_school_savings = Economic.indicator,
            trial_low_trust_prime = as.integer(prime))]
## attribute row positions (identical in all 4 tasks for every respondent)
stopifnot(sv[, all(F.1.1 == F.4.1 & F.1.2 == F.4.2 & F.1.3 == F.2.3 & F.1.4 == F.3.4)])
pos <- sv[, .(id = as.integer(id), a1 = F.1.1, a2 = F.1.2, a3 = F.1.3, a4 = F.1.4)]
pmap <- c("decision-making involves" = "decision_making_involves",
          "implementation information is available to" = "implementation_info_available_to",
          "reduce annual CO2 emission (metric tones)" = "co2_reduction",
          "save schools' annual expense" = "school_savings")
for (nm in names(pmap)) pos[, paste0("attrpos_", pmap[[nm]]) := fifelse(a1 == nm, 1L, fifelse(a2 == nm, 2L, fifelse(a3 == nm, 3L, fifelse(a4 == nm, 4L, NA_integer_))))]
pos[, c("a1", "a2", "a3", "a4") := NULL]
stopifnot(!anyNA(pos))
cov <- sv[, .(id = as.integer(id), cov_trust = as.numeric(trust), cov_manip_check = as.integer(mc),
              cov_manip_check_pass = as.integer(mc.t), cov_attention_pass = as.integer(at), cov_us = as.integer(us),
              cov_gender = fifelse(female == 1, "female", fifelse(male == 1, "male", NA_character_)), cov_race = fifelse(white == 1, 1L, fifelse(blk == 1, 2L, fifelse(his == 1, 3L, fifelse(asian == 1, 4L, 5L)))),
              cov_age = as.integer(age), cov_income = as.integer(income), cov_education_code = as.integer(education),
              cov_ideology = as.integer(ideo), cov_duration_sec = as.integer(duration))]
stopifnot(sv[, all(is.na(sex) | (sex == 1 & male == 1 & female == 0) | (sex == 2 & female == 1 & male == 0))])
stopifnot(nrow(pos) == uniqueN(d$id), nrow(cov) == uniqueN(d$id))
d <- merge(merge(d, pos, by = "id"), cov, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "liu_2023_program_evaluation.csv"))
