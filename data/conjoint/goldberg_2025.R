##Three citizens'-forum (minipublic) conjoint experiments from
##Goldberg, S., Lindell, M., & Bächtiger, A. (2025). Empowered minipublics for democratic
##renewal? Evidence from three conjoint experiments in the United States, Ireland, and
##Finland. American Political Science Review, 119(3), 1393-1410.
##https://doi.org/10.1017/S0003055424001163 (online 2024-11-12)
##Replication data: Harvard Dataverse doi:10.7910/DVN/DN2QHA, CC0 1.0. Files read:
##conjointdata_long_FIN_select.sav, conjointdata_long_IRE_select.sav,
##conjointdata_long_USA_select.sav (attributes as unlabelled codes, plus covariates),
##conjointdata_long_combined.sav (only to link Finnish respondents to socio_Fin.sav via
##its Qualtrics response-ID labels, which are not kept), socio_Fin.sav (Finnish age,
##gender, education). Level text: "Survey questions and responses.docx" and the
##preregistration (Preregestration_ANONYMOUS-1.pdf) in the deposit.
##Usage: Rscript goldberg_2025.R <dir holding the .sav files> <output dir>
##
##One table per country (separate samples, fielded separately; same design):
##  goldberg_2025_minipublics_finland  2,005 respondents (Qualtrics panel, Dec 2021-Feb 2022)
##  goldberg_2025_minipublics_ireland  2,007 respondents (Psyma panel, Jan-Mar 2022)
##  goldberg_2025_minipublics_usa      2,045 respondents (Psyma panel, Jan-Mar 2022)
##Each respondent compared 5 pairs of hypothetical citizens' forums ("Citizens' forum A/B")
##described by 9 attributes. Attribute order was randomized per respondent; the order is
##not in the data. Outcomes:
##  choice = "As a general matter, which of the two scenarios do you prefer?" (forced
##           choice, no opt-out; every pair has exactly one chosen profile).
##  rating = "As a general matter, how strongly do you support or oppose Citizens' forum
##           A/B", 1 = strongly oppose ... 7 = strongly support. Ireland and USA only: the
##           rating was not collected in Finland (Qualtrics implementation problem, per the
##           article), so the Finland table has no rating column.
##Attribute codes -> displayed text. The .sav files carry no labels for the country files;
##the combined file's value labels (e.g. initiative 1 = "Think Tank/NGO", size 1 = "Small",
##majority 1 = "Narrow majority") map the codes to the levels of the deposit's survey
##document, whose wording is used here:
##  issue 1 "measures to reduce greenhouse gas emissions"; 2 = country-specific:
##    USA "admission of undocumented residents", Ireland "Replacing Direct Provision",
##    Finland "Increase in the refugee quota".
##  initiative 1 "a non-partisan organization", 2 "a committee of the Government";
##  recruitment 1 "random selection", 2 "self-selection"; size 1 "about 20", 2 "about 500";
##  composition 1 "only citizens discuss", 2 "citizens discuss with politicians, civil
##    servants, and stakeholders"; aim 1 "Efficient decision-making (even if this implies
##    the exclusion of certain interests)", 2 "Appropriate consideration of all interests
##    (even if this implies inefficiency)"; consensus 1 "52%", 2 "71%"; authorization
##    1 "Binding decision", 2 "Recommendation to public officials", 3 "Recommendation to a
##    public referendum".
##  output: CAVEAT. "output" has no value labels anywhere in the deposit (the authors
##    analyse only the derived outcome.fav). 1 = "in favor of the measure", 2 = "against
##    the measure" is INFERRED from the preregistration's level order, which every one of
##    the 8 labelled attributes follows (code 1 = first-listed level). The level TEXT is
##    confirmed by the survey document ("[Output] = [in favor of the measure / against
##    the measure]"); only which code is which is inferred. Indirect check (2026-10-07):
##    outcome.fav (output matches the respondent's own view) is 1 for code 1 at rates
##    0.34 (FIN: raise the refugee quota), 0.64 (IRE: replace Direct Provision) and 0.56
##    (USA: admit undocumented residents). Read as the share favouring each measure these
##    are plausible; the reverse mapping would put Finnish support for a larger refugee
##    quota at 0.66. Consistent with 1 = in favor, not proof of it.
##Finnish respondents saw a Finnish version; the English master wording is used.
##Covariates (source codes; 997, or 8 in Finland, = don't know on the trust and
##  satisfaction items): cov_satisfaction_democracy (1-7), cov_trust_parliament,
##  cov_trust_government, cov_trust_politicians (1-7), cov_salience_climate,
##  cov_salience_immigration (1-7), cov_familiarity (q15: 1 not familiar, 2 heard of,
##  3 know well, 4 participated), cov_experience_value (q16, 1-7, asked if familiar),
##  cov_retro_appropriate (q20, asked after the conjoint, 1-7), cov_trust_minipublics (1-7),
##  cov_trust_citizens1/2 (1-7). Ireland/USA also: cov_video_time_spent,
##  cov_recruitment_time_spent, cov_authorization_time_spent, cov_conjoint_time_spent
##  (seconds on those survey pages). Finland also: cov_age (free-text answer; values
##  outside 18-99 set missing, 10 rows), cov_gender (1 male, 2 female, 3 other, 4 prefer
##  not to say), cov_education (Finnish codes 1-11, 9 no education, 10 prefer not to say,
##  11 don't know). Finland's video_time_spent is on an undocumented scale and is dropped.
##Dropped: outcome.fav (derived: output x respondent's own issue preference; the issue-
##  preference items themselves are not in the deposit), pair, choice (A/B, duplicated in
##  `choice` here), the Qualtrics response IDs. No survey weight ships.
##Counts match the article (2,005 / 2,007 / 2,045 = 6,057).
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
issue2 <- c(FIN = "Increase in the refugee quota", IRE = "Replacing Direct Provision", USA = "admission of undocumented residents")
lv <- list(initiative = c("a non-partisan organization", "a committee of the Government"),
           recruitment = c("random selection", "self-selection"), size = c("about 20", "about 500"),
           composition = c("only citizens discuss", "citizens discuss with politicians, civil servants, and stakeholders"),
           aim = c("Efficient decision-making (even if this implies the exclusion of certain interests)",
                   "Appropriate consideration of all interests (even if this implies inefficiency)"),
           majority = c("52%", "71%"), output = c("in favor of the measure", "against the measure"),
           authorization = c("Binding decision", "Recommendation to public officials", "Recommendation to a public referendum"))
anames <- c(initiative = "initiative", recruitment = "recruitment", size = "group_size", composition = "group_composition",
            aim = "aim", majority = "degree_of_consensus", output = "output", authorization = "authorization")
covmap <- list(
  FIN = c(q2_satisfaction = "satisfaction_democracy", q3_1 = "trust_parliament", q3_2 = "trust_government", q3_3 = "trust_politicians",
          q12_1 = "salience_climate", q12_2 = "salience_immigration", q15 = "familiarity", q16 = "experience_value",
          q20_retro = "retro_appropriate", q21_trust = "trust_minipublics", q25_1 = "trust_citizens1", q25_2 = "trust_citizens2"),
  IRE = c(q2_IRE = "satisfaction_democracy", q3_01 = "trust_parliament", q3_02 = "trust_government", q3_03 = "trust_politicians",
          q12_01 = "salience_climate", q12_02 = "salience_immigration", q15 = "familiarity", q16 = "experience_value",
          q20 = "retro_appropriate", q21 = "trust_minipublics", q22_01 = "trust_citizens1", q22_02 = "trust_citizens2",
          video_time_spent = "video_time_spent", recruitment_time_spent = "recruitment_time_spent",
          authorization_time_spent = "authorization_time_spent", conjoint_time_spent = "conjoint_time_spent"))
covmap$USA <- covmap$IRE; names(covmap$USA)[1] <- "q2_US"
tname <- c(FIN = "finland", IRE = "ireland", USA = "usa")
for (cc in names(tname)) {
  x <- as.data.table(zap_labels(read_sav(file.path(raw, sprintf("conjointdata_long_%s_select.sav", cc)))))
  d <- x[, .(id = as.integer(respondent_id), task = as.integer(task), profile = as.integer(profile), choice = as.integer(chosen))]
  if (cc != "FIN") d[, rating := as.integer(x$rating)] else stopifnot(all(is.na(x$rating)))
  d[, attr_issue := c("measures to reduce greenhouse gas emissions", issue2[[cc]])[x$issue]]
  for (v in names(anames)) d[, paste0("attr_", anames[[v]]) := lv[[v]][x[[v]]]]
  cm <- covmap[[cc]]
  for (v in names(cm)) d[, paste0("cov_", cm[[v]]) := x[[v]]]
  if (cc == "FIN") {
    cb <- read_sav(file.path(raw, "conjointdata_long_combined.sav"))
    link <- unique(data.table(id = as.integer(zap_labels(cb$respondent_id)), rid = as.character(as_factor(cb$respondent_id)), country = cb$country))[country == "FIN"]
    stopifnot(nrow(link) == uniqueN(d$id), setequal(link$id, d$id))
    s <- as.data.table(read_sav(file.path(raw, "socio_Fin.sav")))
    age <- suppressWarnings(as.integer(s$S1_age)); age[!is.na(age) & (age < 18 | age > 99)] <- NA
    s <- data.table(rid = s$ResponseId, cov_age = age, cov_gender = as.integer(zap_labels(s$S2_gender)), cov_education = as.integer(zap_labels(s$S4_education)))
    s <- merge(link[, .(id, rid)], s, by = "rid", all.x = TRUE)[, rid := NULL]
    stopifnot(nrow(s) == nrow(link))
    d <- merge(d, s, by = "id")
  }
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, sprintf("goldberg_2025_minipublics_%s.csv", tname[[cc]])))
}
