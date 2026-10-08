##PTA partner-country conjoints in Costa Rica and Nicaragua from
##Spilker, G., Bernauer, T., & Umana, V. (2016). Selecting partner countries for preferential
##trade agreements: Experimental evidence from Costa Rica, Nicaragua, and Vietnam.
##International Studies Quarterly, 60(4), 706-718. https://doi.org/10.1093/isq/sqv024
##Replication data: Harvard Dataverse doi:10.7910/DVN/NRQFDQ, CC0 1.0, no restricted files.
##Files read: COSTARICA.dta, Nicaragua.dta (Dataverse "original format" downloads). Also read
##as text, not run: CostaRica.do, Nicaragua.do, Vietnam.do, Supplementary_Material.docx
##(Appendix 2: intro text, randomization, the example Vietnam task in English).
##Usage: Rscript spilker_2016.R <raw dir> <output dir>
##
##Same face-to-face surveys (Dec 2013 - Feb 2014) as the agreement-design conjoint in
##spilker_2018.R, but a DIFFERENT experiment: pairs of hypothetical partner COUNTRIES.
##Costa Rica 820 respondents, Nicaragua 800 (Appendix 2 and A1 give the same counts); each
##saw 5 tasks of 2 countries ("Country 1", "Country 2") with 8 attributes. TWO TABLES, one per
##country: the article estimates each country separately and the attributes are worded
##relative to the respondent's own country. The Vietnam file is NOT built: its alliance
##coding is contradictory (value label and the authors' figure label say military code 1 =
##ally; the authors' alliance dummy is 1 for code 2), so the shown level is not knowable.
##Task and profile are RECORDED: `conjoint` = task*10 + profile.
##Outcomes:
##  choice = country, "Which country would you prefer?" (Vietnam example; the instructions ask
##           which of the two countries the respondent prefers [country] to choose for a new
##           trade agreement). Forced choice, no opt-out.
##  rating = like, "On a scale from 1 to 7, how much would you support a trade agreement
##           between [country] and COUNTRY 1/2? 1 means that you would not support at all the
##           agreement, and 7 means that you would strongly support the agreement."
##           Higher = more favourable. The 0-1 rescaled like2 is dropped.
##Level text: respondents saw Spanish; the deposit gives no Spanish text, so levels are the
##authors' English labels from the figure label definitions in the .do files (e.g.
##"Smaller economic size", "Military ally", "Semi-democratic", "Same culture"). In the Vietnam
##example the attributes read "Size of the economy, compared to [country]", "Distance from
##[capital]", "Religion", "Political leaders" (e.g. "Chosen by citizens (voters) through general
##elections"), "Environmental / Worker rights protection standards, compared to [country]",
##"Security alliance with [country]"; for Costa Rica and Nicaragua the culture attribute is
##Spanish as the language (Appendix 4, the .do comments). Economic size is coded from the
##authors' dummies (econ_size_sma/_sim/_large), which agree with their figure labels; the
##Stata value label of econ_size in the Costa Rica file has larger/smaller reversed. All other
##categorical codes agree 100% with the authors' dummies.
##Religion: in Nicaragua code 2 = Christian per the value label and the rel_chri dummy; the
##figure labels in Nicaragua.do are a copy of the Costa Rica ones (code 2 = Diverse) and are
##not used for religion.
##Nicaragua task 5 profile 1 has no economic-size level for 536 of 800 respondents (deposit
##defect), so that task is dropped for them.
##Spot check: the authors' Figure 3 best/worst-case predictions (Scenarios.csv; like2 on the
##attribute dummies) are Costa Rica .356/.658, Nicaragua .491/.691; the same model on these
##tables gives .361/.656 and .480/.692 (differences from the dropped tasks).
##Randomization: "completely independent randomization of the values for each attribute";
##attribute order was randomized per respondent (fixed across their tasks) but not recorded.
##DROPPED: tasks where a profile has no level for an attribute (political system missing in
##311 Costa Rica and 335 Nicaragua rows, economic size in 536 Nicaragua rows; all dummies 0),
##and 13 Costa Rica tasks where neither country is chosen (forced choice, so the answer is
##missing). Two Costa Rica ratings are missing and kept as NA.
##Covariates as in the source: cov_gender (1/2; which is female is not documented),
##cov_education (0 illiterate .. 6 postgraduate), cov_trade_salience (1 = thought much about
##trade .. 4 = not at all), cov_income (Costa Rica: code 0-5; Nicaragua: amount as reported,
##currency not documented). The surveys' respondent id is re-keyed to `respondent` (1..n).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- list(labor = c("Lower labor standards", "Similar labor standards", "Higher labor standards"),
           env = c("Lower environmental standards", "Similar environmental standards", "Higher environmental standards"),
           military = c("Military ally", "No military ally"),
           democracy = c("Autocratic", "Semi-democratic", "Democratic"),
           culture = c("Same culture", "Different culture"),
           distance = c("1 000 km", "5 000 km", "10 000 km"))
build <- function(file, rel, tab, nresp) {
  s <- as.data.table(zap_labels(read_dta(file.path(raw, file))))
  stopifnot(s[, .N, respondent][, all(N == 10)], uniqueN(s$respondent) == nresp, s[, uniqueN(conjoint), respondent][, all(V1 == 10)])
  ##codes agree with the authors' dummies
  stopifnot(s[, all(lab_weak == (labor == 1) & lab_stro == (labor == 3))], s[, all(env_weak == (env == 1) & env_stro == (env == 3))],
            s[, all(alliance == (military == 1))], s[, all(cult_sim == (culture == 1))],
            s[, all(short == (distance == 1) & far == (distance == 3))],
            s[!is.na(democracy), all(no_dem == (democracy == 1) & dem == (democracy == 3))],
            s[is.na(democracy), all(no_dem + sem_dem + dem == 0)])
  s[, econ := fifelse(econ_size_sma == 1, "Smaller economic size", fifelse(econ_size_sim == 1, "Same economic size",
                fifelse(econ_size_large == 1, "Larger economic size", NA_character_)))]
  stopifnot(s[, all(econ_size_sma + econ_size_sim + econ_size_large <= 1)], s[!is.na(econ), all(!is.na(econ_size))])
  s[, task := as.integer(conjoint %/% 10)][, profile := as.integer(conjoint %% 10)]
  s[, bad := anyNA(democracy) | anyNA(econ) | sum(country) != 1, .(respondent, task)]
  cat(tab, ": dropped tasks", s[bad == TRUE, uniqueN(paste(respondent, task))], "\n")
  s <- s[bad == FALSE]
  d <- s[, .(id = as.integer(respondent), task, profile, choice = as.integer(country), rating = as.integer(like),
             attr_economic_size = econ, attr_culture = lv$culture[culture], attr_distance = lv$distance[distance],
             attr_religion = rel[religion], attr_political_system = lv$democracy[democracy],
             attr_environmental_standards = lv$env[env], attr_labor_standards = lv$labor[labor],
             attr_military_alliance = lv$military[military],
             cov_gender = as.integer(gender), cov_education = as.integer(education),
             cov_trade_salience = as.integer(salience), cov_income = as.numeric(income))]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)],
            d[, uniqueN(cov_education), id][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
##religion codes differ by file (value labels = the authors' figure labels in each .do)
build("COSTARICA.dta", c("Islam", "Diverse", "Christian"), "spilker_2016_pta_partners_costa_rica", 820L)
build("Nicaragua.dta", c("Islam", "Christian", "Diverse"), "spilker_2016_pta_partners_nicaragua", 800L)
