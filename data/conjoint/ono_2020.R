##Gender-stereotype candidate conjoint (Japan, Osaka) from
##Ono, Y., & Yamada, M. (2020). Do voters prefer gender stereotypic candidates? Evidence from a
##conjoint survey experiment in Japan. Political Science Research and Methods, 8(3), 477-492.
##https://doi.org/10.1017/psrm.2018.41
##Replication data: Harvard Dataverse doi:10.7910/DVN/DOZCK5, CC0 1.0, no restricted files.
##File read: conjoint_data.csv from PSRM_replication.tar.gz (the other CSVs are figure/table
##inputs). ReadMe.txt and the authors' .Rmd files read as text, not run. Design and wording:
##the authors' working paper (RIETI DP 18-E-039, https://www.rieti.go.jp/jp/publications/dp/18e039.pdf),
##Table 1, Figure 1, pp. 9-16, and the online appendix (Cambridge supplementary PDF).
##Usage: Rscript ono_2020.R <dir holding conjoint_data.csv> <output dir>
##
##2,686 adults in Osaka Prefecture (Rakuten Research online panel, November 2015, quotas on
##sex x age from the 2010 census), 4 pairs of hypothetical House of Representatives candidates
##"in the same party", 7 attributes. 2,686 respondents and 21,488 profiles, as in the paper.
##Outcome: choice = selected. Wording (Figure 1, translated from Japanese): "Let's suppose the
##following two potential candidates in the same party are considering to run in the national
##election. Which of the two candidates would you like to vote for? Even if you are not entirely
##sure, please indicate which of the two you would prefer if you had to choose either one of
##them." Forced choice, no opt-out (exactly one chosen in every task).
##Attribute text. The survey was in Japanese; only the authors' English translation survives
##(Table 1). The file stores short labels; attr_ holds the translated displayed text of Table 1:
##sex, education and issue specialization as stored; personality a03 and the three ideological
##placements a05 (social), a06 (economic), a07 (military) replaced by the Table 1 statements
##(attribute-to-column mapping from the attribute.names of Figure2 code.Rmd). Figure 1 renders
##the liberal economic statement differently ("Poverty alleviation should be treated as a
##societal responsibility rather than an individual's personal responsibility"); Table 1's
##wording is used. Attribute order randomized per respondent, fixed across the 4 tasks (p. 15);
##not recorded. 1,152 possible profiles = all combinations (p. 15), so no restrictions; level
##probabilities not stated (data shares near-equal).
##Dropped: `Candidate Sex` (duplicate of a01), context (the authors' pair-sex flag
##mixed/mm/ww, derived). trial_response_time = `response time`, constant within task (unit not
##documented; values look like seconds).
##Covariates (as stored, text): cov_gender (Respondent Sex Female/Male lowercased),
##cov_age_group (Respondent age group: 20-29 ... 60above), cov_ba (Respondent BA: BA / No BA,
##the authors' dichotomy of the 5-category education question in appendix Table A1, so not
##cov_education), cov_income_level (Lower/Middle/Upper level, the authors' bands of household
##income), cov_party_id (Respondent Party: "Party support" in appendix Table A1; stored as the
##authors' short names LDP, DPJ, CGP, JCP, Osaka ishin, Other, Independent = "None
##(independent)"). No survey weight (quota sample). No task is repeated.
##Spot check: lm(choice ~ attributes) with SEs clustered by id gives the female AMCE of the
##paper's Figure 2 (see return).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint_data.csv"), check.names = FALSE)
stopifnot(uniqueN(s$respondentIndex) == 2686, s[, .N, respondentIndex][, all(N == 8)],
          s[, sum(selected), .(respondentIndex, task)][, all(V1 == 1)], all(s$a01 == s$`Candidate Sex`),
          s[, uniqueN(`response time`), .(respondentIndex, task)][, all(V1 == 1)])
rc <- function(x, map) { y <- unname(map[x]); stopifnot(!anyNA(y)); y }
d <- s[, .(id = as.integer(respondentIndex), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_sex = rc(a01, c(Male = "Male", Female = "Female")),
           attr_education = rc(a02, c("High school degree" = "High school degree", "University degree" = "University degree",
                                       "Graduate degree" = "Graduate degree")),
           attr_personality = rc(a03, c(
             Persuasive = "Is able to explain and persuade others of his/her point of view",
             Visionary = "Has a clear vision of the future and foresight",
             Mediator = "Mediates differences in opinions to solve conflicts",
             Listener = "Diligently listens to the various opinions and perspectives of others")),
           attr_issue_specialization = a04,
           attr_ideology_social = rc(a05, c(
             Conservative = "Housework and raising children are within a women's domain",
             Liberal = "Men should engage in housework and raising children equally to women")),
           attr_ideology_economic = rc(a06, c(
             Conservative = "Poverty is an individual's responsibility and is not the responsibility of society",
             Liberal = "Poverty is the problem of society and is not an individual's responsibility")),
           attr_ideology_military = rc(a07, c(
             Conservative = "International conflicts should be resolved through military means (hawkish)",
             Liberal = "International conflicts should be resolved through peaceful measures (dovish)")),
           cov_gender = rc(`Respondent Sex`, c(Female = "female", Male = "male")),
           cov_age_group = `Respondent age group`, cov_ba = `Respondent BA`,
           cov_income_level = `Respondent Income level`, cov_party_id = `Respondent Party`,
           trial_response_time = `response time`)]
stopifnot(d[, uniqueN(attr_issue_specialization)] == 6, !anyNA(d$cov_age_group))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ono_2020_gender_stereotypes.csv"))
