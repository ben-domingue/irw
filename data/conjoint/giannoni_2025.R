##Firm-job conjoint (Brazil) from
##Giannoni, M. (2025). From the factory floor to the ballot box: Firm-based origins of Brazil's populist right.
##British Journal of Political Science. https://doi.org/10.1017/S0007123425100859
##Replication data: Harvard Dataverse doi:10.7910/DVN/K9EZ32, CC0 1.0. Files read: conjoint_brazil_clean.csv
##(one row per respondent, two Qualtrics header rows; datafile 11800886, original CSV) and brazil_clean.csv (respondent
##covariates, datafile 11800889, joined on ResponseId); README.Rmd and brazil_qualtrics_conjoint.R read as text.
##Usage: Rscript giannoni_2025.R <dir holding the two csv files, named conjoint_brazil_clean.csv and brazil_clean.csv> <output dir>
##
##Online survey of Brazilian employees (Portuguese). Each respondent saw TWO tasks; a task is a pair of hypothetical
##firms/jobs described by 7 attributes. Attribute ORDER is randomized per task (the file stores, for each position
##k=1..7, the attribute name F-t-k and the level text of profile 1 (F-t-1-k) and profile 2 (F-t-2-k)); attrpos_* is the
##row position of each attribute in that task. Level text is the Portuguese text displayed. The 7 attributes: work schedule,
##pension contributions, CEO pay ratio, contract type, ownership, benefits, how promotions are decided.
##Outcomes: after the profiles, 11 statements were each answered by picking profile 1 or 2 (values 1/2 in Q54..Q67 for
##task 1 and Q76..Q89 for task 2, as in the authors' brazil_qualtrics_conjoint.R, which feeds c(Q54,Q76) etc. to cjoint's
##read.qualtrics as the selected profile of tasks 1 and 2). The question STEM is not in the deposit; only the statement
##texts ship (header row 2), so the design record gives the statement text with "(paraphrase)". Forced choice, no
##opt-out. Each statement is its own choice_* column (same tasks, one table). Q59, Q62, Q63 (and their task 2
##counterparts) are not in the file.
##Respondents: 1,763 rows in the file; 389 have attribute columns but no outcome at all (they did not reach the
##conjoint questions: the covariate file also has blank firm and treatment fields for them) and are omitted as rows
##with no outcome. 1,374 respondents remain. A handful skip single statements in one task (NA in that choice_ column).
##Covariates (Portuguese answer text from brazil_clean.csv; value labels are the displayed text): cov_gender
##(Feminino -> female, Masculino -> male), cov_race (Branca/Parda/Preta/Amarela/Outra), cov_education (education_q
##text), cov_party_id (party_close text; "Outro (escreva)" kept as text; empty -> NA).
##Dropped: Qualtrics ResponseId (re-keyed to an integer id), the information-experiment treatment and the firm/industry
##covariates (not conjoint), the attitude scales.
##Randomization restrictions: none documented in the deposit; every attribute has two levels, shares 49-51% each (level weights near uniform, not documented).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- names(fread(file.path(raw, "conjoint_brazil_clean.csv"), nrows = 0, encoding = "UTF-8"))
x <- fread(file.path(raw, "conjoint_brazil_clean.csv"), skip = 2, header = FALSE, encoding = "UTF-8", colClasses = "character")
setnames(x, h)
cv <- fread(file.path(raw, "brazil_clean.csv"), encoding = "UTF-8", colClasses = "character",
            select = c("ResponseId", "gender_q", "race", "education_q", "party_close"))
stopifnot(!anyDuplicated(x$ResponseId), !anyDuplicated(cv$ResponseId))
x <- merge(x, cv, by = "ResponseId", all.x = TRUE, sort = FALSE)
stopifnot(!anyNA(x$gender_q))
x[, id := .I]
q1 <- c("Q54","Q55","Q56","Q57","Q58","Q60","Q61","Q64","Q65","Q66","Q67")
q2 <- c("Q76","Q77","Q78","Q79","Q80","Q82","Q83","Q86","Q87","Q88","Q89")
nm <- c("represented","treated_unfairly","elite_gap","minorities_influence","no_real_democracy","poor_influence",
        "migrants_threat","strikes","overthrow","antimigrant_protest","antisystem_vote")
shortn <- c("Como é organizado o horario de trabalho?" = "schedule",
            "A empresa faz contribuições para sua previdência ou aposentadoria?" = "pension",
            "Quanto ganha o CEO?" = "ceo_pay", "Qual é o tipo de contrato?" = "contract",
            "Quem é o proprietário da empresa?" = "owner", "Quais são os benefícios?" = "benefits",
            "Como são decididas as promoções?" = "promotion")
build <- function(t) {
  qs <- if (t == 1) q1 else q2
  has <- x[, rowSums(!is.na(.SD) & .SD != "") > 0, .SDcols = qs]
  y <- x[has]
  rbindlist(lapply(1:2, function(p) {
    d <- data.table(id = y$id, task = t, profile = p)
    for (k in 1:7) {
      an <- shortn[y[[sprintf("F-%d-%d", t, k)]]]
      stopifnot(!anyNA(an))
      lvl <- y[[sprintf("F-%d-%d-%d", t, p, k)]]
      stopifnot(all(nzchar(lvl)))
      for (a_ in unique(an)) {
        m <- an == a_
        if (is.null(d[[paste0("attr_", a_)]])) { d[, (paste0("attr_", a_)) := NA_character_]; d[, (paste0("attrpos_", a_)) := NA_integer_] }
        set(d, which(m), paste0("attr_", a_), lvl[m]); set(d, which(m), paste0("attrpos_", a_), k)
      }
    }
    for (j in seq_along(qs)) {
      v <- suppressWarnings(as.integer(y[[qs[j]]]))
      set(d, j = paste0("choice_", nm[j]), value = fifelse(is.na(v), NA_integer_, as.integer(v == p)))
    }
    d[, c("cov_gender", "cov_race", "cov_education", "cov_party_id") := .(
        c(Feminino = "female", Masculino = "male")[y$gender_q], y$race, y$education_q,
        fifelse(y$party_close == "", NA_character_, y$party_close))]
    d
  }))
}
d <- rbindlist(list(build(1), build(2)))
d[, id := frank(id, ties.method = "dense")]
ac <- grep("^attr_", names(d), value = TRUE)
stopifnot(!anyNA(d[, ..ac]), length(ac) == 7, d[, uniqueN(id)] == 1374)
cc <- grep("^choice_", names(d), value = TRUE)
for (c_ in cc) stopifnot(d[!is.na(get(c_)), sum(get(c_)), .(id, task)][, all(V1 == 1)])
setcolorder(d, c("id", "task", "profile", cc))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "giannoni_2025_firm_jobs.csv"))
