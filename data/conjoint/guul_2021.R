##Client-vignette experiment on caseworker creaming (client competence x motivation x gender) from
##Guul, T. S., Pedersen, M. J., & Petersen, N. B. G. (2021). Creaming among caseworkers: Effects of client competence and client
##motivation on caseworkers' willingness to help. Public Administration Review, 81(1). https://doi.org/10.1111/puar.13297
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZUOSR8, CC0 1.0. Files read: replication_data.tab (Stata original, saved locally as
##d.dta) and replication_analysis.do (rep.do; text, not run). The deposit removes covariates "for reasons of discretion".
##Usage: Rscript guul_2021.R <dir holding d.dta> <output dir>
##
##1,793 caseworker respondents (the sample is not described in the deposit; the paper's sample is Danish caseworkers), one client
##vignette each, 2 x 2 x 2 between-subject, near-equal cells (209-269). Attribute level text = the Stata VALUE LABELS (the vignette wording
##is not in the deposit and the article could not be retrieved: LABELS: tags only; flag for Ben, ruling 10-13):
##  attr_competence: Expert / Novice (incompetent 0/1);  attr_motivation: Diligent / Lazy (unmotivated 0/1);
##  attr_client_gender: Male / Female (client_female 0/1).
##Outcome: rating_willingness = willingness, 0-10, "Willingness to help. 0-10. 10 = Very likely" (label; value labels Very unlikely .. Very
##likely), higher = more willing; question wording itself is not stored. 198 respondents with no willingness are omitted, leaving 1,595,
##the N the do-file posts for its models (ereturn post obs(1595)). No opt-out.
##Dropped: the manipulation checks (check_competence, check_motivation), random_id (re-keyed). random_groupid (50 clusters used for the
##authors' clustered standard errors and the fixed-effects model) is kept as trial_cluster (re-keyed to 1..50).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "d.dta")))
stopifnot(nrow(d) == 1793, all(d$incompetent %in% 0:1), all(d$unmotivated %in% 0:1), all(d$client_female %in% 0:1))
d <- d[!is.na(willingness)]
stopifnot(nrow(d) == 1595, all(d$willingness %in% 0:10))
g <- function(x) as.integer(zap_labels(x))
r <- d[, .(id = .I, task = 1L, profile = 1L, rating_willingness = g(willingness),
  attr_competence = c("Expert", "Novice")[g(incompetent) + 1L], attr_motivation = c("Diligent", "Lazy")[g(unmotivated) + 1L],
  attr_client_gender = c("Male", "Female")[g(client_female) + 1L], trial_cluster = match(random_groupid, sort(unique(random_groupid))))]
setorder(r, id, task, profile)
fwrite(r, file.path(out, "guul_2021_caseworker_creaming.csv"))
