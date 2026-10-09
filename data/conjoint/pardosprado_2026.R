##NHS funding policy-package conjoint (Great Britain, Deltapoll) from
##Pardos-Prado, S., & Xena, C. (2026). Immigration, tax progressivity, and support for
##redistribution. Journal of European Public Policy. https://doi.org/10.1080/13501763.2026.2685818
##Replication data: Pardos-Prado, S. Harvard Dataverse doi:10.7910/DVN/HUCLUE, CC0 1.0, no restricted
##files, no terms. File read: conjoint_dataset_income_long.dta (Dataverse original format; one row per
##respondent x task x option). conjoint_dofile.do read as text, not run. Design and wording from the
##article (Glasgow eprint 387758): "Conjoint experiment" section and Table 3.
##Usage: Rscript pardosprado_2026.R <dir holding the .dta> <output dir>
##
##3,570 British adults (Deltapoll online panel; the article says 3,500 and 56,000 observations; the
##file has 3,570 x 8 tasks x 2 = 57,120 rows). Each respondent saw 8 pairs (task) of hypothetical
##policy packages to fund the NHS (profile 1 = Option A, 2 = Option B, source `option`).
##Attributes (article Table 3): income tax British nationals would pay in five annual-income
##brackets, one attr_ column per bracket (attr_tax_below_14733, attr_tax_14733_25688,
##attr_tax_25689_43662, attr_tax_43663_75500, attr_tax_over_75500; levels "0%" ... "45%"); share of
##annual Government spending going to the NHS (attr_nhs_spending, the .dta value-label text, e.g.
##"15% would be spent on the NHS"); groups entitled to free health care (attr_eligibility, value-label
##text "British nationals only" / "All immigrants to Britain and British nationals").
##RESTRICTION: the tax schedule was drawn as one of the 126 non-decreasing schedules (CJ1 1-126,
##cj1_str): "we never allowed tax burdens to be higher in lower income brackets" (article); all 126
##occur, so bracket rates are NOT independent (higher brackets get high rates more often). The
##authors' AMCEs condition on this design. Exact grid wording of the bracket rows is not deposited;
##the article's Table 3 wording is recorded in the header and design record.
##Outcomes:
##  choice: PC6 "Generally speaking, if you had to choose, which one of these two options would you
##    prefer?" (the .dta label is truncated after "wo"; "would you prefer" follows the article's "asked
##    which one they would prefer") Option A / Option B / Don't know. Don't know (98) is an opt-out:
##    3,805 of 28,560 tasks, choice = 0 on both profiles (the authors set it missing).
##  rating: PC7 (Option A) / PC8 (Option B) "And just thinking of option A [B], how do you feel about
##    it?" 1 I like it a lot, 2 I like it a bit, 3 I don't like it very much, 4 I don't like it at all;
##    stored raw (LOWER = more favourable); Don't know (98) -> NA.
##Covariates (.dta value-label text): cov_gender (QDP1: Male/Female/I identify in another way ->
##male/female/other; Prefer not to answer -> NA), cov_age (QDP2, years), cov_region (QDP3),
##cov_education (QDP4; "Prefer not to answer" -> NA, "Don't know" kept), cov_work_status (QDP5),
##cov_housing (QDP6), cov_vote_intention (QDP8, general election tomorrow), cov_vote_2019 (QDP9b),
##cov_eu_ref_2016 (QDP10b), cov_political_attention (QDP11, 0-10; 99 Don't know -> NA),
##cov_marital_status (QDP12), cov_ethnicity (QDP17), cov_social_grade (SocGrade), cov_income_band (the
##authors' yearly gross personal income band 1-13, harmonised from the weekly/monthly/yearly amount or
##band answers, stored as the text of the yearly band, AS3_year2 labels; 99 -> NA; the article splits
##respondents by it), cov_survey_weight (GBw8, Deltapoll "Political Weight") and
##cov_survey_weight_nonpolitical (NonPolW8). The article's models are unweighted.
##Dropped: Deltapoll respondent ID (re-keyed to 1..N in file order), parliamentary constituency names
##and codes (small-area geography), exact income amounts, party-leader and EU items, children items,
##timing, the authors' derived choice/taxinc_b*/cj1_str columns (used only for checks).
##Spot check: the authors' LPM (choice on all attributes, Don't-know tasks dropped) for low-income
##respondents (income band 1-2, 1,014 here) with British-nationals-only eligibility gives -0.122 for a 15%
##bottom-bracket rate and -0.004 for 45%, as the article reports (12 points; 45% insignificant).
##The deposit also holds a separate YouGov 2x2 vignette experiment (Yougov.dta, one vignette per
##respondent) and a large observational file; neither is built here.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x0 <- read_dta(file.path(raw, "conjoint_dataset_income_long.dta"))
lab <- function(v) as.character(as_factor(x0[[v]], levels = "labels"))
x <- as.data.table(zap_labels(x0))
stopifnot(x[, .N, ID][, all(N == 16)], all(x$option %in% c("A", "B")), x[, uniqueN(PC6), .(ID, task)][, all(V1 == 1)])
rates <- c("0%", "15%", "25%", "35%", "45%")
br <- c("below_14733", "14733_25688", "25689_43662", "43663_75500", "over_75500")
ids <- unique(x$ID)
d <- data.table(id = match(x$ID, ids), task = as.integer(x$task), profile = fifelse(x$option == "A", 1L, 2L))
d[, choice := fifelse(x$PC6 == 98, 0L, as.integer((x$PC6 == 1) == (x$option == "A")))]
r <- fifelse(x$option == "A", x$PC7, x$PC8); d[, rating := fifelse(r == 98, NA_integer_, as.integer(r))]
tx <- tstrsplit(x$cj1_str, " / ", fixed = TRUE)
for (i in 1:5) { d[, paste0("attr_tax_", br[i]) := tx[[i]]]; stopifnot(all(tx[[i]] == rates[x[[paste0("taxinc_b", i)]]])) }
d[, attr_nhs_spending := lab("CJ2")][, attr_eligibility := lab("CJ3")]
stopifnot(all(x$CJ3 %in% 1:2), all(x$CJ2 %in% 1:4), uniqueN(x$cj1_str) == 126, !anyNA(d$rating[x$PC7 != 98 & x$option == "A"]))
nar <- function(v, bad = "Prefer not to answer") { s <- lab(v); s[s %in% bad] <- NA; s }
d[, `:=`(cov_gender = c("male", "female", "other", NA)[x$QDP1], cov_age = as.integer(x$QDP2), cov_region = lab("QDP3"),
         cov_education = nar("QDP4"), cov_work_status = nar("QDP5"), cov_housing = nar("QDP6"), cov_vote_intention = nar("QDP8"),
         cov_vote_2019 = nar("QDP9b"), cov_eu_ref_2016 = nar("QDP10b"),
         cov_political_attention = fifelse(x$QDP11 > 10, NA_integer_, as.integer(x$QDP11)),
         cov_marital_status = nar("QDP12"), cov_ethnicity = nar("QDP17"), cov_social_grade = lab("SocGrade"))]
yb <- attr(x0$AS3_year2, "labels"); stopifnot(all(x$income_band %in% c(1:13, 99)))
d[, cov_income_band := names(yb)[match(x$income_band, yb)]][x$income_band == 99, cov_income_band := NA]
d[, `:=`(cov_survey_weight = x$GBw8, cov_survey_weight_nonpolitical = x$NonPolW8)]
stopifnot(all(x$QDP1 %in% 1:4), all(d$cov_age %in% 18:99), d[, sum(choice), .(id, task)][, all(V1 <= 1)],
          d[, sum(choice), .(id, task)][, sum(V1 == 0)] == 3805)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pardosprado_2026_nhs_tax.csv"))
