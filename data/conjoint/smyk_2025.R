##Working-time vignette experiment (Poland) from
##Smyk, M., van der Velde, L., & Tyrowicz, J. (2025). Paying for ideal discretion: A framed
##field experiment on working time arrangements. Gospodarka Narodowa: The Polish Journal of
##Economics, 322(2), 1-28. https://doi.org/10.33119/gn/202289
##Replication data: Harvard Dataverse doi:10.7910/DVN/YHCI85, CC0 1.0. File read from
##"Replication package.7z" (extracted with py7zr): Data/Raw/Results_20210811.xlsx, sheet
##Results (the raw Profitest/Answeo export: 343 rows; column headers hold the Polish question
##text and answer options). Read as text only: Code/_01_experimental_data.do (the authors'
##cleaning: column mapping, wage-change formula, gender and initiator coding) and
##__ReadMe.txt; the article PDF (pdftotext) for the design.
##Usage: Rscript smyk_2025.R <dir holding Results_20210811.xlsx> <output dir>
##
##Answeo online panel, Poland, from 23 April 2021. Each respondent read three third-person
##vignettes in a fixed order (task 1 hairdresser, base pay 3,200 PLN "do ręki"; task 2 lawyer
##in a large law firm, 6,400 PLN; task 3 retail salesperson, part time, 1,600 PLN; one
##profile per task) about a worker whose fixed working hours become flexible (same average
##hours). Two factors were randomized per vignette (article, "Treatments"/"Randomization"):
##  attr_name       the worker's name, shown in text and as a cartoon, which carries the
##                  worker's gender: Adam/Anna (task 1), Marek/Maria (task 2),
##                  Krzysztof/Karolina (task 3; the article's figure note says Karol, the
##                  questionnaire text in the export says Krzysztof, which is used).
##  attr_initiator  who initiates the change: "Employee" / "Employer" (the authors' value
##                  labels in _01_experimental_data.do). The vignette sentence itself is not in
##                  the deposit or the article; on screen the employer was the salon owner
##                  ("właściciel"), the law-firm partners or the shop owners (manipulation-
##                  check options in the export). Taken from the assignment string GROUP#1,
##                  e.g. "Adam - właściciel, Marek - sam, Karolina - manager": sam/sama =
##                  employee, właściciel/manager = employer (this reproduces the authors'
##                  treatment_initiator coding for all 16 strings).
##Randomization is restricted (article): tasks 1 and 2 have opposite gender and opposite
##initiator, and task 3 takes one of the two remaining gender x initiator combinations, so
##every respondent sees both genders and both initiators and no combination twice (16
##sequences): restrictions = yes.
##Outcomes (export headers, Polish):
##  rating            "Zgodnie z wcześniejszym opisem, <imię> będzie mieć odtąd zmienne godziny
##                    czasu pracy. Jak Twoim zdaniem powinno zmienić się wynagrodzenie
##                    <imienia> w związku z tą zmianą?" 1 = powinno zmaleć (decrease),
##                    2 = powinno pozostać bez zmian (no change), 3 = powinno wzrosnąć
##                    (increase); codes as stored.
##  rating_wage_change_pln  the follow-up amount, signed: "o 50 zł", "o 100 zł", ... options
##                    (60, 120 and 30 options of 50 PLN for tasks 1-3), stored as -50 x option
##                    for a decrease, +50 x option for an increase, 0 for no change (the
##                    authors' formula in PLN; they then convert to USD). The "other amount"
##                    fields are empty in the export.
##Task-level: trial_occupation (English, from the article) and trial_base_pay_pln.
##Not kept: the manipulation checks and the "would most Poles agree" follow-ups, the later
##waiting-time discrete choice (GROUP#3), value rankings.
##22 respondents have no answer for task 3 (those tasks are omitted; the authors drop these
##respondents, leaving the article's 321 participants and 963 vignettes). One TOKEN occurs
##twice (two rows from different collector samples, 14 minutes apart); kept as two ids, as in
##the authors' reshape (i(TOKEN START)). id = row number of the export.
##Covariates: cov_gender (COLLECTOR "ANSWEO Kobiety" -> female, "ANSWEO Mężczyźni" -> male,
##the sample the panel recruited from; the authors' `female` coding), cov_age (years, typed
##number; kept when a plausible whole number), cov_education (Polish answer text: podstawowe,
##zasadnicze zawodowe, średnie, wyższe), cov_income (household finances, Polish answer text),
##cov_manager (managerial experience, Polish answer text), cov_duration_sec (TIME, whole
##survey). Dropped: TOKEN (panel token), START (timestamp); the EMAIL, NAME, ID and
##PROMO_CODE columns of the export are empty.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_excel(file.path(raw, "Results_20210811.xlsx"), sheet = "Results")
nm <- names(x)
stopifnot(nrow(x) == 343, all(sapply(c("EMAIL", "NAME", "ID", "PROMO_CODE"), function(v) all(is.na(x[[v]])))))
opts <- function(i) { h <- strsplit(nm[i], "\n", fixed = TRUE)[[1]]; sub("^\\([0-9]+\\)\\s*", "", trimws(h[grepl("^\\([0-9]+\\)", trimws(h))])) }
## (task, female name, male name, direction cols F/M, decrease cols F/M, increase cols F/M, n options)
tk <- list(list(1L, "Anna", "Adam", c(24, 26), c(28, 30), c(32, 34), 60L),
           list(2L, "Maria", "Marek", c(56, 58), c(60, 62), c(64, 66), 120L),
           list(3L, "Karolina", "Krzysztof", c(88, 90), c(92, 94), c(96, 98), 30L))
g1 <- x[["GROUP#1"]]
rows <- list()
for (t in tk) {
  fem <- t[[2]]; mal <- t[[3]]
  stopifnot(grepl(fem, nm[t[[4]][1] - 1]), grepl(mal, nm[t[[4]][2] - 1]),
            grepl(paste0(fem, ".*zmaleć"), nm[t[[5]][1] - 1]) || t[[1]] == 3L,
            all(sapply(c(t[[5]], t[[6]]), function(i) length(opts(i)) == t[[7]])),
            opts(t[[4]][1]) == c("powinno zmaleć", "powinno pozostać bez zmian", "powinno wzrosnąć"))
  who <- regmatches(g1, regexpr(paste0("(", fem, "|", mal, ") - [^ ,]+"), g1))
  stopifnot(length(who) == 343)
  name <- sub(" - .*", "", who); role <- sub(".* - ", "", who)
  stopifnot(all(role %in% c("sam", "sama", "właściciel", "manager")))
  f <- name == fem
  dir <- ifelse(f, x[[t[[4]][1]]], x[[t[[4]][2]]])
  stopifnot(all(is.na(x[[t[[4]][1]]][!f])), all(is.na(x[[t[[4]][2]]][f])))
  dec <- ifelse(f, x[[t[[5]][1]]], x[[t[[5]][2]]]); inc <- ifelse(f, x[[t[[6]][1]]], x[[t[[6]][2]]])
  amt <- fifelse(dir == 2, 0, fifelse(dir == 1, -50 * dec, 50 * inc))
  stopifnot(all(!is.na(amt[!is.na(dir)])), all(is.na(dec[dir %in% 2:3])), all(is.na(inc[dir %in% 1:2])))
  rows[[t[[1]]]] <- data.table(id = seq_len(343), task = t[[1]], profile = 1L, rating = as.integer(dir),
                               rating_wage_change_pln = amt, attr_name = name,
                               attr_initiator = fifelse(role %in% c("sam", "sama"), "Employee", "Employer"))
}
d <- rbindlist(rows)[!is.na(rating)]
d[, `:=`(trial_occupation = c("hairdresser", "lawyer", "retail salesperson")[task], trial_base_pay_pln = c(3200L, 6400L, 1600L)[task])]
## the authors' initiator coding (treatment index ranges) and the string parse agree
enc <- match(g1, sort(unique(g1)))
auth <- rbind(data.table(id = 1:343, task = 1L, emp = enc %in% c(1:4, 9:12)),
              data.table(id = 1:343, task = 2L, emp = enc %in% c(5:8, 13:16)),
              data.table(id = 1:343, task = 3L, emp = enc %in% c(2, 3, 6, 7, 10, 12, 13, 16)))
chk <- merge(d, auth, by = c("id", "task"))
stopifnot(all((chk$attr_initiator == "Employee") == chk$emp))
stopifnot(d[, .N, task][order(task), N] == c(343, 343, 321))
## covariates
lab <- function(i, v) opts(i)[as.integer(v)]
age <- suppressWarnings(as.numeric(x[[154]])); age[!(age %% 1 == 0 & age >= 15 & age <= 100)] <- NA
tm <- as.numeric(difftime(as.POSIXct(paste("1970-01-01", x$TIME), tz = "UTC"), as.POSIXct("1970-01-01", tz = "UTC"), units = "secs"))
stopifnot(all(x$COLLECTOR %in% c("ANSWEO Kobiety", "ANSWEO Mężczyźni")), grepl("wykształcenie", nm[151]),
          grepl("wiek", nm[153]), grepl("gospodarowania", nm[155]), grepl("nadzorujesz", nm[109]))
cv <- data.table(id = 1:343, cov_gender = fifelse(x$COLLECTOR == "ANSWEO Kobiety", "female", "male"), cov_age = as.integer(age),
                 cov_education = lab(152, x[[152]]), cov_income = lab(156, x[[156]]), cov_manager = lab(110, x[[110]]),
                 cov_duration_sec = tm)
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "smyk_2025_working_time.csv"))
