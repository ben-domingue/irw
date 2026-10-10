##Renewable portfolio standard (RPS) bill factorial vignette from
##Stokes, L. C., & Warshaw, C. (2017). Renewable energy policy design and framing influence public
##support in the United States. Nature Energy, 2(8), 17107. https://doi.org/10.1038/nenergy.2017.107
##Replication data: Harvard Dataverse doi:10.7910/DVN/DL4JY8, CC0 1.0, no restricted files.
##Files read: rps_experiment.tab (original-format download = R save file holding data.frame
##`master`, saved as rps_experiment.orig), variables.tab (original csv, the authors' figure labels),
##readme.txt; Experiment.R read as text, not run. Design and wording: the authors' accepted
##manuscript (MIT DSpace hdl 1721.1/158530), Methods "Survey Experiment Design".
##Usage: Rscript stokes_2017.R <raw dir> <output dir>
##
##SSI online sample of US adults, August 2016 (paper: "2,500"; deposit 2,564 rows, 2,521 with an
##answer). One task, one profile: respondents read "Over the past decade, many state legislatures
##passed renewable energy laws. ... imagine legislators may consider a new bill that would require
##[respondent's state] to meet 35% of its electricity needs with renewable energy sources by the
##year 2025. Where available, here are a couple details about the bill in [respondent's state]."
##followed by up to five randomized statements (between-subjects; each factor has a control in
##which no statement was shown, stored as "(not shown)"):
##  attr_cost (Randomization2b)      0 control, 1 "Increase costs $2 per month", 2 "Increase costs $10 per month"
##  attr_jobs (Randomization3b)      0 control, 1 "No increase in jobs", 2 "Large increase in jobs"
##  attr_air_pollution (4b)          0 control, 1 "Would reduce harmful air pollution, including mercury"
##  attr_climate (Randomization5b)   0 control, 1 "Anti-climate change argument", 2 "Pro-climate change
##                                   argument", 3 "Balanced argument" (both statements shown)
##  attr_legislator_support (1b)     0 control, 1 "Most Democrats support", 2 "Most Republicans support"
##LEVEL TEXT is the authors' short labels (variables.tab, Figure 2), not the sentences displayed; the
##Methods paraphrase the sentences: cost "the bill would likely add $10 [$2] per month to each
##resident's electricity bill"; jobs "experts predict the bill would probably create several thousand
##jobs in their state" / "probably would not create many jobs"; air "supporters of the bill argued
##the bill would reduce harmful air pollution in their state, including toxins like mercury";
##climate "the bill's supporters argue that climate change is a serious problem, and the bill would
##reduce greenhouse gas emissions that cause climate change" / "the bill's opponents argue that
##climate change is not a serious problem, and for this reason increasing renewable energy is not
##important" / both; partisan "most Democrats [Republicans] in the state legislature support these
##renewable energy requirements". Code-to-label mapping: the authors' Experiment.R places
##coef(factor(Randomization_k)j) on the j-th listed level of variables.tab; checked against the
##paper's text (cost -0.18/-0.36, no jobs -0.10, many jobs +0.12, air +0.13: all reproduce from
##this table). The climate code order (1 anti, 2 pro, 3 balanced) rests on that mapping alone
##(all three effects are null in the paper). Statement order on screen is not documented.
##Outcome: rating = billsup, support for the bill on a 4-point scale "from strongly support to
##strongly oppose" (Methods; exact question text not deposited); stored 1-4 as in the source,
##4 = strongly support (the authors' billsup_binary codes 3-4 as support, and cost raises lower it).
##43 respondents with no answer are omitted.
##Covariates (source text): cov_gender (female/male), cov_age (years), cov_education (educ text),
##cov_party_id (pid3a: Democrat / Independent / Other Party / Republican), cov_income (income text;
##"Prefer not to say" -> NA), cov_state, cov_ideo7_code (ideo7, -3..3, labels and direction not
##deposited), cov_race (the authors' 4-category recode white/black/hispanic/other; the raw race
##checkboxes are only partly deposited and are dropped). Dropped as derived: billsup_binary,
##pid3_leaners, age2, income2, race_1/race_3/race_4. The paper's raking weight is computed in
##Experiment.R from census targets, not deposited (not kept).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "rps_experiment.orig"), envir = e); m <- as.data.table(e$master)
stopifnot(nrow(m) == 2564L)
m[, id := .I]
lab <- function(x, levs) { stopifnot(!anyNA(x), x %in% (seq_along(levs) - 1L)); levs[x + 1L] }
d <- m[!is.na(billsup), .(id, task = 1L, profile = 1L, rating = as.integer(billsup),
  attr_cost = lab(Randomization2b, c("(not shown)", "Increase costs $2 per month", "Increase costs $10 per month")),
  attr_jobs = lab(Randomization3b, c("(not shown)", "No increase in jobs", "Large increase in jobs")),
  attr_air_pollution = lab(Randomization4b, c("(not shown)", "Would reduce harmful air pollution, including mercury")),
  attr_climate = lab(Randomization5b, c("(not shown)", "Anti-climate change argument", "Pro-climate change argument", "Balanced argument")),
  attr_legislator_support = lab(Randomization1b, c("(not shown)", "Most Democrats support", "Most Republicans support")),
  cov_gender = gender, cov_age = as.integer(age), cov_education = educ, cov_party_id = pid3a,
  cov_income = ifelse(income == "Prefer not to say", NA_character_, income), cov_state = state,
  cov_ideo7_code = as.integer(ideo7), cov_race = race)]
stopifnot(nrow(d) == 2521L, d$rating %in% 1:4, d$cov_gender %in% c("female", "male", NA))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "stokes_2017_rps_support.csv"))
