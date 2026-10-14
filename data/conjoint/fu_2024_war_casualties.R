##Factorial war-casualty vignette (Taiwan) from the replication data of
##Fu, R., Yin, W., & Han, E. (2024). The human cost of war: An experimental study of Taiwanese attitudes towards war
##casualties. Conflict Management and Peace Science, 42(5). https://doi.org/10.1177/07388942241290445
##(authors as in the deposit's .do file; first-name initial of the first author from that file, article details from Crossref).
##Replication data: Harvard Dataverse doi:10.7910/DVN/OJJLZC, CC0 1.0. Files read: Casualty_analysis.tab (Stata original
##with haven, saved as c.dta) and Taiwan_casualty_code.do as text.
##Usage: Rscript fu_2024_war_casualties.R <dir holding c.dta> <output dir>
##
##2,505 Taiwanese online respondents (all Finished), ONE vignette each: 4 warring parties (`group`: 1 US, 2 Taiwan, China
##[the do-file's label], 3 PLA, 4 Civilian: whose casualties) x 3 casualty sizes (`treat_size`: 1 = 1,000, 2 = 10,000,
##3 = 100,000 deaths; the do-file's coefplot labels and its "bylabel(1,000 deaths)" etc.). 12 cells.
##LABELS: tags only. The deposit has no questionnaire (the paper was not read): the vignette text and the question wording are not
##recoverable, so the attribute levels are the do-file's short labels ("US", "Taiwan, China", "PLA", "Civilian",
##"1,000 deaths", ...), not the displayed text. Ben to decide.
##Outcome: rating = `score` (= `support`), integer 1-5, "support" for war; the authors' `percentage` (0/100) is
##100 for scores 4-5, 0 for 1-2 and missing for 3, and is called "Predicted Support Percentage", so higher = more
##support (direction inferred from that recode, not from a questionnaire; anchors unknown). Raw score stored.
##One vignette per respondent, no respondent id: id = row order. No opt-out. Randomization restrictions and
##probabilities not documented (all cells occur; party shares 558-664, size shares 812-854).
##Covariates (unlabelled in the deposit, kept as codes): cov_gender_code (0/1), cov_age_group_code (1-6).
##PII FOUND: IPAddress, LocationLatitude/Longitude, RecipientEmail/names, ResponseId, ExternalReference (dropped).
##Dropped: all other questionnaire items, timings, derived dummies, `percentage`.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "c.dta"), col_select = c("group", "treat_size", "score", "gender", "age")))
stopifnot(nrow(x) == 2505, all(x$group %in% 1:4), all(x$treat_size %in% 1:3), all(x$score %in% 1:5))
d <- x[, .(id = .I, task = 1L, profile = 1L, rating = as.integer(score),
           attr_casualty_party = c("US", "Taiwan, China", "PLA", "Civilian")[as.integer(group)],
           attr_casualty_size = c("1,000 deaths", "10,000 deaths", "100,000 deaths")[as.integer(treat_size)],
           cov_gender_code = as.integer(gender), cov_age_group_code = as.integer(age))]
stopifnot(d[, .N, .(attr_casualty_party, attr_casualty_size)][, .N] == 12)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "fu_2024_war_casualties.csv"))
