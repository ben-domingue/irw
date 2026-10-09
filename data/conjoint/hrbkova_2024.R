##Conversation-partner conjoint (Czech Republic) from
##Hrbkova, L., Voda, P., & Havlik, V. (2024). Politically motivated interpersonal biases: Polarizing
##effects of partisanship and immigration attitudes. Party Politics, 30(3), 450-464.
##https://doi.org/10.1177/13540688231156409
##Replication data: Harvard Dataverse doi:10.7910/DVN/WRRTDC, CC0 1.0, no restricted files, no terms.
##File read: conjoint_data.csv (semicolon-separated, Windows-1250 encoding, one row per profile).
##Read as text only: cj_tg_r.R (authors' analysis code). The trust-game files (trust_r.csv,
##trust_stata.xlsx, tg.R, trustgame.do) are a separate experiment and are not used; conjoint_stata.csv
##is the authors' recoded copy of the same data. Design facts and English attribute table from the
##article (open access, CC BY 4.0), "Data and methods" and Table 1.
##Usage: Rscript hrbkova_2024.R <raw dir> <output dir>
##
##Focus Marketing and Social Research online panel, 22 May - 3 June 2019, quota sample of Czech
##adults. "Subjects were presented with profiles of two strangers and asked to evaluate them on
##feeling thermometers. Subsequently, they had to choose the one they would prefer to talk to. The
##task was repeated five times per subject." Six attributes; "The conjoint design was unrestricted,
##and the attribute values were generated randomly. The order of attributes was kept constant for
##each respondent." Profiles mirror the respondents' own pre-treatment answers.
##Outcomes (exact Czech wording not in the deposit; article paraphrase):
##  rating: feeling thermometer 0-100 for each profile (stored raw; anchors not given).
##  choice: which of the two people the respondent would prefer to talk to; forced choice.
##Structure: id = Qualtrics ResponseId plus a suffix ".1"/".2" = profile (recorded); time = task
##(1-5, recorded). 1,092 respondent IDs x 10 rows. 321 tasks have blank attribute text and no
##outcome (attributes not saved / task not shown) and 14 tasks have attributes but no outcome: both
##dropped. Result 1,032 respondents, 5,125 tasks, 10,250 rows, matching the article's N = 1,032 and
##"10,250 cases". The ResponseId (a Qualtrics platform ID) is re-keyed to integers in file order.
##Attribute text is the Czech text stored in the data (the profile levels the authors' code
##analyses; the article's Table 1 gives English translations): gender (Muz/Zena), education,
##value (four value statements), party (ANO, CSSD, KDU-CSL, KSCM, ODS, Pirati, SPD, STAN, TOP 09,
##"Zadnou" = no party), immigration (three statements), political talk (Casto/Obcas/Skoro nikdy).
##The source column `traits` (all six joined by "|") is dropped.
##Covariates (answer text as stored, Czech): cov_gender (Gender: Zena -> female, Muz -> male),
##cov_age_group (Age, e.g. "55-64 let"), cov_education (Education), cov_municipality_size (VelObce),
##cov_region (Q64, kraj), cov_ideology (Ideology_1, left-right as stored 1-9), cov_vote_intention
##(Party: the party the respondent would most likely vote for, per the article; a vote intention,
##not party identification), cov_nonvoter_lean (PartyNonVoter), cov_never_vote_party (NegatParty, the
##party the respondent would never vote for), cov_sympathy_<party> (PartySympathy_*/PartySmpathy_*,
##0-10 like-dislike), cov_immigration (Immigration statement), cov_immigration_salience,
##cov_values_1/3/4/5 (Values_*, codes 1-4 as stored; wording not in the deposit), cov_most_value
##(MostValue, text from the authors' code), cov_polit_talk (PolitTalk), cov_interest (Interest).
##Dropped: ideology (duplicate of Ideology_1), Exclude (0 for everyone), traits. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
txt <- iconv(readLines(file.path(raw, "conjoint_data.csv"), warn = FALSE), "CP1250", "UTF-8")
s <- fread(text = txt, sep = ";", na.strings = "NA", encoding = "UTF-8")
stopifnot(nrow(s) == 10920L)
s[, rid := trimws(sub("\\s*\\.[12]$", "", id))][, profile := as.integer(sub("^.*\\.", "", id))]
stopifnot(all(s$profile %in% 1:2), s[, .N, .(rid, time, profile)][, all(N == 1)], all(s$time %in% 1:5))
s[, blank := trait_gender == ""]
stopifnot(s[, uniqueN(blank), .(rid, time)][, all(V1 == 1)], all(is.na(s$choice[s$blank])))
s <- s[!blank & !is.na(choice)]
stopifnot(!anyNA(s$rating), s[, .N, .(rid, time)][, all(N == 2)], s[, sum(choice), .(rid, time)][, all(V1 == 1)])
ids <- unique(s$rid); s[, idn := match(rid, ids)]
mv <- c("Promýšlení nových myšlenek a tvořivost, dělat věci originálním způsobem",
        "Překvapení a vyhledávání nových aktivit. Dělat v životě mnoho různých věcí",
        "Chovat se spořádaně, vyhýbat se tomu, co ostatní označují za špatné",
        "Žít v bezpečném prostředí a vyhýbat se všemu, co by mohlo ohrozit bezpečnost")
stopifnot(all(s$Gender %in% c("Muž", "Žena", NA)), all(s$MostValue %in% c(1:4, NA)))
d <- s[, .(id = as.integer(idn), task = as.integer(time), profile, choice = as.integer(choice), rating = as.integer(rating),
           attr_gender = trait_gender, attr_education = trait_education, attr_value = trait_value, attr_party = trait_party,
           attr_immigration = trait_immigration, attr_political_talk = trait_politicaltalk,
           cov_gender = c(`Žena` = "female", `Muž` = "male")[Gender], cov_age_group = Age, cov_education = Education,
           cov_municipality_size = VelObce, cov_region = Q64, cov_ideology = Ideology_1, cov_vote_intention = Party,
           cov_nonvoter_lean = PartyNonVoter, cov_never_vote_party = NegatParty)]
sym <- grep("^PartyS(y)?mpathy_", names(s), value = TRUE)
stopifnot(length(sym) == 9L)
for (v in sym) d[, paste0("cov_sympathy_", tolower(gsub("[^A-Za-z0-9]", "", iconv(sub("^PartyS(y)?mpathy_", "", v), "UTF-8", "ASCII//TRANSLIT")))) := as.integer(s[[v]])]
d[, `:=`(cov_immigration = s$Immigration, cov_immigration_salience = s$ImmigrationSalience,
         cov_values_1 = as.integer(s$Values_1), cov_values_3 = as.integer(s$Values_3), cov_values_4 = as.integer(s$Values_4),
         cov_values_5 = as.integer(s$Values_5), cov_most_value = mv[s$MostValue], cov_polit_talk = s$PolitTalk, cov_interest = s$Interest)]
d[, cov_gender := unname(cov_gender)]
stopifnot(uniqueN(d$id) == 1032L, nrow(d) == 10250L)
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hrbkova_2024_conversation_partners.csv"))
