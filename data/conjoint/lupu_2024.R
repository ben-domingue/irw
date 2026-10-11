##Laws-of-war vignette experiment, three national samples, from
##Lupu, Y., & Wallace, G. P. R. (2024). The laws of war and public support for foreign combatants.
##International Organization. https://doi.org/10.1017/S0020818324000274
##Replication data: Harvard Dataverse doi:10.7910/DVN/WYYEWK, CC0 1.0. Files read: "USA.txt", "UK.txt",
##"France.txt" (comma-separated Qualtrics exports with the authors' recoded variables, text-valued) and the authors'
##replication code "Lupu Wallace IO Replication Code-1.txt" (read as text, not run). "USA_followup.txt" (a later
##US wave, numeric 0/1 codes only, 549 respondents) and the .tab copies are not used.
##Usage: Rscript lupu_2024.R <dir holding USA.txt, UK.txt, France.txt saved as usa.txt, uk.txt, fr.txt> <output dir>
##
##Three tables, one per sample (US 2,009 respondents, UK 2,198, France 2,051; Lucid-type online panels), because the
##authors analyse each country separately with the same code (no pooled data analysis); the design is identical and
##the attribute text is shared, so the tables have the same columns. lupu_2024_laws_of_war_us / _uk / _fr.
##Each respondent read ONE vignette about a conflict abroad, 2 x 2 x 2 x 2 between-subject (expgroup, balanced: 114-145 per
##cell): attr_rebel_aims (rebaims: Secession / Overthrow), attr_government_type (govtype: Autocracy / Democracy),
##attr_rebel_law (reblaw: Comply / Violate the laws of war), attr_government_law (govlaw: Comply / Violate). The
##deposit stores only these condition names, not the vignette paragraphs (the do-file/code never prints them), so the
##levels are the authors' labels. The order in which rebel and government are described was also randomized
##(rebfirst; trial_actor_order "Govt First" / "Rebel First").
##Presentation text, profile = 1, task = 1, id = row number (platform ids dropped).
##Outcomes (code, Figure 1: "Average approval of government/opposition"; the question wording is not in the deposit, so
##the design record says paraphrase): rating_government = app_gov5, rating_rebels = app_reb5, five-point text answers mapped
##1 Strongly disapprove, 2 Somewhat disapprove, 3 Neither approve nor disapprove, 4 Somewhat approve, 5 Strongly approve
##(the authors' 0-1 rescale app_gov5S confirms this order). Rows with a blank answer to both are omitted.
##Covariates: cov_gender (the authors' `male` text: Female / Male; blank -> NA), cov_age (age in years, US and France
##only), cov_age_group (agecat), cov_education (educat text in each country's own categories).
##PII in the deposit (dropped): ResponseID, panel respondent id (rid), Name, ExternalDataReference, EmailAddress,
##IPAddress, zip (US), location latitude/longitude, free-text answers.
##Dropped: the 300+ block/timing columns, the other outcomes (reputation, morality, legitimacy, speech, sanctions,
##military intervention) and attitudes scales, manipulation checks, derived dummies.
##Count check: respondent counts equal the file rows (2,009 / 2,198 / 2,051); the paper's N was not checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- c("Strongly disapprove" = 1L, "Somewhat disapprove" = 2L, "Neither approve nor disapprove" = 3L, "Somewhat approve" = 4L, "Strongly approve" = 5L)
build <- function(file, tab, n) {
  r <- fread(file.path(raw, file), encoding = "UTF-8", data.table = TRUE)
  stopifnot(nrow(r) == n, all(r$rebaims %in% c("Secession", "Overthrow")), all(r$govtype %in% c("Autocracy", "Democracy")),
            all(r$reblaw %in% c("Comply", "Violate")), all(r$govlaw %in% c("Comply", "Violate")))
  stopifnot(all(r$app_gov5 %in% c(names(lv), "")), all(r$app_reb5 %in% c(names(lv), "")))
  d <- data.table(id = seq_len(nrow(r)), task = 1L, profile = 1L,
                  rating_government = unname(lv[r$app_gov5]), rating_rebels = unname(lv[r$app_reb5]),
                  attr_rebel_aims = r$rebaims, attr_government_type = r$govtype, attr_rebel_law = r$reblaw, attr_government_law = r$govlaw,
                  cov_gender = ifelse(r$male %in% c("Female", "Male"), tolower(r$male), NA_character_),
                  cov_age = if ("age" %in% names(r) && is.numeric(r$age)) ifelse(r$age >= 16 & r$age <= 100, as.integer(r$age), NA_integer_) else NA_integer_,
                  cov_age_group = ifelse(r$agecat == "", NA_character_, r$agecat),
                  cov_education = ifelse(r$educat == "", NA_character_, r$educat),
                  trial_actor_order = r$actor_order)
  stopifnot(all(d$trial_actor_order %in% c("Govt First", "Rebel First")))
  d <- d[!(is.na(rating_government) & is.na(rating_rebels))]
  if (all(is.na(d$cov_age))) d[, cov_age := NULL]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("lupu_2024_laws_of_war_", tab, ".csv")))
  cat(tab, nrow(d), "\n")
}
build("usa.txt", "us", 2009); build("uk.txt", "uk", 2198); build("fr.txt", "fr", 2051)
