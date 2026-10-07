##Return-migrant conjoint (Colombia) from
##Scholten, M. (2025). The prodigal child returns? Attitudes towards return migration in a
##developing economy. International Studies Quarterly, 69(2), sqaf041.
##https://doi.org/10.1093/isq/sqaf041
##Replication data: Harvard Dataverse doi:10.7910/DVN/LTTBK3, CC0 1.0. File read:
##isq_replication.zip -> isq_replication/experimental/conjoint.csv (raw Qualtrics export, wide:
##header row, question-text row, ImportId row, 2,101 responses; Netquest online panel, Feb-Mar
##2024). scholten_isq_experiment.Rmd and readme.txt were read as text (not run). The article
##is paywalled and was not read; the respondent count below is not checked against it.
##Usage: Rscript scholten_2025.R <dir holding conjoint.csv> <output dir>
##
##Colombian adults compared 6 pairs of hypothetical Colombians living abroad who want to return
##("Opción 1" / "Opción 2"), 4 attributes, levels as displayed (Spanish):
##  empleo_previsto (intended employment): "Tiene la intención de trabajar para otra persona" /
##    "Tiene la intención de iniciar su propio negocio"; ahorros (savings): "No tiene ahorros" /
##    "Tiene ahorros ganados en el extranjero"; politica: "No quiere involucrarse en política" /
##    "Quiere involucrarse en política"; pais_de_retorno (country returning from): "Estados
##    Unidos" / "Venezuela".
##Attribute order was randomized per respondent and fixed across that respondent's tasks; kept
##as attrpos_* (1 = top row). No randomization restrictions are documented.
##Outcomes (same screen, one experiment):
##  choice = "¿Cuál de estas opciones prefieres?" Opción 1 / Opción 2, forced choice, no opt-out
##           (the consent page describes it as which of the two the respondent would rather see
##           return to their community).
##  rating = "Indique qué tan favorables considera ambas opciones" - Opción 1 / Opción 2, 0-10.
##           The anchor wording is not in the deposit; higher = more favourable is read from the
##           question text and is consistent with the data (chosen profiles are rated higher on
##           average). Not recoded.
##A task is kept if it has a choice or either rating; a missing outcome is left blank. The
##authors' analysis set keeps only respondents with all 6 choices (see count check below);
##this table keeps every respondent with any outcome: 1,642 respondents, 9,642 tasks, of whom
##1,572 answered all 6 choices (the authors' set; 459 of 2,101 responses never reached the
##conjoint). The paper's N was not checked. From the 1,572 the choice AMCEs (lm, clustered by
##id) are savings +0.167, work for someone else (vs own business) -0.120, Venezuela (vs US)
##-0.186, wants political involvement -0.119: the signs the abstract describes.
##Covariates keep the source's codes. Meanings from the authors' Rmd where given:
##  cov_urban_rural (urbrur: 1 urban, 2 rural, 3 don't know), cov_ideology (pol1: 1 right,
##  4 = missing/don't know in the authors' coding; other codes unlabelled), cov_ideology_other
##  (pol2, asked if pol1 = "Otro": 1 right, 2 left), cov_labor (labor 1-7; authors treat 1, 2, 4
##  as working, 7 missing), cov_lived_abroad (live1: 1 yes, 2 no, 3 n/a), cov_family_abroad
##  (live2: 1 yes, 2 no, 3 n/a), cov_democracy_view (dem: 1 = the pro-democracy statement, 2-3
##  other statements, 4 don't know), cov_facilitate_return ("En general, ¿cree que el gobierno
##  debería facilitar el retorno ...": 1 yes, 2 no, 3 don't know), cov_age (years), and the
##  panel quota fields cov_ses (source `sel`, 1-6, probably Netquest's socioeconomic level; not
##  documented) and cov_region (1-6, labels
##  not in the deposit).
##Dropped: IP address, latitude/longitude, Qualtrics ResponseId, the Netquest panel ticket, the
##consent item, an empty `sex` column, dates and durations. Ids re-keyed 1..N in file order.
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "conjoint.csv"), colClasses = "character", encoding = "UTF-8")[-(1:2)]
stopifnot(nrow(x) == 2101)
x[, id := .I]
att <- c("Empleo previsto" = "empleo_previsto", "Ahorros" = "ahorros", "Política" = "politica", "País de retorno" = "pais_de_retorno")
rows <- list()
for (t in 1:6) for (p in 1:2) {
  d <- data.table(id = x$id, task = t, profile = p)
  ch <- x[[paste0("conjoint", t)]]
  d[, choice := fifelse(ch == "", NA_integer_, as.integer(ch == as.character(p)))]
  d[, rating := suppressWarnings(as.integer(x[[sprintf("slide%d%d", t, p)]]))]
  d[, ok := ch != "" | x[[sprintf("slide%d1", t)]] != "" | x[[sprintf("slide%d2", t)]] != ""]
  for (j in 1:4) {
    nm <- x[[sprintf("P-%d-%d", t, j)]]; lv <- x[[sprintf("P-%d-%d-%d", t, p, j)]]
    for (k in names(att)) {
      w <- nm == k
      d[w, paste0("attr_", att[[k]]) := lv[w]]
      d[w, paste0("attrpos_", att[[k]]) := j]
    }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows, use.names = TRUE, fill = TRUE)[ok == TRUE][, ok := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", att), paste0("attrpos_", att)))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)],
          d[, .N, .(id, task)][, all(N == 2)], all(d$rating %between% c(0, 10) | is.na(d$rating)))
cvs <- c(urbrur = "urban_rural", pol1 = "ideology", pol2 = "ideology_other", labor = "labor", live1 = "lived_abroad",
         live2 = "family_abroad", dem = "democracy_view", baseline = "facilitate_return", age = "age", sel = "ses", region = "region")
cv <- data.table(id = x$id)
for (v in names(cvs)) cv[, paste0("cov_", cvs[[v]]) := suppressWarnings(as.integer(x[[v]]))]
d <- merge(d, cv, by = "id")
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "scholten_2025_return_migrants.csv"))
