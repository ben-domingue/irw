##Migration-policy package conjoint in six European countries (PACES survey) from
##Jeannet, A.-M., & Rubio, M. G. (2026). PACES public opinion dataset [Data set]. DANS Data
##Station Social Sciences and Humanities. https://doi.org/10.17026/SS/R6LXP1
##Analysed in Jeannet, A.-M., & Rubio, M. G. (2026). Understanding public ambivalence about
##immigration: The role of legal heuristics (PACES Working Paper No. 12, D6.6). International
##Institute of Social Studies (no DOI).
##Deposit: DANS SSH Data Station doi:10.17026/SS/R6LXP1, CC BY 4.0. Files read:
##final_dataset_10062025.csv and PACES-survey-codebook.csv (attribute level text). Design from
##the working paper (pp. 8-10).
##Usage: Rscript jeannet_2026.R <dir holding final_dataset_10062025.csv and PACES-survey-codebook.csv> <output dir>
##
##jeannet_2026_migration_policy: 9,045 adults (Bilendi & Respondi online panel, quotas on gender,
##  age and region; April-May 2025): Austria 1,505, Netherlands 1,500, Italy 1,508, Slovakia
##  1,506, Spain 1,525, Sweden 1,501; the paper reports ~9,000 (1,500 per country). One table
##  with cov_country because the authors pool the six countries in their main AMCEs and the
##  codebook gives one English master text per level. Each respondent saw 5 tasks of 2 policy
##  packages (Policy A, Policy B), 6 attributes: asylum seekers/refugees (3 levels), skills &
##  labour shortages (3), social welfare (3), regularization (3), borders (3), returns (4).
##  attr_* hold the codebook's English master text, with "[pipe: COUNTRY]" standing for the
##  respondent's country name; respondents saw a translation in German, Italian, Dutch, Slovak,
##  Spanish or Swedish. The data file truncates level text at 80 characters; each truncated value
##  is matched to the unique codebook level it begins with.
##  Outcomes (both asked about the same tasks):
##    choice = QCon3: a forced choice of "POLICY option A" / "POLICY option B" (the paper: "a
##      binary choice about which policy they preferred"; the exact stem is not in the deposit).
##      No opt-out.
##    rating = C1xRA / C1xRB, support for each policy, 1 = "Extremely oppose" to 7 = "Extremely
##      support"; higher = more support.
##  Randomization (paper): fully randomized, A and B must differ on at least one attribute; the
##  order of the six dimensions was randomized per respondent and held across their 5 tasks but
##  is NOT recorded (no attrpos_). Level frequencies differ strongly between cards (e.g. asylum
##  level 1 on 5,015 of 9,045 task-1 Policy A cards, level 3 on 987) but balance over all 10
##  cards (about 30,000 each), so levels were not drawn independently per card; the scheme
##  is not documented.
##  Spot check: where the two ratings differ, the chosen policy has the higher rating in 84%
##  of tasks.
##  Covariates: cov_country, cov_survey_weight (Weight), cov_gender (A01 answer text Male/Female/
##  Other in the data file and codebook -> male/female/other; Refusal NA), cov_birth_year (A02),
##  cov_education (A06 "How would you describe your education attainment?", the codebook's English
##  answer text, as in the data file; Refusal/Don't know NA), cov_income_feeling (A07, 1 living
##  comfortably .. 4 finding it very difficult), cov_work_status (A08, 1-9), cov_political_views (A09, 1 very
##  conservative .. 5 very progressive, 6 none of the above), cov_discriminated_group (A10,
##  1 yes 2 no); codes as in the codebook, Refusal/Don't know set missing. Not kept: qtime /
##  qtime_min (interview time) and the page timings. No attention check in the codebook.
##  No repeated task.
##  Dropped: uuid (panel participant id; ids re-keyed to integers in file order), record, the
##  PRIVACY consent flag (all consented), region/province of residence, migration history and
##  attitude batteries (B*, C*, D*), page timings.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "final_dataset_10062025.csv"), encoding = "UTF-8")
cb <- fread(file.path(raw, "PACES-survey-codebook.csv"), header = TRUE, encoding = "UTF-8")[, 2:6]
setnames(cb, c("var", "desc", "type", "code", "label"))
cb[, var := trimws(var)][, var := c(NA, var)[cummax(seq_len(.N) * (var != "")) + 1L]]
cb[, label := trimws(label)]
stopifnot(nrow(s) == 9045, uniqueN(s$uuid) == 9045)
s[, id := seq_len(.N)]
anames <- c(ATTRIBUTE = "asylum", ATTRIBUT0 = "labour_shortages", ATTRIBUT1 = "welfare", ATTRIBUT2 = "regularization",
            ATTRIBUT3 = "borders", ATTRIBUT4 = "returns")
L <- list()
for (t in 1:5) for (p in 1:2) {
  dd <- data.table(id = s$id, task = t, profile = p,
                   choice = as.integer(s[[paste0("QCon3_CHOICESET", t)]] == c("POLICY option A", "POLICY option B")[p]),
                   rating = as.integer(sub("^Extremely (oppose|support)", "", s[[paste0("C1x", c("RA", "RB")[p], "_CHOICESET", t)]])))
  for (k in names(anames)) {
    v <- paste0("CHOICESET", t, "_CHOICECARD", p, "_", k)
    lev <- cb[var == v & label != "", label]
    stopifnot(length(lev) %in% 3:4)
    x <- s[[v]]
    m <- vapply(x, function(z) { h <- which(startsWith(lev, z)); if (length(h) == 1) h else NA_integer_ }, 1L)
    stopifnot(!anyNA(m))
    dd[, paste0("attr_", anames[[k]]) := lev[m]]
  }
  L[[length(L) + 1]] <- dd
}
d <- rbindlist(L)
stopifnot(!anyNA(d$rating), d[, all(rating %in% 1:7)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
code <- function(v, labs) match(s[[v]], labs)
lab <- function(v, labs) fifelse(s[[v]] %in% labs, s[[v]], NA_character_)
cv <- s[, .(id, cov_country = country, cov_survey_weight = Weight,
            cov_gender = c(Male = "male", Female = "female", Other = "other")[A01], cov_birth_year = as.integer(A02),
            cov_education = lab("A06", c("No formal education", "Incomplete secondary school or less", "Complete secondary school",
                                          "Some university-level education, without degree", "University-level education, with degree",
                                          "Post-graduate education or above")),
            cov_income_feeling = code("A07", c("Living comfortably on present income", "Coping on present income",
                                               "Finding it difficult on present income", "Finding it very difficult on present income")),
            cov_work_status = code("A08", c("In paid work (employee, self-employed, working for your family business)",
                                            "In education (not paid for by employer)", "Unemployed and actively looking for a job",
                                            "Unemployed, wanting a job but not actively looking for a job", "Permanently sick or disabled",
                                            "Retired", "In community or military service",
                                            "Doing housework, looking after children or other persons", "Other")),
            cov_political_views = code("A09", c("Very conservative", "Moderately conservative", "Moderate/centrist",
                                                "Moderately progressive", "Very progressive", "None of the above")),
            cov_discriminated_group = code("A10", c("Yes", "No")))]
stopifnot(cv[, sum(is.na(cov_education))] == s[, sum(A06 %in% c("Refusal", "Don't know"))],
          cv[, sum(is.na(cov_work_status))] == s[, sum(A08 %in% c("Refusal", "Don't know"))])
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jeannet_2026_migration_policy.csv"))
