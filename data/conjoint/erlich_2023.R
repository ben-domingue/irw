##Local-candidate conjoint (Ukraine, Study 2) from
##Erlich, A., & Beauvais, E. (2023). Explaining women's political underrepresentation in
##democracies with high levels of corruption. Political Science Research and Methods, 11(4),
##804-822. https://doi.org/10.1017/psrm.2022.46
##Replication data: Harvard Dataverse doi:10.7910/DVN/P9E3WZ, CC0 1.0, no restricted files, no
##terms. File read: STUDY_2_V2.1.zip -> ukr_gender_coint/raw_data/2020_gender_survey_data_wt_v2.dta
##(one row per respondent; Stata value labels carry the level text). The authors' cleaning
##script (scripts/01_gender_conjoint_clean.R) and cjoint design (04_cjoint_constraints.R) were
##read as text only. STUDY_1_V2.zip (Study 1, a photo experiment with one manipulated factor,
##candidate gender) is not a conjoint and is not built.
##Usage: Rscript erlich_2023.R <dir holding the .dta> <output dir>
##
##Info Sapiens online opt-in panel (fielded for NDI), 20-24 July 2020, urban Ukraine (villages
##not in the frame). 2,201 rows in the file; the authors keep SPEED == 2 (46 speeders dropped),
##giving 2,155 respondents, which matches the article (2,155; 17,240 profiles). 4 pairs of
##hypothetical local candidates (P1-P4 = task; suffix 1/2 = profile, both RECORDED).
##Attributes (value labels = the English translation; the survey ran in Ukrainian or Russian,
##QLANG, so the displayed Cyrillic text is not in the deposit):
##  attr_name        candidate name, shown first (48 names). The randomized factors were name
##                   gender (P*GEND*: "Female names"/"Male names") and name type (P*TYPE*:
##                   Ukrainian / Russian / Neutral names); each name belongs to one cell, so
##                   both are recoverable from the name and are not stored as attributes. Name
##                   type, per the file: Ukrainian = Shpak, Martseniuk, Protsiv, Didukh, Stanko,
##                   Halytska, Kovalchuk, Kulish, Kulyk, Humeniuk, Stefaniv, Shymanskyi, Stetsko,
##                   Zaporozhets, Boichuk, Yarema; Russian = Kuznetsova, Iershova, Nikitina,
##                   Kalinina, Tokareva, Kondratieva, Volkova, Beliaieva, Lebedev, Fedorov,
##                   Smyrnov, Krupenin, Ilyin, Nikonov, Popov, Ivanov; Neutral = the other 16.
##                   8 names per gender x type cell; the script checks each name has one cell.
##  attr_issue (priority issue), attr_age, attr_family (family status), attr_children,
##  attr_experience (political experience). attrpos_* = position 1-5 of these five below the
##  name, from ATTRBT1-5 (attribute order randomized per respondent; constant across tasks).
##RESTRICTION: in the data a 25-year-old candidate never has 15 years of experience (checked
##below). The authors' cjoint design (04_cjoint_constraints.R) also lists 35 years old x 15
##years as excluded, but that combination occurs in every task (about 300 profiles each), so the
##data follow the 25-only rule. Age shares are unequal (25 years old about 28%) as a result.
##Other attributes look independent and uniform.
##Outcomes, both asked of each candidate separately (one, both or neither can be yes), so
##they are binary ratings, not choices (1 = Yes, 0 = No):
##  rating      "Would you vote for these candidates?" (lead-in in the article: "Imagine that
##              these candidates are from the party that you would consider supporting in local
##              elections.")
##  rating_win  "Do you think these candidates could win local election?" (variable label only;
##              not discussed in the article's main text). In pair 2 the WIN value labels are
##              Russian (Да/Нет) instead of Yes/No, same codes; both map to 1/0 here. (The
##              authors' WIN == "Yes" recode would score every pair-2 answer 0.)
##Covariates: cov_female (1 = female respondent), cov_age (years), cov_interview_language
##(Ukrainian/Russian), cov_macroregion, cov_settlement_type, cov_survey_weight (wt_fin, the
##authors' weight to the non-rural population). Dropped: PANELID (panel member ID), ID re-keyed,
##dates, all other survey items, the authors' derived sexism scales (hs, bs).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "2020_gender_survey_data_wt_v2.dta"))
s <- s[as.integer(s$SPEED) == 2L, ]
stopifnot(nrow(s) == 2155)
lab <- function(x) as.character(as_factor(x))
s$rid <- seq_len(nrow(s))
pos <- sapply(1:5, function(k) lab(s[[paste0("ATTRBT", k)]]))
anames <- c(issue = "Priority issue", age = "Age", family = "Family status", children = "Children",
            experience = "Political experience")
stopifnot(all(pos %in% anames))
d <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  v <- function(x) lab(s[[sprintf("P%d%s%d", t, x, p)]])
  yn <- function(x) { z <- v(x); stopifnot(all(z %in% c("Yes", "No", "Да", "Нет"))); as.integer(z %in% c("Yes", "Да")) }
  data.table(id = s$rid, task = t, profile = p, rating = yn("VOTE"), rating_win = yn("WIN"),
             attr_name = gsub("\\s+", " ", v("NAME")), attr_issue = v("ISS"), attr_age = v("AGE"),
             attr_family = v("FAM"), attr_children = v("CHILD"), attr_experience = v("EXP"),
             gend = v("GEND"), type = v("TYPE"))
}))))
for (n in names(anames)) d[, paste0("attrpos_", n) := apply(pos, 1, function(r) match(anames[[n]], r))[id]]
cv <- data.table(id = s$rid, cov_female = as.integer(lab(s$RSPSEX) == "Female"), cov_age = as.integer(s$RSPAGE),
                 cov_interview_language = lab(s$QLANG), cov_macroregion = lab(s$MACREG),
                 cov_settlement_type = lab(s$SETTTYPE), cov_survey_weight = as.numeric(s$wt_fin))
d <- merge(d, cv, by = "id")
stopifnot(d[, uniqueN(paste(gend, type)), attr_name][, all(V1 == 1)], d[, uniqueN(attr_name), .(gend, type)][, all(V1 == 8)])
d[, c("gend", "type") := NULL]
stopifnot(!anyNA(d$attr_name), d[, uniqueN(attr_name)] == 48, d[attr_experience == "15 years", !any(attr_age == "25 years old")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "erlich_2023_ukraine_candidates.csv"))
