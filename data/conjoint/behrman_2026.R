##Preferred-family-scenario conjoint (US women 18-35) from
##Behrman, J. A., Marshall, E., & Percheski, C. (2026). Economic resources and parity among
##US women: A conjoint experiment on preferred family scenarios. Demographic Research,
##54(34), 1095-1124. https://doi.org/10.4054/DemRes.2026.54.34
##Replication data: OSF https://osf.io/85kgh/, CC BY 4.0. The OSF licence field was empty;
##the depositor granted the IRW permission by email on 2026-10-23 and asked for CC BY 4.0
##(oneoff/licence-asks-2026-10/outbox/85kgh_behrman.txt, outreach_log 2026-10-23).
##File read: dta_raw.dta, the raw TESS/NORC export. dta_clean.dta is NOT used: its cleaning
##file replaces the displayed level text with short codes ("extra", "40 hrs", "cohab",
##1_data_clean.do L218-243) and drops the desirability ratings. 1_data_clean.do,
##2_analysis.do and readme.rtf were read as text (not run); the article (open access) gives
##Table 2 (attributes and levels), the design restrictions and the attribute-order rule.
##Usage: Rscript behrman_2026.R <raw dir> <output dir>
##
##Fielded on the NORC AmeriSpeak panel, 15 September - 4 October 2023, funded by TESS:
##1,794 US women aged 18-35, each shown 6 pairs of "life situations" (12 profiles) built
##from 6 attributes. 21,528 rows = 1,794 x 6 x 2.
##  attr_parity              You have no children .. You have four children (5)
##  attr_economic_resources  plenty extra / just enough / struggles to pay your bills (3)
##  attr_care_division       who does the household work (and childcare) (6 displayed forms)
##  attr_work_intensity      You work 60 / 40 / 25 hours a week / You do not have a job (4)
##  attr_family_policy       generous support / a $300 monthly child tax credit / (not shown)
##  attr_marital_status      married / single / unmarried and living with a partner (3)
##Level text is the displayed wording from the raw export's value labels. Two repairs,
##both from the article's Table 2: the generous family-policy label is truncated at 80
##characters in the .dta ("... 6 months of paid parental") and is restored to the full
##sentence; the raw export's "BLANK" family-policy level is the designed blank third
##condition ("The third family policy condition is always left blank, which we expect will
##lead participants to assume the status quo of limited policy support for families",
##article Table 2 notes), so it is stored as the reserved `(not shown)`.
##Restrictions (article Table 2 notes, and checked below): in a scenario with zero children
##the care attribute names only housework, never childcare; with marital status "single"
##only a "You do most of the household work" form is used (with childcare added when the
##scenario has children).
##Attribute order was randomized once per respondent and held constant across that
##respondent's pairs (article Figure A-1 notes); attrpos_* carry it, from the export's
##Attribute<j>_Order_* columns ("1st attribute shown" .. "6th attribute shown").
##
##Outcomes:
##  choice  which of the two scenarios the respondent would personally prefer (article,
##          Methods). Forced choice, one per pair, so opt_out = no. Source Q1, Q3, Q5, Q7,
##          Q9, Q11, each naming the chosen "Life Situation k".
##  rating  desirability of that scenario, 0 "Not desirable at all" to 10 "Very desirable"
##          (export labels Desirability_LS<k>). Asked for pairs 1-5 only: the sixth pair has
##          no rating columns, so rating is NA on its rows.
##trial_repeat_of = 1 on the rows of task 6, which repeats task 1 with the two profiles
##SWAPPED (life situation 11 = situation 2, situation 12 = situation 1; verified below).
##The authors use it as a consistency check (1_data_clean.do L123-125 "agree") and exclude
##it from their analyses, which is why the article counts 5 pairs and 8,970 paired
##evaluations; this table keeps all 6 pairs and marks the repeat.
##trial_time_choice_sec and trial_time_rating_sec are the export's TIME_Q<k> seconds for the
##pair's choice screen and its rating screen (the rating screen covers both profiles of the
##pair, so its value repeats within a task; NA for task 6).
##
##Covariates (NORC panel profile unless noted): cov_survey_weight (WEIGHT1, the final
##weight for women 18-35) and cov_survey_weight_racethnicity (WEIGHT2, normalized by
##race/ethnicity); cov_gender (all "female" -- the sample is women by design);
##cov_age (years, 18-35); cov_education, cov_race, cov_income (9-level band),
##cov_marital_status, cov_employment, cov_party_id7, cov_ideology, cov_religion,
##cov_religious_attendance, cov_region, cov_metro, cov_household_size, cov_hh_age_0_1,
##cov_hh_age_2_5, cov_hh_age_6_12, cov_hh_age_13_17, cov_hh_age_18_plus, cov_state,
##cov_device; cov_own_children (Q13, the respondent's own parity); cov_attention_pass_1
##(Q12, 1 = correctly said that none of the life situations mentioned the gender of
##children, the authors' pass_check, 1_data_clean.do L82).
##"SKIPPED ON WEB" and "Unknown" are the export's non-answer sentinels and become NA.
##Dropped: CaseId and the AmeriSpeak CBCVersion/SAMPLE_SOURCE bookkeeping, RELIG_OE
##(free-text religion), STARTDT/ENDDT, the redundant AGE4/AGE7/INCOME/INCOME4/REGION9/
##PartyID5 recodes, and the housing/home-type/phone/internet panel columns.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "dta_raw.dta")))
SENT <- c("SKIPPED ON WEB", "Unknown", "")
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[y %in% SENT] <- NA; y }
POLICY_FULL <- paste("Parents receive lots of support: affordable childcare, 6 months of",
                     "paid parental leave, flexible work, and generous sick leave")
POLICY_TRUNC <- "Parents receive lots of support: affordable childcare, 6 months of paid parental"
ATTR <- c(parity = 1, work_intensity = 2, care_division = 3, family_policy = 4,
          economic_resources = 5, marital_status = 6)
ORDCOL <- c(parity = "Attribute1_Order_ChildBearing", work_intensity = "Attribute2_Order_TimeIntensityOf",
            care_division = "Attribute3_Order_DivisionOfCareI", family_policy = "Attribute4_Order_FamilyPolicy",
            economic_resources = "Attribute5_Order_FinancialStabil", marital_status = "Attribute6_Order_MaritalStatus")
CHOICE <- c("Q1", "Q3", "Q5", "Q7", "Q9", "Q11")

## attribute order: 1..6, randomized once per respondent
pos <- sapply(ORDCOL, function(v) {
  i <- match(lab(k[[v]]), paste0(c("1st", "2nd", "3rd", "4th", "5th", "6th"), " attribute shown"))
  stopifnot(!anyNA(i)); i
})
stopifnot(apply(pos, 1, function(z) length(unique(z)) == 6L))

d <- rbindlist(lapply(1:6, function(t) rbindlist(lapply(1:2, function(p) {
  ls_i <- 2L * (t - 1L) + p                      # life situation 1..12
  ch <- lab(k[[CHOICE[t]]])
  stopifnot(all(ch %in% c(paste("Life Situation", 2L * (t - 1L) + 1:2), NA)))
  rt <- if (t <= 5) lab(k[[sprintf("Q%d_%d", 2L * t, p)]]) else rep(NA_character_, nrow(k))
  x <- data.table(rid = seq_len(nrow(k)), task = t, profile = p,
                  choice = as.integer(ch == paste("Life Situation", ls_i)),
                  rating = as.integer(sub(" .*", "", rt)),
                  trial_repeat_of = if (t == 6L) 1L else NA_integer_,
                  trial_time_choice_sec = as.integer(k[[paste0("TIME_", CHOICE[t])]]),
                  trial_time_rating_sec = if (t <= 5) as.integer(k[[sprintf("TIME_Q%d", 2L * t)]]) else NA_integer_)
  for (a in names(ATTR)) {
    v <- lab(k[[sprintf("LS%dA%d", ls_i, ATTR[[a]])]])
    if (a == "family_policy") { v[v == POLICY_TRUNC] <- POLICY_FULL; v[v == "BLANK"] <- "(not shown)" }
    x[, paste0("attr_", a) := v][, paste0("attrpos_", a) := pos[, a]]
  }
  x
}))))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          all(d$rating %in% c(0:10, NA)),
          d[, sum(choice), .(rid, task)][, all(V1 == 1)],
          ## the two documented design restrictions
          d[attr_parity == "You have no children", all(!grepl("childcare", attr_care_division))],
          d[attr_marital_status == "You are single",
            all(grepl("^You do most of the household work", attr_care_division))])
## task 6 is task 1 with the profiles swapped
key <- function(x) do.call(paste, c(x[, .SD, .SDcols = patterns("^attr_")], sep = "|"))
stopifnot(identical(key(d[task == 6 & profile == 1]), key(d[task == 1 & profile == 2])),
          identical(key(d[task == 6 & profile == 2]), key(d[task == 1 & profile == 1])))

cv <- data.table(
  rid = seq_len(nrow(k)),
  cov_survey_weight = as.numeric(k$WEIGHT1),
  cov_survey_weight_racethnicity = as.numeric(k$WEIGHT2),
  cov_gender = tolower(lab(k$GENDER)),
  cov_age = as.integer(k$AGE),
  cov_education = lab(k$EDUC5),
  cov_race = lab(k$RACETHNICITY),
  cov_income = lab(k$INCOME9),
  cov_marital_status = lab(k$MARITAL),
  cov_employment = lab(k$EMPLOY),
  cov_party_id7 = lab(k$PartyID7),
  cov_ideology = lab(k$IDEO),
  cov_religion = lab(k$RELIG),
  cov_religious_attendance = lab(k$ATTEND),
  cov_region = lab(k$REGION4),
  cov_metro = lab(k$METRO),
  cov_household_size = lab(k$HHSIZE),
  cov_hh_age_0_1 = as.integer(k$HH01), cov_hh_age_2_5 = as.integer(k$HH25),
  cov_hh_age_6_12 = as.integer(k$HH612), cov_hh_age_13_17 = as.integer(k$HH1317),
  cov_hh_age_18_plus = as.integer(k$HH18OV),
  cov_state = as.character(k$STATE),
  cov_device = as.character(k$Device),
  cov_own_children = lab(k$Q13),
  cov_attention_pass_1 = as.integer(grepl("^None of the life situations", lab(k$Q12))))
cv[is.na(lab(k$Q12)), cov_attention_pass_1 := NA_integer_]
stopifnot(all(cv$cov_gender == "female"), all(cv$cov_age %in% 18:35),
          cv[, all(cov_survey_weight > 0)])

d <- merge(d, cv, by = "rid")
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
stopifnot(nrow(d) == 21528L, uniqueN(d$id) == 1794L)
fwrite(d, file.path(out, "behrman_2026_family_scenarios.csv"))
