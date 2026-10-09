##Candidate-race vignette experiments (two studies, US) from
##Wu, J. D., & Huber, G. A. (2024). How and when candidate race affects inferences about ideology and
##group favoritism. Political Science Research and Methods. https://doi.org/10.1017/psrm.2024.50
##Replication data: Harvard Dataverse doi:10.7910/DVN/ECBIHS, CC0 1.0. Files read (Dataverse
##"original format"): study_1_raw.csv, study_2_raw.csv (Qualtrics exports; the README says respondent
##identifiers were removed; `rid` is already a row number). Read as text: READ.me, 1_clean_data.do,
##2_study1_analysis.do, 3_study2_analysis.do; the article and its Online Appendix (Cambridge
##supplementary docx: design, levels, randomization) were read for wording.
##Usage: Rscript wu_2024_candidate_race.R <dir holding study_1_raw.csv and study_2_raw.csv> <output dir>
##Two tables (different attribute sets, samples and outcomes): wu_2024_candidate_race_s1, _s2.
##
##STUDY 1 (Lucid Marketplace, spring 2021 per appendix / "early 2020" per article; 2,467 respondents
##in the export = the article's N; 128 answered no outcome and are dropped: 2,339): one text vignette per respondent (task = profile = 1): "[Name Withheld] is a
##[age] year old [race] [sex] who has served as a Democrat in the state legislature for the past 8
##years", then policy positions. Age 40-60, sex man/woman, race White/Black (equal probabilities).
##Two non-racial positions drawn from 4 issue areas (abortion, tax, health, environment; at most one
##per area, one of two positions each) and an affirmative-action position (none / 3 positions, each
##1/4); positions shown in random order (cattr_policya/b/c = display slots). Stored as one attr_ per
##issue: the displayed sentence (<li> tags stripped), "(not shown)" when the issue was not drawn
##(affirmative action "(not shown)" = the "(none)" condition); attrpos_<issue> = rank among the
##shown positions (an empty slot is skipped). Outcomes (article; options as text in the export, coded
##here as ordered integers in the order of the response scale):
##  rating_ideology / _econ / _social: candidate's overall / economic / social ideology, 1 = Extremely
##    Liberal .. 7 = Extremely Conservative (article: "7-point scale from Extremely Liberal (1) to
##    Extremely Conservative (7)").
##  rating_priority_<issue> (tax, jobs, health, environment, abortion, criminal justice reform, social
##    justice): 1 = Low priority, 2 = Moderate priority, 3 = High priority.
##  rating_fair_<group> (whites, blacks, asians, hispanics, republicans, democrats, men, women): "how
##    fair they believe the candidate will be to each of the following groups of Americans", 1 = Very
##    unfair .. 7 = Very fair.
##  The three predicted-policy items (TANF, minimum wage, reparations) are NOT kept: their wording is
##  not in the deposit or appendix and the TANF/reparations answer texts (Remove/Keep/Reduce; Cash /
##  Preferential treatment / No benefits) cannot be ordered without it.
##  Rows with no outcome answered (break-offs) are dropped.
##STUDY 2 (Lucid Marketplace, January 2022): 5 candidate vignettes per respondent ("Candidate #X",
##task = candidate number, profile = 1): "[NAME WITHHELD] is a [Age] year old Democratic [Race] [Sex]
##who [Experience]. This candidate is running in a district with the following characteristics: It is
##[W]% White, [B]% Black, [H]% Hispanic, [A]% Asian, and [O]% Other. In the 2020 presidential election,
##Democrat Joe Biden received [Vote Share]% of the district's votes. Additionally, this candidate has
##taken the following policy positions: [Policy A] [Policy B] [Policy C]". Race restricted (each
##respondent sees Black, White, Asian, Hispanic once and a fifth Black or White); district
##composition (7 fixed vectors) and Biden share (51-59%) drawn without replacement across the five
##profiles; experience 5 levels; policies as in Study 1 (health and affirmative-action wording differ;
##"End affirmative action ..."). attr_district = the composition sentence rebuilt from the five
##stored shares in the template's wording; attr_biden_share = the share followed by "%". CAUTION:
##the appendix lists the seven vectors as White, Black, Asian, Hispanic, Other (e.g. "23% White, 20%
##Black, 21% Asian, 31% Hispanic, 5% Other"), while the export's piped fields cattr<k>_hispa and
##cattr<k>_asian hold 21 and 31 for that vector. The sentence follows the export's field names
##(Hispanic = cattr_hispa); which number respondents saw next to "Hispanic" vs "Asian" cannot be
##confirmed from the deposit.
##Sample: the authors' pre-registered attention-check rule (1_clean_data.do: keep if acq_pass == 1 or
##acq_identity == "Because he left his ID"): 1,447 respondents (= article).
##Outcomes (labels in the export; wording in the article): rating_vote (vote likelihood; 1 = Very
##unlikely .. 5 = Very likely; wording not in the deposit), rating_ideology (1 = Extremely Liberal ..
##7 = Extremely Conservative; middle option "Moderate/Middle of the road"), rating_prioritize_<group>
##("If elected, how much do you think this candidate will prioritize the interests of the following
##groups in their district", 1 = None at all .. 5 = A great deal).
##Covariates (both): cov_birth_year (dem_birthyr; implausible values -> NA), cov_age (panel age),
##cov_gender (panel code 1 -> male, 2 -> female, from the authors' 1_clean_data.do), cov_region
##(panel code 1-4 -> Northeast/Midwest/South/West, from 1_clean_data.do), cov_employment, cov_race
##(answer text), cov_ideology (answer text), cov_vote20 (answer text), Study 1 cov_ideology_econ /
##_social, cov_vote16, cov_sr1..4 (racial resentment items, answer text), cov_overt_<trait>_<1-4> (1-7
##group ratings as stored); Study 2 cov_party_id (dem_pid), cov_party_strength_rep / _dem, cov_party
##_lean; panel codes kept as cov_hhi_code, cov_ethnicity_code, cov_hispanic_code, cov_education_code,
##cov_party_code (no codebook in the deposit). Dropped: free-text "_text" fields, display-order
##(_do_) variables, timers, attention items, progress, rid. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
strip <- function(x) trimws(gsub("</?li>", "", x))
issues <- c(abortion = "abortion", tax = "tax rate", health = "health|Obamacare", environment = "renewable",
            affirmative_action = "affirmative action")
put_policies <- function(d, slots) {
  for (iss in names(issues)) { d[, paste0("attr_", iss) := "(not shown)"]; d[, paste0("attrpos_", iss) := NA_integer_] }
  rank <- matrix(0L, nrow(d), length(slots)); shown <- sapply(slots, function(s) !is.na(s) & !(s %in% c("", "NA")))
  rank[] <- t(apply(shown, 1, cumsum)) * shown
  for (j in seq_along(slots)) for (iss in names(issues)) {
    w <- which(shown[, j] & grepl(issues[[iss]], slots[[j]]))
    stopifnot(all(d[[paste0("attr_", iss)]][w] == "(not shown)"))
    d[w, paste0("attr_", iss) := strip(slots[[j]][w])]; d[w, paste0("attrpos_", iss) := rank[w, j]]
  }
  stopifnot(all(rowSums(shown) == rowSums(sapply(names(issues), function(i) d[[paste0("attr_", i)]] != "(not shown)"))))
  d
}
code <- function(x, lv) { y <- match(x, lv); stopifnot(all(is.na(y) == (is.na(x) | x %in% c("", "NA")))); y }
nz <- function(x) { x <- trimws(as.character(x)); x[x %in% c("", "NA")] <- NA; x }
by_ok <- function(x) { y <- suppressWarnings(as.integer(x)); y[!(y %between% c(1900, 2010))] <- NA; y }
ideo <- c("Extremely Liberal", "Liberal", "Slightly Liberal", "Moderate", "Slightly Conservative", "Conservative", "Extremely Conservative")
lucid <- function(s) s[, .(cov_age = as.integer(age), cov_gender = c(`1` = "male", `2` = "female")[as.character(gender)],
  cov_region = c(`1` = "Northeast", `2` = "Midwest", `3` = "South", `4` = "West")[as.character(region)],
  cov_hhi_code = as.integer(hhi), cov_ethnicity_code = as.integer(ethnicity), cov_hispanic_code = as.integer(hispanic),
  cov_education_code = as.integer(education), cov_party_code = as.integer(political_party))]

## ---- Study 1
s <- fread(file.path(raw, "study_1_raw.csv"), colClasses = "character")
stopifnot(nrow(s) == 2467)
d <- s[, .(id = seq_len(.N), task = 1L, profile = 1L)]
d[, `:=`(attr_age = s$cattr_age, attr_sex = s$cattr_sex, attr_race = s$cattr_race)]
d <- put_policies(d, list(s$cattr_policya, s$cattr_policyb, s$cattr_policyc))
d[, `:=`(rating_ideology = code(s$cattr_ideo7, ideo), rating_ideology_econ = code(s$cattr_ideo_econ, ideo),
         rating_ideology_social = code(s$cattr_ideo_soc, ideo))]
pr <- c(tax = "tax", jobs = "job", health = "health", environment = "enviro", abortion = "abort", criminal_justice = "crim", social_justice = "sj")
for (p in names(pr)) d[, paste0("rating_priority_", p) := code(s[[paste0("cattr_priority_", pr[[p]])]], c("Low priority", "Moderate priority", "High priority"))]
fr <- c(whites = "whites", blacks = "blacks", asians = "asians", hispanics = "hispanics", republicans = "gop", democrats = "dem", men = "men", women = "women")
fair <- c("Very Unfair", "Unfair", "Somewhat Unfair", "Neutral", "Somewhat Fair", "Fair", "Very Fair")
for (g in names(fr)) d[, paste0("rating_fair_", g) := code(s[[paste0("cattr_fair_", fr[[g]])]], fair)]
cv <- cbind(s[, .(cov_birth_year = by_ok(dem_birthyr), cov_employment = nz(dem_emp), cov_race = nz(dem_race),
  cov_ideology = nz(dem_ideo), cov_ideology_econ = nz(dem_ideo_econ), cov_ideology_social = nz(dem_ideo_soc),
  cov_vote16 = nz(dem_vote16), cov_vote20 = nz(dem_vote20), cov_sr1 = nz(sr1), cov_sr2 = nz(sr2), cov_sr3 = nz(sr3), cov_sr4 = nz(sr4))],
  lucid(s))
for (tr in c("lazy", "unintel", "peaceful", "trust")) for (k in 1:4) cv[, paste0("cov_overt_", tr, "_", k) := suppressWarnings(as.integer(s[[paste0("overt_", tr, "_", k)]]))]
d <- cbind(d, cv)
rc <- grep("^rating", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..rc])) > 0]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wu_2024_candidate_race_s1.csv"))

## ---- Study 2
s <- fread(file.path(raw, "study_2_raw.csv"), colClasses = "character")
s <- s[acq_pass == "1" | acq_identity == "Because he left his ID"]
stopifnot(nrow(s) == 1447)
s[, id := seq_len(.N)]
ideo2 <- replace(ideo, 4, "Moderate/Middle of the road")
vote <- c("Very unlikely", "Somewhat unlikely", "Equally likely or unlikely", "Somewhat likely", "Very likely")
prio <- c("None at all", "A littlebit", "Somewhat", "A moderateamount", "A greatdeal")
grp <- c(whites = "whites", blacks = "blacks", asians = "asians", hispanics = "hispanics", republicans = "gop", democrats = "dem", men = "men", women = "women")
cv2 <- cbind(s[, .(id, cov_birth_year = by_ok(dem_birthyr), cov_employment = nz(dem_emp), cov_race = nz(dem_race),
  cov_party_id = nz(dem_pid), cov_party_strength_rep = nz(dem_pid_strongr), cov_party_strength_dem = nz(dem_pid_strongd),
  cov_party_lean = nz(dem_pid_lean), cov_ideology = nz(dem_ideo), cov_vote20 = nz(dem_vote20))], lucid(s))
d2 <- rbindlist(lapply(1:5, function(k) {
  g <- function(v) s[[sprintf("cattr%d_%s", k, v)]]
  x <- data.table(id = s$id, task = k, profile = 1L, attr_age = g("age"), attr_sex = g("sex"), attr_race = g("race"),
                  attr_experience = g("exp"),
                  attr_district = sprintf("It is %s%% White, %s%% Black, %s%% Hispanic, %s%% Asian, and %s%% Other.", g("white"), g("black"), g("hispa"), g("asian"), g("other")),
                  attr_biden_share = paste0(g("biden"), "%"))
  x <- put_policies(x, list(g("policya"), g("policyb"), g("policyc")))
  x[, rating_vote := code(s[[sprintf("cand%d_vote", k)]], vote)][, rating_ideology := code(s[[sprintf("cand%d_ideo", k)]], ideo2)]
  sfx <- if (k == 1) "" else paste0("_", k - 1)
  for (gg in names(grp)) x[, paste0("rating_prioritize_", gg) := code(s[[paste0("cattr_fair_", grp[[gg]], sfx)]], prio)]
  x
}))
stopifnot(d2[, all(c("Asian", "Black", "Hispanic", "White") %in% attr_race), id][, all(V1)])
d2 <- merge(d2, cv2, by = "id")
rc <- grep("^rating", names(d2), value = TRUE)
d2 <- d2[rowSums(!is.na(d2[, ..rc])) > 0]
for (v in grep("^attr_", names(d2), value = TRUE)) stopifnot(!anyNA(d2[[v]]), all(d2[[v]] != ""), !any(grepl("NA", d2[[v]])))
setorder(d2, id, task, profile)
fwrite(d2, file.path(out, "wu_2024_candidate_race_s2.csv"))
