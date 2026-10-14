##Iraq protest-support paired conjoint from
##Yamao, D. (2025). Support for protests in post-conflict societies: Evidence from survey experiments in Iraq
##[Data set]. Harvard Dataverse. No article DOI in the deposit.
##Replication data: Harvard Dataverse doi:10.7910/DVN/TFGM5Z, CC0 1.0. Files read: conjoint_data_tr.csv,
##cjoint_amce.Rmd (as text). vignette_data.csv (second experiment) is read by yamao_2025_protest_vignette.R if built.
##Usage: Rscript yamao_2025_protest.R <dir holding f10576114 = conjoint_data_tr.csv> <output dir>
##
##917 respondents in the file (916 kept) in Iraq (online panel; the sister vignette file is recorded Nov 2023), 5 tasks x 2 hypothetical protests,
##choice = 1 for the protest chosen (the deposit has `choice`; the question wording, e.g. which protest the respondent
##would support, is NOT in the deposit and is not claimed). Forced choice: every kept task has exactly one chosen
##profile, no opt-out column. Five attributes as stored (authors' English tags; LABELS: tags only, the Arabic
##displayed text is not in the deposit; two tags carry the authors' typos "Election fraus" and "Wealfare", kept as
##stored): place (Capital / Provincial capital / Other), sect (Sunni / Shia / Kurd / Mixture / Minority: the
##protesters' sect), reason (9 levels: Corruption, Election fraus, Environment, Inflation, Intervention,
##Political system, Public goods, Unemployment, Wealfare), timing (During-campaign / Election day / Non-election /
##Post-election), organizer (Imtidad / Non-organizer / Non-party / Sadr / Tribal chief). Restrictions or level
##probabilities are not documented.
##Dropped tasks: one respondent task with a single row and five tasks with four rows (duplicated pairs, two chosen)
##are removed; 916 of 917 respondents remain (the one-row respondent is lost). 103 respondents have fewer than
##five complete tasks (partial responses), kept.
##Covariates: cov_gender_code (Gender, 1/2; the Rmd does not map it), cov_age (Age, years), cov_sect (respondent's
##sect, Sect: 1 Sunni, 2 Shia, 3 Christian, 4 Kurd, 5 others, per the Rmd recode), cov_education_code, cov_income_code
##(unlabeled), cov_will_vote (Q2: 1 will vote, 2 will not vote, per the Rmd recode `gotovote`). Trust items Q3_*
##(reverse scale 7 - x in the Rmd, labels undocumented), Q4_*, `answer` (respondent-level, undocumented) are not kept.
##Dropped: the platform id (`id` is a UUID, re-keyed to integers), row index.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "f10576114"), encoding = "UTF-8")
d[, n := .N, .(id, task)]
d[, k := sum(choice), .(id, task)]
d <- d[n == 2L & k == 1L]
d[, uid := .GRP, by = id]
o <- d[, .(id = uid, task = as.integer(task), profile = as.integer(profile), choice = as.integer(choice),
           attr_place = place, attr_sect = sect, attr_reason = reason, attr_timing = timing, attr_organizer = organizer,
           cov_gender_code = as.integer(Gender), cov_age = as.integer(Age),
           cov_sect = c("Sunni", "Shia", "Christian", "Kurd", "others")[as.integer(Sect)],
           cov_education_code = as.integer(Education), cov_income_code = as.integer(Income),
           cov_will_vote = c("will vote", "will not vote")[as.integer(Q2)])]
stopifnot(o[, uniqueN(profile), .(id, task)][, all(V1 == 2)])
setorder(o, id, task, profile)
fwrite(o, file.path(out, "yamao_2025_iraq_protests.csv"))
