##Green New Deal policy-package conjoints (US, Qualtrics panel, June 7 - July 15, 2019) from
##Bergquist, P., Mildenberger, M., & Stokes, L. C. (2020). Combining climate, economic, and
##social policy builds public support for climate action in the US. Environmental Research
##Letters, 15(5), 054019. https://doi.org/10.1088/1748-9326/ab81c1
##Replication data: Harvard Dataverse doi:10.7910/DVN/FYQWMS, CC0 1.0, no restricted files.
##Files read: gnd_weighted-1.csv (published as gnd_weighted.csv: the July 15 Qualtrics export
##after the authors' raking.R filters, 2,476 respondents, with their raked weight) and
##gnd_weighted_conjoint2-1.csv (gnd_weighted_conjoint2.csv: the 2,427 of them whose second
##conjoint showed the final attribute set, re-raked). "GND Conjoint_July 15, 2019_15.06-1.csv"
##was inspected for the question text and column map (header row 1), not read by this script.
##Read as text only: readme.txt,
##raking.R, analysis_stackdata.R, analysis_main.R.
##Usage: Rscript bergquist_2020.R <dir holding the two weighted csv files> <output dir>
##
##TWO TABLES (two experiments with different attribute sets, same respondents and id):
##  bergquist_2020_gnd_social  Experiment 1, Scenarios 1-3 (Qualtrics blocks s, t, u),
##     6 attributes: Economic Programs, Social Programs, Carbon Tax, Increased Energy Costs
##     for Average US Household, Annual Government Spending, Sponsor.
##  bergquist_2020_gnd_energy  Experiment 2, Scenarios 4-6 (blocks m, n, o), 7 attributes:
##     Carbon Tax, Fossil Fuel Companies, Electricity Generation, Investments, Increased Energy
##     Costs for Average US Household, Annual Government Spending, Transportation.
##     Early in fielding the 7th attribute was Sponsor instead of Transportation; the authors
##     dropped those respondents from this experiment (raking.R: out.m_9 / n_9 / o_9 not
##     Democrats...), so this table has 2,427 respondents. The article reports 2,476 for both.
##Respondents chose in each scenario between Policy Package A (profile 1) and B (profile 2):
##"Which policy package would you prefer?" (conjoint.s ... question text); forced choice,
##exactly one per task (checked). task = scenario order within the experiment (1-3).
##Level text: the Qualtrics embedded-data values as displayed, exported as out.<block>_<k>
##(export header: out.s_1 = econ1.S = package A ... out.s_10 = econ2.S = package B; out.m_3-9
##package A, out.m_12-18 package B; out.<block>_19 = attribute order). An empty value means the package had no policy in that category: the
##authors recode it to "none" / "no energy policy" etc. (analysis_stackdata.R) and the article
##counts the "absence of an alternative" (fn 5); stored as "(not shown)". Carbon Tax shows the
##text "No carbon tax".
##Attribute order: randomized once per respondent within each experiment and recorded
##(order.S / order.M lists of attribute names; identical across the three scenarios):
##attrpos_<name> = position. Level probabilities and restrictions are not documented (the
##JavaScript in the question text is truncated in the export).
##trial_benefits: between-respondent framing sentence carried in embedded data `benefits`
##("Supporters argue this bill will also ..."), leading ". " removed; "none" when empty
##(the authors' treatment variable: none / jobs / economy / justice / weather / deaths).
##Where it was displayed is not documented.
##Covariates: cov_gender (gender: Female/Male; the authors kept only these), cov_age_group
##(age_Q: the authors' band from the survey answer or the panel's age file, raking.R),
##cov_race (race_Q: authors' recode, a stray code 6 -> Native American/Pacific Islander),
##cov_education (edu, answer text), cov_party_id (PID, "Generally speaking, do you consider
##yourself a..."), cov_ideology (ideo), cov_income (Q106, "Prefer not to answer" -> NA),
##cov_attention_pass (table 1: Q116 "which category was NOT included in the previous
##screen?" answered "Foreign Affairs"; table 2: Q117 answered "Trade Policy" -- the only
##listed category absent from that experiment; NA when unanswered), cov_duration_sec (survey
##duration), cov_survey_weight (the authors' raked, trimmed weight of the file used).
##Dropped: StartDate/EndDate, ResponseId (re-keyed), panel ids (rid, psid, uid, RISN, PID.1,
##opp, K2, med, LS), LocationLatitude/LocationLongitude and zip (PII), Recipient* (empty),
##timing, all other survey items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
w1 <- fread(file.path(raw, "gnd_weighted-1.csv"))
w2 <- fread(file.path(raw, "gnd_weighted_conjoint2-1.csv"))
stopifnot(all(w2$ResponseId %in% w1$ResponseId), !anyDuplicated(w1$ResponseId))
ids <- data.table(ResponseId = w1$ResponseId, id = seq_len(nrow(w1)))
wcol <- "weights(gnd.svy.rake.trim)"
cov <- function(w, att) {
  na <- function(v) { v[v %in% c("", "Prefer not to answer")] <- NA; v }
  data.table(ResponseId = w$ResponseId, cov_gender = tolower(w$gender), cov_age_group = na(w$age_Q), cov_race = na(w$race_Q),
             cov_education = na(w$edu), cov_party_id = na(w$PID), cov_ideology = na(w$ideo), cov_income = na(w$Q106),
             cov_attention_pass = att, cov_duration_sec = as.numeric(w[["Duration..in.seconds."]]),
             cov_survey_weight = as.numeric(w[[wcol]]))
}
# export column out.<block>_<k> holds embedded field <src><profile>.<BLOCK> (export header row 1)
stack <- function(w, blocks, src, nm, disp, k1, k2) {
  rbindlist(lapply(seq_along(blocks), function(t) {
    b <- blocks[t]; bl <- tolower(b)
    ord <- strsplit(w[[paste0("out.", bl, "_19")]], ",")
    rbindlist(lapply(1:2, function(p) {
      d <- data.table(ResponseId = w$ResponseId, task = t, profile = p,
                      choice = as.integer(w[[paste0("conjoint.", tolower(b))]] == c("Policy Package A", "Policy Package B")[p]))
      for (k in seq_along(src)) {
        v <- w[[paste0("out.", bl, "_", list(k1, k2)[[p]][k])]]
        stopifnot(!anyNA(v))
        d[, paste0("attr_", nm[k]) := ifelse(v == "", "(not shown)", v)]
        d[, paste0("attrpos_", nm[k]) := vapply(ord, function(z) match(disp[k], z), 1L)]
      }
      d
    }))
  }))
}
fin <- function(d, w, att, name) {
  stopifnot(d[, sum(choice), .(ResponseId, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attrpos_")]))
  b <- sub("^\\. ?", "", w$benefits); b[b == ""] <- "none"
  d <- merge(d, data.table(ResponseId = w$ResponseId, trial_benefits = b), by = "ResponseId")
  d <- merge(d, cov(w, att), by = "ResponseId")
  d <- merge(ids, d, by = "ResponseId")[, ResponseId := NULL]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, name))
}
# names in the order.* lists; Qualtrics embedded-data names; table names
d1 <- stack(w1, c("S", "T", "U"), c("econ", "social", "carbon", "cost", "size", "sponsor"),
            c("economic_programs", "social_programs", "carbon_tax", "energy_costs", "government_spending", "sponsor"),
            c("Economic Programs", "Social Programs", "Carbon Tax", "Increased Energy Costs for Average US Household",
              "Annual Government Spending", "Sponsor"), c(1, 2, 3, 7, 8, 9), c(10, 11, 12, 16, 17, 18))
fin(d1, w1, ifelse(w1$Q116 == "", NA, as.integer(w1$Q116 == "Foreign Affairs")), "bergquist_2020_gnd_social.csv")
stopifnot(!any(c(w2$out.m_9, w2$out.n_9, w2$out.o_9) %in% c("Democrats", "Democrats and some Republicans")))
d2 <- stack(w2, c("M", "N", "O"), c("carbon", "legacy", "energy", "invest", "cost", "size", "sponsor"),
            c("carbon_tax", "fossil_fuel_companies", "electricity_generation", "investments", "energy_costs",
              "government_spending", "transportation"),
            c("Carbon Tax", "Fossil Fuel Companies", "Electricity Generation", "Investments",
              "Increased Energy Costs for Average US Household", "Annual Government Spending", "Transportation"), 3:9, 12:18)
fin(d2, w2, ifelse(w2$Q117 == "", NA, as.integer(w2$Q117 == "Trade Policy")), "bergquist_2020_gnd_energy.csv")
