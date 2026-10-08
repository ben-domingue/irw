##Foreign-direct-investment conjoint (Tunisia) from
##Jamal, A., & Milner, H. V. (2022). Islam and mass preferences toward foreign direct
##investment in Tunisia. Journal of Experimental Political Science, 9(3), 314-325.
##https://doi.org/10.1017/XPS.2021.5 (full text not read; the landing page gives N = 1,502)
##Replication data: Harvard Dataverse doi:10.7910/DVN/745PK1, CC0 1.0, no restricted files.
##File read: cj_a.rds (the authors' analysis extract of the Qualtrics/SPSS conjoint file, a
##tibble with SPSS variable labels). jepsr.Rmd, amce.R and jepsr.pdf (results appendix) were
##read as text (not run). The deposit's vignette experiment (the_data.rds) is a separate,
##non-conjoint experiment and is not used.
##Usage: Rscript jamal_2022.R <dir holding cj_a.rds> <output dir>
##
##1,505 rows in the extract; one (no attribute values, as the authors note) is dropped, and
##respondents with no rating and no choice are omitted: 1,497 respondents (article: 1,502). Five tasks, each a
##pair of hypothetical foreign investments (task = round 1-5, profile 1 = the first of the
##pair, "Investment A", from the source item number 1-10: task = (item + 1) %/% 2, as the
##authors parse it). Six attributes, English text as stored: company nationality (American,
##French, Saudi Arabian, Tunisian), industry ("in banks", "in call centers", "in factories",
##or "(not shown)" = not mentioned), urban/rural location, who the jobs are for ("for men", "for women
##who don't wear the hijab,", "for women who wear the hijab", "for women, including those who
##wear the hijab,", or "(not shown)"), skill sentence (or "(not shown)"), wadu/prayer-room
##sentence (or "(not shown)"). "(not shown)" codes the randomized "not mentioned" level (blank in
##the source; the authors model it as level "NA"): the design left that attribute off the profile. Trailing commas are as in the source.
##Outcomes, same tasks, one table:
##  choice = "Which investment do you prefer most? Investment A or Investment B?" (SPSS label),
##    forced; 4 tasks that have ratings but no choice keep choice missing.
##  rating = support for each investment, REVERSED so that higher = more support: source
##    1 = "Very strongly support" .. 7 = "Very strongly oppose"; rating = 8 - source, as the
##    authors do (jepsr.Rmd make_y_cj). The stem wording is not in the deposit (labels only
##    "Investment A" / "Investment B"). "Decline to answer (do not read)" set missing as the
##    authors do. 14,637 of the 14,970 rows have a rating.
##Rows with neither outcome are omitted. Randomization rules and attribute order are not
##documented; level shares are roughly equal, with the "(not shown)" level 1/5 to 1/3 of profiles.
##The survey was administered in Tunisia (enumerator-recorded gender), presumably in Arabic;
##the deposit holds English text only.
##Covariates: cov_religiosity (Devoutly/Somewhat/Hardly religious), cov_gender (male/female,
##lowercased from the factor labels of Setup1b "Enumerator: Please indicate whether the respondent
##is male or female."), cov_age (Demo1 "How old are you", years), cov_employment, cov_income
##(monthly, dinar bands), cov_education (Demo10 "What is the highest level of education you have
##completed?", factor label text, e.g. "Secondary"), cov_raised (Rural/Urban), all as the English
##label text in cj_a.rds.
##Spot check (appendix Table 6, under-40 respondents with employment recorded, lm): jobs for
##women who don't wear the hijab vs for men, rating -0.905 / choice -0.167 (appendix -0.911 /
##-0.169), factories vs call centers +0.549 / +0.106 (0.548 / 0.106), n 974 / 986 respondents
##(970 / 981): close; the authors' cjoint estimator and covariate-join filtering differ slightly.
##PII: the source Qualtrics ResponseId is dropped; id = rank of ResponseId, re-keyed 1-1,497.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(as.data.frame(readRDS(file.path(raw, "cj_a.rds"))))
x <- x[nationality1 != ""]
stopifnot(nrow(x) == 1504, !anyDuplicated(x$ResponseId))
x[, id := match(ResponseId, sort(ResponseId))]
num <- function(f) { v <- as.integer(f); v[!is.na(v) & v > 7] <- NA_integer_; v }
d <- rbindlist(lapply(1:10, function(i) {
  t <- (i + 1L) %/% 2L; p <- 2L - i %% 2L
  ch <- as.integer(x[[sprintf("cj%db", t)]]); r <- num(x[[sprintf("cj%da_%d", t, p)]])
  data.table(id = x$id, task = t, profile = p, choice = as.integer(ch == p), rating = 8L - r,
             attr_nationality = x[[paste0("nationality", i)]], attr_industry = x[[paste0("industry", i)]],
             attr_location = x[[paste0("urbanrural", i)]], attr_jobs_for = x[[paste0("benefactor", i)]],
             attr_skill = x[[paste0("skill", i)]], attr_prayer_facilities = x[[paste0("wadu", i)]])
}))
for (v in grep("^attr_", names(d), value = TRUE)) d[get(v) == "", (v) := "(not shown)"]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
stopifnot(!anyNA(d$attr_nationality), !anyNA(d$attr_location), d[, all(rating %in% 1:7 | is.na(rating))])
## level check: the source rating labels are 1 = Very strongly support .. 7 = Very strongly oppose
stopifnot(levels(x$cj1a_1)[c(1, 7)] == c("1 - Very strongly support", "7 - Very strongly oppose"))
d <- d[!is.na(choice) | !is.na(rating)]
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
lab <- function(f) as.character(f)
cv <- x[, .(id, cov_religiosity = lab(Relig2), cov_gender = tolower(lab(Setup1b)), cov_age = as.integer(Demo1),
            cov_employment = lab(Emp1), cov_income = lab(Inc1), cov_education = lab(Demo10), cov_raised = lab(Demo4))]
stopifnot(all(cv$cov_gender %in% c("female", "male")))
d <- merge(d, cv, by = "id")
d[, id := match(id, sort(unique(id)))]
stopifnot(uniqueN(d$id) == 1497)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jamal_2022_fdi_tunisia.csv"))
