##Birthright-citizenship conjoint (Italy) from
##Donnaloja, V., & Vink, M. (2023). Like parent, like child: how attitudes towards immigrants
##spill over to the political inclusion of their children. Journal of Ethnic and Migration
##Studies, 50(14), 3435-3452. https://doi.org/10.1080/1369183X.2023.2282388
##Replication data: Harvard Dataverse doi:10.7910/DVN/CRZQSM, CC0 1.0, no restricted files.
##Files read: my_data.dta (Dataverse "original format" download; Stata labels used) and
##Questionnaire_YouGov (a .docx: the YouGov fielding spec, read for the Italian question and
##level wording). The authors' 1-Replication.do was read as text (not run) for the sample
##restriction and the outcome recode. Design facts from the (CC BY) article.
##Usage: Rscript donnaloja_2023.R <dir holding my_data.dta> <output dir>
##
##YouGov Italy online panel, December 2021, 1,521 respondents; as in the article (and the
##authors' .do file: keep if citizenship==1 | citizenship_check==999) only Italian citizens are
##kept: 1,463 respondents (58 non-citizens / don't know / refused dropped). A different study
##from Donnaloja (2022) (UK, adult naturalisation; doi:10.7910/DVN/NYXQMG).
##Each respondent saw 5 screens (task 1-5) of 2 profiles (profile 1 = Profilo A, 2 = Profilo
##B) of children born in Italy on 1 December 2021 to foreign parents without Italian
##citizenship. Instruction (Italian, repeated each screen): "Ora ti mostreremo i profili di
##cinque coppie di bambini che sono nati in Italia il 1° dicembre 2021 da genitori stranieri
##che non hanno la cittadinanza italiana. Per ogni bambino/a, indica se saresti a favore che
##gli/le venga data la cittadinanza italiana alla nascita." Question: "Per favore, indica a chi
##daresti la cittadinanza italiana alla nascita": Profilo A / Profilo B / Entrambi / Nessuno.
##Outcome: rating = 1 if the respondent would grant this child Italian citizenship at birth
##(answer names this profile, or "Entrambi"), 0 if not (the other profile, or "Nessuno"); this
##is the authors' recode. It is a per-profile yes/no, NOT a forced choice (both or neither
##allowed), so it is in rating, not choice; higher = grant (more favourable).
##Attributes (11), as Italian level text from the YouGov spec, mapped from the .dta codes
##(English value labels in brackets): attr_sex Maschio/Femmina; attr_team_support "Agli eventi
##sportivi internazionali, come i Mondiali di calcio o le Olimpiadi, i genitori tifano"
##Italia/Paese d'origine/Sia Italia che Paese d'origine; attr_country (Paese di nascita dei
##genitori) Argentina/Cina/Romania/Pakistan/Senegal; attr_residence_length (Durata di
##soggiorno in Italia dei genitori) 3/5/10/20 anni; attr_legal_status (Stato di residenza dei
##genitori) Con/Senza permesso di soggiorno; attr_employment (Stato di occupazione dei
##genitori) Entrambe i genitori lavorano/Solo la madre lavora/Solo il padre lavora/Nessuno dei
##genitori lavora; attr_education (Livello di istruzione dei genitori) Diploma di scuola
##elementare/Diploma di scuola superiore/Laurea; attr_italian (Padronanza della lingua
##italiana dei genitori) Limitata/Sufficiente per la comunicazione efficace/Eccellente;
##attr_religion (Religione dei genitori) Musulmana/Cattolica/Non credenti; attr_friends
##(Nazionalità dei quattro migliori amici di famiglia) Tutti italiani/Due italiani e due
##stranieri/Tutti stranieri; attr_children (Numero totale di figli in famiglia) Un figlio/Due
##figli/Quattro figli. The text is the commissioning spec's, not a screenshot, so small
##differences from the screen (capitalisation, spacing) are possible.
##Restriction: Romania never appears with "Senza permesso di soggiorno" (EU citizens);
##checked. Attribute row order was randomized (spec) but is not recorded in the deposit.
##Covariates: cov_age (years, "Quanti anni hai?"); cov_gender ("Sei...?", .dta labels 1 = Uomo,
##2 = Donna, stored as male/female); cov_education ("Qual è il più alto livello di istruzione o
##qualifica che hai raggiunto?", education_level_it), stored as the Italian .dta label text
##(Nessun diploma, Licenza di scuola elementare, ... Dottorato / master di secondo livello,
##Altro, Preferisco non rispondere). The rest are source codes (labels in the .dta, Italian):
##cov_region (1 = Nord Ovest, 2 = Nord Est, 3 = Centro, 4 = Sud,
##5 = Isole), cov_vote_2018 (1 = M5S,
##2 = Lega, 3 = Forza Italia, 4 = Fratelli d'Italia, 5 = PD, 6 = +Europa, 7 = Liberi e
##Uguali, 8 = abstain, 98 = other, 99 = ref/DK), cov_vote_ep_2019 (1 = Lega, 2 = M5S, 3 = PD,
##4 = FI, 5 = FdI, 6 = other, 7 = abstain, 8 = ref/DK), cov_employment (empl_stat_eu,
##1 = full time .. 8 = unemployed, 97 = other, 99 = refused), cov_household_income
##(profile_gross_household_eu, euro bands, 1 = under 5,000 ...), cov_survey_weight (YouGov).
##Dropped: YouGov Panman sample ID (caseid; id re-keyed 1..n in file order), RecordNo,
##birth year (age kept), recoded age/region/quota bands, YouGov's derived income tercile,
##the citizenship screener, and YouGov's quota flags.
##Count check: 1,463 respondents x 5 screens x 2 = 14,630 rows, matching the article's 1,463.
##Spot checks against the article: average acceptance 59.5% (here 59.53% unweighted); 64.0% with
##documented parents and 52.6% with undocumented (here 64.00%, 52.60%); 362 respondents granted
##every profile and 142 none (same here); weighted OLS AMCEs of employment vs "neither works":
##both work +0.150, only father +0.112, only mother +0.099 (article 15, 11.2, 9.9 points).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "my_data.dta")))
k <- k[citizenship == 1 | (!is.na(citizenship_check) & citizenship_check == 999)]
stopifnot(nrow(k) == 1463, uniqueN(k$caseid) == 1463)
k[, id := .I]
lev <- list(
  sex = c("Maschio", "Femmina"),
  team_support = c("Italia", "Paese d'origine", "Sia Italia che Paese d'origine"),
  country = c("Argentina", "Cina", "Romania", "Pakistan", "Senegal"),
  residence_length = c("3 anni", "5 anni", "10 anni", "20 anni"),
  legal_status = c("Con permesso di soggiorno", "Senza permesso di soggiorno"),
  employment = c("Entrambe i genitori lavorano", "Solo la madre lavora", "Solo il padre lavora", "Nessuno dei genitori lavora"),
  education = c("Diploma di scuola elementare", "Diploma di scuola superiore", "Laurea"),
  italian = c("Limitata", "Sufficiente per la comunicazione efficace", "Eccellente"),
  religion = c("Musulmana", "Cattolica", "Non credenti"),
  friends = c("Tutti italiani", "Due italiani e due stranieri", "Tutti stranieri"),
  children = c("Un figlio", "Due figli", "Quattro figli"))
## the .dta value labels, checked so the code -> Italian mapping is the intended one
eng <- list(c("Male", "Female"), c("Italy", "CountryofOrigin", "Both"), c("Argentina", "China", "Romania", "Pakistan", "Senegal"),
            c("3y", "5y", "10y", "20y"), c("Regular", "Irregular"), c("WorkBoth", "WorkMother", "WorkFather", "WorkNone"),
            c("Elementary", "HighSchool", "Uni"), c("Limited", "Sufficient", "Excellent"), c("Muslim", "Catholic", "Atheist"),
            c("AllItalian", "2v2", "Allforeign"), c("One", "Two", "Four"))
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  ans <- as.integer(k[[paste0("conjoint", t)]])
  x <- data.table(id = k$id, task = t, profile = p,
                  rating = as.integer(ans == p | ans == 3L))
  x[is.na(ans), rating := NA_integer_]
  for (j in seq_along(lev)) {
    v <- k[[sprintf("src_%d_attribut%d_%d", t, j, p)]]
    l <- attr(v, "labels"); stopifnot(identical(unname(names(l))[order(l)][seq_along(eng[[j]])], eng[[j]]))
    v <- as.integer(v); stopifnot(!anyNA(v), all(v %in% seq_along(lev[[j]])))
    x[, paste0("attr_", names(lev)[j]) := lev[[j]][v]]
  }
  x
}))))
stopifnot(!anyNA(d$rating))
stopifnot(d[attr_country == "Romania", all(attr_legal_status == "Con permesso di soggiorno")])
z <- function(x) as.integer(zap_labels(x))
cv <- k[, .(id, cov_age = as.integer(age), cov_gender = c("male", "female")[z(gender)], cov_region = z(region_grouped_it),
            cov_education = as.character(as_factor(education_level_it, levels = "labels")), cov_vote_2018 = z(vote_18_quote_it), cov_vote_ep_2019 = z(epl_19_quote_it),
            cov_employment = z(empl_stat_eu), cov_household_income = z(profile_gross_household_eu),
            cov_survey_weight = as.numeric(weight))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "donnaloja_2023_birthright_citizenship.csv"))
