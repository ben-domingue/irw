##Coal phase-out policy choice experiment (Germany, Rhineland, Lusatia) from
##Rinscheid, A., & Wüstenhagen, R. (2019). Germany's decision to phase out coal by 2038 lags
##behind citizens' timing preferences. Nature Energy, 4(10), 856-863.
##https://doi.org/10.1038/s41560-019-0460-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/TEFCBL, CC0 1.0, no restricted files.
##Files read: coalphaseout.csv (";"-separated, decimal comma); codebook.xlsx (variable labels
##only, German question text); read as text: code_coalphaseout.do, "code Figures.R".
##Level text: the article's Table 1 (English; respondents saw a German questionnaire that is not
##deposited), matched to the codes 1..k by the order of the labels in "code Figures.R"
##(GetLabels) and the .do file (attime baseline ib3 = 2040; atcost 1=0 2=250 3=500 4=750).
##Usage: Rscript rinscheid_2019.R <raw dir> <output dir>
##
##Three tables, one per sample (hidsample, .do: 1 = Germany, 2 = Rhineland, 3 = Lusatia). The
##attribute text is shared, but the authors analysed the samples separately (Germany = main
##results, Rhineland and Lusatia = Fig. 4 / Tables S4-S6) and the regional samples are separate
##populations, so they are not pooled:
##  rinscheid_2019_coal_phaseout_germany   2,161 respondents (paper: 2,161; 1,984 after attention check)
##  rinscheid_2019_coal_phaseout_rhineland   533 (paper: 533; 491)
##  rinscheid_2019_coal_phaseout_lusatia     501 (paper: 501; 473)
##Each respondent saw 8 pairs of phase-out scenarios (Index1 1-16: pair = task (Index1+1)%/%2,
##profile = 1 for odd Index1, 2 for even; exactly one profile selected per pair, checked).
##Attributes (Table 1): end date (By 2025 / 2030 / 2040 / 2100), annual costs, lost jobs in the
##coal industry, newly created jobs, measures for structural change.
##COST FRAMING: half the respondents (Conjoint_type) saw the household cost only ("€6"), the
##other half also the economy-wide cost ("€6 (€250 million)"; Table 1, Methods). The deposit
##does not say which code is which (the .do calls the economy-wide framing "the 2nd mode", which
##suggests Conjoint_type 2, not confirmed). attr_annual_cost therefore holds the household amount,
##which everyone saw; the economy-wide amount is a fixed function of it (0/250/500/750 million);
##trial_conjoint_type keeps the source code 1/2.
##Fixed blocked design: 500 design versions (Q1_Version = trial_design_version); restrictions not
##documented. Attribute order randomized per respondent, fixed across tasks (Methods); not recorded.
##Outcomes (exact wording not deposited; Methods paraphrase):
##  choice = which of the two scenarios the respondent preferred; forced choice, no opt-out.
##  rating = rating of each scenario, 1-7, 1 = very poor, 7 = very good (rating_raw; the paper
##           dichotomizes at > 4).
##Attention check D0 ("bitte wählen Sie das Wort 'Energie'", 5 = correct) -> cov_attention_pass;
##the paper excludes failures; all are kept here.
##Covariates (codes as in the source unless stated): cov_birth_year (X1r1), cov_age (Hidager1,
##years, as recorded), cov_age_group_code (hidX1, no labels), cov_gender_code (X2, "Ihr
##Geschlecht", no value labels in the deposit), cov_d4_consensus (D4, % of climate scientists,
##slider), cov_d5_works_coal / cov_d6_knows_coal (1 = yes, 2 = no, per the .do's use), cov_d7_leans
##(D7), cov_party_id (D8a, text from the .do comment: 1 SPD, 2 CDU, 3 CSU, 4 FDP, 5 Bündnis
##90/Die Grünen, 6 Die Linke, 7 AFD, 8 Eine andere Partei; NA when D7 = 2, not asked),
##cov_d8b_strength, cov_income_code (D9), cov_education_code (D12, no labels), cov_q1_timer_min
##(Q1_Timer, DCM timer in minutes, as recorded).
##DROPPED: postcode (D10r1), place of residence (D11r1) and the free-text "other" answers
##(D8ar8oe, D12r10oe): location/free text; X3 (eligible to vote; constant 1); noanswerD10_r2;
##record re-keyed to integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "coalphaseout.csv"), sep = ";", dec = ",", encoding = "Latin-1")
stopifnot(s[, .N, record][, all(N == 16)], all(s$Index1 %in% 1:16))
lv <- list(
  end_date = c("By 2025", "By 2030", "By 2040", "By 2100"),
  annual_cost = c("€0", "€6", "€12", "€18"),
  lost_jobs = c("-5,000", "-10,000", "-15,000", "-20,000"),
  new_jobs = c("5,000", "10,000", "15,000", "20,000"),
  structural_measures = c("Investment in expansion of renewable energies",
    "Investment in regional funding programs for new businesses (e.g. start-up funding)",
    "Investment in modern infrastructure (electric vehicles, digitalization)",
    "Investment in research and development",
    "Mixture of further training and early retirement of coal industry employees"))
src <- c(end_date = "Attr.1_recode", lost_jobs = "Attr.2_recode", structural_measures = "Attr.3_recode",
         new_jobs = "Attr.4_recode", annual_cost = "Attr.5_recode")   # .do renames
ids <- unique(s$record)
d <- data.table(id = match(s$record, ids), task = (s$Index1 + 1L) %/% 2L, profile = 2L - s$Index1 %% 2L,
                choice = as.integer(s$selected), rating = as.integer(s$rating_raw),
                trial_conjoint_type = s$Conjoint_type, trial_design_version = s$Q1_Version)
for (k in names(lv)) { x <- s[[src[[k]]]]; stopifnot(all(x %in% seq_along(lv[[k]]))); d[, paste0("attr_", k) := lv[[k]][x]] }
party <- c("SPD", "CDU", "CSU", "FDP", "Bündnis 90/Die Grünen", "Die Linke", "AFD", "Eine andere Partei")
stopifnot(all(s$D8a %in% c(NA, 1:8)))
d[, `:=`(cov_sample = c("Germany", "Rhineland", "Lusatia")[s$hidsample],
         cov_attention_pass = as.integer(s$D0 == 5), cov_birth_year = s$X1r1, cov_age = s$Hidager1,
         cov_age_group_code = s$hidX1, cov_gender_code = s$X2, cov_d4_consensus = s$D4,
         cov_d5_works_coal = s$D5, cov_d6_knows_coal = s$D6, cov_d7_leans = s$D7,
         cov_party_id = party[s$D8a], cov_d8b_strength = s$D8b, cov_income_code = s$D9,
         cov_education_code = s$D12, cov_q1_timer_min = s$Q1_Timer)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
for (k in 1:3) {
  x <- d[cov_sample == c("Germany", "Rhineland", "Lusatia")[k]][, cov_sample := NULL]
  x[, id := match(id, unique(id))]
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("rinscheid_2019_coal_phaseout_", c("germany", "rhineland", "lusatia")[k], ".csv")))
}
