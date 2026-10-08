##Filler-attribute (survey satisficing) conjoints, stage 2 of both studies, from
##Bansak, K., Hainmueller, J., Hopkins, D. J., & Yamamoto, T. (2019). Beyond the breaking
##point? Survey satisficing in conjoint experiments. Political Science Research and Methods,
##9(1), 53-71 (2021 issue; online May 2019). https://doi.org/10.1017/psrm.2019.13
##Replication data: Harvard Dataverse doi:10.7910/DVN/JYC2TH, CC0 1.0. Files read (inside
##replication_materials.zip): data/cand_s2_SSI.csv, data/hotel_s2.csv. Also read: readme.txt
##(deposit codebook), the helper and figure scripts as text (not run), and the SSRN preprint
##(abstract 2959146, via MIT DSpace) for the design, sample dates and Figure 3 wording.
##Usage: Rscript bansak_2019.R <dir holding the two csv files> <output dir>
##
##TWO TABLES (separate experiments with different attribute sets; the authors analyse each
##sample separately):
##  bansak_2019_satisficing_candidates_ssi: Study 1, US Senate candidates, SSI sample,
##    Nov 30 - Dec 8 2016, 2,786 respondents (article: 2,786).
##  bansak_2019_satisficing_hotels: Study 2, hotel rooms, MTurk, March 6-7 2017, 3,307
##    respondents (article: 3,307).
##NOT BUILT: cand_s2_MTurk.csv (Study 1 on MTurk, 4,097 respondents in 3 waves): every
##attribute is a numeric code and neither the deposit nor the code maps codes to level text
##(the appendix lists levels, but not the code order) -> held (J4). Stage 1 files
##(cand_s1.csv, hotel_s1.csv) are a guessing task with no profile evaluation outcome.
##Design: 15 tasks x 2 profiles. `profile` is A1, A2, ..., O2: the letter is the task (A = 1st
##of 15, as on screen "(1/15)"), the digit the profile (1 = Candidate/left column A). Recorded.
##Each respondent was randomly assigned a number of filler attributes (`condition`; SSI 0, 1, 2,
##4, 6, 8, 10, 15, 25, 35 [the article omits 1; 287 respondents have it]; hotels 0-6, 8, 10,
##14, 18) fixed for the whole survey; the
##fillers shown were drawn at random from the pool, and the four core attributes were
##"randomly interspersed" with them (attribute order randomized, not recorded).
##Core attributes: candidates - age (42/54/72), party, position on health care, position on
##same-sex marriage; hotels - floor, view, bedroom furniture, in-room internet.
##Filler attributes: per the readme, value 0 = the filler was not shown to this respondent
##and NA = not in the respondent's pool; both are stored as "(not shown)". Column names are
##the deposit's abbreviations (cdogm -> attr_dog); display names are in the article's
##Tables A.1/A.3/A.8 (e.g. attr_dog = "Family Dog's Name", attr_pillows = "Material in
##bed pillows"). Numeric fillers (attr_vote = age when first voted, attr_thermo = default
##thermostat temperature F) are stored as displayed text. cemailm ("Prefers to Respond to
##E-mail in": Morning/Afternoon/Evening) becomes attr_email_time_of_day (no address in it;
##the validator's PII hint on this name is a false alarm).
##Outcomes (same tasks, one table each):
##  choice = pref. Candidates: "Which candidate would you prefer to vote for?" Candidate A /
##           Candidate B (Figure 3). Hotels: forced choice between the two rooms (wording not
##           shown; paraphrase). Forced choice, one per task (checked).
##  rating = rate, 1-7. Candidates: "On a scale from 1 to 7, where 1 indicates that you
##           definitely would NOT vote for the candidate and 7 indicates that you definitely
##           would vote for the candidate, how would you rate each of the candidates
##           described above?" Hotels: 1-7 rating of each room (wording not shown).
##trial_n_fillers = condition (number of filler attributes shown; checked against the
##non-"(not shown)" fillers in every row).
##Covariates. Text mappings from the deposit readme.txt (r_ variable list): cov_gender
##(r_gender 1 = male, 2 = female), cov_age (r_age, years), cov_education (r_educ, readme text:
##"less than high school", "high school", "some college", "2-year college degree", "4-year
##college degree", "graduate degree"), cov_party_id (r_party: 1 Republican, 2 Democrat,
##3 Independent, 4 Other). Kept as codes: cov_income (1-7, readme brackets $0-24,999 ...
##$200,000+), cov_party_strength (readme says 1 strong / 2 not very strong, but the data hold
##0/1: stored as in the data), cov_lean (-1 Dem, 0 neither, 1 Rep). No survey weight,
##attention check or duration in the deposit. No repeated task.
##Dropped: r_id (Qualtrics ResponseId; re-keyed to integers in file order), the authors'
##recoded concordance variables (cpartyp, cmarriagep, chealthcarep, cagep) and `partisan`.
##Spot check: hotels, condition 0, lm(pref ~ view + floor + furniture + internet) clustered
##by respondent gives ocean view +0.175 and paid internet -0.303 (article 0.175, -0.303).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
NS <- "(not shown)"
ren <- function(v) { x <- sub("^c(.*)m$", "\\1", v); if (x == "email") "email_time_of_day" else x }
build <- function(f, core, n_id, tab) {
  s <- fread(file.path(raw, f), colClasses = "character")
  stopifnot(uniqueN(s$r_id) == n_id, s[, .N, r_id][, all(N == 30)])
  fill <- setdiff(names(s)[(which(names(s) == "rate") + 1):ncol(s)], c("partisan", "cpartyp", "cmarriagep", "chealthcarep", "cagep", "wave"))
  stopifnot(all(grepl("^c.*m$", fill)))
  tl <- substr(s$profile, 1, 1); stopifnot(all(tl %in% LETTERS[1:15]), all(substr(s$profile, 2, 2) %in% c("1", "2")))
  d <- data.table(id = match(s$r_id, unique(s$r_id)), task = match(tl, LETTERS), profile = as.integer(substr(s$profile, 2, 2)),
                  choice = as.integer(s$pref), rating = as.integer(s$rate))
  for (v in names(core)) { x <- s[[v]]; stopifnot(!anyNA(x), all(x != ""), all(x != "0")); d[, paste0("attr_", core[[v]]) := x] }
  for (v in fill) {
    x <- s[[v]]; x[is.na(x) | x %in% c("", "NA", "0")] <- NS
    d[, paste0("attr_", ren(v)) := x]
  }
  d[, trial_n_fillers := as.integer(s$condition)]
  fa <- paste0("attr_", sapply(fill, ren))
  stopifnot(rowSums(d[, ..fa] != NS) == d$trial_n_fillers)
  lab <- function(x, v) { y <- unname(v[x]); stopifnot(!anyNA(y) | is.na(x)); y }
  ed <- c("1" = "less than high school", "2" = "high school", "3" = "some college", "4" = "2-year college degree",
          "5" = "4-year college degree", "6" = "graduate degree")
  d[, `:=`(cov_gender = lab(s$r_gender, c("1" = "male", "2" = "female")), cov_age = as.integer(s$r_age),
           cov_education = lab(s$r_educ, ed), cov_income = as.integer(s$r_income),
           cov_party_id = lab(s$r_party, c("1" = "Republican", "2" = "Democrat", "3" = "Independent", "4" = "Other")),
           cov_party_strength = as.integer(s$r_strength), cov_lean = as.integer(s$r_lean))]
  stopifnot(!anyNA(d$choice), !anyNA(d$rating), d[, all(rating %in% 1:7)], !anyDuplicated(d[, .(id, task, profile)]),
            d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
build("cand_s2_SSI.csv", c(cage = "age", cparty = "party", chealthcare = "health_care", cmarriage = "same_sex_marriage"),
      2786, "bansak_2019_satisficing_candidates_ssi")
build("hotel_s2.csv", c(cfloor = "floor", cview = "view", cfurniture = "furniture", cinternet = "internet"),
      3307, "bansak_2019_satisficing_hotels")
