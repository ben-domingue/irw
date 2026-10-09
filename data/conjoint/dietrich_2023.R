##Welfare-client prioritisation conjoint (Germany, four samples) from
##Dietrich, B., Jankowski, M., Schnapp, K., & Tepe, M. (2023). Prioritizing exceptional social
##needs: Experimental evidence on the role of discrimination and client deservingness in public
##employees' and citizens' discretionary behavior. Public Policy and Administration.
##https://doi.org/10.1177/09520767231210025
##Replication data: Harvard Dataverse doi:10.7910/DVN/6MLKJZ, CC0 1.0, no restricted files.
##Files read: data_civic.tab, data_HSVN.tab, data_rh.tab, data_UHH.tab (Dataverse "original
##format" = Qualtrics CSV exports with two header rows; row 1 holds the question text) and
##survey_data.tab (original CSV; only v9 = Qualtrics response ID, student, sector, west).
##Read as text, not run: 01_preparation_function.R, 03_data_prep_and_merge.R, 04_analysis.R.
##Usage: Rscript dietrich_2023.R <raw dir> <output dir>
##
##Respondents play a caseworker at a German job centre: in each of 8 paired tasks they see two
##applicants for basic income support (ALG II), "Person A" and "Person B", described by 8
##attributes, and answer "Wessen Antrag lassen Sie zuerst bewilligen?" (Whose application do
##you approve first?), forced choice, no opt-out (choice). Qualtrics conjoint export: F-t-a =
##attribute shown in row a of task t, F-t-p-a = its level for profile p; tasks 7-8 are stored
##in Q87/Q90 (the authors' 01_preparation_function.R maps them to cj7/cj8). Attribute row
##order was randomized per respondent (fixed across that respondent's tasks; checked), kept
##as attrpos_<attribute> (1-8).
##Attributes (German displayed text, the authors' English in 01_preparation_function.R):
##  gender (Geschlecht: Maennlich/Weiblich), age (Alter: 23/36/48/57 Jahre), citizenship
##  (Staatsangehoerigkeit: Vietnam, Syrien, Rumaenien, Tuerkei, Frankreich, Deutschland),
##  education (Bildungsgrad), duration_benefits (Dauer des ALG II Bezuges), household
##  (Zusammensetzung der Bedarfsgemeinschaft), unemployment_reason (Grund fuer
##  Arbeitslosigkeit), cooperation (Grad der Mitwirkung (zum Beispiel Puenktlichkeit oder
##  Vollstaendigkeit der Unterlagen)).
##ONE TABLE with cov_sample: the authors pool the four samples in one data frame and compare
##them (Figures 1-4 by sample/sector); the attribute text is identical. cov_sample = the file:
##"civic" (general-population online sample; cov_sector = the authors' public/private-sector
##employment variable, NA outside civic employees), "uhh", "hsvn", "rh" (student samples;
##cov_student = the authors' label from survey_data: General Student Sample / Public
##Administration / Social Work).
##Exclusions as the authors (01_preparation_function.R): preview responses, Progress < 100,
##and respondents who refused the consent item cj0_daten ("Nein"; their rows are not used at
##all). Tasks with no answer are dropped. The authors recode a choice value "x" in task 4 to
##Person A; that one task (1 respondent) is dropped here instead, since "x" is not an answer option.
##Covariates (answer text as stored, German): cov_gender (Geschlecht: Weiblich -> female,
##Maennlich -> male, other answers -> other, empty -> NA); cov_age (Alter, typed; whole numbers
##16-99 kept, else NA); cov_left_right (cj22_sd_1, left-right self-placement as stored: the
##end points as their labels "links"/"rechts", the points between as numbers 2-9); cov_east_west (survey_data `west`, the authors' coding). Further
##attitude batteries, income, religion, migration background, children and free-text fields
##(study programme, employer, job function, "other" texts) are not kept.
##PII in the deposit, dropped: IP addresses and GPS latitude/longitude in all four exports,
##Qualtrics ResponseIds (also v9 in survey_data), a panel offer_click_id in the civic export.
##Respondent ids are re-keyed to 1..N (civic first, then hsvn, rh, uhh).
##No survey weight is deposited (the authors' entropy-balancing weights are derived, not kept).
##N: 3,882 respondents (civic 2,482, uhh 744, hsvn 528, rh 128); the article was not accessible,
##so N is not checked against it. No reported number reproduced.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
an <- c("Geschlecht" = "gender", "Alter" = "age", "Staatsangehörigkeit" = "citizenship", "Bildungsgrad" = "education",
        "Dauer des ALG II Bezuges" = "duration_benefits", "Zusammensetzung der Bedarfsgemeinschaft" = "household",
        "Grund für Arbeitslosigkeit" = "unemployment_reason",
        "Grad der Mitwirkung (zum Beispiel Pünktlichkeit oder Vollständigkeit der Unterlagen)" = "cooperation")
sv <- fread(file.path(raw, "survey_data.csv"), encoding = "UTF-8", select = c("v9", "student", "sector", "west"), colClasses = "character")
one <- function(file, sam) {
  x <- fread(file.path(raw, file), encoding = "UTF-8", colClasses = "character")[-(1:2)]
  x <- x[!grepl("preview", DistributionChannel)]
  pr <- suppressWarnings(as.numeric(x$Progress)); x <- x[pr == 100 | is.na(pr)]
  x <- x[cj0_daten != "Nein"]
  ch <- c(paste0("cj", 1:6, "_choice"), "Q87", "Q90")
  rbindlist(lapply(1:8, function(t) {
    rbindlist(lapply(1:2, function(p) {
      r <- data.table(rid = x$ResponseId, sample = sam, task = t, profile = p, ans = x[[ch[t]]])
      for (k in 1:8) {
        nm <- x[[sprintf("F-%d-%d", t, k)]]; lv <- x[[sprintf("F-%d-%d-%d", t, p, k)]]
        r[, paste0("n", k) := nm][, paste0("l", k) := lv]
      }
      r[, `:=`(gender_r = x$Geschlecht, age_r = x$Alter, lr = x$cj22_sd_1)]
    }))
  }))
}
d <- rbindlist(list(one("data_civic.csv", "civic"), one("data_HSVN.csv", "hsvn"), one("data_rh.csv", "rh"), one("data_UHH.csv", "uhh")))
cat("choice values:", paste(names(table(d$ans)), table(d$ans), collapse = "; "), "\n")
d <- d[grepl("^Person [AB]", ans)]
d[, choice := as.integer(substr(sub("^Person ", "", ans), 1, 1) == c("A", "B")[profile])]
stopifnot(d[, sum(choice), .(rid, task)][, all(V1 == 1)], d[, .N, .(rid, task)][, all(N == 2)])
# attribute names and positions: complete, the 8 known names, fixed within respondent
nms <- as.matrix(d[, paste0("n", 1:8), with = FALSE]); stopifnot(all(nms %in% names(an)), all(apply(nms, 1, uniqueN) == 8))
d[, ord := do.call(paste, c(.SD, sep = "|")), .SDcols = paste0("n", 1:8)]
cat("respondents whose attribute order varies across tasks:", d[, uniqueN(ord), rid][V1 > 1, .N], "\n")
for (k in 1:8) for (nmk in names(an)) {
  v <- an[[nmk]]; w <- d[[paste0("n", k)]] == nmk
  if (k == 1) d[, paste0("attr_", v) := NA_character_][, paste0("attrpos_", v) := NA_integer_]
  d[w, paste0("attr_", v) := get(paste0("l", k))][w, paste0("attrpos_", v) := k]
}
stopifnot(!anyNA(d[, grep("^attr", names(d)), with = FALSE]), all(as.matrix(d[, grep("^attr_", names(d)), with = FALSE]) != ""))
d <- merge(d, sv, by.x = "rid", by.y = "v9", all.x = TRUE)
d[, cov_gender := fcase(gender_r == "Weiblich", "female", gender_r == "Männlich", "male", gender_r == "", NA_character_, default = "other")]
ag <- suppressWarnings(as.numeric(d$age_r)); d[, cov_age := fifelse(!is.na(ag) & ag == round(ag) & ag >= 16 & ag <= 99, as.integer(ag), NA_integer_)]
d[, cov_left_right := fifelse(lr == "", NA_character_, lr)]
d[, `:=`(cov_sample = sample, cov_student = fifelse(student %in% c("", NA), NA_character_, student),
         cov_sector = fifelse(sector %in% c("Private Sector", "Public Sector"), sector, NA_character_),
         cov_east_west = fifelse(west %in% c("east", "west"), west, NA_character_))]
so <- c(civic = 1, hsvn = 2, rh = 3, uhh = 4)
ids <- unique(d[, .(rid, s = so[sample])])[order(s, rid)][, id := .I]
d <- merge(d, ids[, .(rid, id)], by = "rid")
keep <- c("id", "task", "profile", "choice", paste0("attr_", an), paste0("attrpos_", an),
          "cov_sample", "cov_student", "cov_sector", "cov_gender", "cov_age", "cov_left_right", "cov_east_west")
d <- d[, ..keep]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dietrich_2023_welfare_priority.csv"))
