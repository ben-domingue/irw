##Blame claiming vs deflecting in crises: factorial vignettes (3 scenarios) from
##Miller, D. R., & Reeves, A. (2022). Pass the buck or the buck stops here? The public costs of claiming and
##deflecting blame in managing crises. Journal of Public Policy, 42(1), 63-91. https://doi.org/10.1017/S0143814X21000039
##Replication data: Harvard Dataverse doi:10.7910/DVN/S0XVEQ, CC0 1.0. File read: MTurk_factorial_data.csv
##(MTurk respondents who passed attention checks; README, CODEBOOK.txt and replicateSI.R read as text).
##Usage: Rscript miller_2022_blame.R <dir holding f4373082 = MTurk_factorial_data.csv> <output dir>
##
##872 MTurk respondents each read three stylized crisis vignettes (task 1 bridge collapse, 2 budget shortfall,
##3 heat wave; task numbers are the scenario index, NOT the order shown: the authors randomized scenario order and
##the order is not in this file), each with an executive and three randomized factors: executive response
##(control / blame claim / blame deflect), crisis severity (low / moderate / high) and the executive's party
##relative to the respondent (copartisan / noncopartisan / baseline). Factors are the SI factorial analysis
##(Tables SI.13-14), pooled across scenarios. One profile (vignette) per task. The deposit stores only 0/1
##treatment dummies; the displayed vignette TEXT is not in the deposit and the article/SI could not be read
##(paywalled): LABELS: tags only (levels are the authors' dummy names). Baselines are those of the authors' dummy
##coding: response baseline = control (the stylized file's BCresponse text: control/blameclaim/blamedeflect);
##severity baseline = low; party baseline = neither dummy set. For Democrats and Republicans the three party
##codes are about equal thirds, so the baseline is a third arm (executive without a matching or contrasting party);
##its displayed text is not documented, hence the label "party baseline (neither co- nor noncopartisan)".
##Outcomes (authors' 4-point codings; the exact wording is not in the deposit):
##  rating_handling = {BC,BS,HW}govapprove: approval of the executive's handling of the crisis, 1-4, higher =
##    more approval (the binary version is 1 for 3-4, "somewhat or strongly approve").
##  rating_vote = {BC,BS,HW}govvote: likelihood of voting for the executive in the next election, 1-4, higher =
##    more likely (binary 1 for 3-4, "somewhat or very likely").
##Rows with a missing outcome or missing party-match code (27 respondents with party "Other" have no
##copartisan coding) are dropped per task. Covariates: cov_gender (female 0 male / 1 female, CODEBOOK), cov_age_code
##(authors' 4-point age scale, labels not documented), cov_race, cov_education, cov_income, cov_party_id (pid),
##cov_ideology (text as in the file). ResponseID dropped, ids re-keyed. Derived dummies/binary outcomes dropped.
##Not built: Flint experiment, stylized one-factor files and TAPS flood study (single-factor arms).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- fread(file.path(raw, "f4373082"))
f[, id := .I]
sc <- c(BC = "bridge collapse", BS = "budget shortfall", HW = "heat wave")
L <- lapply(seq_along(sc), function(t) {
  p <- names(sc)[t]; g <- function(s) f[[paste0(p, s)]]
  data.table(id = f$id, task = t, profile = 1L,
    rating_handling = as.integer(g("govapprove")), rating_vote = as.integer(g("govvote")),
    attr_executive_response = c("control", "blame claim", "blame deflect")[1L + g("response_blameclaim") + 2L * g("response_blamedeflect")],
    attr_severity = c("low", "moderate", "high")[1L + g("severity_mod") + 2L * g("severity_high")],
    attr_executive_party = c("party baseline (neither co- nor noncopartisan)", "copartisan", "noncopartisan")[1L + g("copart") + 2L * g("noncopart")],
    trial_scenario = unname(sc[t]))
})
d <- rbindlist(L)
cp <- rbindlist(lapply(c("BC", "BS", "HW"), function(p) data.table(id = f$id, ok = !is.na(f[[paste0(p, "copart")]]) & !is.na(f[[paste0(p, "noncopart")]]))))
d[, ok := cp$ok]
d <- d[ok == TRUE & !is.na(rating_handling) & !is.na(rating_vote)][, ok := NULL]
d <- merge(d, f[, .(id, cov_gender = c("male", "female")[female + 1L], cov_age_code = as.integer(age), cov_race = race,
                    cov_education = educ, cov_income = income, cov_party_id = pid, cov_ideology = ideo)], by = "id")
setcolorder(d, c("id", "task", "profile", "rating_handling", "rating_vote", grep("^attr_", names(d), value = TRUE)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miller_2022_blame_crisis.csv"))
