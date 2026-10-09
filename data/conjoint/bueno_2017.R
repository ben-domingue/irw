##Mayor credit-claiming conjoint (Brazil) from
##Bueno, N. S. (2017). Bypassing the enemy: Distributive politics, credit claiming, and
##nonstate organizations in Brazil. Comparative Political Studies, 51(3), 304-340.
##https://doi.org/10.1177/0010414017710255
##Replication data: Harvard Dataverse doi:10.7910/DVN/XAUYEM, CC0 1.0, no restricted files.
##File read: final_replication.RData (object `conjointff` only, loaded into its own environment).
##Codebook: codebook.xlsx (sheet variables, block conjointff); questionnaire:
##survey_questionnaire.pdf (Qualtrics print, Portuguese; conjoint blocks pp. 2-5).
##Usage: Rscript bueno_2017.R <dir holding final.RData (final_replication.RData renamed)> <output dir>
##
##1,103 Brazilian online respondents (Qualtrics, 2017; the sample answered a forced PT-vs-PSDB
##question), up to 4 tasks comparing "Município A" and "Município B", each described by three
##sentences, one per attribute, shown as rows of a two-column table:
##  attr_partisanship  the mayor's party ("O prefeito pertence ao PSDB (número 45)." / PT 13)
##  attr_federal       daycare built or not through a municipal-federal agreement (convênio)
##  attr_provider      who runs the homeless shelter: an NGO or the city hall (PREFEITURA),
##                     with or without federal funds (4 levels)
##Level text is the Portuguese text as stored in the deposit (stored text = the piped
##${e://Field/Row*} strings); internal double spaces are collapsed and ends trimmed.
##Attribute row order was randomized once per respondent (row1-row3 constant within every
##respondent): attrpos_<attr> = the row (1-3) where it appeared. task = the source's `task`
##(codebook "classification task order"); profile = panel (A = 1, B = 2).
##Outcomes (questionnaire p. 3, same for every task):
##  choice: "Qual prefeito você prefere? Mesmo que você ache que os dois prefeitos são
##    semelhantes, escolha o prefeito que você ache melhor." Forced, no opt-out (d_choice).
##  rating: "Na sua opinião, como está o desempenho de cada prefeito? ..." 7-point, stored
##    as in ratef, 1 = Péssimo ... 7 = Ótimo (the same coding as the vignette's
##    outcome_blamerf in the deposit: Péssimo 1, Ruim 3; chosen profiles average 4.4 vs 3.2).
##  rating_federal: "Na sua opinião e com base na informação dada, como está o desempenho do
##    governo federal?" (ratefedf), same 7-point scale, asked ONCE per task about the federal
##    government, not about a profile: the value is repeated on both profile rows.
##Tasks: 995 respondents have 4 tasks, 105 have 3 and 3 have 2 (incomplete tasks are not in
##the source); nothing is dropped. The deposit's separate 2x2 vignette experiment (vignetteff,
##credit/blame attribution with categorical "who is responsible" answers) is not included.
##Covariates (text as stored, questionnaire wording): cov_gender (Feminino -> female, Masculino
##-> male), cov_birth_year (`age` holds the year of birth; the authors' computed age agef is
##dropped), cov_state (uf_1), cov_religion, cov_income (MW, salary bands), cov_education (answer
##text), cov_vote2014 (as stored, incl. "Prefiro não responder"), cov_party_forced (party: "se
##você tivesse que escolher entre PT e PSDB, qual partido você diria que mais lhe representa?";
##a forced choice, so not cov_party_id), cov_survey_weight (weights). Numeric duplicates
##(*f columns, agegf, regionf) are dropped. Respondent ids are Qualtrics ResponseIds in the
##source and are re-keyed to integers (order of first appearance).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "final.RData"), envir = e)
s <- as.data.table(e$conjointff); rm(e)
stopifnot(nrow(s) == 8602L, s[, uniqueN(paste(row1, row2, row3)), respID][, all(V1 == 1)])
cl <- function(x) trimws(gsub("\\s+", " ", x))
s[, id := match(respID, unique(respID))]
pos <- function(attr) as.integer(fifelse(s$row1 == attr, 1L, fifelse(s$row2 == attr, 2L, fifelse(s$row3 == attr, 3L, NA_integer_))))
d <- s[, .(id = as.integer(id), task = as.integer(task), profile = match(panel, c("A", "B")),
           choice = as.integer(d_choice), rating = as.integer(ratef), rating_federal = as.integer(ratefedf),
           attr_partisanship = cl(partisanship), attr_federal = cl(federal), attr_provider = cl(nsp_city))]
d[, `:=`(attrpos_partisanship = pos("partisanship"), attrpos_federal = pos("federal"), attrpos_provider = pos("nsp_city"))]
stopifnot(!anyNA(d$attrpos_partisanship), !anyNA(d$attrpos_federal), !anyNA(d$attrpos_provider))
d[, `:=`(cov_gender = c(Feminino = "female", Masculino = "male")[s$gender], cov_birth_year = as.integer(s$age),
         cov_state = s$uf_1, cov_religion = s$religion, cov_income = s$MW, cov_education = s$education,
         cov_vote2014 = s$vote2014, cov_party_forced = s$party, cov_survey_weight = s$weights)]
stopifnot(!anyNA(d$cov_gender), !anyNA(d$profile), d[, .(sum(choice), .N), .(id, task)][, all(V1 == 1 & N == 2)])
stopifnot(d[, uniqueN(rating_federal), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bueno_2017_credit_claiming.csv"))
