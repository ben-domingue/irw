##Two factorial vignette surveys on German support for COVID-19 aid, from
##Heermann, M., Koos, S., & Leuffen, D. (2022). Who deserves European solidarity? How recipient
##characteristics shape public support for international medical and financial aid during COVID-19.
##British Journal of Political Science. https://doi.org/10.1017/S0007123422000357
##Replication data: Harvard Dataverse doi:10.7910/DVN/RCO69B, CC0 1.0, no restricted files, no terms.
##Files read: surveyI.tab (Survey I, April/May 2020), surveyII.tab (Survey II, May 2021), BJPS_replication.R
##(text, variable meanings and the authors' figure labels). surveyIII.tab (an appendix-L experiment of
##Nov 2020, n = 3,341, two rows per respondent) is NOT used: its dummy directions are undocumented.
##Level text: from the paper's Online Appendix A (vignette wording, translated from German;
##https://static.cambridge.org/.../S0007123422000357sup001.docx) and the appendix-L table of levels.
##Appendix A prints ONE variant of each vignette and the deposit stores 0/1 dummies, so:
##  * the printed variant is used as the text of the level whose dummy is 1 (checked: Survey I dummy-1 =
##    raw code 1 for health/fiscal and risk/tax; Survey II dummy-1 levels are the favourable ones in the
##    authors' figure and in the sign of the effects, except need: see below);
##  * the opposite level is the PARAPHRASE of the other pole given in the appendix-L table
##    (Nov 2020) or the authors' figure labels. Marked "(paraphrase)" in this header only; the stored text
##    is the short displayed-style phrase. Direction of the dummies is not stated in the codebook;
##    EU_need_recode_* = 1 is read as RICH (authors' figure label "Need: Wealth"; lower support, -0.17/-0.21).
##    Attribute level text taken from the article appendix (Appendix A and L); the deposit stores 0/1 codes.
##Usage: Rscript heermann_2022.R <raw dir> <output dir>   (raw dir holds surveyI.tab, surveyII.tab)
##
##Both surveys: Respondi online panel, Germany, quotas on age, gender, education, region (East oversampled;
##weights gewichtRESPONDI kept as cov_survey_weight). Each respondent read TWO vignettes, a medical-aid and a
##financial-aid one; each is a separate task (task 1 = medical aid VMA, task 2 = financial aid VFA; the
##numbering is by vignette, not the order shown: Survey I has no order variable, Survey II has Order 0/1 whose
##meaning is not documented, kept as trial_order_code; task_source = unknown). One profile per task.
##No opt-out. Outcome rating: 7-point support ("not support at all" 1 ... "strongly support" 7).
##
##TABLE heermann_2022_covid_aid_2020 (Survey I, 4,775 respondents; paper analysis n = 4,775 of 4,799):
##  12 cells (vigA_rand / vigB_rand 1-12 = 3 x 2 x 2), independent for the two vignettes.
##  attr_community: German state ("another German state") / EU country / non-EU country  (raw 1/2/3; the dummies
##                  vigAregion/vigAEU/vigAnonEU confirm 1 = German region, 2 = EU, 3 = non-EU)
##  attr_control: medical: "well-developed healthcare system" (dummy 1) / "healthcare system not well developed";
##                financial: "built up financial reserves" / "limited financial reserves because of overly generous
##                spending policies" (the printed template is the latter). Authors' label "Control: public health
##                system" / "Control: fiscal discipline".
##  attr_costs:   medical: "medical disadvantages for you and your region cannot be entirely ruled out" /
##                "medical disadvantages unlikely"; financial: "temporarily higher tax rates" / "no tax increase".
##  Outcome rating = solidhlth (vigA_v1, medical) / solidecon (vigB_v1, financial); verified identical to
##  the authors' variables. "Would you support such an initiative?" (translated). vigA_v2/vigB_v2 (a second
##  7-point item, wording not in the deposit) are dropped.
##TABLE heermann_2022_covid_aid_2021 (Survey II, 4,016 respondents; paper n = 4,016 of 4,027):
##  32 cells (2^5; Vig1Cntryrand / Vig2Cntryrand), VFA = Vig1, VMA = Vig2 (authors' code: Vig1Help = financial).
##  attr_wealth ("poorer EU member state" / "richer EU member state"), attr_covid_policy ("government rapidly
##  implemented measures to contain the virus" / "slow implementation of pandemic measures"), attr_efficiency
##  (medical "public health system efficient" / "inefficient"; financial "public administration efficient" /
##  "inefficient"), attr_rule_of_law ("diligent in the implementation of the rule of law and democratic
##  principles" / "regular allegations of violations of democratic principles and the rule of law"),
##  attr_refugees ("strongly participated in the accommodation of refugees" / "hardly participates in the
##  accommodation of refugees").
##  Outcome: Vig2Help_SQ001 (medical) / Vig1Help_SQ001 (financial): "Would you support it, if the EU offers
##  medical (financial) aid to this country?" (translated).
##Covariates: cov_survey_weight, cov_gender (female 0/1 from the authors' dummy), cov_age_group, cov_education
##  (deposit categories low/middle/high), cov_income (text bands), cov_east (ost 0/1), cov_left_right (0-10),
##  cov_eu_identity (1-4), cov_altruism (1-7), cov_cosmopolitanism (as recorded). Respondent id = row order.
##Dropped: the authors' vignette dummies, binary splits, cell ids (kept as trial_cell).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cov <- function(d) data.table(cov_survey_weight = d[[grep("^gewicht", names(d), ignore.case = TRUE, value = TRUE)]],
  cov_gender = ifelse(d$female == 1, "female", "male"), cov_age_group = d$age, cov_education = d$edu,
  cov_income = ifelse(d$income == "", NA, d$income), cov_east = d$ost, cov_left_right = d$leftright,
  cov_eu_identity = d$EU_identity, cov_altruism = d$altruism, cov_cosmopolitanism = d$cosmopolitanism)
s1 <- fread(file.path(raw, "surveyI.tab")); stopifnot(!anyDuplicated(s1$id)); s1[, rid := .I]
stopifnot(all(s1$vigA_v1 == s1$solidhlth), all(s1$vigB_v1 == s1$solidecon))
comm <- c("another German state", "another EU country", "another country outside the EU")
mk1 <- function(task, pre, rat, vig, ctrl, cost) {
  data.table(id = s1$rid, task = task, profile = 1L, rating = s1[[rat]],
    attr_community = comm[s1[[paste0(pre, "_region")]]],
    attr_control = ctrl[s1[[paste0(pre, "_gesund")]]], attr_costs = cost[s1[[paste0(pre, "_nacht")]]],
    trial_vignette = vig, trial_cell = s1[[paste0(pre, "_rand")]])
}
x1 <- rbind(
 mk1(1L, "vigA", "solidhlth", "medical aid", c("well-developed healthcare system", "healthcare system not well developed"),
     c("medical disadvantages for you and your region cannot be entirely ruled out", "medical disadvantages unlikely")),
 mk1(2L, "vigB", "solidecon", "financial aid", c("built up financial reserves", "limited financial reserves because of overly generous spending policies"),
     c("temporarily higher tax rates", "no tax increase")))
# dummy 1 = raw code 1 for the control and cost attributes (checked); the printed template text is dummy 1 for health, 2 for fiscal
cv1 <- cbind(id = s1$rid, cov(s1)); x1 <- merge(x1, cv1, by = "id")
setorder(x1, id, task, profile)
stopifnot(!anyNA(x1$attr_community), !anyNA(x1$rating)); fwrite(x1, file.path(out, "heermann_2022_covid_aid_2020.csv"))

s2 <- fread(file.path(raw, "surveyII.tab")); stopifnot(!anyDuplicated(s2$id)); s2[, rid := .I]
tx <- function(d, sfx, eff) data.table(
  attr_wealth = ifelse(d[[paste0("EU_need_recode_", sfx)]] == 1, "richer EU member state", "poorer EU member state"),
  attr_covid_policy = ifelse(d[[paste0("EU_control_", sfx)]] == 1, "government rapidly implemented measures to contain the virus", "slow implementation of pandemic measures"),
  attr_efficiency = ifelse(d[[paste0("init_efficiency_", sfx)]] == 1, paste(eff, "considered efficient"), paste(eff, "considered inefficient")),
  attr_rule_of_law = ifelse(d[[paste0("EU_democ_", sfx)]] == 1, "diligent in the implementation of the rule of law and of democratic principles", "regular allegations of violations of democratic principles and the rule of law"),
  attr_refugees = ifelse(d[[paste0("EU_refugee_", sfx)]] == 1, "strongly participated in the accommodation of refugees", "hardly participates in the accommodation of refugees"))
m2 <- cbind(data.table(id = s2$rid, task = 1L, profile = 1L, rating = s2$Vig2Help_SQ001), tx(s2, "m", "public health system"),
            data.table(trial_vignette = "medical aid", trial_cell = s2$Vig2Cntryrand, trial_order_code = s2$Order))
f2 <- cbind(data.table(id = s2$rid, task = 2L, profile = 1L, rating = s2$Vig1Help_SQ001), tx(s2, "f", "public administration"),
            data.table(trial_vignette = "financial aid", trial_cell = s2$Vig1Cntryrand, trial_order_code = s2$Order))
x2 <- merge(rbind(m2, f2), cbind(id = s2$rid, cov(s2)), by = "id"); setorder(x2, id, task, profile)
stopifnot(!anyNA(x2$rating)); fwrite(x2, file.path(out, "heermann_2022_covid_aid_2021.csv"))
cat(nrow(x1), uniqueN(x1$id), nrow(x2), uniqueN(x2$id), "\n")
