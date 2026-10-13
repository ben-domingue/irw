##Trump audience-costs vignette experiment (US) from
##Evers, M. M., Fisher, A., & Schaaf, S. D. (2019). Is there a Trump effect? An experiment on political
##polarization and audience costs. Perspectives on Politics, 17(2), 433-452.
##https://doi.org/10.1017/S1537592718003390
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZELWZ7, CC0 1.0, no restricted files. File read:
##TrumpAudienceCosts_FullDataSet.tab (read as the "original format" .dta download for value labels; 1,991 rows),
##TrumpAudienceCosts_appendix.do (as text; the main .do is empty). Usage: Rscript evers_2019.R <dir holding full.dta> <out dir>
##
##1,991 US online respondents (2017). Each read ONE foreign-policy scenario in which a president made a commitment
##and then behaved in one of three ways, with the president being one of three: 3 x 3 = 9 cells (treatment2):
##  president: "President" (unnamed), "Obama", "Trump"
##  action: "Stay Out" (stayed out of the conflict), "Back Down", "Justify" (backed down with a justification)
##Level text is the authors' value labels (treatments / treatment2: "Pres. Stay Out", "Obama Back Down", "Trump
##Justification" ...); the scenario wording is NOT in the deposit, so the action strings are those short labels.
##One task, one profile; id = row number (no respondent id in the file).
##Outcome: rating = Approve, "Presidential Approval", 0 Strongly disapprove, 1 Somewhat disapprove, 2 Neither,
##3 Somewhat approve, 4 Strongly approve (value labels; question wording not in the deposit). Higher = more approval.
##The authors' regressions use pass == 1 (passed both manipulation checks, n = 1,699); all 1,991 rows are kept with
##cov_attention_pass = pass. A 'dup' flag (1,853 = 0; 138 flagged 1-3, meaning undocumented) is not applied.
##PII FOUND and dropped: LocationLatitude, LocationLongitude, LocationAccuracy; also dropped: free text (AppWrite,
##Party_Sim_TEXT, gender_TEXT, race_TEXT), vote/feeling-thermometer/knowledge items, derived dummies.
##Covariates: cov_gender (gender 1/2; 2 = female per the authors' derived `female` dummy, checked identical),
##cov_age, cov_education (edu value labels), cov_party_id7 (Party value labels).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "full.dta"))
n <- nrow(s)
stopifnot(all((as.integer(s$gender) == 2) == (as.integer(s$female) == 1)), !anyNA(s$treatment2), !anyNA(s$Approve))
t2 <- as.integer(s$treatment2)
pres <- c("President", "Obama", "Trump")[(t2 - 1L) %/% 3L + 1L]
act <- c("Stay Out", "Back Down", "Justify")[(t2 - 1L) %% 3L + 1L]
lab <- function(v) as.character(as_factor(s[[v]], levels = "labels"))
d <- data.table(id = seq_len(n), task = 1L, profile = 1L, rating = as.integer(s$Approve),
  attr_president = pres, attr_action = act,
  cov_gender = c("male", "female")[as.integer(s$gender)], cov_age = as.integer(s$age),
  cov_education = lab("edu"), cov_party_id7 = lab("Party"), cov_attention_pass = as.integer(s$pass))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "evers_2019_audience_costs.csv"))
