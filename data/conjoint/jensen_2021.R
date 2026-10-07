##Local economic development plan conjoint (eight US metro areas) from
##Jensen, A., Marble, W., Scheve, K., & Slaughter, M. J. (2021). City limits to partisan
##polarization in the American public. Political Science Research and Methods, 9(2),
##223-241. https://doi.org/10.1017/psrm.2020.56
##Replication data: Harvard Dataverse doi:10.7910/DVN/JYKRGY, CC0 1.0, no restricted files.
##File read: STAN0107_OUTPUT_8msas.dta (Dataverse "original format" download of the .tab;
##the raw YouGov file, with value labels). Wording and design from the deposited
##questionnaire "Eight City Survey Questionnaire January__10_2018_YouGov_pub.pdf"; the
##long-format construction follows the authors' conjoint_analysis.do (read as text only).
##Usage: Rscript jensen_2021.R <raw dir> <output dir>
##
##7,800 YouGov respondents (January 2018), 1,000 in each of Charlotte, Cleveland, Houston,
##Indianapolis, Memphis, St. Louis and Seattle metro areas and 800 in Rochester. Q16: "We will
##provide you with several possible development plans to help <city> adapt to technology and
##globalization. ... We will always show you two possible proposals in comparison. For each
##comparison, please indicate which of the two plans you prefer. ... You may like both or not
##like either one. In any case, choose the one you prefer the most. In total, we will show you
##five comparisons." 5 tasks (q16a-q16e) x 2 plans (Development Plan 1 = profile 1, Plan 2 =
##profile 2). choice = the plan preferred (q16_a-q16_e); forced choice, no opt-out.
##6 attributes, fully randomized (questionnaire: "FULL RANDOMIZATION OF ATTRIBUTES"): education,
##higher education, investment and taxes, governance, workers and entrepreneurs, local
##services. Row order of the dimensions was random across respondents but fixed within
##respondent; that order is not in the data, so no attrpos_ columns.
##Attribute text is the label stored in the .dta. Three levels carry the placeholders
##$msaname / $statename, which the survey filled with the respondent's metro area and its
##state (questionnaire); they are filled in here (Charlotte/North Carolina, Cleveland/Ohio,
##Houston/Texas, Indianapolis/Indiana, Memphis/Tennessee, Rochester/New York, St. Louis/
##Missouri, Seattle/Washington), so the text is as displayed.
##ONE TABLE pooling the eight cities with cov_city: the authors pool them (pooled AMCE table
##A-5, hierarchical model) and the attribute set is the same everywhere.
##Covariates: cov_city (metro area text); cov_survey_weight (YouGov weight, used in the
##paper); cov_birth_year; cov_gender 1=Male 2=Female 3=Other; cov_race (q58) 1=White 2=Black
##or African American 3=Hispanic or Latino 4=Asian or Asian-American 5=Native American
##6=Mixed race 7=Other; cov_education (q51) 1=No schooling .. 4=High school graduate 5=Some
##college 6=Associate's 7=Bachelor's 8=Master's 9=Professional 10=Doctorate; cov_party_id
##(q41) 1=Democrat 2=Republican 3=Independent 4=Something else; cov_party_strength (q41_a)
##1=strong 2=not very strong; cov_party_lean (q41_b, independents etc.) 1=closer to the
##Republican Party 2=closer to the Democratic Party 3=neither; cov_ideology (q40) 1=very
##conservative .. 5=very liberal; cov_vote_2016 (q43) 1=Clinton 2=Trump 3=Other (NA = did
##not vote / unsure); cov_us_born (q48) 1=United States 2=other.
##Dropped: county, ZIP code and state of residence (fine geography), the free-text items
##(q9, q63, *_other), start/end times, all other survey items.
##N = 7,800 respondents and 78,000 rows, as in appendix Table A-5. Spot check: weighted OLS of
##choice on the attribute dummies (base = the "keep current" levels) reproduces Table A-5
##(e.g. public safety 0.059, pay teachers more 0.053, limit unions -0.046).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "STAN0107_OUTPUT_8msas.dta")); names(k) <- tolower(names(k))
stopifnot(nrow(k) == 7800, !anyDuplicated(k$caseid))
city <- as.character(as_factor(k$msa))
state <- c(Charlotte = "North Carolina", Cleveland = "Ohio", Houston = "Texas", Indianapolis = "Indiana",
           Memphis = "Tennessee", Rochester = "New York", "St. Louis" = "Missouri", Seattle = "Washington")[city]
stopifnot(!anyNA(state))
dims <- c("educ", "hieduc", "invest", "gov", "workers", "local")
anames <- c(educ = "education", hieduc = "higher_education", invest = "investment_taxes", gov = "governance",
            workers = "workers_entrepreneurs", local = "local_services")
id <- seq_len(nrow(k))  # re-keyed 1..7800 in source order (caseid is a YouGov panel id)
num <- function(v) as.integer(zap_labels(k[[v]]))
cv <- data.table(cov_city = city, cov_survey_weight = as.numeric(k$weight), cov_birth_year = num("q47"),
                 cov_gender = num("q50"), cov_race = num("q58"), cov_education = num("q51"), cov_party_id = num("q41"),
                 cov_party_strength = num("q41_a"), cov_party_lean = num("q41_b"), cov_ideology = num("q40"),
                 cov_vote_2016 = num("q43"), cov_us_born = num("q48"))
rows <- list()
for (t in 1:5) for (p in 1:2) {
  L <- letters[t]
  ch <- num(paste0("q16_", L)); stopifnot(all(ch %in% 1:2))
  d <- data.table(id = id, task = t, profile = p, choice = as.integer(ch == p))
  for (v in dims) {
    x <- as.character(as_factor(k[[paste0("q16", L, "_", p, "_", v)]]))
    stopifnot(!anyNA(x), !any(x %in% c("skipped", "not asked")))
    x <- mapply(function(s, m, st) gsub("$statename", st, gsub("$msaname", m, s, fixed = TRUE), fixed = TRUE), x, city, state,
                USE.NAMES = FALSE)
    d[, paste0("attr_", anames[[v]]) := x]
  }
  rows[[length(rows) + 1]] <- cbind(d, cv)
}
d <- rbindlist(rows)
stopifnot(!any(grepl("$", unlist(d[, .SD, .SDcols = patterns("^attr_")]), fixed = TRUE)))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 78000)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jensen_2021_city_development_plans.csv"))
