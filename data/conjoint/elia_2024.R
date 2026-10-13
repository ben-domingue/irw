##2x2 vignette experiment on voting for women after corruption scandals (Mexico, Guatemala, Chile, Uruguay) from
##Elia, E. (2024). Can the fairer sex save the day? Voting for women after corruption scandals in Latin America.
##Political Behavior, 47, 97-117. https://doi.org/10.1007/s11109-024-09943-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/JAVSYJ, CC0 1.0. File read: ScandalsExpData_ANONYMOUS.tab (Dataverse tab
##export of the authors' .dta); EliaPOBEFairerSex_Code-1.R and the Stata SI .do read as text.
##Usage: Rscript elia_2024.R <dir holding the .tab saved as data.tab> <output dir>
##
##One mayoral-candidate vignette per respondent (id = a running number; task = profile = 1), online panels in four countries,
##Spanish. Respondents were randomized to one of four conditions (variable condition; the authors' labels in code.R:
##1 Man, 2 Woman, 3 M-Scandal, 4 W-Scandal): candidate sex (a man or a woman) crossed with whether a corruption scandal
##involved the candidate's party (the new candidate of the scandalized incumbent party). The vignette text itself is in the
##paper's SI (Spanish), which is not in the deposit: attribute levels are therefore stored as the authors' own condition
##labels: attr_candidate_sex Man / Woman; attr_scandal "No scandal" / "Corruption scandal" (the do file's own
##balance-table labels "No Scandal", "Scandal"). Check them against the SI vignettes before relying on the wording.
##Three outcomes, each asked of the one candidate; the questionnaire is not in the deposit, so the wording is not available:
##  rating_vote   likelihood of voting for the candidate (paper: 'vote likelihood'), the text answers map 1 'Muy improbable',
##                2 'Algo improbable', 3 'Ni probable ni improbable', 4 'Algo probable', 5 'Muy probable' (numeric `vote`)
##  rating_tell   a second 5-point likelihood item (variable `tell`), same answer scale; the question is not described in the
##                paper's open text or the code (stored as `tell`)
##  rating_trust  trust in the candidate ('trustworthiness'): 1 Nada, 2 Poco, 3 Algo, 4 Mucho (numeric `trust`); 'No se' = NA (216)
##Higher = more likely / more trust. The wide columns cleanmanvote..corruptwomantrust (one per condition) are reduced to these
##three; the text answers and the numeric codes agree (checked cross-tab). No choice or opt-out.
##Sample: the authors' analysis uses incomplete == 0 (3,215 respondents; Chile 843, Guatemala 996, Mexico 865, Uruguay 511);
##the 74 respondents flagged incomplete (they answered the vignette items) are dropped to match. 1,156 rows have no
##condition (never reached the experiment) and are dropped. Manipulation-check variables (manicheck*, passed*) are not kept.
##Covariates kept: cov_country, cov_gender (sex: Hombre = male, Mujer = female, 'Otro/Prefiero no decirlo' = NA), cov_age_group
##(age bands as in the source; the bands differ by country; '85 o mas' accent repaired), cov_duration_sec (Durationinseconds).
##Dropped (no IP or coordinates in this file): Qualtrics ResponseId, StartDate/EndDate, ticket (a UUID), state, consent, education text
##(accents garbled in the .tab export), stereotype and ideology items, the authors' derived variables and model outputs.
##Respondents also saw an unrelated 'ICJCondition' module (not part of this experiment); not kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "data.tab"), encoding = "UTF-8", showProgress = FALSE)
d <- d[incomplete == 0 & !is.na(condition)]
vote_txt <- c("Muy improbable" = 1, "Algo improbable" = 2, "Ni probable ni improbable" = 3, "Algo probable" = 4, "Muy probable" = 5)
pick <- function(cols) { m <- as.matrix(d[, ..cols]); apply(m, 1, function(r) { r <- r[!is.na(r) & r != ""]; if (length(r) == 1) r else NA_character_ }) }
vt <- pick(c("cleanmanvote", "cleanwomanvote", "corruptmanvote", "corruptwomanvote"))
tt <- pick(c("cleanmantell", "cleanwomantell", "corruptmantell", "corruptwomantell"))
stopifnot(all(unname(vote_txt[vt]) == d$vote), all(unname(vote_txt[tt]) == d$tell))
tr <- pick(c("cleanmantrust", "cleanwomantrust", "corruptmantrust", "corruptwomantrust"))
trm <- c("Nada" = 1, "Poco" = 2, "Algo" = 3, "Mucho" = 4)
stopifnot(all(unname(trm[tr]) == d$trust, na.rm = TRUE), sum(is.na(d$trust)) == sum(is.na(trm[tr])))
ag <- sub("^85 o m.*s$", "85 o mas", d$age)
sx <- ifelse(d$sex == "Hombre", "male", ifelse(d$sex == "Mujer", "female", NA))
o <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L, rating_vote = as.integer(d$vote), rating_tell = as.integer(d$tell),
  rating_trust = as.integer(d$trust),
  attr_candidate_sex = ifelse(d$condition %in% c(1, 3), "Man", "Woman"),
  attr_scandal = ifelse(d$condition %in% c(1, 2), "No scandal", "Corruption scandal"),
  cov_country = d$Country, cov_gender = sx, cov_age_group = ag, cov_duration_sec = as.integer(d$Durationinseconds))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "elia_2024_scandal_women_candidates.csv"))
print(table(o$cov_country))
