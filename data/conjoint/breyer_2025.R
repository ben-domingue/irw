##Social status conjoint (Switzerland) from
##Breyer, M. (2025). Perceptions of the social status hierarchy and its cultural and economic sources.
##European Journal of Political Research, 64(2), 810-833. https://doi.org/10.1111/1475-6765.12712
##Replication data: Harvard Dataverse doi:10.7910/DVN/8JFKC1, CC0 1.0. Files read: df_choice_rep.rds,
##df_rating_rep.rds (long conjoint files) and the column map stored as an attribute of df_wide_rep.rds
##(Qualtrics question text, German). replication_cj.Rmd/.html read as text, not run.
##Usage: Rscript breyer_2025.R <dir holding the .rds files> <output dir>
##
##Online survey of Swiss residents, in German (the column map's question text; the survey is about
##"Gruppen am oberen Rand der Gesellschaft ... in der Schweiz"). 5 tasks x 2 persons ("Person 1",
##"Person 2"), 8 attributes, all shown in every task. task and profile are recorded in both files.
##Outcomes (same tasks, one table):
##  choice = df_choice_rep `selected`: "Welche der beiden Personen steht Ihrer Meinung nach aktuell in
##           der Schweiz weiter oben? Bitte wählen Sie diese Person aus." Forced, no opt-out (exactly
##           one chosen per task, checked).
##  rating = df_rating_rep `selected`: "Bitte positionieren Sie beide Personen ebenfalls auf der
##           gesellschaftlichen Skala von «unten» (1) bis «oben» (10)." 1-10, higher = higher status.
##LINKAGE (inferred): the two files number respondents differently (2,382 in the choice file, 2,436 in
##the rating file) and share no key. Each respondent's 10 profiles (task, profile, 8 attributes) form a
##signature that is unique within each file; 2,319 respondents match exactly on all 10 rows and are
##joined. 63 choice-file respondents have no rating match (rating NA) and 117 rating-file respondents
##have no choice match (choice NA, covariates NA). No partial matches exist: an unmatched choice-file
##respondent shares at most 1 of 10 rows with any unmatched rating-file respondent (unrelated pairs
##share up to 3 rows by chance). id = choice-file respondent
##number; rating-only respondents get 2383-2499 in rating-file order. Total 2,499 respondents. The
##authors analyse the two files separately (cregg, clustered by their own respondent numbers).
##Attribute text: the files store the authors' English level labels (factor levels); the German
##screen text is not deposited. Restrictions: occupation and education never combine freely
##(Electrician only with Vocational degree; Primary school teacher, Engineer, Lawyer only with
##University degree; Gardener never with University degree); the authors model Occupation *
##Education; no source states the rule -> observed. Level weights observed: migration background
##None ~60% vs ~10% each for the four countries. Attribute order is not recorded or documented.
##Covariates (choice file, constant within respondent): the authors' respondent groupings, kept with
##their names and labels: cov_gender (male/female; the wide file also has "other", absent here),
##cov_age_group (18-39 years etc.), cov_edu (low/medium/high), cov_income_group_eq, cov_sexual_orientation,
##cov_migrationb, cov_migrationb_not_german, cov_lr_group, cov_urban_cat, cov_urban_2cat, cov_sss_group2,
##cov_sss_group3, cov_sss_past_group, cov_sss_future_group, cov_sdo_group. The wide file (raw age, SSS,
##SDO, left-right) has no respondent key and is not used. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ch <- as.data.table(readRDS(file.path(raw, "df_choice_rep.rds")))
ra <- as.data.table(readRDS(file.path(raw, "df_rating_rep.rds")))
att <- c(education = "Education", occupation = "Occupation", income = "Income", residence = "Place.of.residence",
         gender = "Gender", sexuality = "Sexuality", migration_background = "Migration.background", age = "Age")
for (d in list(ch, ra)) {
  for (v in att) set(d, j = v, value = as.character(d[[v]]))
  stopifnot(d[, .N, respondent][, all(N == 10)], d[, .N, .(respondent, task, profile)][, all(N == 1)], !anyNA(d[, ..att]))
  setorder(d, respondent, task, profile)
  d[, row := do.call(paste, c(.SD, sep = "|")), .SDcols = c("task", "profile", unname(att))]
}
sig <- function(d) d[, .(sig = paste(row, collapse = "#")), respondent]
sc <- sig(ch); sr <- sig(ra)
stopifnot(!anyDuplicated(sc$sig), !anyDuplicated(sr$sig))
m <- merge(sc, sr, by = "sig", suffixes = c("_c", "_r"))
stopifnot(nrow(m) == 2319L)
## no partial matches: unmatched respondents share at most one row with each other
x <- merge(ch[, .(rc = respondent, row)], ra[, .(rr = respondent, row)], by = "row", allow.cartesian = TRUE)[, .N, .(rc, rr)]
stopifnot(x[!(rc %in% m$respondent_c) & !(rr %in% m$respondent_r), all(N <= 1)], x[!paste(rc, rr) %in% paste(m$respondent_c, m$respondent_r), max(N)] <= 3)
ra_only <- setdiff(sr$respondent, m$respondent_r)
key <- rbind(data.table(rr = m$respondent_r, id = m$respondent_c),
             data.table(rr = sort(ra_only), id = 2382L + seq_along(ra_only)))
covs <- c("gender", "age_group", "edu", "income_group_eq", "sexual_orientation", "migrationb", "migrationb_not_german",
          "lr_group", "urban_cat", "urban_2cat", "sss_group2", "sss_group3", "sss_past_group", "sss_future_group", "sdo_group")
for (v in covs) set(ch, j = v, value = as.character(ch[[v]]))
stopifnot(ch[, lapply(.SD, uniqueN), respondent, .SDcols = covs][, all(unlist(.SD) == 1), .SDcols = covs])
dc <- ch[, c("respondent", "task", "profile", unname(att), "selected", covs), with = FALSE]
setnames(dc, c("respondent", "selected"), c("id", "choice"))
dr <- merge(ra[, .(rr = respondent, task, profile, rating = selected)], key, by = "rr")[, rr := NULL]
d <- merge(dc, dr, by = c("id", "task", "profile"), all = TRUE)
## attributes for rating-only respondents
ro <- merge(ra[respondent %in% ra_only, c("respondent", "task", "profile", unname(att)), with = FALSE],
            key[id > 2382L], by.x = "respondent", by.y = "rr")
d[ro, on = c("id", "task", "profile"), (unname(att)) := mget(paste0("i.", unname(att)))]
stopifnot(!anyNA(d[, ..att]), nrow(d) == 24990L, uniqueN(d$id) == 2499L)
setnames(d, unname(att), paste0("attr_", names(att)))
setnames(d, covs, paste0("cov_", covs))
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
d[, `:=`(choice = as.integer(choice), rating = as.integer(rating))]
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)],
          d[!is.na(rating), all(rating %in% 1:10)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "breyer_2025_social_status.csv"))
