##Wind-turbine factorial vignette experiment (Switzerland) from
##Umit, R., & Schaffer, L. M. (2022). Wind turbines, public acceptance, and electoral outcomes.
##Swiss Political Science Review, 28(4), 712-727. https://doi.org/10.1111/spsr.12521
##Replication data: Harvard Dataverse doi:10.7910/DVN/B6NVRM, CC0 1.0. Files read:
##03_data_survey.Rdata (one data.frame `x`, loaded into its own environment); vignette, level text,
##outcome wording and covariate codes from 01_article.Rmd ("Experimental component", Table
##"Outcome Measures") and 02_appendix.Rmd ("Questionnaire"), read as text.
##Usage: Rscript umit_2022.R <dir holding the .Rdata> <output dir>
##
##4,151 respondents (respondi online panel, Swiss voting-age population quotas on age, gender, region,
##rural areas over-sampled; 6-20 September 2019; German, French or Italian questionnaire) each read ONE
##vignette (task = 1, profile = 1) from a 2 x 2 x 2 full factorial (pre-registered, EGAP 20190903AA):
##  "To increase the amount of electricity generated from renewable sources of energy, there are
##  proposals to place wind turbines in the canton of [own / different canton], in landscapes similar to
##  the one pictured below. [photograph with / without a wind turbine] There has been a mixed reaction
##  to these proposals. Some ['people' / 'political parties, such as the Social Democratic Party of
##  Switzerland,'] support these proposals while other ['people' / 'political parties, such as the
##  Swiss People's Party,'] oppose them."
##attr_locality (iv_location 1/0): "own canton" / "different canton". The vignette named the canton:
##  the respondent's own (cov_canton) or one drawn at random from the other 25; which other canton was
##  shown is not recorded, so the level is stored as the authors' description.
##attr_exposure (iv_exposure 1/0): "photograph with a wind turbine" / "photograph without a wind
##  turbine" (a landscape in Entlebuch, LU, and the same photo with the turbine removed).
##attr_politicisation (iv_politicisation 1/0): "political parties, such as the Social Democratic Party
##  of Switzerland / the Swiss People's Party" / "people" (the two slots of the sentence move together).
##Levels are the English text of the article/appendix; respondents saw a German, French or Italian
##translation (cov_language), which is not deposited. 145 respondents have no treatment recorded
##(all three factors NA) and are dropped (4,006 left); 22 more with none of the outcomes below are
##omitted: 3,984 respondents. The article reports 4,151 respondents obtained.
##Outcomes (all asked after the one vignette; 1-5, 5 = most supportive/likely; "Don't know" (9999)
##already recoded to NA by the authors, so it cannot be told from item non-response):
##  rating = dv_acceptance, "How about you? Do you support or oppose these wind turbine proposals?"
##           5 Strongly support ... 1 Strongly oppose.
##  rating_turnout = dv_turnout, "The Swiss federal election is being held on 20 October 2019. How
##           likely is that you will vote?" 5 Very likely ... 1 Very unlikely; NA also for respondents
##           not eligible to vote (-9999).
##  rating_vote_sp / rating_vote_svp = dv_supvote / dv_oppvote, "How likely is it that you will vote
##           for the Social Democratic Party of Switzerland?" / "... the Swiss People's Party?" (eligible
##           voters only, in random order), 5 Very likely ... 1 Very unlikely.
##The authors' derived dv_ntrvote (count of neutral/DK vote answers) is dropped.
##Covariates: cov_language (questionnaire language), cov_canton (canton of residence, German names as
##stored), cov_urbanrural (FSO commune type as coded by the authors: 1 Urban, 2 Intermediate, 3 Rural,
##labels from 02_appendix.Rmd figure code), cov_canton_years (years lived in canton), cov_gender
##(authors' `female`: 1 -> female, 0 -> male, as counted in the article's sample description; the
##questionnaire's "Other" is not distinguishable and is NA with refusals), cov_age (age in 2019 that
##the authors computed from year of birth), cov_education (questionnaire Q5 answer text for codes
##1-10; Don't know is already NA), cov_income (Q14 codes 1-10, CHF bands in the appendix
##questionnaire), cov_climate (Q6, 1 Not at all ... 4 Very worried), cov_polinterest (Q7, 1-4),
##cov_leftright (as stored, 0-9; the questionnaire describes 0-10, so the stored coding is the
##authors'), cov_fmc_type / cov_fmc_result (which factual manipulation check was asked and 1 =
##answered correctly). The commune of residence (`municipality`) is dropped as a fine-grained
##location; pid is already a 1..4151 sequence and is kept as id. No survey weight in the deposit.
##Spot check (the article's estimates are computed inline, so only the direction is checkable):
##OLS of rating on the three factors gives exposure +0.13 (photo with turbine vs without), locality
##-0.04, politicisation +0.01 on the 1-5 scale, matching the article's "exposure increases
##acceptance, locality and politicisation no effect".
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "03_data_survey.Rdata"), envir = e)
s <- as.data.table(e$x)
stopifnot(nrow(s) == 4151, uniqueN(s$pid) == 4151)
s <- s[!(is.na(iv_location) & is.na(iv_exposure) & is.na(iv_politicisation))]
stopifnot(nrow(s) == 4006, !anyNA(s[, .(iv_location, iv_exposure, iv_politicisation)]))
edu <- c("Incomplete compulsory school/primary school", "Compulsory school", "Transitional educational programme",
         "General training without maturity", "Elementary vocational training or apprenticeship",
         "Maturity or teacher training school", "Post-secondary education, non tertiary",
         "Vocational high school with federal or master certificate", "University of applied science, university, ETH",
         "Doctorate, habilitation")
stopifnot(all(s$education %in% c(1:10, NA)), all(s$female %in% c(0, 1, NA)), all(s$urbanrural %in% c(1:3, NA)))
d <- s[, .(id = as.integer(pid), task = 1L, profile = 1L,
           rating = as.integer(dv_acceptance), rating_turnout = as.integer(dv_turnout),
           rating_vote_sp = as.integer(dv_supvote), rating_vote_svp = as.integer(dv_oppvote),
           attr_locality = fifelse(iv_location == 1, "own canton", "different canton"),
           attr_exposure = fifelse(iv_exposure == 1, "photograph with a wind turbine", "photograph without a wind turbine"),
           attr_politicisation = fifelse(iv_politicisation == 1,
             "political parties, such as the Social Democratic Party of Switzerland / the Swiss People's Party", "people"),
           cov_language = language, cov_canton = canton,
           cov_urbanrural = c("Urban", "Intermediate", "Rural")[urbanrural],
           cov_canton_years = as.integer(cantonyears),
           cov_gender = c("male", "female")[female + 1],
           cov_age = as.integer(age), cov_education = edu[education], cov_income = as.integer(income),
           cov_climate = as.integer(climate), cov_polinterest = as.integer(polinterest), cov_leftright = as.integer(leftright),
           cov_fmc_type = fmc_type, cov_fmc_result = as.integer(fmc_result))]
d <- d[!(is.na(rating) & is.na(rating_turnout) & is.na(rating_vote_sp) & is.na(rating_vote_svp))]
for (v in c("rating", "rating_turnout", "rating_vote_sp", "rating_vote_svp")) stopifnot(all(d[[v]] %in% c(1:5, NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "umit_2022_wind_turbines.csv"))
