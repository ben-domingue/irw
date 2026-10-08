##Ukraine-support strategy conjoint (United States) from
##Rudolph, L. (2026). Is there a partisan divide in citizens' preferences on Ukraine support?
##Survey-experimental evidence from the US. Public Opinion Quarterly.
##https://doi.org/10.1093/poq/nfag026
##Replication data: Harvard Dataverse doi:10.7910/DVN/G8BI88, CC0 1.0, no restricted files.
##File read: yougov_master.dta (Dataverse "original format" download; one row per respondent).
##Level text: the author's English labels in 1-us_ukraine_data_gen.do (read as text), checked
##against the preprint's Figure 1 (OSF 5whx9_v2) and yougov_codebook.xlsx (German master
##questionnaire value labels). The US survey showed English text; the exact displayed text is in
##the OSF pre-registration (doi:10.17605/OSF.IO/TVZSA), not read. Known gaps: the two aid
##attributes displayed a dollar amount plus the GDP share ("X bn (0.1% of US GDP)"); only the
##share survives, stored as "0.1% of GDP" etc. Territory and self-determination levels are the
##author's short labels ("2014 LoC (8%)", "No EU/NATO"); the displayed text was longer
##(codebook: "Abtretung der Krim und der Separatistengebiete von 2014 ... (ca. 8% ...)").
##Usage: Rscript rudolph_2026.R <dir holding yougov_master.dta> <output dir>
##
##2,334 US adults (YouGov opt-in panel, June-August 2023; the article's N), 4 tasks of 2
##"strategies" for supporting Ukraine, 9 attributes (Ukrainian soldiers killed, Russian soldiers
##killed, Ukrainian civilians killed, destroyed infrastructure, US military aid, US economic aid,
##nuclear-strike risk, territorial cessions, self-determination). The article: uniform random
##display without restrictions; attribute order block-randomized and constant within respondent
##(not recorded). Identical levels on both profiles (ties) occur by design; the author's main
##choice models drop tied tasks attribute by attribute; nothing is dropped here.
##task = the YouGov screen (1-4), profile = concept (1 = Strategy A, 2 = Strategy B).
##trial_task_no = the source's UKR_ROUND2_task<k> ("task no. identifier"; a permutation of 1-4
##within every respondent, used by the author for round-order checks). Whether task (screen) or
##trial_task_no is the display order is not documented; the author treats trial_task_no as the
##round number.
##Outcomes (wording translated from the German master questionnaire in the codebook):
##  choice: "If you had to choose between one of the two strategies, which would you personally
##    prefer?" Strategy A / Strategy B, forced, no opt-out (every task has one choice).
##  rating: "Now consider both strategies individually. On a scale from 1 to 7, ..." 1 =
##    definitely reject, 7 = definitely support after the author's recode: the endpoint order was
##    randomized per respondent (scale_Q8_Q12_Q13 = 2: 1 = definitely support), and those
##    answers are reversed (8 - x) as in the author's do-file. Kept as trial_scale_reversed.
##    The rating was asked in 2 of the 4 tasks only (article fn 10); rating is blank in the
##    other two (9,334 of 18,672 rows).
##Covariates. As text, from the .dta value labels (identical in yougov_codebook.xlsx, sheet
##Labels): cov_gender (gender: 1 Male, 2 Female; stored male / female), cov_education
##(education, "What is your highest level of education? ...": the 10 option labels as stored,
##e.g. "Bachelors or equivalent level degree"; labels 6 and 7 are cut at 120 characters in both
##the .dta and the codebook, and are kept as cut), cov_party_id (pid3 "3 point party ID":
##Democrat, Republican, Independent, Other, Not sure). Source codes (labels in the codebook):
##cov_age (years), cov_state, cov_region, cov_employ, cov_household_size, cov_income,
##cov_pol_interest, cov_left_right (0-10), cov_presvote20 (2020 vote), cov_vote_intention
##(Q4_2_US), cov_survey_weight (W8). The article's partisan groups
##(Democrat 758, Republican 739, other 837) come from presvote20post (1 / 2 / else) and
##reproduce from cov_presvote20. Dropped: the vignette experiment (Q13*, one-factor, separate),
##the open vote-intention text (Q4_2_US_open), quota cell (pastvote_by_race), the scale endpoint
##pipe text, and the source respondent id (re-keyed to 1..2,334 in file order).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
m <- read_dta(file.path(raw, "yougov_master.dta"))
z <- function(x) as.integer(zap_labels(x))
lab <- list(c("12,500", "25,000", "50,000"), c("25,000", "50,000", "100,000"), c("4,000", "8,000", "16,000"),
            c("$50B", "$100B", "$200B"), c("0.1% of GDP", "0.2% of GDP", "0.3% of GDP"),
            c("0.1% of GDP", "0.2% of GDP", "0.3% of GDP"), c("Not present (0%)", "Low (5%)", "Moderate (10%)"),
            c("None", "Crimea (4%)", "2014 LoC (8%)", "2023 LoC (16%)"), c("Full", "No EU/NATO", "Russian influence"))
anm <- c("ukr_soldiers_killed", "rus_soldiers_killed", "ukr_civilians_killed", "infrastructure_destroyed",
         "us_military_aid", "us_economic_aid", "nuclear_risk", "territorial_cessions", "self_determination")
n <- nrow(m); rev <- z(m$scale_Q8_Q12_Q13) == 2L
stopifnot(all(z(m$scale_Q8_Q12_Q13) %in% 1:2))
d <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = seq_len(n), task = t, profile = p,
                  choice = as.integer(z(m[[paste0("Q12A", t)]]) == p),
                  rating = z(m[[paste0("Q12B", t, "_", p)]]))
  x[rev, rating := 8L - rating]
  for (k in 1:9) {
    v <- z(m[[sprintf("q2_attr%d_concept%d_task%d", k, p, t)]])
    stopifnot(all(v %in% seq_along(lab[[k]])))
    x[, paste0("attr_", anm[k]) := lab[[k]][v]]
  }
  x[, trial_task_no := z(m[[paste0("UKR_ROUND2_task", t)]])]
  x[, trial_scale_reversed := as.integer(rev)]
  x
}))))
cv <- c(cov_age = "age", cov_gender = "gender", cov_state = "inputstate", cov_region = "vRegionGrouped",
        cov_education = "education", cov_employ = "employ", cov_household_size = "profile_household_size",
        cov_income = "profile_gross_household", cov_pol_interest = "lmu_polInterest", cov_left_right = "pol_spect",
        cov_presvote20 = "presvote20post", cov_party_id = "pid3", cov_vote_intention = "Q4_2_US")
for (v in names(cv)) d[, (v) := z(m[[cv[[v]]]])[id]]
vl <- function(v) { l <- attr(m[[v]], "labels"); x <- z(m[[v]]); stopifnot(all(x %in% l)); names(l)[match(x, l)] }
stopifnot(identical(names(attr(m$gender, "labels"))[1:2], c("Male", "Female")))
d[, cov_gender := tolower(vl("gender"))[id]][, cov_education := vl("education")[id]][, cov_party_id := vl("pid3")[id]]
stopifnot(all(d$cov_gender %in% c("male", "female")))
d[, cov_survey_weight := as.numeric(m$W8)[id]]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, sum(!is.na(rating)), .(id, task)][, all(V1 %in% c(0L, 2L))],
          d[!is.na(rating), all(rating %in% 1:7)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rudolph_2026_ukraine_support.csv"))
