##Austerity-package conjoint (Italy, Spain; 2019 survey) from
##Bansak, K., Bechtel, M. M., & Margalit, Y. (2021). Why austerity? The mass politics of a
##contested policy. American Political Science Review, 115(2), 486-505.
##https://doi.org/10.1017/S0003055420001136
##Replication data: Harvard Dataverse doi:10.7910/DVN/JH5UU8, CC0 1.0. Files read (inside
##replication_materials.zip): data/conjdata_svy2.csv, data/respdata_svy2.csv,
##data/weights/weights_svy2/weights_it.csv and weights_sp.csv; codebooks
##data/codebooks/codebook_conjdata_svy2.txt and codebook_respdata_svy2.txt;
##code/helpers_functions/preprocess2_svy2.R and code/analysis/2_1_fig4.R read as text.
##Usage: Rscript bansak_2021.R <replication_materials/data dir> <output dir>
##
##2019 survey (Bilendi online panel, January 2019, quotas on age, gender, education): 3,968
##respondents in the file (Italy 1,998; Spain 1,970). The article reports N = 3,950 for this
##survey (and 1,985 / 1,967 in its prediction analyses); the file holds 18 more.
##The authors analyse the two countries separately (separate weights, separate models and
##figure panels), and the party-endorsement levels are each country's own parties, so this
##script writes TWO tables: bansak_2021_austerity_italy and bansak_2021_austerity_spain.
##The 2015 five-country survey (respdata_svy1) has no conjoint and is not used.
##Design: 10 pairs of austerity packages per respondent (task = pair letter A-J, profile =
##1/2, from source `profs`). Eight quantitative attributes, each an even integer 0-30 drawn
##for every profile: cuts to defence, education, welfare spending, public-sector jobs and
##pensions (stored NEGATIVE in the source, e.g. -26 = a 26% cut), and increases in income,
##sales and corporate tax (0-30). The levels are stored as the source numbers (text, e.g.
##"-26", "18"); the exact on-screen format (respondents saw Italian or Spanish; screenshot in
##the article's Appendix Figure A9, not deposited) is not in the deposit, the codebook calls
##them percentages ("Defense spending cuts percentage"). attr_party: the endorsing party, as
##stored (party names in the national language); shown only on tasks 6-10 for respondents in
##the endorsement arm (conj_trt *T), "(not shown)" on all other tasks.
##trial_block_order: the source conj_trt first letter, A = spending cuts listed above tax
##increases, B = tax increases above spending cuts (randomized between respondents, constant
##within). Within-block order is not recorded, so there are no attrpos_ columns.
##trial_endorsement_arm: T = endorsements on the last five pairs, C = no endorsements.
##Outcomes:
##  choice = pref: forced choice of the preferred package in the pair (wording not quoted in
##    the article; paraphrase). Exactly one per pair.
##  rating = rate: "If you could vote on each of these options in a referendum, how likely is
##    it that you would vote in favor or against each of the options?" 1 = vote definitely
##    against ... 10 = vote definitely in favor (article; respondents saw it translated).
##Covariates (respdata_svy2.csv; codebook): cov_age; cov_gender from `female` (1 -> female,
##0 -> male); cov_eisced_code (ES-ISCED level 1-7, codes as stored); cov_inc_decile (0 =
##missing in the authors' preprocess code -> NA); cov_num_child, cov_employed, cov_union_mem
##(1 current, 2 past, 3 never), cov_public_job, cov_own_stocks, cov_public_inc, cov_mort,
##cov_aust_pref, cov_layoff, cov_voted, cov_ideo11, cov_gov_int, cov_gov_red, cov_gov_doright,
##cov_gov_competent, cov_empathy1, cov_empathy2, cov_know_unemp/pm/inf/term (all as stored);
##cov_party_vote (vote in the last national election, codebook code mapped to the
##codebook's party text; this is vote choice, not party identification).
##cov_survey_weight: the authors' raking weight (weights_svy2). Dropped: derived empathy index,
##party_vote_lr (CHES score), the authors' recodes. Qualtrics ResponseId re-keyed to integers
##(ids numbered across both countries).
##Randomization restrictions: none documented; level weights not stated in the article.
##Check: support (rating > 5.5, the authors' ratebin) falls with pension cuts in both
##countries, as in the article's Figure 4 (point values not compared).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjdata_svy2.csv"), encoding = "UTF-8")
r <- fread(file.path(raw, "respdata_svy2.csv"), encoding = "UTF-8")
w <- rbind(fread(file.path(raw, "weights/weights_svy2/weights_it.csv")), fread(file.path(raw, "weights/weights_svy2/weights_sp.csv")))
stopifnot(!anyDuplicated(r$ResponseId), !anyDuplicated(w$ResponseId), all(r$ResponseId %in% w$ResponseId))
stopifnot(s[, .N, ResponseId][, all(N == 20)], all(s$ResponseId %in% r$ResponseId))
s[, task := match(substr(profs, 1, 1), LETTERS)][, profile := as.integer(substr(profs, 2, 2))]
stopifnot(all(s$task %in% 1:10), all(s$profile %in% 1:2), s[, sum(pref), .(ResponseId, task)][, all(V1 == 1)])
stopifnot(s[, all(is.na(att_party) == !(task >= 6 & substr(conj_trt, 2, 2) == "T"))])
it <- c("Non ha votato", "Movimento Cinque Stelle", "Lega Nord", "Partito Democratico", "Forza Italia",
        "Fratelli d'Italia", "Liberi e Uguali", "Noi con l’Italia-Udc", "Piu' Europa", "Altro",
        "Ha votato scheda bianca", "Non lo so")
sp <- c("No votó", "Partido Popular (PP)", "Partido Socialista Obrero Español (PSOE)", "Unidos Podemos",
        "Ciudadanos (Cs)", "Esquerra Republicana de Catalunya–Catalunya Sí (ERC–CatSí)",
        "Partit Demòcrata Europeu Català (PDeCAT)", "Partido Nacionalista Vasco (PNV); Euzko Alderdi Jeltzalea",
        "Partido Animalista Contra el Maltrato Animal (PACMA)", "Euskal Herria Bildu (EH Bildu)",
        "Coalición Canaria (CC–PNC)", "Otro", "Votó en blanco", "No lo sé")
stopifnot(all(r[cty == "Italy", party_vote] %in% c(NA, 1:12)), all(r[cty == "Spain", party_vote] %in% c(NA, 1:14)))
stopifnot(all(r$female %in% 0:1))
r[, cov_party_vote := fifelse(cty == "Italy", it[party_vote], sp[party_vote])]
cv <- r[, .(ResponseId, cty, cov_age = as.integer(age), cov_gender = c("male", "female")[female + 1L],
            cov_eisced_code = EISCED, cov_inc_decile = fifelse(inc_decile == 0, NA_integer_, as.integer(inc_decile)),
            cov_num_child = num_child, cov_employed = employed, cov_union_mem = union_mem, cov_public_job = public_job,
            cov_own_stocks = own_stocks, cov_public_inc = public_inc, cov_mort = mort, cov_aust_pref = aust_pref,
            cov_layoff = layoff, cov_party_vote, cov_voted = voted, cov_ideo11 = ideo11, cov_gov_int = gov_int,
            cov_gov_red = gov_red, cov_gov_doright = gov_doright, cov_gov_competent = gov_competent,
            cov_empathy1 = empathy1, cov_empathy2 = empathy2, cov_know_unemp = know_unemp, cov_know_pm = know_pm,
            cov_know_inf = know_inf, cov_know_term = know_term)]
cv <- merge(cv, w[, .(ResponseId, cov_survey_weight = weight)], by = "ResponseId")
ids <- sort(unique(s$ResponseId))
d <- s[, .(ResponseId, task, profile, choice = as.integer(pref), rating = as.integer(rate),
           attr_defence_cut = as.character(att_defe), attr_education_cut = as.character(att_educ),
           attr_welfare_cut = as.character(att_welf), attr_public_jobs_cut = as.character(att_jobs),
           attr_pension_cut = as.character(att_pens), attr_income_tax = as.character(att_inct),
           attr_sales_tax = as.character(att_salt), attr_corporate_tax = as.character(att_cort),
           attr_party = fifelse(is.na(att_party), "(not shown)", att_party),
           trial_block_order = substr(conj_trt, 1, 1), trial_endorsement_arm = substr(conj_trt, 2, 2))]
stopifnot(all(d$rating %in% 1:10))
d <- merge(d, cv, by = "ResponseId", sort = FALSE)
d[, id := match(ResponseId, ids)][, ResponseId := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
for (cc in c("Italy", "Spain")) {
  x <- d[cty == cc][, cty := NULL]
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("bansak_2021_austerity_", tolower(cc), ".csv")))
  cat(cc, nrow(x), uniqueN(x$id), "\n")
}
