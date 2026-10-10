##Lynching-scenario conjoint (Brazil) from
##Freire, D., & Skarbek, D. (2023). Vigilantism and institutions: Understanding attitudes
##toward lynching in Brazil. Research & Politics, 10(1). https://doi.org/10.1177/20531680221150389
##Replication data: Harvard Dataverse doi:10.7910/DVN/F4WGOY, CC0 1.0. Files read:
##data-conjoint.tab (Dataverse "original format" CSV, Qualtrics export with two header rows),
##data-portuguese.tab (original-format CSV; the authors' cleaned file with covariate answer
##text, joined by response id); appendix.pdf (Section C, Table 12) and lynchings.R read as text.
##Usage: Rscript freire_2023.R <dir holding data-conjoint.csv and data-portuguese.csv> <output dir>
##
##Qualtrics online survey, Brazil, 30 Oct - 14 Dec 2020, quotas on gender and region. The
##export has 2,460 respondents (appendix: "2406 Brazilians", the number who consented); 2,084
##answered the conjoint and are in this table (all five tasks each; nobody answered only some).
##Five pairs of "Caso 1" / "Caso 2" profiles of a lynching victim (the suspected criminal),
##eight attributes, fixed order (the F-t-a name columns never vary), levels in Portuguese as
##displayed (Qualtrics F-<task>-<profile>-<attr> columns, the text piped into the question):
##  attr_perpetrator_gender (Gênero do(a) criminoso(a)): Masculino / Feminino
##  attr_perpetrator_age (Idade do(a) criminoso(a)): Adolescente / Adulto(a) / Idoso(a)
##  attr_perpetrator_race (Raça do(a) criminoso(a)): Asiático(a) / Branco(a) / Indígena / Negro(a)
##  attr_perpetrator_residence (Residência do criminoso): Mora na vizinhança / Mora em outro bairro
##  attr_offense (Crime): Bateu a carteira / Roubou o carro / Molestou / Estuprou / Assassinou
##  attr_victim_gender (Gênero da vítima), attr_victim_age (Idade da vítima: Criança /
##  Adolescente / Adulto(a) / Idoso(a)), attr_lynchers (Linchadores: Pedestres / Vizinhos /
##  Família da vítima / Gangues / Polícia).
##Restrictions (appendix C.1): no female rapists; when the offense is car theft the victim is
##never a child or a teenager; otherwise independent (PHP randomizer, not deposited).
##Outcome: choice (Q13-Q17): "Em qual dos dois casos você acha que o linchamento é mais
##justificado?" (In which of the two cases do you think the lynching is more justified?);
##the prompt asks respondents to pick one even if unsure. No opt-out; skipped tasks (none among
##the 2,084) would be dropped. The optional "why?" free text (Q13_TEXT ...) is dropped.
##Dropped as personal data: LocationLatitude/LocationLongitude (present in both files), the
##free-text answers; Qualtrics ResponseId re-keyed to integers. Also dropped: consent, progress,
##the second and third (single-factor) experiments (Q18-Q25).
##Covariates from data-portuguese.csv, where the authors lower-cased every answer text:
##cov_age (q2, typed whole number; kept when 18-110), cov_gender (feminino -> female,
##masculino -> male, outro -> other, prefiro não responder -> NA), cov_race, cov_education
##(answer text, lower-case; "prefiro não responder" -> NA where present), cov_region,
##cov_household_income, cov_ideology, cov_death_penalty, cov_views_police, cov_views_justice,
##cov_previous_victim (multi-select text as stored); "prefiro não responder" set to NA in the
##text covariates, "não sei" kept. The code -> text join was checked against the conjoint
##export's codes (Q3 1/2/3/4 = masculino/feminino/prefiro não responder/outro; Q5 1-6).
##No survey weight in the deposit.
##Check: marginal means of the choice: rape 0.72, murder 0.61, molestation 0.54, car theft
##0.35, pick-pocketing 0.31; male perpetrator 0.55 (article figures not compared).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
q <- read.csv(file.path(raw, "data-conjoint.csv"), check.names = FALSE, encoding = "UTF-8", stringsAsFactors = FALSE)
stopifnot(grepl("linchamento", q[1, "Q13"]))
q <- as.data.table(q[-1, ])
p <- fread(file.path(raw, "data-portuguese.csv"), encoding = "UTF-8")
stopifnot(nrow(q) == 2460, !anyDuplicated(q$ResponseId), all(tolower(q$ResponseId) %in% p$response_id))
an <- c("Gênero do(a) criminoso(a)" = "perpetrator_gender", "Idade do(a) criminoso(a)" = "perpetrator_age",
        "Raça do(a) criminoso(a)" = "perpetrator_race", "Residência do criminoso" = "perpetrator_residence",
        "Crime" = "offense", "Gênero da vítima" = "victim_gender", "Idade da vítima" = "victim_age",
        "Linchadores" = "lynchers")
rows <- list()
for (t in 1:5) for (pr in 1:2) {
  x <- data.table(ResponseId = q$ResponseId, task = t, profile = pr, resp = q[[paste0("Q", 12 + t)]])
  for (k in 1:8) {
    nm <- unique(q[[paste0("F-", t, "-", k)]]); stopifnot(length(nm) == 1, nm %in% names(an))
    x[, paste0("attr_", an[[nm]]) := q[[paste0("F-", t, "-", pr, "-", k)]]]
  }
  rows[[length(rows) + 1]] <- x
}
d <- rbindlist(rows)
d <- d[resp %in% c("1", "2")]
d[, choice := as.integer(resp == as.character(profile))][, resp := NULL]
stopifnot(d[, .N, .(ResponseId, task)][, all(N == 2)], d[, sum(choice), .(ResponseId, task)][, all(V1 == 1)])
stopifnot(!anyNA(d), d[, all(sapply(.SD, function(v) all(v != ""))), .SDcols = patterns("^attr_")])
stopifnot(d[attr_offense == "Estuprou", all(attr_perpetrator_gender == "Masculino")],
          d[attr_offense == "Roubou o carro", !any(attr_victim_age %in% c("Criança", "Adolescente"))])
nr <- function(x) { x <- as.character(x); fifelse(x %in% c("", "prefiro não responder"), NA_character_, x) }
gmap <- c("feminino" = "female", "masculino" = "male", "outro" = "other", "prefiro não responder" = NA)
stopifnot(all(p$gender %in% c(NA, names(gmap))))
p[, age_i := suppressWarnings(as.numeric(age))]
cv <- p[, .(rid = response_id, cov_age = fifelse(!is.na(age_i) & age_i == round(age_i) & age_i >= 18 & age_i <= 110, as.integer(age_i), NA_integer_),
            cov_gender = unname(gmap[gender]), cov_race = nr(race), cov_education = nr(education), cov_region = nr(region),
            cov_household_income = nr(household_income), cov_ideology = nr(ideology), cov_death_penalty = nr(death_penalty),
            cov_views_police = nr(views_police), cov_views_justice = nr(views_justice), cov_previous_victim = nr(previous_victim))]
d[, rid := tolower(ResponseId)]
d <- merge(d, cv, by = "rid", all.x = TRUE, sort = FALSE)[, rid := NULL]
ids <- sort(unique(d$ResponseId))
d[, id := match(ResponseId, ids)][, ResponseId := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "freire_2023_lynching.csv"))
cat(nrow(d), uniqueN(d$id), "\n")
