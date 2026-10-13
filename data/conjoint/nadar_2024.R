##Pedodontists' likelihood of using atraumatic restorative treatment (ART) for 11 hypothetical child patients
##Nadar, B., G. V., U., Almalki, S. A., & Gowdar, I. M. (2024). Understanding decision making for the use
##of atraumatic restorative approach based on non-clinical factors by Indian pedodontists: a conjoint analysis.
##F1000Research, 13, 1401. https://doi.org/10.12688/f1000research.157561.1
##Deposit: figshare doi:10.6084/m9.figshare.27188796, CC BY 4.0. File read: "Conjoint study - data file.csv"
##(saved as data.csv). Usage: Rscript nadar_2024.R <dir holding data.csv> <output dir>
##
##432 life members of the Indian Association of Pedodontic and Preventive Dentistry (the paper's N; rows with
##consent "Agree"/"agree"; row 1 of the file is a scale-legend row and is dropped). Each rated 11 single-profile
##scenarios (9 orthogonal profiles + 2 holdouts, fixed design: all respondents saw the same 11 scenarios) that
##combine child's age (4, 6, 12 years), cooperation (cooperative, moderately cooperative, uncooperative) and
##vulnerability (vulnerable, non-vulnerable). Scenario text = the column header, e.g. "A 4 year old cooperative
##child belonging to non-vulnerable section"; attributes are parsed from it (some headers omit
##"child"; parsing is by keyword). The file is read as Latin-1 (one stray byte in a free-text field). task = scenario number (1-11) in the file's column order, which is the
##numbering of the questionnaire; whether the display order was randomized is not documented (task_source inferred).
##Outcome: rating = how likely the respondent is to use ART in that scenario ("rate how likely they were to use
##ART", F1000Research methods); 1 = very likely ... 5 = very unlikely (legend row of the file: 1=very likely,
##2=likely, 3=somewhat likely, 4=unlikely, 5=very unlikely). Lower = more likely: stored raw, not reversed.
##Rows with a missing rating (one respondent skipped scenarios) are omitted.
##Covariates: cov_gender (Female/Male -> female/male), cov_practice_type (answer text), cov_art_view ("Definitive"
##or "Interim": whether ART is regarded as definitive or interim treatment), cov_years_practice (only entries that
##are plain whole numbers; free-typed text such as "2 yrs" or "Fresher" -> NA, as the field was free text).
##Dropped: the empty e-mail column (no address is present in the file), consent item, free-text answers
##(factors influencing selection, where ART was learned, comments). ids are row numbers (the file has no
##respondent id).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.csv"), encoding = "Latin-1", header = TRUE)
nm <- names(x)
x <- x[tolower(trimws(x[[3]])) == "agree"]
stopifnot(nrow(x) == 432)
x[, id := .I]
sc <- 4:14
stopifnot(all(grepl("^[0-9]+\\.\\s*A [0-9]+ year old", nm[sc])))
long <- rbindlist(lapply(seq_along(sc), function(k) {
  h <- nm[sc[k]]
  age <- sub("^.*A ([0-9]+) year old.*$", "\\1", h)
  coop <- if (grepl("moderately cooperative", h)) "moderately cooperative" else if (grepl("uncooperative", h)) "uncooperative" else if (grepl("cooperative", h)) "cooperative" else NA_character_
  vul <- if (grepl("non ?- ?vulnerable", h)) "non-vulnerable" else if (grepl("vulnerable", h)) "vulnerable" else NA_character_
  stopifnot(!is.na(coop), !is.na(vul))
  data.table(id = x$id, task = k, profile = 1L, rating = as.integer(x[[sc[k]]]),
             attr_age = paste(age, "years"), attr_cooperation = coop, attr_vulnerability = vul)
}))
long <- long[!is.na(rating)]
cv <- x[, .(id, cov_gender = tolower(trimws(x[[18]])), cov_practice_type = trimws(x[[19]]),
            cov_art_view = trimws(x[[15]]), yp = iconv(trimws(x[[20]]), "latin1", "ASCII", sub = ""))]
cv[, cov_years_practice := ifelse(grepl("^[0-9]+$", yp), suppressWarnings(as.integer(yp)), NA_integer_)][, yp := NULL]
for (v in c("cov_gender", "cov_practice_type", "cov_art_view")) cv[get(v) == "", (v) := NA_character_]
d <- merge(long, cv, by = "id")
stopifnot(d[, all(rating %in% 1:5)], uniqueN(d$id) == 432, d[, .N, .(id, task)][, all(N == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nadar_2024_art_pedodontists.csv"))
