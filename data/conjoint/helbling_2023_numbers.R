##Immigration-policy factorial vignettes (Studies 1-3) from
##Helbling, M., Maxwell, R., & Traunmüller, R. (2023). Numbers, selectivity, and rights: The
##conditional nature of immigration policy preferences. Comparative Political Studies, 57(2),
##254-286. https://doi.org/10.1177/00104140231178737
##Replication data: Harvard Dataverse doi:10.7910/DVN/RCVA0X, CC0 1.0, no restricted files.
##Files read (Dataverse "original format" downloads): replication_data_numbers_selectivity_
##rights_study_1_2.dta (saved as study12.dta) and replication_data_numbers_selectivity_rights_
##study_3.dta (saved as study3.dta). replication_code_numbers_selectivity_rights.R (authors'
##code) read as text. The article is not open access; the deposit has no questionnaire.
##Usage: Rscript helbling_2023_numbers.R <raw dir> <output dir>
##
##In each study respondents read a proposed German immigration policy and said how far they
##agreed with it. Every factor describes the evaluated policy. THREE TABLES (three fieldings with
##different factor sets, analysed separately by the authors):
##
##Study 1 (study12.dta waves 1-13, 7,145 rated vignettes) is HELD (batch 6): its levels below are the
##  survey's condition names, not displayed text; its builder is in oneoff/conjoint-scouting/batch6/held_scripts.
##  (was helbling_2023_numbers_rights_s1) 2 x 2 x 2,
##  one vignette per row (Gruppe_1, 8 cells). Attribute text = the three components of the
##  Gruppe_1 value labels (the survey software's condition names, e.g. "erhöhen-erleichtern-
##  ausweiten"), NOT the displayed sentence, which the deposit does not hold:
##    attr_numbers       erhöhen / verschärfen (the authors' highnumb: increase / decrease numbers)
##    attr_requirements  erleichtern / verschärfen (easyacc: lower / raise entry requirements)
##    attr_rights        ausweiten / einschränken (morerights: extend / restrict migrant rights)
##  checked against the authors' recodes of Gruppe_1 (code lines 33-44).
##helbling_2023_numbers_rights_s2 (Study 2, waves 14-23, 9,806 rated vignettes): displayed text fragments
##  as stored in c_0034-c_0036 ("exp politik_1-3"); the deposit stores some of them in Latin-1,
##  converted to UTF-8 here:
##    attr_numbers       "zu erhöhen." / "zu veringern." (sic)
##    attr_requirements  "in Bezug auf Bildung erleichtern" / "... verschärfen" / "in Bezug auf
##                       Nationalitäten erleichtern" / "... verschärfen"
##    attr_rights        "Rechte ausweiten, damit sie stärker vom Wohlfahrtsstaat profitieren
##                       können." and the three other rights x welfare/customs sentences
##  Outcome for S1 and S2: rating = agree_vig, "Inwieweit wären Sie mit einer solchen
##  Zuwanderungspolitik einverstanden?" (variable label of v_228 and its per-wave copies),
##  1 "Voll und ganz" ... 5 "Überhaupt nicht" (value labels), stored raw: LOWER = MORE AGREEMENT
##  (the authors reverse it). 9 "Weiß nicht" and 0 (unlabelled) are NA, as in the authors' code.
##  The .dta has no respondent id: id = row number. Rows are respondent x wave; whether
##  the waves re-interview the same people is not documented. cov_wave = wave.
##  Covariates (value labels of study12.dta): cov_gender (v_2 Männlich/Weiblich/Divers ->
##  male/female/other), cov_birth_year (v_3 "Jahr"; the authors compute age as 2020 - v_3),
##  cov_education (v_4 Bildung, label text), cov_german_citizen (v_9 Staatsbürgerschaft, Ja /
##  Nein; 0 = NA), cov_birth_country (v_284 Land, label text; code 1 "Bitte Geburtsland
##  auswählen" = NA), cov_left_right (v_121, label text "0 - links" ... "10 - rechts"; 0 = NA),
##  cov_vote_intention (v_122 Wahlabsicht, label text incl. "Weiß nicht", "Ich würde nicht
##  wählen gehen"; 0 = NA), cov_limit_immigration (v_240 "Deutschland sollte die Zuwanderung
##  begrenzen.", label text "0 - Stimme gar nicht zu" ... "7 - Stimme voll und ganz zu"; 0 = NA).
##  Rows with no Gruppe_1 / c_0034 (the 645 rows with wave missing) or no valid rating are omitted.
##  NOT BUILT from study12.dta: a paired-profile experiment on who should receive intensive care
##  (c_0004-c_0020: Geschlecht, Alter, Job, Überlebenschance, Kinder, Migration, Strafe for Person
##  1/2, question template in the Auswahl_Person labels). It is not part of this article, and its
##  answers are spread over version-specific variables (Auswahl_Person, dupl1_v_3_*, Personenexp)
##  that the deposit does not document.
##
##helbling_2023_numbers_rights_s3 (Study 3, study3.dta, Qualtrics, 2022): respondents who passed
##  attention_check_1 (answer "Stimme überhaupt nicht zu"; the authors' filter; only they saw the
##  experiment): 2,397; 2,321 with at least one rating (4,591 rated vignettes). Two vignettes each:
##    task 1 (tradeoff_a): a policy to raise or lower immigration from a region:
##      attr_region   tradeoff_a1 "dem Mittleren Osten und Nordafrika" / "europäischen Ländern,
##                    die nicht in der EU sind," (1,584 vs 813: unequal level weights)
##      attr_numbers  tradeoff_a2 "erhöhen" / "verringern"
##      attr_requirements, attr_rights "(not shown)"
##    task 2 (tradeoff_b): the same region and direction (as displayed in task 2: tradeoff_b3,
##      tradeoff_b2 "erhöht" / "verringert") traded off against entry requirements and rights:
##      attr_requirements tradeoff_b5 "erleichtern" / "verschärfen"; attr_rights tradeoff_b9
##      "nur sehr wenige" / "sehr weitgehende". tradeoff_b1 echoes the respondent's task-1
##      answer ("einverstanden" / "nicht einverstanden"): kept as trial_task1_echo. The other
##      fragments (tradeoff_b4, b6, b7, b8) repeat a2, b9, a2, b5 and are not kept.
##  Outcome: rating = support for the policy, answer text mapped as in the authors' code:
##  6 "Voll und ganz unterstützen", 5 "sehr unterstützen", 4 "etwas unterstützen", 3 "etwas
##  ablehnen", 2 "sehr ablehnen", 1 "voll und ganz ablehnen"; "Weiß nicht" / "NA" = NA (higher =
##  more support). Question wording not in the deposit. tradeoff_b_dontknow (a follow-up for 67
##  respondents) is not kept.
##  Covariates (answer text): cov_gender (gender Weiblich/Männlich/Divers), cov_birth_year (age,
##  which holds a year of birth; the authors compute 2022 - age), cov_education (education text;
##  the free-text "Anderer Schulabschluss" field is dropped), cov_left_right (left_right as stored),
##  cov_quality (finished_survey: yes / quality_fail).
##  PII in study3.dta: IPAddress and LocationLatitude/Longitude for all 5,220 rows, plus
##  ResponseId and timestamps: none is read into the table. id = row number among kept rows.
##N vs paper: not checked (paywalled). Randomization restrictions: S1 and S2 are full factorials
##per the authors' cell codes; S3 none documented.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x, drop = integer(0)) { v <- as.numeric(x); l <- attr(x, "labels")
  r <- names(l)[match(v, l)]; r[v %in% drop] <- NA; stopifnot(all(is.na(v) | v %in% drop | !is.na(r))); r }
fix <- function(s) { s <- as.character(s); bad <- !validUTF8(s); s[bad] <- iconv(s[bad], "latin1", "UTF-8"); s }
d12 <- read_dta(file.path(raw, "study12.dta"))
rv <- as.numeric(d12$agree_vig); rv[rv %in% c(0, 9)] <- NA
cv <- data.table(cov_gender = c(Männlich = "male", Weiblich = "female", Divers = "other")[lab(d12$v_2)],
                 cov_birth_year = as.integer(d12$v_3), cov_education = lab(d12$v_4),
                 cov_german_citizen = lab(d12$v_9, 0), cov_birth_country = lab(d12$v_284, 1),
                 cov_left_right = lab(d12$v_121, 0), cov_vote_intention = lab(d12$v_122, 0),
                 cov_limit_immigration = lab(d12$v_240, 0), cov_wave = as.integer(d12$wave))
## Study 1
g <- as.integer(d12$Gruppe_1)
parts <- strsplit(gsub(" ", "", lab(d12$Gruppe_1)), "-")
s1 <- data.table(task = 1L, profile = 1L, rating = as.integer(rv),
                 attr_numbers = sapply(parts, `[`, 1), attr_requirements = sapply(parts, `[`, 2), attr_rights = sapply(parts, `[`, 3), cv)
k <- !is.na(g) & d12$wave %in% 1:13
s1 <- s1[k]; gk <- g[k]
stopifnot(all((s1$attr_numbers == "erhöhen") == (gk %in% 1:4)), all((s1$attr_requirements == "erleichtern") == (gk %in% c(1, 3, 5, 8))),
          all((s1$attr_rights == "ausweiten") == (gk %in% c(1, 2, 5, 7))),
          all(s1$attr_numbers %in% c("erhöhen", "verschärfen")), all(s1$attr_requirements %in% c("erleichtern", "verschärfen")))
## Study 2
s2 <- data.table(task = 1L, profile = 1L, rating = as.integer(rv),
                 attr_numbers = fix(d12$c_0034), attr_requirements = fix(d12$c_0035), attr_rights = fix(d12$c_0036), cv)
s2 <- s2[d12$wave %in% 14:23]
stopifnot(all(s2$attr_numbers %in% c("zu erhöhen.", "zu veringern.")), uniqueN(s2$attr_requirements) == 4, uniqueN(s2$attr_rights) == 4)
for (nm in c("s2")) {   # s1 held: condition names only
  x <- get(nm)[!is.na(rating)]
  stopifnot(all(x$rating %in% 1:5))
  x[, id := seq_len(.N)]; setcolorder(x, "id"); setorder(x, id, task, profile)
  fwrite(x, file.path(out, sprintf("helbling_2023_numbers_rights_%s.csv", nm)))
}
## Study 3
d3 <- as.data.table(read_dta(file.path(raw, "study3.dta"), col_select = c("attention_check_1", "gender", "age", "education", "left_right",
        "finished_survey", "tradeoff_a", "tradeoff_b", "tradeoff_a1", "tradeoff_a2", "tradeoff_b1", "tradeoff_b2", "tradeoff_b3",
        "tradeoff_b5", "tradeoff_b9")))
d3 <- d3[attention_check_1 == "Stimme überhaupt nicht zu"]
stopifnot(nrow(d3) == 2397, all(d3$tradeoff_a1 != ""), all(d3$tradeoff_a1 == d3$tradeoff_b3))
sc <- c("voll und ganz ablehnen" = 1L, "sehr ablehnen" = 2L, "etwas ablehnen" = 3L, "etwas unterstützen" = 4L, "sehr unterstützen" = 5L,
        "Voll und ganz unterstützen" = 6L)
rt <- function(x) { stopifnot(all(x %in% c(names(sc), "Weiß nicht", "NA", ""))); unname(sc[x]) }
d3[, id := seq_len(.N)]
cv3 <- d3[, .(id, cov_gender = c(Weiblich = "female", "Männlich" = "male", Divers = "other")[ifelse(gender == "", NA, gender)],
              cov_birth_year = as.integer(age), cov_education = ifelse(education == "", NA, education),
              cov_left_right = ifelse(left_right == "", NA, as.character(left_right)), cov_quality = ifelse(finished_survey == "", NA, finished_survey))]
t1 <- d3[, .(id, task = 1L, profile = 1L, rating = rt(tradeoff_a), trial_task1_echo = NA_character_, attr_region = tradeoff_a1,
             attr_numbers = tradeoff_a2, attr_requirements = "(not shown)", attr_rights = "(not shown)")]
t2 <- d3[, .(id, task = 2L, profile = 1L, rating = rt(tradeoff_b), trial_task1_echo = ifelse(tradeoff_b1 == "", NA, tradeoff_b1),
             attr_region = tradeoff_b3, attr_numbers = tradeoff_b2, attr_requirements = tradeoff_b5, attr_rights = tradeoff_b9)]
s3 <- rbind(t1, t2)[!is.na(rating)]
stopifnot(!anyNA(s3[, .(attr_region, attr_numbers, attr_requirements, attr_rights)]), all(s3$attr_requirements %in% c("(not shown)", "erleichtern", "verschärfen")))
s3 <- merge(s3, cv3, by = "id")
setorder(s3, id, task, profile)
fwrite(s3, file.path(out, "helbling_2023_numbers_rights_s3.csv"))
