##Nuclear-strike vignette experiments (regime type x country race; two tables) from
##Rathbun, B. C., Parker, C. S., & Pomeroy, C. (2024). Separate but unequal: Ethnocentrism and
##racialization explain the "democratic" peace in public opinion. American Political Science Review.
##https://doi.org/10.1017/S0003055424000509
##Replication data: Harvard Dataverse doi:10.7910/DVN/9JWDKK, CC0 1.0, no restricted files, no terms.
##Files read: qualtrics_survey.rds, prolific_survey.rds. Read as text only: README.txt,
##qualtrics_survey_analysis_rep.R, prolific_survey_analysis_rep.R (authors' coding of the arms),
##dataverse_appendix.pdf (B1: covariate instruments), supplementary_material.pdf (A2.2.3: threat and
##immorality wording) and the article (vignette text, outcome wording, fielding). The GloVe/Hansard
##embedding files and the re-analysis files of earlier studies (Johns & Davies, Tomz & Weeks, Dafoe et
##al.) are not used.
##Usage: Rscript rathbun_2024.R <raw dir> <output dir>
##
##Design (article): Tomz-Weeks style bullet-point vignette about a country developing nuclear weapons,
##one vignette per respondent (task = 1, profile = 1). Fixed bullets: "A country is developing nuclear
##weapons and will have its first nuclear bomb within six months."; not a military ally; low levels of
##trade; military forces half as strong as American forces in the region; "The country is predominantly
##Christian." Randomized bullets describing the country:
##  attr_regime: "The country is a democracy and shows every sign that it will remain a democracy" /
##    "The country is not a democracy and shows no sign of becoming a democracy" (source nukes_regime
##    dem / nondem; the article gives the two clauses after "The country").
##  attr_race: "The country's population is predominantly white" / "The country's population is
##    predominantly non-white" / (not shown) = no racial information and no bullet (source nukes_race
##    white / nonwhite / only; codes per the authors' scripts: only = race unspecified).
##Two samples, analysed separately by the authors and with different arms -> two tables:
##  rathbun_2024_nuclear_strike_qualtrics: Qualtrics panel, 7-13 April 2022, US adults with race,
##    education and gender quotas; 2 x 3 arms; N = 1,626 (as in the paper).
##  rathbun_2024_nuclear_strike_prolific: Prolific, 27 Sep - 10 Oct 2022, US adults; the white arm was
##    dropped (2 x 2: regime x nonwhite / no race bullet); N = 2,659 (as in the paper).
##All cells occur with near-equal shares; the article states random assignment but no probabilities.
##Outcomes:
##  rating: "Would you favor or oppose using the U.S. military to attack the country's nuclear
##    development sites?" (preceded by "By attacking the country's nuclear development sites now, the
##    United States could prevent the country from making any nuclear weapons."). Source nukes_strike,
##    stored raw. COUNT DISCREPANCY: the article says a five-point scale from "oppose strongly" (=1) to
##    "favor strongly" (=5), but both files hold 1-7 with every value used (and the authors' intercepts,
##    3.4-4.1, fit 1-7). Higher = more support for a strike (article; the democracy arm lowers it, as the
##    paper reports); the labels of the seven points are not deposited, so the anchors are recorded as
##    unknown.
##  rating_threat (Prolific only): agreement with "If the U.S. does not attack the nuclear development
##    sites, the country's nuclear weapons would pose a serious security threat to the U.S. and its
##    allies." 1 = strongly disagree ... 7 = strongly agree.
##  rating_immoral (Prolific only): agreement with "It would be morally wrong for the U.S. to attack the
##    country's nuclear development sites." 1 = strongly disagree ... 7 = strongly agree.
##No opt-out (single rating). No respondent id in the deposit: id = row number within each file.
##Covariates (as deposited, already recoded by the authors; dichotomies are the authors'):
##  cov_gender_male: authors' "male"/"nonmale" (the instrument had Male/Female/Non-binary; nonmale pools
##    female and non-binary, so the reserved cov_gender cannot be filled); cov_race_white (white /
##    nonwhite); cov_college (college / noncollege); cov_age = age in years as deposited (the instrument
##    asked year of birth; the authors' derived age; values outside 18-100, one Qualtrics value of 122, set
##    to NA); cov_party_id7_code and cov_ideology_code = the 1-7 codes (no file maps the party codes;
##    the authors' Qualtrics plot labels ideology 1 = "Extremely Liberal", 7 = "Extremely Conservative",
##    the reverse of the instrument's listed order, so codes are kept); cov_ethno<k> = the raw ethnocentrism items
##    (Qualtrics: 3 Neuliep-McCroskey items, 7-point; Prolific: 12 Bizumic superiority items, 5-point,
##    unreversed as deposited).
##Dropped: the authors' factor and additive scores (ethnocentrism, racial resentment) and summed scales
##(mil_int, sdo, rwa) -- derived, their items are not deposited.
##Spot check (printed): Qualtrics, race unspecified arm, mean strike support nondem - dem; the authors'
##Table A11-style estimate of the democracy effect with race unspecified (Prolific A14 without covariates).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
regime <- c(dem = "The country is a democracy and shows every sign that it will remain a democracy",
            nondem = "The country is not a democracy and shows no sign of becoming a democracy")
race <- c(white = "The country's population is predominantly white",
          nonwhite = "The country's population is predominantly non-white", only = "(not shown)")
build <- function(f, n, extra) {
  s <- as.data.table(readRDS(file.path(raw, f)))
  stopifnot(nrow(s) == n, !anyNA(s$nukes_strike), all(s$nukes_strike %in% 1:7))
  s[, id := .I]
  d <- s[, .(id, task = 1L, profile = 1L, rating = as.integer(nukes_strike))]
  for (v in extra) d[, (paste0("rating_", sub("nukes_", "", v))) := as.integer(s[[v]])]
  d[, attr_regime := unname(regime[as.character(s$nukes_regime)])]
  d[, attr_race := unname(race[as.character(s$nukes_race)])]
  stopifnot(!anyNA(d$attr_regime), !anyNA(d$attr_race))
  age <- s$age
  d[, `:=`(cov_gender_male = as.character(s$gender), cov_race_white = s$race, cov_college = s$education,
           cov_age = as.integer(ifelse(age >= 18 & age <= 100 & age == round(age), age, NA)),
           cov_party_id7_code = as.integer(s$pid), cov_ideology_code = as.integer(s$ideology))]
  for (v in grep("^eth[a-z]*[0-9]+$", names(s), value = TRUE))
    d[, (paste0("cov_ethno", sub("^eth[a-z]*", "", v))) := as.integer(s[[v]])]
  setorder(d, id, task, profile)
  d
}
q <- build("qualtrics_survey.rds", 1626, character(0))
p <- build("prolific_survey.rds", 2659, c("nukes_threat", "nukes_immoral"))
stopifnot(all(p$rating_threat %in% 1:7), all(p$rating_immoral %in% 1:7), uniqueN(p$attr_race) == 2)
fwrite(q, file.path(out, "rathbun_2024_nuclear_strike_qualtrics.csv"))
fwrite(p, file.path(out, "rathbun_2024_nuclear_strike_prolific.csv"))
for (x in list(q, p)) message("race unspecified: dem - nondem strike support = ",
  round(x[attr_race == "(not shown)" & grepl("is a democracy", attr_regime), mean(rating)] -
        x[attr_race == "(not shown)" & grepl("not a democracy", attr_regime), mean(rating)], 3),
  "; N = ", nrow(x), "; ages set NA: ", sum(is.na(x$cov_age)))
