##Successor-nomination vignette experiment from
##Nukui, H., Miwa, H., & Ono, Y. (2025). Preferences for female successors: Evidence from a
##survey experiment among Japanese local politicians. Electoral Studies, 96, 102956.
##https://doi.org/10.1016/j.electstud.2025.102956
##Replication data: Harvard Dataverse doi:10.7910/DVN/6TRWIQ, CC0 1.0, no restricted files.
##Files read: replication_data.tab (Dataverse original format, saved as replication_data.csv);
##level text, outcome wording and covariate codes from codebook.pdf; readme.txt.
##Usage: Rscript nukui_2025.R <raw dir> <output dir>
##
##7,209 Japanese local council members (survey of elected local politicians; the paper reports
##"over 7000"). Each respondent read ONE vignette about a hypothetical potential successor in a
##2 x 2 between-subject design: gender (attr_gender: Man / Woman) x age (attr_age: 65 years old /
##32 years old). The level text is the codebook's English labels (woman 0 = Man, 1 = Woman;
##young 0 = 65 years old, 1 = 32 years old); respondents saw Japanese, and the full vignette
##wording is not in the deposit or codebook. Assignment used multivariate continuous blocking
##(codebook: cluster = "ID of the block used for multivariate continuous blocking"; kept as
##cov_block); no restriction on level combinations is documented and all four cells occur.
##NO RESPONDENT ID: the authors randomized the row order before release (readme); each row is one
##respondent and id = row number in the file. task = 1, profile = 1 throughout.
##Outcomes (codebook wording, translated; all 1-4, higher = more favourable, kept raw):
##  rating = nomination willingness: "If you were thinking of retiring from your position as a
##    local council member and were looking for a successor, would you be willing to nominate this
##    person as your successor? ..." 1 I would be unwilling to appoint them .. 4 I would be willing
##    to appoint them.
##  rating_support = "If this person were to become your successor, how satisfied do you think your
##    supporters and local support base would be? ..." 1 I think they would not accept it .. 4 I
##    think they would accept it.
##  rating_electability = "If this person were to become your successor, do you think this person
##    would be able to obtain enough support to get elected from the local constituencies? ..."
##    1 ... would not gain the necessary support to win .. 4 ... would gain the necessary support to win.
##Rows with all three outcomes missing are dropped (count printed).
##Covariates (codebook): cov_gender (R.woman 0 = Man -> male, 1 = Woman -> female);
##cov_age_group (R.age, coarsened by the authors: 20s or 30s / 40s / 50s / 60s / 70s or older);
##cov_tenure (years in office, coarsened: less than 5 years / 5-9 years / 10-19 years /
##20-29 years / 30 or more years); cov_did_code (coarsened DID population share of the
##municipality, 1 = <0.2, 2 = 0.2-0.3, ..., 9 = 0.9-1, 10 = 1); cov_magnitude_code (coarsened
##average district magnitude, 1 = M<10, 2 = 10-15, ..., 7 = 35-40, 8 = 40+); cov_designated
##(ordinance-designated city 0/1); cov_municipality (anonymized municipality code; 999 = missing
##-> NA); cov_block (randomization block; 999 = missing -> NA). Raw age, tenure, DID share and
##magnitude were withheld by the authors for anonymity (readme).
##Spot check (printed): difference in mean nomination willingness, Woman minus Man.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "replication_data.csv"), na.strings = "NA")
stopifnot(nrow(r) == 7209, all(r$woman %in% 0:1), all(r$young %in% 0:1))
lab <- function(x, lv) { stopifnot(all(is.na(x) | x %in% seq_along(lv))); lv[x] }
na999 <- function(x) fifelse(x == 999, NA_integer_, as.integer(x))
d <- data.table(id = seq_len(nrow(r)), task = 1L, profile = 1L,
  rating = as.integer(r$nomination), rating_support = as.integer(r$support),
  rating_electability = as.integer(r$electability),
  attr_gender = c("Man", "Woman")[r$woman + 1], attr_age = c("65 years old", "32 years old")[r$young + 1],
  cov_gender = c("male", "female")[r$R.woman + 1],
  cov_age_group = lab(r$R.age, c("20s or 30s", "40s", "50s", "60s", "70s or older")),
  cov_tenure = lab(r$tenure, c("less than 5 years", "5-9 years", "10-19 years", "20-29 years", "30 or more years")),
  cov_did_code = as.integer(r$DID), cov_magnitude_code = as.integer(r$magnitude),
  cov_designated = as.integer(r$designated), cov_municipality = na999(r$code), cov_block = na999(r$cluster))
stopifnot(d[, all(rating %in% c(1:4, NA) & rating_support %in% c(1:4, NA) & rating_electability %in% c(1:4, NA))])
n0 <- nrow(d)
d <- d[!(is.na(rating) & is.na(rating_support) & is.na(rating_electability))]
cat("dropped rows with no outcome:", n0 - nrow(d), "\n")
print(d[, .(mean_nomination = mean(rating, na.rm = TRUE), .N), attr_gender])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nukui_2025_female_successors.csv"))
