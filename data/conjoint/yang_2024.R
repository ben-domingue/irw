##Charity-regulation conjoint (China, online, Experiment 2 of the OSF project) from
##Yang, Y., & Wang, H. (2024). Government regulation preferences for charities' information
##disclosure [Data set]. OSF. https://osf.io/2r7n4/ (no article found; the OSF project has no
##linked publication).
##Replication data: OSF project 2r7n4, CC BY 4.0 (node licence "CC-By Attribution 4.0
##International"). Files read: "data for analysis.dta" (one row per respondent x task x
##profile, Stata value labels on the attribute codes) and "conjoint experiment questionaire
##(English translation).docx" (the English translation of the instrument: attribute text and
##questions). Read as text only: "dofile for replication.do".
##Usage: Rscript yang_2024.R <dir holding the .dta> <output dir>
##
##981 respondents x 4 tasks x 2 charities (Charity A / B), 7 attributes. The deposit holds only
##the questionnaire's Experiment 2 (charity regulation); Experiment 1 (donation / volunteering
##for charities with different attributes) is in the questionnaire but not in the data.
##task = tens digit of profile_order, profile = `order` (= units digit, 1 = Charity A). The task
##number coincides with the charity field named in the task's introduction ("Here is a
##description of two charities that focus on poverty alleviation and relief / education /
##environmental reservation / culture and arts"): task 1 poverty, 2 education, 3 environment,
##4 arts in every respondent, kept as trial_field. Whether tasks were shown in this order is
##not documented.
##Outcomes (questionnaire, English translation; respondents saw Chinese):
##  choice = Choice: "Of the two charities above, which do you expect the government to adopt
##           the flexible regulation instead of rigid regulation?" (1) Charity A (2) Charity B;
##           forced, exactly one per task (checked).
##  rating = Rating: "To what extent do you support the government to adopt the flexible
##           regulation for Charity A [B]?" 1-7, "the higher value, the higher levels of
##           support"; as stored.
##  The questions follow definitions of flexible regulation (published transparency indices and
##  rankings, priority in government purchasing) and rigid regulation (mandatory disclosure
##  with penalties).
##Attributes: codes mapped to the questionnaire's level text via the .dta value labels (same
##order): attr_public_fundraising (public: 1 "public fundraising", 0 "non-public fundraising"),
##attr_gongo (GONGO: 1 "government-organized charity", 0 "civil-organized charity"),
##attr_transparency (disclose 1-3), attr_collaboration (partner 1-4), attr_reputation (1-3),
##attr_industry_selfregulation (industry 1-3), attr_third_party_regulation (third 1-3).
##Attribute order: questionnaire lists a fixed order; randomization rules, level probabilities
##and attribute-order randomization are not documented.
##Covariates (as stored; the .dta holds recodes of the questionnaire answers): cov_gender_code
##(gender 0/1: the questionnaire codes 1 Male / 2 Female and the recode is not documented),
##cov_age (age in years; the questionnaire asks year of birth, so computed by the authors),
##cov_age_quota (QtaAge value-label text), cov_area (QtaArea value-label text), cov_province
##(pro, Q9_1), cov_edu (edu, as stored: years of schooling, recoded by the authors),
##cov_marriage, cov_ccp_member, cov_hukou_urban (value labels 0/1 as stored), cov_familiar
##(familiar, 1-10), cov_familiar_charity, cov_trust_charity, cov_trust (generalized trust 1-10).
##Dropped: the authors' dummies (field1-4, public1-2, ..., third1-3), religion recodes, other
##attitude items. No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "data for analysis.dta"))
z <- function(v) as.integer(zap_labels(v))
lv <- list(
  public = c(`0` = "non-public fundraising", `1` = "public fundraising"),
  GONGO = c(`0` = "civil-organized charity", `1` = "government-organized charity"),
  disclose = c("no information disclosure", "disclose information to some extent, with a lot of issues",
               "comprehensive, timely, and accurate information disclosure"),
  partner = c("No collaboration", "Good collaboration with governments", "Good collaboration with firms",
              "Good collaboration with other charities"),
  reputation = c("poor reputation", "average reputation", "good reputation"),
  industry = c("no industry self-regulation", "industry self-regulation with bad effect", "industry self-regulation with good effect"),
  third = c("no third-party regulation", "transparency indices and rankings for charities released by third parties with limited influence",
            "transparency indices and rankings for charities released by third parties with great influence"))
# value labels must match the questionnaire order used above
vl <- function(v) names(sort(attr(x[[v]], "labels")))
stopifnot(identical(vl("disclose"), c("no", "somewhat", "good")), identical(vl("partner"), c("no", "with government", "with firms", "with other charities")),
          identical(vl("reputation"), c("poor", "average", "good")), identical(vl("industry"), c("no", "issued but poor", "issued and good")),
          identical(vl("third"), c("no", "little influence", "great influence")),
          identical(vl("public"), c("non public fundraising", "public fundraising")), identical(vl("GONGO"), c("civil-organized charity", "government-organized charity")))
fieldtxt <- c("poverty alleviation and relief", "education", "environmental reservation", "culture and arts")
d <- data.table(id = z(x$ID), task = z(x$profile_order) %/% 10L, profile = z(x$order), choice = z(x$Choice), rating = z(x$Rating),
                attr_public_fundraising = unname(lv$public[as.character(z(x$public))]),
                attr_gongo = unname(lv$GONGO[as.character(z(x$GONGO))]),
                attr_transparency = lv$disclose[z(x$disclose)], attr_collaboration = lv$partner[z(x$partner)],
                attr_reputation = lv$reputation[z(x$reputation)], attr_industry_selfregulation = lv$industry[z(x$industry)],
                attr_third_party_regulation = lv$third[z(x$third)], trial_field = fieldtxt[z(x$field)],
                cov_gender_code = z(x$gender), cov_age = z(x$age),
                cov_age_quota = as.character(as_factor(x$QtaAge, levels = "labels")), cov_area = as.character(as_factor(x$QtaArea, levels = "labels")),
                cov_province = x$pro, cov_edu = z(x$edu), cov_marriage = z(x$marriage), cov_ccp_member = z(x$party),
                cov_hukou_urban = z(x$hukou), cov_familiar = z(x$familiar), cov_familiar_charity = z(x$familiar_charity),
                cov_trust_charity = z(x$trust_charity), cov_trust = z(x$trust))
stopifnot(all(z(x$profile_order) %% 10L == d$profile), all(d$task == z(x$field)), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7), d[, .N, id][, all(N == 8)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "yang_2024_charity_regulation.csv"))
