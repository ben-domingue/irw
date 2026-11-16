##Gender x leadership style of a hypothetical candidate for chair / vice-chair of a municipal council (Japan), from the deposit
##"Gender and Presiding Roles in Legislatures: Discrepancies in Mass and Elite Perceptions from Parallel Survey Experiments"
##(Endo, Miwa, Nuku & Ono, Legislative Studies Quarterly; year taken as 2026 from the deposit date; no article DOI located 2026-11-10)
##(Harvard Dataverse doi:10.7910/DVN/LQPORZ, CC0 1.0).
##Files read: voter_data.tab, elite_data.tab, codebook.pdf (variable text and value labels, read with pdftotext), replication_code.R (read as text:
##recoding of voter gender, the elite council-code exclusion), blocking_data.tab (council-level blocking).
##Usage: Rscript endo_2026.R <dir holding the .tab files> <output dir>
##
##Factorial vignette experiment (presentation = text), one vignette per respondent, 2 x 2 between-subject: gender of the hypothetical council member
##(woman = 1 Female, 0 Male) x leadership style (agentic = 1 "Initiative-oriented (agentic)", 0 "Collaborative (communal)"). The deposit gives only these
##codebook descriptions, not the Japanese vignette wording, so the level text is the codebook's description (paraphrased from the codebook; "LABELS: paraphrase").
##Two parallel surveys with the same factors and outcomes but different respondents and question wording, so TWO TABLES (Ben's grouping rule: different populations
##and wording): endo_2026_presiding_voters (4,743 Japanese voters, all with outcomes; they judge how the council would see the person) and endo_2026_presiding_elites (7,386
##municipal council members with an outcome, of 7,702 in the file; they judge their own support). One row per respondent: id = row number (no respondent id in the file; rows were randomly ordered by the
##depositors), task = profile = 1 (inferred, one vignette per respondent).
##Outcomes, the same four on the same vignette, 4-point scales, 4 = more favourable (stored as recorded): rating_chair_support (voters: expected support within the council for the
##person as chair; elites: own support), rating_chair_success (managing the council effectively as chair), rating_vice_support (as vice-chair), rating_vice_success. Codebook
##wording: voters chair.support "If this person were nominated as a candidate for the chair of your municipal council, and setting aside [his/her] party/group
##affiliation, how likely do you think this person would be supported within the council?" (1 I think he/she would not be supported ... 4 I think he/she would be supported);
##elites "If this person were nominated as a candidate for chair of your municipal council ... how likely would you be to support this person?" (1 I would not support him/her ...
##4 I would support him/her); success items: 1 he/she would not be able to manage the council effectively ... 4 he/she would be able to. Full wording in design_outcomes.
##Elite outcome missing: 336-374 elites left single outcomes blank; respondents are kept when at least one of the four outcomes is present (7,386 of the 7,702
##rows; 316 elites answered none and are omitted as "no outcome"), with the blank outcomes as NA. Randomization: elite vignettes were assigned at the council level in blocks (multivariate continuous blocking; blocking_data.tab; 699 of 716
##identified councils have a single vignette across their respondents, 17 have two): cov_council_code and cov_block keep this structure (999 = unknown -> NA). Voter
##assignment is individual (cell sizes 1,185-1,187).
##Authors' analysis sample: the main tables use all respondents with an outcome; a robustness analysis drops elites with unknown council (code == 999, about half of the elites);
##no respondent is dropped here (reproduce with cov_council_code non-missing). The voter manipulation check is kept as cov_manipulation_check (answer text).
##Covariates, voters: cov_gender (gender code 1 -> male, 2 -> female per the authors' code, which treats 2 as woman and 3 as NA; code 3 -> NA; the codebook lists R.woman for the voter file but
##the file holds `gender`), cov_age (years), cov_prefecture (codebook list of 47 prefectures), cov_manipulation_check ("What was the gender of the council member you just saw?": Male /
##Female / I do not remember), cov_hostile_sexism_1..4 (agree codes 1 Strongly agree ... 6 Strongly disagree, as recorded). Elites: cov_gender (R.woman 0 man, 1 woman), cov_age_group
##(coarsened bands from the codebook), cov_tenure (years in office, coarsened bands), cov_effort / cov_housework / cov_scrutiny (1 Strongly agree ... 6 Strongly disagree, 7 I do not know,
##codes as recorded), cov_council_code, cov_block. No weights. PII FOUND: none (age and tenure of elites are coarsened by the depositors; municipality codes are anonymised).
##Respondent count vs paper: not checked (paper not located); the replication code's count of elites with at least one valid outcome is computed below and printed.
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
pref <- c("Hokkaido","Aomori","Iwate","Miyagi","Akita","Yamagata","Fukushima","Ibaraki","Tochigi","Gunma","Saitama","Chiba","Tokyo","Kanagawa","Niigata","Toyama","Ishikawa","Fukui","Yamanashi","Nagano","Gifu","Shizuoka","Aichi","Mie","Shiga","Kyoto","Osaka","Hyogo","Nara","Wakayama","Tottori","Shimane","Okayama","Hiroshima","Yamaguchi","Tokushima","Kagawa","Ehime","Kochi","Fukuoka","Saga","Nagasaki","Kumamoto","Oita","Miyazaki","Kagoshima","Okinawa")
common <- function(d) {
  d[, `:=`(id = .I, task = 1L, profile = 1L,
           attr_gender = fifelse(woman == 1, "Female", "Male"),
           attr_leadership_style = fifelse(agentic == 1, "Initiative-oriented (agentic)", "Collaborative (communal)"),
           rating_chair_support = as.integer(chair.support), rating_chair_success = as.integer(chair.success),
           rating_vice_support = as.integer(vice.support), rating_vice_success = as.integer(vice.success))]
  stopifnot(d[, all(woman %in% 0:1)], d[, all(agentic %in% 0:1)])
  d[!(is.na(rating_chair_support) & is.na(rating_chair_success) & is.na(rating_vice_support) & is.na(rating_vice_success))]
}
fin <- function(d, nm) {
  setorder(d, id, task, profile); fwrite(d, file.path(out, nm)); cat(nm, nrow(d), d[, uniqueN(id)], "\n")
}
oc <- c("rating_chair_support", "rating_chair_success", "rating_vice_support", "rating_vice_success")
# voters
v <- fread(file.path(raw, "voter_data.tab")); stopifnot(nrow(v) == 4743)
v <- common(v)
v[, `:=`(cov_gender = fcase(gender == 1, "male", gender == 2, "female", default = NA_character_), cov_age = as.integer(age), cov_prefecture = pref[prefecture],
         cov_manipulation_check = c("Male", "Female", "I do not remember")[manipulation],
         cov_hostile_sexism_1 = sexism.1, cov_hostile_sexism_2 = sexism.2, cov_hostile_sexism_3 = sexism.3, cov_hostile_sexism_4 = sexism.4)]
fin(v[, c("id", "task", "profile", "attr_gender", "attr_leadership_style", oc, grep("^cov_", names(v), value = TRUE)), with = FALSE], "endo_2026_presiding_voters.csv")
# elites
e <- fread(file.path(raw, "elite_data.tab")); stopifnot(nrow(e) == 7702)
cat("elites with at least one outcome:", nrow(common(copy(e))), "\n")
e <- common(e)
ag <- c("20s or 30s", "40s", "50s", "60s", "70s or older"); tn <- c("Less than 5 years", "5-9 years", "10-19 years", "20-29 years", "30 or more years")
e[, `:=`(cov_gender = fcase(R.woman == 0, "male", R.woman == 1, "female", default = NA_character_), cov_age_group = ag[age], cov_tenure = tn[tenure],
         cov_effort = effort, cov_housework = housework, cov_scrutiny = scrutiny,
         cov_council_code = fifelse(code == 999L, NA_integer_, as.integer(code)), cov_block = fifelse(cluster == 999L, NA_integer_, as.integer(cluster)))]
fin(e[, c("id", "task", "profile", "attr_gender", "attr_leadership_style", oc, grep("^cov_", names(e), value = TRUE)), with = FALSE], "endo_2026_presiding_elites.csv")
