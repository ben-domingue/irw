##Economic-sanctions news-story vignette experiment (US MTurk, 2019) from
##Caton, C., & Webb, C. (2025). A public demand theory of economic sanctions. International
##Interactions, 51(3), 396-424. https://doi.org/10.1080/03050629.2025.2489368
##Replication data: Harvard Dataverse doi:10.7910/DVN/QDXWFS, CC0 1.0, no restricted files, no terms.
##Files read: DPDSspbb.tab (saved as data.tab; 858 rows, Qualtrics export with recodes) and Survey.docx (the
##full survey text, extracted with unzip; the vignette texts, question wording and answer options below
##come from it). The authors' R script and README were read as text only.
##Usage: Rscript caton_2025.R <raw dir> <output dir>   (raw dir holds data.tab)
##
##858 US adults recruited on Amazon Mechanical Turk (July 2019, University of Kansas). Each read ONE
##hypothetical news story about a conflict and the US President imposing sanctions: a 2 x 2 x 2 factorial,
##one vignette per respondent, between-subject (8 cells of 102-111; `condition` names the cell):
##  attr_countries  conflict between Spain and Portugal (Spain acts) / Brazil and Bolivia (Brazil acts)
##  attr_dispute    "a 25 % tariff on all goods imported from <neighbour>" / "troops moved into <neighbour>'s
##                  territory (a river declared sovereign territory)"
##  attr_sanction_cost  "Experts are worried that the sanctions will impose significant costs on United States
##                  businesses" (headline, lede and a paragraph on firms pulling back, recession risk and a quoted
##                  analyst) / (not shown): the no-cost stories omit that clause and paragraph
##The levels are short descriptions of the story elements; the full stories are in Survey.docx (country-specific
##details such as leaders' names, the Guadiana/Mamore river and the treaties come with the country pair and the
##dispute and are not separate attributes).
##Outcomes asked after the story (task 1, profile 1):
##  choice (opt_out yes, single-profile accept/reject)  sanctionyn "Do you think the decision to impose sanctions
##        was the right one?" Yes = 1, No = 0
##  choice_lift_sanctions (opt_out yes)  concedeyn "If the sanctions start imposing significant costs on the U.S.
##        economy and <country> hasn't lifted tariffs [removed troops], do you think the President should lift the
##        sanctions?" Yes = 1, No = 0 (the territory stories' wording in the survey is garbled, "hasn't troops")
##  rating_handling  "How would you rate the President's handling of the conflict between <A> and <B>?" 0 Very Poor
##        .. 10 Excellent
##  rating_approval  "How would you rate your approval of the President's job performance?" 0 Very Poor .. 10 Excellent
##  rating_competence  "How would you rate the President's competence?" 0 Very Poor .. 10 Excellent
##  rating_concern_cost_us  "How concerned are you about the costs of the economic sanctions to the US?" 0 Not
##        Concerned .. 10 Very Concerned
##  rating_concern_cost_you  "... to you?" same scale
##  rating_national_interest  "How important do you think the conflict between <A> and <B> is to U.S. national
##        interests?" 0 Not Important .. 10 Very Important
##Dropped: IP address, latitude, longitude (PII FOUND: ip, latitude, longitude in DPDSspbb.tab), Qualtrics
##ResponseId, timestamps, click/timing paging variables, the two open-ended items (mie, advice), the
##manipulation-check answers and the authors' derived dummies/scales. Respondent id = row number.
##Covariates: cov_gender (sex Male/Female/Other), cov_age_group (age bands as worded), cov_education (as worded),
##cov_party_id (partisana: Democrat/Republican/Independent/Something Else), cov_income (bands as worded),
##cov_race, cov_region, cov_duration_sec (Qualtrics survey duration, seconds).
##Count check: 858 respondents x 1 task x 1 profile. The paper's sample size was not checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.tab"), colClasses = "character", na.strings = c("", "NA"))
stopifnot(nrow(x) == 858, !anyDuplicated(x$responseid))
chk <- function(v, lv) { y <- x[[v]]; stopifnot(all(is.na(y) | y %in% lv)); y }
lastnum <- function(t) as.integer(sub("^.*?(\\d+)$", "\\1", gsub("\\\\n|\\n", "", t), perl = TRUE))
sc <- function(v, vn) { n <- lastnum(x[[v]]); stopifnot(all(n == as.integer(as.numeric(x[[vn]]))), all(n %in% 0:10)); n }
yn <- function(v) { y <- chk(v, c("Yes", "No")); as.integer(y == "Yes") }
cond <- x$condition
cell <- c("sp-trade-c", "sp-territory-c", "bb-trade-c", "bb-territory-c", "sp-trade-nc", "sp-territory-nc", "bb-trade-nc", "bb-territory-nc")
stopifnot(all(cond %in% cell))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L,
  choice = yn("sanctionyn"), choice_lift_sanctions = yn("concedeyn"),
  rating_handling = sc("handling", "handlingn"), rating_approval = sc("approval", "approvaln"),
  rating_competence = sc("competence", "competencen"), rating_concern_cost_us = sc("concerncostus", "concerncostusn"),
  rating_concern_cost_you = sc("concerncostyou", "concerncostyoun"),
  rating_national_interest = sc("nationalinterest", "nationalinterestn"),
  attr_countries = ifelse(grepl("^sp", cond), "Spain and Portugal", "Brazil and Bolivia"),
  attr_dispute = ifelse(grepl("trade", cond), "a 25 % tariff on all goods imported from the neighbouring country",
                        "troops moved into the neighbouring country's territory"),
  attr_sanction_cost = ifelse(grepl("-c$", cond), "Experts worried that the sanctions will impose significant costs on United States businesses", "(not shown)"))
stopifnot(identical(as.integer(x$cost), as.integer(grepl("-c$", cond))), identical(as.integer(x$territory), as.integer(grepl("territory", cond))))
sx <- chk("sex", c("Male", "Female", "Other"))
cv <- data.table(id = d$id, cov_gender = c(Male = "male", Female = "female", Other = "other")[sx],
  cov_age_group = chk("age", c("18 to 25 years", "26 to 35 years", "36 to 55 years", "56 to 75 years", "Over 75 years")),
  cov_education = x$education, cov_party_id = chk("partisana", c("Democrat", "Republican", "Independent", "Something Else")),
  cov_income = x$income, cov_race = x$race, cov_region = x$region, cov_duration_sec = as.integer(as.numeric(x$duration)))
stopifnot(d[, all(!is.na(choice))])
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "caton_2025_sanction_vignettes.csv"))
