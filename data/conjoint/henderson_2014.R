##Candidate-profile party-guessing experiment from
##Henderson, J. (2017). CCES 2014, Team Module of Yale University (JAH) [Data set].
##Harvard Dataverse. https://doi.org/10.7910/DVN/WL6VCW (CC0 1.0; no article named in the deposit)
##Files read: CCES14_JAH_OUTPUT_Aug2015_vm.sav (Dataverse "original format" download; value
##labels), CCES14_JAH.docx (pre-election questionnaire, read as text),
##CCES14_JAH_OUTPUT_Aug2015_vm_CODEBOOK.txt.
##Usage: Rscript henderson_2014.R <dir holding data.sav> <output dir>
##
##Cooperative Congressional Election Study 2014, Yale team module (YouGov, US, 1,000
##respondents, pre-election wave). Intro: "On the next few screens, you will be shown
##information about randomly selected candidates for political office ... They were asked for
##their top 3 issue priorities (in order) and about their background. We want to see how well
##people do at guessing the political parties of the candidates with just these pieces of
##information." Four candidates, one per screen ("Candidate k of 4", $cand<k>table), so one
##profile per task. Attributes (cand<k>*): gender, family, religion, military, job, issue 1-3.
##Level text = the .sav value labels; the HTML profile table itself is not deposited, so the
##exact on-screen layout and labels around the levels are unknown. Issues 1-3 are always
##three different issues (no repeats in 4,000 profiles; no rule documented). No source states
##the randomization probabilities.
##Outcomes (questionnaire JAH373-376 a/b/c):
##  rating_party = "If you had to guess, do you think this candidate is a Democrat or
##                  Republican?" 1 Democrat, 2 Republican (a guess about each profile, not a pick
##                  among profiles, so a rating; codes kept).
##  rating_sure  = "How sure are you about the candidate's party?" 1 Very sure .. 4 Very unsure
##                  (higher = less sure; codes kept).
##  rating       = "How favorably or unfavorably do you feel toward this candidate?" slider 0 Very
##                  Unfavorable .. 10 Very Favorable, with a "Not sure" box (code 997, about 19% of
##                  answers): stored NA, like Skipped (998) / Not Asked (999).
##Skipped/Not asked (8/9) on the other two are NA; rows where all three are NA are omitted.
##The post-election wave showed four new profiles (cand<k>*_post) and asked liberal or
##conservative (CCES14_JAH_post.docx), but its answers are not in the .sav: not built.
##Covariates from the CCES common content (.sav value labels): cov_gender (1 Male, 2 Female),
##cov_birth_year (birthyr), cov_education (educ text), cov_party_id (pid3 text; "Not sure"
##kept as text), cov_party_id7 (pid7 text), cov_race (race text); Skipped/Not Asked = NA.
##cov_survey_weight = weight ("Team weights"). Case id V101 re-keyed to 1..n; all other
##module and common-content columns (zip codes, local candidate names, etc.) dropped.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "data.sav"))
s <- s[order(s$V101), ]
txt <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[y %in% c("Skipped", "Not Asked")] <- NA; y }
num <- function(x, ok) { y <- as.integer(zap_labels(x)); y[!y %in% ok] <- NA; y }
d <- rbindlist(lapply(1:4, function(k) {
  q <- paste0("JAH", 372 + k, "_")
  p <- paste0("cand", k)
  data.table(id = seq_len(nrow(s)), task = k, profile = 1L,
             rating_party = num(s[[paste0(q, "a")]], 1:2),
             rating_sure = num(s[[paste0(q, "b")]], 1:4),
             rating = num(s[[paste0(q, "c")]], 0:10),
             attr_gender = txt(s[[paste0(p, "gender")]]), attr_family = txt(s[[paste0(p, "fam")]]),
             attr_religion = txt(s[[paste0(p, "relig")]]), attr_military = txt(s[[paste0(p, "military")]]),
             attr_job = txt(s[[paste0(p, "job")]]), attr_issue1 = txt(s[[paste0(p, "issue1")]]),
             attr_issue2 = txt(s[[paste0(p, "issue2")]]), attr_issue3 = txt(s[[paste0(p, "issue3")]]))
}))
d <- d[!(is.na(rating_party) & is.na(rating_sure) & is.na(rating))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, all(attr_issue1 != attr_issue2 & attr_issue1 != attr_issue3 & attr_issue2 != attr_issue3)])
cv <- data.table(id = seq_len(nrow(s)),
                 cov_gender = c("male", "female")[num(s$gender, 1:2)],
                 cov_birth_year = num(s$birthyr, 1900:2000),
                 cov_education = txt(s$educ), cov_party_id = txt(s$pid3), cov_party_id7 = txt(s$pid7),
                 cov_race = txt(s$race), cov_survey_weight = as.numeric(s$weight))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "henderson_2014_party_guess.csv"))
