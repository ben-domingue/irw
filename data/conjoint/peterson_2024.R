##Economic-statecraft proposal vignette conjoint (US) from
##Peterson, T. M., & Miller, S. M. (2024). Contextualizing individual attitudes on economic
##statecraft. Foreign Policy Analysis, 20(3), orae016. https://doi.org/10.1093/fpa/orae016
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z85LLW, CC0 1.0. Files read (Qualtrics CSV
##exports, Dataverse "original format"): "Conjoint - Statecraft_competence - {1,2,3}_April 22,
##2021_22.csv" (saved as exp1.csv, exp2.csv, exp3.csv). Read as text: exp{1,2,3}_coding.R,
##Replication_file.R. No questionnaire or codebook ships; wording comes from the Qualtrics
##question-text header row of each export.
##Usage: Rscript peterson_2024.R <dir holding exp1.csv exp2.csv exp3.csv> <output dir>
##
##Three experiments in separate US online samples (export files dated 22 April 2021; vendor not
##named in the deposit), one hypothetical US policy proposal per respondent (task = profile = 1).
##ONE table with trial_experiment (1-3): the authors stack the three files and estimate all
##models on the pooled data (Replication_file.R `combo`), and the attribute structure is the same;
##the experiments differ in the target countries and in the second bad behaviour:
##  exp 1: China, India, North Korea, Pakistan, Russia; democracy repression or nuclear weapons
##  exp 2: Cuba, Iran, Sudan, Syria; democracy repression or state sponsorship of terrorism
##  exp 3: Afghanistan, Colombia, Mexico, Morocco, Myanmar; democracy repression or narcotics
##Displayed vignette (Qualtrics template): "The United States is considering taking action in
##[country] following reports of [behaviour]. [country] [background]." then a table "Country and
##Proposal Information": "Proposal: [policy] [country]" and four rows whose ORDER was randomized
##(c1_attrib1..4_name): Effect on economy, Outcome of Inaction, US Rationale for Proposal,
##Proposal Author. attr_* hold the displayed text: attr_behaviour (the phrase after "following
##reports of", from the question header of the block the respondent answered), attr_country,
##attr_background (countrybackground), attr_policy (policy; the country name followed it on
##screen), attr_economy / attr_inaction / attr_rationale / attr_author (the composed row text, as
##saved); attrpos_* give their row (1-4). Several texts name the country, and background,
##rationale and inaction text depend on the behaviour and the policy (restrictions = yes).
##Outcomes: six statements rated on a 0-100 slider (anchors not in the export; stored as
##answered); each respondent answered the block for their behaviour (exactly one block checked):
##  rating "I support the proposed policy"; rating_us_interests "This policy advances US
##  interests"; rating_too_costly "This policy is too costly to the US" (higher = more costly);
##  rating_effective "This policy will be effective in changing [country]'s behavior";
##  rating_us_strength "This policy demonstrates US strength"; rating_message "This policy sends a
##  strong message to the international community about US commitment to [democracy promotion /
##  end nuclear proliferation / end state sponsorship of terrorism / end narcotics trafficking]".
##Dropped: 5 respondents with no saved attributes (1, 1, 3 per experiment) and 39 respondents with
##no rating at all (7,392 exported -> 7,348). Covariates: cov_age (years), cov_party_id (Q46 answer text), cov_party_strength
##_dem (Q48), cov_party_strength_rep (Q50), cov_party_lean (Q52), cov_urban_rural (Q118), all as
##answer text; cov_fav_<country> (Q25_1..19, favourability of 19 countries, answer text);
##cov_gender_code, cov_ethnicity_code, cov_hispanic_code, cov_education_code keep the panel's
##numeric codes (no codebook in the deposit). Blank answers are NA. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
favn <- c("uk", "canada", "india", "china", "egypt", "south_africa", "russia", "north_korea", "argentina", "pakistan",
          "iran", "syria", "cuba", "sudan", "mexico", "colombia", "myanmar", "afghanistan", "morocco")
outc <- c("I support the proposed policy" = "rating", "This policy advances US interests" = "rating_us_interests",
          "This policy is too costly to the US" = "rating_too_costly", "This policy will be effective" = "rating_effective",
          "This policy demonstrates US strength" = "rating_us_strength", "This policy sends a strong message" = "rating_message")
anames <- c("Effect on economy" = "economy", "Outcome of Inaction" = "inaction", "US Rationale for Proposal" = "rationale",
            "Proposal Author" = "author")
nz <- function(x) { x <- trimws(x); x[x == ""] <- NA; x }
one <- function(k) {
  hdr <- unlist(fread(file.path(raw, sprintf("exp%d.csv", k)), nrows = 1, header = TRUE))
  s <- fread(file.path(raw, sprintf("exp%d.csv", k)), colClasses = "character")[-(1:2)]
  s[, rid := .I]
  s <- s[c1_attrib1_name != ""]
  qc <- grep("^1_Q", names(s), value = TRUE)
  blk <- sub("^1_(Q[0-9]+)_.*", "\\1", qc)
  stmt <- sub(".* - ", "", hdr[qc])
  beh <- sub("\\. \\[Field-country1\\].*", "", sub(".*following reports of ", "", hdr[qc]))
  oc <- sapply(stmt, function(z) outc[startsWith(z, names(outc))][1])
  stopifnot(!anyNA(oc), uniqueN(blk) == 2)
  ans <- sapply(unique(blk), function(b) rowSums(s[, lapply(.SD, function(z) z != ""), .SDcols = qc[blk == b]]) > 0)
  stopifnot(all(rowSums(ans) <= 1))
  s <- s[rowSums(ans) == 1]; ans <- ans[rowSums(ans) == 1, , drop = FALSE]
  b <- unique(blk)[max.col(ans)]
  d <- data.table(rid = s$rid, trial_experiment = k, attr_behaviour = beh[match(b, blk)])
  for (o in outc) d[, (o) := NA_integer_]
  for (bb in unique(blk)) for (j in which(blk == bb)) {
    w <- which(b == bb); d[w, (oc[j]) := as.integer(s[[qc[j]]][w])]
  }
  d[, `:=`(attr_country = s$country1, attr_background = s$countrybackground, attr_policy = s$policy)]
  for (p in 1:4) {
    nm <- anames[s[[paste0("c1_attrib", p, "_name")]]]; stopifnot(!anyNA(nm))
    for (an in anames) {
      w <- which(nm == an)
      d[w, paste0("attr_", an) := s[[paste0("c1_attrib", p)]][w]]
      d[w, paste0("attrpos_", an) := p]
    }
  }
  d[, `:=`(cov_age = as.integer(s$age), cov_party_id = nz(s$Q46), cov_party_strength_dem = nz(s$Q48),
           cov_party_strength_rep = nz(s$Q50), cov_party_lean = nz(s$Q52), cov_urban_rural = nz(s$Q118),
           cov_gender_code = as.integer(s$gender), cov_ethnicity_code = as.integer(s$ethnicity),
           cov_hispanic_code = as.integer(s$hispanic), cov_education_code = as.integer(s$education))]
  for (i in 1:19) d[, paste0("cov_fav_", favn[i]) := nz(s[[i]])]
  d
}
d <- rbindlist(lapply(1:3, one), use.names = TRUE)
d <- d[!(is.na(rating) & is.na(rating_us_interests) & is.na(rating_too_costly) & is.na(rating_effective) &
         is.na(rating_us_strength) & is.na(rating_message))]
d[, id := .I][, `:=`(task = 1L, profile = 1L)][, rid := NULL]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
stopifnot(all(unlist(d[, .SD, .SDcols = patterns("^rating")]) %between% c(0, 100), na.rm = TRUE))
setcolorder(d, c("id", "task", "profile", "trial_experiment", unname(outc)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "peterson_2024_economic_statecraft.csv"))
