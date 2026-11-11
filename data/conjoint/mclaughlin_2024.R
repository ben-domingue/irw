##Veteran candidate vignettes (US): candidate party x veteran status x issue discussed, two experiments, from
##McLaughlin, P. T., Geras, M. J., & Rhinehart, S. (2024). Supporting veterans: Source cues, issue ownership, and the
##electoral benefits of military service. Political Behavior, 46(1), 307-330. https://doi.org/10.1007/s11109-022-09827-w
##(online 2022; paywalled, not read).
##Replication data: Harvard Dataverse doi:10.7910/DVN/AINILA, CC0 1.0 (no terms, no restricted files). Files read:
##Vets_Experiment_1_Data.RData (datafile 6544130, object dsorg, 1,914 rows), Vets_Experiment_2_Data.RData (6544133,
##2,276 rows); Vets_Experiment_1_Code.Rmd and Vets_Experiment_2_Code.Rmd read as text (treatment and outcome coding).
##Usage: Rscript mclaughlin_2024.R <dir holding the two .RData files> <output dir>
##
##Design: one text vignette per respondent (task = 1, profile = 1), a candidate described by party, veteran status and
##the issue the candidate discusses. Qualtrics randomizer: FL_66_DO / FL_82_DO picks the party block (Dem_Vet_* or
##Rep_Vet_*), whose *_DO column names the vignette block, e.g. "vet_crime" = veteran candidate discussing crime.
##Experiment 1 (table mclaughlin_2024_veteran_candidates_s1): 2 parties x 2 (vet/nonvet) x 2 issues (crime/ns).
##Experiment 2 (table mclaughlin_2024_veteran_candidates_s2): 2 parties x 2 x 3 issues (deficit/ns/poverty). Different
##issue sets and separate fieldings -> separate tables; the authors analyse them separately.
##CODED ATTRIBUTES (#3474). The vignette text is not deposited and the article is paywalled, so all three attributes keep
##the authors' Qualtrics block codes, as deposited: attr_party_code = Dem / Rep (block Dem_Vet_* / Rep_Vet_*; the Rmd
##codes these "dem"/"rep" = Democratic / Republican candidate), attr_veteran_code = vet / nonvet (Rmd exp 2:
##"veteran" / "nonveteran"), attr_issue_code = crime / ns (exp 1), deficit / ns / poverty (exp 2) (Rmd exp 2:
##"deficit", "nat_sec", "poverty"; ns = national security/defense). The attribute identities are the authors' own (Rmd
##treatment_vet_status / treatment_issue / candidate_party); what each block's text said is unknown.
##Outcomes (wording NOT deposited; the Dem and Rep branches store the same questions in parallel columns, coalesced as
##the authors do): rating_therm = feeling thermometer toward the candidate, 0-100 (the Rmd plots it as "Mean Feeling
##Thermometer Rating"; higher = warmer by the thermometer convention; anchors unknown). rating_defense_own (issue_own_1,
##"National Defense Issue Ownership" in the Rmd), rating_patriotism (traits_1), rating_courage (traits_2): 0-10, the
##authors' own mapping of these sub-items; higher = more (the authors read higher means as more ownership/trait, and
##veteran profiles score higher on patriotism and courage as the paper reports); anchors unknown. rating_vote: answer
##text Extremely unlikely .. Extremely likely stored 1-7 (1 = Extremely unlikely, 4 = Neither likely nor unlikely,
##7 = Extremely likely); rating_cand_ideology: perceived candidate ideology, answer text stored 1-7 (1 = Very liberal,
##2 Liberal, 3 Somewhat liberal, 4 Middle of the road, 5 Somewhat conservative, 6 Conservative, 7 Very conservative).
##Dropped outcomes: traits_3/traits_4 (Empathetic / Intelligent in an unknown order) and issue_own_2..6 (Immigration,
##Crime, Healthcare, The Economy, Education in an unknown order): no source maps item number to trait/issue.
##Rows: consenting respondents with a vignette block and at least one kept outcome (a few answered later questions but
##skipped the thermometer; kept, as the batch-13 ruling keeps every respondent with an outcome; the authors' exp 2
##code drops therm NA: reproduce with !is.na(rating_therm)). The authors' exp 1 analysis sample also keeps only
##respondents who passed the attention check (atten = "Kansas"); NOT applied here (Ben 2026-11-10): reproduce with
##cov_attention_pass == 1. Exp 2 has no such filter (attention_1/attention_2 are constant pre-screen answers; dropped).
##Covariates: exp 1 cov_gender (self-report "woman": Man/Woman/Non-binary -> male/female/other, Prefer not to say -> NA;
##the panel's 1/2 gender column is dropped as a duplicate), cov_education (answer text); exp 2 cov_gender (gender 1 =
##Man, 2 = Woman per the authors' Rmd), cov_education_code (1-8 plus -3105, unlabelled; the Rmd collapses 3/4 and
##7/8). Both: cov_age, cov_race (answer text, multi-select comma-joined), cov_ideology (7-point text), cov_income
##(bracket text), cov_party_id (party question text; independents' lean in cov_party_lean), cov_region (1 Northeast,
##2 Midwest, 3 South, 4 West per the Rmd comment). Exp 1 also cov_religion (attendance text), cov_military (personal
##/ family service, multi-select text), cov_issue_rank_defense (issue_ranking_1, renamed national_security by the
##authors, 1-10). Blank strings -> NA. No respondent IDs, IPs or free text in the deposit; id = row number.
##No survey weight. Randomization: Qualtrics randomizer blocks (*_DO columns); settings not documented, full factorial
##observed at near-equal cell counts.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(f) { e <- new.env(); n <- load(file.path(raw, f), envir = e); stopifnot(n == "dsorg"); as.data.table(e$dsorg) }
bl <- function(x) { x <- as.character(x); x[!is.na(x) & trimws(x) == ""] <- NA_character_; x }
co <- function(x, y) fcoalesce(bl(x), bl(y))
coi <- function(x, y) fcoalesce(as.integer(x), as.integer(y))
vl <- c("Extremely unlikely", "Moderately unlikely", "Slightly unlikely", "Neither likely nor unlikely",
        "Slightly likely", "Moderately likely", "Extremely likely")
il <- c("Very liberal", "Liberal", "Somewhat liberal", "Middle of the road", "Somewhat conservative", "Conservative",
        "Very conservative")
ordn <- function(x, lv) { x <- bl(x); stopifnot(all(is.na(x) | x %in% lv)); match(x, lv) }
regn <- c("Northeast", "Midwest", "South", "West")
build <- function(k, flv, dem_do, rep_do, issues, sfx) {
  k <- k[consent == "I agree to participate"]
  blk <- co(sub("\\|.*$", "", k[[dem_do]]), sub("\\|.*$", "", k[[rep_do]]))
  blk <- sub("^d_", "", blk)
  pty <- fifelse(!is.na(bl(k[[dem_do]])), "Dem", fifelse(!is.na(bl(k[[rep_do]])), "Rep", NA_character_))
  stopifnot(all(is.na(bl(k[[dem_do]])) | is.na(bl(k[[rep_do]]))),
            all(pty[!is.na(pty)] == c(Dem = "Dem", Rep = "Rep")[sub("_Vet_.*", "", bl(k[[flv]])[!is.na(pty)])]))
  k[, `:=`(blk = blk, pty = pty)]
  k[, `:=`(vet = sub("_.*$", "", blk), iss = sub("^[^_]*_", "", blk))]
  stopifnot(all(is.na(k$blk) | (k$vet %in% c("vet", "nonvet") & k$iss %in% issues)))
  k
}
# ---- experiment 1
k <- ld("Vets_Experiment_1_Data.RData")
k <- build(k, "FL_66_DO", "Dem_Vet_Experiment_DO", "Rep_Vet_Experiment_DO", c("crime", "ns"))
k[, therm := coi(therm_1, therm_1_d)]
stopifnot(k[is.na(blk), all(is.na(therm))])
k <- k[!is.na(blk)]
g <- bl(k$woman)
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating_therm = k$therm, rating_defense_own = coi(k$issue_own_1, k$issue_own_1_d),
  rating_patriotism = coi(k$traits_1, k$traits_1_d), rating_courage = coi(k$traits_2, k$traits_2_d),
  rating_vote = ordn(co(k$vote, k$vote_d), vl), rating_cand_ideology = ordn(co(k$cand_ideology, k$cand_ideology_d), il),
  attr_party_code = k$pty, attr_veteran_code = k$vet, attr_issue_code = k$iss,
  cov_gender = fcase(g == "Man", "male", g == "Woman", "female", g == "Non-binary", "other", default = NA_character_),
  cov_age = as.integer(k$age), cov_education = bl(k$education), cov_race = bl(k$race), cov_ideology = bl(k$ideology),
  cov_income = bl(k$income), cov_party_id = bl(k$party), cov_party_lean = bl(k$independent),
  cov_region = regn[as.integer(k$region)], cov_religion = bl(k$religion), cov_military = bl(k$military_personal),
  cov_issue_rank_defense = as.integer(k$issue_ranking_1))
at <- co(k$atten, k$atten_d); stopifnot(all(is.na(at) | at %in% c("Kansas", "Florida", "Maine", "Oregon")))
d[, cov_attention_pass := fifelse(is.na(at), NA_integer_, as.integer(at == "Kansas"))]
stopifnot(all(na.omit(d$rating_therm) %between% c(0, 100)), all(na.omit(c(d$rating_defense_own, d$rating_patriotism, d$rating_courage)) %between% c(0, 10)))
d <- d[rowSums(!is.na(d[, .SD, .SDcols = patterns("^rating_")])) > 0L]; d[, id := seq_len(.N)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mclaughlin_2024_veteran_candidates_s1.csv"))
cat("s1", nrow(d), "\n"); print(d[, .N, .(attr_party_code, attr_veteran_code, attr_issue_code)])
# ---- experiment 2
k <- ld("Vets_Experiment_2_Data.RData")
k <- build(k, "FL_82_DO", "Dem_Vet_Exp_DO", "Rep_Vet_Exp_DO", c("deficit", "ns", "poverty"))
k[, therm := coi(therm_1, d_therm_1)]
stopifnot(k[is.na(blk), all(is.na(therm))])
k <- k[!is.na(blk)]
gg <- as.integer(k$gender)
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating_therm = k$therm, rating_defense_own = coi(k$issue_own_1, k$d_issue_own_1),
  rating_patriotism = coi(k$traits_1, k$d_traits_1), rating_courage = coi(k$traits_2, k$d_traits_2),
  rating_vote = ordn(co(k$vote, k$d_vote), vl), rating_cand_ideology = ordn(co(k$cand_ideology, k$d_cand_ideology), il),
  attr_party_code = k$pty, attr_veteran_code = k$vet, attr_issue_code = k$iss,
  cov_gender = fcase(gg == 1L, "male", gg == 2L, "female", default = NA_character_),
  cov_age = as.integer(k$age), cov_education_code = as.integer(k$education), cov_race = bl(k$race), cov_ideology = bl(k$ideo),
  cov_income = bl(k$income), cov_party_id = bl(k$party), cov_party_lean = bl(k$inds_party),
  cov_region = regn[as.integer(k$region)])
stopifnot(all(na.omit(d$rating_therm) %between% c(0, 100)), all(na.omit(c(d$rating_defense_own, d$rating_patriotism, d$rating_courage)) %between% c(0, 10)))
d <- d[rowSums(!is.na(d[, .SD, .SDcols = patterns("^rating_")])) > 0L]; d[, id := seq_len(.N)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mclaughlin_2024_veteran_candidates_s2.csv"))
cat("s2", nrow(d), "\n"); print(d[, .N, .(attr_party_code, attr_veteran_code, attr_issue_code)])
