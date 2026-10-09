##Emerging-politician conjoints in Germany, South Korea and among North Korean migrants from
##Brehm, N., Zhou, A. H., & Denney, S. (2025). From division to democracy: Integrating
##post-socialist citizens in Germany and South Korea. Communist and Post-Communist Studies.
##https://doi.org/10.1525/cpcs.2025.2636997
##Replication data: Harvard Dataverse doi:10.7910/DVN/8GUUP5. Dataverse licence field: CC0 1.0;
##the deposit's own LICENSE file and README say CC BY 4.0. The licence fields here carry
##CC BY 4.0 (the authors' stated terms, the stricter of the two).
##Files read: germany_politician.csv, korea_politician.csv, nk_politician.csv (the authors'
##prepared long files, one row per respondent x task x profile). Read as text: README.md,
##data_dictionary_{germany,korea,nk}.md, prepare_data.R, analysis.R.
##Usage: Rscript brehm_2025.R <raw dir> <output dir>
##
##Respondents chose between two hypothetical emerging politicians described by their positions
##on 5 issues (each a statement): Democracy (3 levels), Economy (2), Welfare (2), Gender (3: a
##gender-roles policy stance, not the politician's gender), Diversity (3). Attribute text is the
##displayed statement in the survey language (German, or Korean in both Korean samples), as in
##the deposit; the dictionaries give English glosses.
##Outcome: choice = politician_choice, forced choice between the two profiles (exactly one per
##task, checked); question wording not deposited.
##Three tables, one per sample (separate fieldings and populations; the Korean and North Korean
##samples share attribute text and the authors compare them in one cregg call by group, but
##the North Korean migrants were recruited separately through an NGO):
##  brehm_2025_politicians_germany     2,071 respondents (README: 2,071), 8 tasks. Quota sample
##     (attention check Q114 applied by the authors) plus an oversample of Eastern Germans
##     (no attention check), combined and filtered by the authors' prepare_data.R.
##  brehm_2025_politicians_korea       1,994 (README: 1,994), 7 tasks; overseas residents removed
##     by the authors.
##  brehm_2025_politicians_nk_migrants   311 (README: 311), 10 tasks; 14 respondents have no
##     survey covariates (NA).
##task/profile from question_profile ("t.p").
##Covariates as deposited: cov_birth_year (yob, as recorded: implausible years remain, Korea 13
##respondents before 1920 and 18 after 2005, North Korean migrants 1 after 2005; the authors'
##age = 2023 - yob is dropped because it inherits them); cov_female (1 = answered female,
##0 = any other answer, per prepare_data.R: so not the reserved cov_gender); cov_education (answer text, German/Korean). Germany:
##cov_region_group (east_germany_F, the authors' Western German / Eastern German / Post-GDR
##citizen classification), cov_state_at_18, cov_current_state, cov_birth_country, cov_party_vote
##(Q11 vote intention, text). Korea: cov_province, cov_ideology (Q12 text), cov_party_vote (Q13
##party support, text). North Korean migrants: cov_province_birth, cov_year_defection,
##cov_year_arrived_sk, cov_years_in_nk, cov_years_in_sk (authors' derived spans, kept as
##recorded), cov_current_residence; education is cov_education (Q7, education in North Korea).
##DROPPED: Qualtrics ResponseId (re-keyed to integers in file order).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
at <- c("Democracy", "Economy", "Welfare", "Gender", "Diversity")
build <- function(f, covs, name) {
  s <- fread(file.path(raw, f), encoding = "UTF-8", colClasses = list(character = "ResponseId"), na.strings = "")
  tp <- tstrsplit(as.character(s$question_profile), ".", fixed = TRUE)
  d <- data.table(id = match(s$ResponseId, unique(s$ResponseId)), task = as.integer(tp[[1]]), profile = as.integer(tp[[2]]),
                  choice = as.integer(s$politician_choice))
  for (v in at) { stopifnot(!anyNA(s[[v]]), all(nzchar(s[[v]]))); d[, paste0("attr_", tolower(v)) := s[[v]]] }
  for (v in names(covs)) d[, paste0("cov_", covs[[v]]) := s[[v]]]
  stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
            !anyDuplicated(d[, .(id, task, profile)]), all(d$cov_female %in% c(NA, 0, 1)))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build("germany_politician.csv", c(yob = "birth_year", female = "female", education = "education",
      east_germany_F = "region_group", state_at_18 = "state_at_18", current_state = "current_state",
      birth_country = "birth_country", party_vote = "party_vote"), "brehm_2025_politicians_germany")
build("korea_politician.csv", c(yob = "birth_year", female = "female", education = "education",
      province = "province", political_ideology = "ideology", party_vote = "party_vote"), "brehm_2025_politicians_korea")
build("nk_politician.csv", c(yob = "birth_year", female = "female", education_nk = "education",
      province_birth = "province_birth", year_defection = "year_defection", year_arrived_sk = "year_arrived_sk",
      years_in_nk = "years_in_nk", years_in_sk = "years_in_sk", current_residence = "current_residence"),
      "brehm_2025_politicians_nk_migrants")
