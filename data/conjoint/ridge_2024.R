##Regime-type conjoint (Egypt, Morocco) from
##Ridge, H. M. (2024). Democratic commitment in the Middle East: A conjoint analysis. Political
##Science Research and Methods, 12(2), 285-300. https://doi.org/10.1017/psrm.2023.21
##Replication data: Harvard Dataverse doi:10.7910/DVN/GBJVAF, CC0 1.0, no restricted files.
##Files read: Egypt.csv (the Dataverse archival .tab download saved under that name, so
##tab-separated; the "original format" download is comma-separated and is not what this reads), Morocco.csv (comma-separated; 12 empty
##trailing columns ignored). Design from the article (CC BY), section 3, footnote 10 and Figure 1
##(English and Arabic screenshots of a task).
##Usage: Rscript ridge_2024.R <raw dir> <output dir>
##
##YouGov MENA panel; Egypt fielded August 2019, Morocco January 2020. 5 sets (task = Set_Number)
##of two government profiles ("OPTION 1" = profile 1, "OPTION 2" = profile 2; the source's Card
##runs 1-10, cards 2s-1 and 2s belong to set s, verified). Six attributes, English level text as
##deposited and as on the English screen (Figure 1): attr_elections, attr_participation
##("Citizen participation"), attr_official_religion, attr_role_religion ("Role for religious
##leaders"), attr_services ("Provision of public services"), attr_unemployment ("Unemployment
##rate"). About 94% took the survey in Arabic (cov_survey_language); the article notes "The
##English-language text is not a translation of the Arabic text", and the Arabic level text is
##not deposited.
##choice: "Which of these two political systems of government would you prefer the most?"
##  (Figure 1; forced choice between OPTION 1 and OPTION 2). Instruction (footnote 10): "You will
##  now be shown descriptions of two potential systems of government based on different features.
##  ... Please choose the potential set-up for a government that you would prefer. You will be
##  offered five pairs of choices."
##Restrictions: otherwise unconstrained randomization, but "The two profiles were never
##  identical" (article p. 292; verified: no identical pair).
##TWO TABLES, one per country (separate fieldings, analysed separately with one script each):
##  ridge_2024_regime_egypt: 1,028 respondents = 1,000 Egyptians (the article's N) + 28 expats;
##  ridge_2024_regime_morocco: 1,009 respondents = 991 Moroccans (the article's N) + 18 expats.
##  Non-nationals were randomized too but the author drops them (EGYPTNat/MOROCCONat ==
##  "Expat"); they are kept here and flagged by cov_nationality ("Egyptian"/"Moroccan"/"Expat").
##Dropped tasks: sets with no chosen profile or both profiles chosen (Egypt 3 + 3, Morocco 1 + 1;
##  data errors).
##Covariates: cov_survey_language (Arabic/English), cov_nationality, cov_education (answer text),
##  cov_q8 (answer text of the source's Q8, e.g. "An elected government is always preferable to
##  any other kind of government"; question wording not deposited). Dropped: Q11 (wording
##  unknown), cor_* (constant country). RecordNo (a sequential number; Morocco has one "57a")
##  is re-keyed to integers in file order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
an <- c(Elections = "elections", Participation = "participation", Official_Religion = "official_religion",
        Role_Religion = "role_religion", Services = "services", Unemployment_Rate = "unemployment")
for (cn in c("egypt", "morocco")) {
  if (cn == "egypt") x <- fread(file.path(raw, "Egypt.csv"), sep = "\t") else x <- fread(file.path(raw, "Morocco.csv"))[, 1:16]
  nat <- if (cn == "egypt") "EGYPTNat" else "MOROCCONat"
  stopifnot(x[, .N, RecordNo][, all(N == 10)], x[, all(Card %in% c(2 * Set_Number - 1, 2 * Set_Number))])
  d <- data.table(id = match(as.character(x$RecordNo), unique(as.character(x$RecordNo))), task = as.integer(x$Set_Number), profile = 2L - x$Card %% 2L,
                  choice = as.integer(x$Choice))
  for (v in names(an)) d[, paste0("attr_", an[[v]]) := x[[v]]]
  d[, `:=`(cov_survey_language = x$language, cov_nationality = x[[nat]], cov_education = x$education, cov_q8 = x$Q8)]
  stopifnot(d[, .N, .(id, task, profile)][, all(N == 1)], !anyNA(d))
  bad <- d[, sum(choice), .(id, task)][V1 != 1]
  cat(cn, "dropped tasks:", nrow(bad), "\n")
  d <- d[!bad, on = .(id, task)]
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("ridge_2024_regime_", cn, ".csv")))
}
