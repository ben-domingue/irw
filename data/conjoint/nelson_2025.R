##Job-offer / state-policy conjoint (US) from
##Nelson, M. J., & Witko, C. (2025). Abortion bans and interstate migration. Political Research
##Quarterly. https://doi.org/10.1177/10659129251394022
##Replication data: Harvard Dataverse doi:10.7910/DVN/IQRRTJ, CC0 1.0. File read: YouGovCleaned.tab
##(Dataverse "original" CSV download; one row per respondent; its first data row repeats the
##header and is dropped). YouGov2022_ConjointCode.R read as text (source of level order and the
##authors' short labels). The other deposit files are observational (CPS/ASEC, ANES, ERA) and not
##used. No questionnaire ships and the article was not read: outcome wording is a PARAPHRASE.
##Usage: Rscript nelson_2025.R <dir holding YouGov.csv> <output dir>
##
##1,200 US adults (YouGov, 2022; `weight` = YouGov sample weight, kept as cov_survey_weight),
##10 tasks, each a pair of hypothetical job offers (Job 1 / Job 2) in another state, 9 attributes
##as displayed text (old-format Qualtrics columns F.<t>.<p>.<k> = level of the attribute in row k,
##F.<t>.<k> = its variable name; equal to the deposit's job<t><A|B>_<attr> columns, stopifnot):
##company size, company culture, 2020 presidential election results in the state, typical home
##price in area, average January temperature, location, salary, recent decision by state
##legislature: economic policy, ... : social policy (incl. the abortion levels). Displayed row
##labels are in `order_conjoint`. Attribute row order was randomized once per respondent (F.t.k
##equal across the 10 tasks; stopifnot) -> attrpos_* (1-9). Trailing spaces in level text trimmed
##(as the authors do). task/profile RECORDED (task t, profile 1 = Job 1 / A, 2 = Job 2 / B).
##Outcomes:
##  choice: which of the two jobs the respondent would take (choice_t 1/2; forced, no opt-out)
##    (paraphrase).
##  rating: each job on a 4-point scale (job1_t, job2_t, 1-4, stored raw). Anchors not deposited;
##    1 is the FAVOURABLE end: the chosen job has the lower rating in most pairs with unequal
##    ratings (printed below); i.e. probably 1 = very likely .. 4 = very unlikely to accept
##    (paraphrase, inferred direction).
##Covariates: cov_survey_weight (weight), cov_birth_year (birthyr); YouGov profile codes kept with
##_code suffix (no codebook deposited): cov_gender_code (gender), cov_education_code (educ),
##cov_pid7_code (pid7), cov_ideo5_code (ideo5), cov_state_code (inputstate, FIPS),
##cov_willingmove_code (willingmove). Dropped: caseid (YouGov id, re-keyed 1..N), the free-text
##`final` comment, all other survey items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "YouGov.csv"), encoding = "UTF-8", colClasses = "character")
stopifnot(x$caseid[1] == "caseid"); x <- x[-1]
stopifnot(nrow(x) == 1200, uniqueN(x$caseid) == 1200)
x[, id := seq_len(.N)]
for (t in 2:10) for (k in 1:9) stopifnot(all(x[[sprintf("F.1.%d", k)]] == x[[sprintf("F.%d.%d", t, k)]]))
d <- rbindlist(lapply(1:10, function(t) rbindlist(lapply(1:2, function(p) {
  y <- data.table(id = x$id, task = t, profile = p,
                  choice = as.integer(x[[paste0("choice_", t)]] == as.character(p)),
                  rating = as.integer(x[[paste0("job", p, "_", t)]]))
  for (k in 1:9) {
    an <- x[[sprintf("F.1.%d", k)]]; lv <- trimws(x[[sprintf("F.%d.%d.%d", t, p, k)]])
    for (v in unique(an)) {
      i <- an == v
      set(y, which(i), paste0("attr_", v), lv[i]); set(y, which(i), paste0("attrpos_", v), k)
      stopifnot(all(lv[i] == trimws(x[[paste0("job", t, c("A", "B")[p], "_", v)]][i])))
    }
  }
  y
}))))
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:4))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(all(d[[v]] != ""))
cv <- x[, .(id, cov_survey_weight = as.numeric(weight), cov_birth_year = as.integer(birthyr),
            cov_gender_code = as.integer(gender), cov_education_code = as.integer(educ), cov_pid7_code = as.integer(pid7),
            cov_ideo5_code = as.integer(ideo5), cov_state_code = as.integer(inputstate), cov_willingmove_code = as.integer(willingmove))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", sort(grep("^attr_", names(d), value = TRUE)), sort(grep("^attrpos_", names(d), value = TRUE))))
setorder(d, id, task, profile)
w <- dcast(d, id + task ~ profile, value.var = c("choice", "rating"))[rating_1 != rating_2]
cat("rows", nrow(d), "resp", uniqueN(d$id), " chosen job has the lower rating in", round(mean((w$rating_1 < w$rating_2) == (w$choice_1 == 1)), 3), "of unequal pairs\n")
print(round(coef(lm(choice ~ attr_statesocial, d)), 3))
fwrite(d, file.path(out, "nelson_2025_abortion_jobs.csv"))
