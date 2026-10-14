##Vaccine immunity x income-loss trade-off vignette for artists, Germany, from
##Seitz, M., Frick, U., Tallon, M., Gotthardt, K. A., & Rakoczy, K. (2024). Career decisions in artistic professions
##during the COVID-19 pandemic in Germany: An experimental study. Humanities and Social Sciences Communications, 11, 512.
##https://doi.org/10.1057/s41599-024-03012-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/TMSJWU, CC0 1.0. Files read: welle2_fusion.sas7bdat (haven::read_sas),
##questionnaire.pdf (German, pdftotext, for the vignette text and value labels), 2_tradeoff_models.sas.txt (as text).
##Usage: Rscript seitz_2024.R <dir holding f9862911 = welle2_fusion.sas7bdat> <output dir>
##
##788 respondents in wave 2 (German students/workers in arts and culture, online panel, early 2021); 688 were drawn into one of six
##vignettes (urn draw GE07_01 -> GE01-GE06; 100 were not assigned and are dropped), 2 x 3 factorial, between-subject:
##  immunity of the vaccine: "Rund 50% / 70% / 90% erreichen einen effektiven Immunschutz nach einer Impfung."
##  pay of the outside job: "... bei vergleichbarer Bezahlung zu Ihrem Vor-Corona-Einkommen" (no loss) vs
##  "... bei vergleichbarer Bezahlung (um 20% geringer) zu Ihrem Vor-Corona-Einkommen" (20% loss).
##Level texts are the questionnaire's German wording (abridged to the clause that varies). Common text: the respondent
##imagines earning a living in an artistic occupation in the pandemic; a vaccine with few side effects is available in
##spring 2021; the culture sector effectively requires proof of vaccination, so no capacity limits.
##Outcome rating_decision = `Decision`, raw 1/2 (1 = resume the previous artistic work with vaccination, with uncertainty about
##how long protection lasts and possible new lockdowns; 2 = accept a job outside the culture sector, a secure position;
##-9 = not answered, dropped). The authors' derived `jobwechsel` = Decision == 2. This is a decision about one vignette, not
##a pick among displayed profiles, hence stored as a rating. 34 assigned respondents without an answer dropped: 654 remain.
##The paper reports its own N: not checked (article not accessible).
##Covariates (labels from the questionnaire value labels): cov_gender (SD01: 1 weiblich = female, 2 maennlich = male, 3 divers =
##other, -9 = NA), cov_age_group (SD27 band text), cov_education (SD10 answer text), cov_state (SD09 Bundesland code, labels not
##read: kept as cov_state_code). Dropped: CASE (questionnaire row id; ids re-keyed), the personal code page, timestamps,
##all other attitude batteries.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_sas(file.path(raw, "f9862911")))
imm <- c(`1` = 50L, `2` = 50L, `3` = 70L, `4` = 70L, `5` = 90L, `6` = 90L)
g <- as.integer(k$GE07_01)
k <- k[!is.na(g)]; g <- g[!is.na(g)]
tx <- c("Rund 50% erreichen einen effektiven Immunschutz nach einer Impfung", "Rund 70% erreichen einen effektiven Immunschutz nach einer Impfung",
        "Rund 90% erreichen einen effektiven Immunschutz nach einer Impfung")
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating_decision = as.integer(k$Decision),
  attr_vaccine_immunity = tx[(g + 1L) %/% 2L],
  attr_job_pay = ifelse(g %% 2L == 1L, "vergleichbare Bezahlung zum Vor-Corona-Einkommen", "vergleichbare Bezahlung (um 20% geringer) zum Vor-Corona-Einkommen"))
stopifnot(all(k$Decision %in% c(1, 2, NA)), identical(as.character(k$Verlust == "Jobwechsel 20% Verlust"), as.character(g %% 2L == 0L)))
d[, `:=`(cov_gender = c("female", "male", "other")[ifelse(k$SD01 %in% 1:3, k$SD01, NA)],
         cov_age_group = c("unter 20 Jahre", "zwischen 20 und 29 Jahren", "zwischen 30 und 39 Jahren", "zwischen 40 und 49 Jahren", "zwischen 50 und 59 Jahren", "über 60 Jahre")[ifelse(k$SD27 %in% 1:6, k$SD27, NA)],
         cov_education = c("keinen formellen Bildungsabschluss (und nicht mehr in Ausbildung)", "Hauptschulabschluss/ beruflicher Abschluss", "Mittlere Reife", "(Fach-)Abitur", "Hochschulabschluss (Bachelor, Master, Promotion, usw.)")[ifelse(k$SD10 %in% 1:5, k$SD10, NA)],
         cov_state_code = ifelse(k$SD09 > 0, as.integer(k$SD09), NA_integer_))]
d <- d[!is.na(rating_decision)]
d[, id := seq_len(.N)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "seitz_2024_artist_vaccine_job.csv"))
