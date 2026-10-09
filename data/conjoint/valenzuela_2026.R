##Generative-AI news-outlet conjoint (Chile) from
##Valenzuela, S., Bachmann, I., Borah, P., & Solis Valdes, N. (2026). The effects of generative AI
##in news on media credibility and selectivity: Evidence from a conjoint experiment in Chile.
##Digital Journalism. https://doi.org/10.1080/21670811.2026.2649018
##Data: OSF project https://osf.io/s2fhz/ (doi 10.17605/OSF.IO/S2FHZ).
##Licence: CC BY 4.0 (OSF node licence), no other terms in the files.
##Files read: data_file.dta. Read as text: syntax.do (authors' Stata code), "Translated
##questionnaire - English.pdf", "Survey flow & original questionnaire - Spanish.pdf" (with the
##Qualtrics PHP randomizer), "Matrix of Attributes and Levels.pdf", ExampleStimuli_translated_original.pdf.
##Usage: Rscript valenzuela_2026.R <raw dir> <output dir>
##
##2,145 adults living in Chile (online quota sample; survey started Sept 2024 per STARTED), 3
##tasks (Tareas) of two hypothetical news outlets (Perfil: Outlet A = 1, Outlet B = 2), seven
##attributes. Level text and attribute row order are taken from G012_01, the JSON the
##randomizer returned to the survey (F-task-profile-attribute = level shown, F-task-attribute =
##attribute in that row), i.e. the exact Spanish text respondents saw; checked against the coded
##attribute columns (Tareas_periodisticas ... Divulgacion), which agree on every row. Attribute
##row order was shuffled once per respondent (PHP: shuffle($featureArrayKeys) before the task
##loop) and is stored as attrpos_*. Levels uniform ($weighted = 0), no restrictions
##($restrictionarray empty), but the two profiles of a task may not be identical
##($noDuplicateProfiles = True). Attributes (English in the matrix PDF): attr_journalistic_tasks,
##attr_visual_content, attr_textual_content, attr_topics, attr_personalization,
##attr_human_oversight, attr_disclosure.
##Outcomes, both forced choices between Outlet A and Outlet B, no opt-out (English questionnaire):
##  choice_credibility (CRED_Binary, Q25_1/Q26_1/Q27_1): "Let's say you don't have any more
##    information about these outlets than the above. If you had to choose one, which do you
##    think could be the most reliable to report the news in a complete, accurate, fair and
##    unbiased manner?"
##  choice_selectivity (SELEC_Binary, Q25_2/...): "Let's say you have to pick one of these outlets
##    to be up to date in current affairs and you don't have any more information than the
##    above. Which one would you choose?"
##Covariates (value labels in the .dta): cov_gender (B002 Masculino/Femenino/Otro -> male/
##female/other; Prefiero no responder -> NA), cov_birth_year (B001_01, typed; kept 1900-2010),
##cov_region (B003 zone text), cov_ses (B007 GSE ABC1/C2/C3/DE), cov_news_interest (C0001 text),
##cov_ai_attitude_1..4 (F0003_01-04, 1 Muy en desacuerdo .. 5 Muy de acuerdo; the authors'
##AI-attitude scale), cov_time_sum (TIME_SUM, total survey time as deposited, unit not stated).
##Dropped: REF (panel reference hash), CASE (re-keyed), comuna (B004, free text), open-ended
##I0005X*, the authors' quota and derived variables, all other survey items. No survey weight.
##N = 2,145 (the authors' code: "for N, divide Freq by 2145"). Spot check in the return.
library(haven); library(data.table); library(jsonlite)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "data_file.dta"),
              col_select = c("CASE", "Tareas", "Perfil", "CRED_Binary", "SELEC_Binary", "G012_01", "Tareas_periodisticas",
                             "Creacion_contenido_visual", "Creacion_contenido_textual", "Tematica", "Personalizacion",
                             "Supervision_humana", "Divulgacion", "B001_01", "B002", "B003", "B007", "C0001",
                             paste0("F0003_0", 1:4), "TIME_SUM"))
k <- as.data.table(k)
stopifnot(k[, .N, CASE][, all(N == 6)], k[, .N, .(CASE, Tareas, Perfil)][, all(N == 1)], k[, uniqueN(G012_01), CASE][, all(V1 == 1)])
an <- c("Tareas periodísticas" = "journalistic_tasks", "Creación de contenido visual" = "visual_content",
        "Creación de contenido textual" = "textual_content", "Temática" = "topics", "Personalización" = "personalization",
        "Supervisión humana" = "human_oversight", "Divulgación" = "disclosure")
cn <- c(journalistic_tasks = "Tareas_periodisticas", visual_content = "Creacion_contenido_visual",
        textual_content = "Creacion_contenido_textual", topics = "Tematica", personalization = "Personalizacion",
        human_oversight = "Supervision_humana", disclosure = "Divulgacion")
d <- k[, .(id = match(CASE, sort(unique(CASE))), task = as.integer(Tareas), profile = as.integer(Perfil),
           choice_credibility = as.integer(zap_labels(CRED_Binary)), choice_selectivity = as.integer(zap_labels(SELEC_Binary)))]
for (v in an) { d[, paste0("attr_", v) := NA_character_]; d[, paste0("attrpos_", v) := NA_integer_] }
js <- lapply(k$G012_01, fromJSON)
for (r in seq_len(nrow(d))) {
  j <- js[[r]]; t <- d$task[r]; p <- d$profile[r]
  for (q in 1:7) {
    v <- an[[j[[sprintf("F-%d-%d", t, q)]]]]
    set(d, r, paste0("attr_", v), j[[sprintf("F-%d-%d-%d", t, p, q)]]); set(d, r, paste0("attrpos_", v), q)
  }
}
for (v in an) {
  stopifnot(!is.na(d[[paste0("attr_", v)]]))
  # the JSON text and the coded column agree (one code per text)
  stopifnot(data.table(x = d[[paste0("attr_", v)]], y = as.integer(zap_labels(k[[cn[[v]]]])))[, uniqueN(y), x][, all(V1 == 1)])
}
stopifnot(d[, uniqueN(paste(attrpos_journalistic_tasks, attrpos_topics, attrpos_disclosure)), id][, all(V1 == 1)])
for (o in c("choice_credibility", "choice_selectivity")) stopifnot(d[, sum(get(o)), .(id, task)][, all(V1 == 1)])
g <- as.integer(zap_labels(k$B002)); stopifnot(all(g %in% c(1:4)))
d[, cov_gender := c("male", "female", "other", NA)[g]]
by <- suppressWarnings(as.integer(k$B001_01)); d[, cov_birth_year := fifelse(by >= 1900 & by <= 2010, by, NA_integer_)]
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[y == "Not answered"] <- NA; y }
d[, cov_region := lab(k$B003)][, cov_ses := lab(k$B007)][, cov_news_interest := lab(k$C0001)]
for (q in 1:4) { x <- as.integer(zap_labels(k[[paste0("F0003_0", q)]])); x[x < 0] <- NA; d[, paste0("cov_ai_attitude_", q) := x] }
d[, cov_time_sum := as.numeric(k$TIME_SUM)]
setcolorder(d, c("id", "task", "profile", "choice_credibility", "choice_selectivity", paste0("attr_", an), paste0("attrpos_", an)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "valenzuela_2026_genai_news.csv"))
