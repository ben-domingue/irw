##Migration-destination conjoints with student subject pools in Chile, China, India and the UK from
##Duch, R. M., Laroze, D., Reinprecht, C., & Robinson, T. S. (2022). Nativist policy: The
##comparative effects of Trumpian politics on migration decisions. Political Science Research
##and Methods, 10(1), 171-187. https://doi.org/10.1017/psrm.2020.33
##Replication data: Harvard Dataverse doi:10.7910/DVN/MYJDHS ("Populism: Magnet or Deterrent?"),
##CC0 1.0, no restricted files. Files read: conjoint{1,2,3}_{chile,china,india,uk}.csv (the
##authors' processed long files) and, for the ratings only, {Chile,China,India,UK}_FINAL.csv (raw
##Qualtrics exports). Also read as text, not run: "NotRun -- initial_data_processing.R" (how the
##processed files were built), PSRM___Populism__Magnet_or_Deterrent__COND_ACCEPT.pdf (accepted
##manuscript with appendix: design, Table 1, wording).
##Usage: Rscript duch_2022.R <raw dir> <output dir>
##
##Student subject pools of the Nuffield CESS centres (online, Qualtrics, 2018): Chile 214, China
##303, India 229, UK 196 = 942 respondents. Each made 3 choices in each of THREE conjoint
##experiments between "Employment Destination 1" and "Employment Destination 2", 5 attributes of
##3 levels each. The three conjoints use different attribute sets (paper Table 1): conjoint 1's
##immigration policy has "Restriction on Muslim immigration/tourist visas" as its negative level,
##conjoint 2's has "Deportation of all illegal immigrants", conjoint 3 replaces the policy with a
##destination country label (Australia / U.K. / U.S.A.; U.K. subjects saw Canada instead of the
##U.K.). So THREE TABLES, one per conjoint; the same 942 respondents (same id) are in all three.
##The four country pools are in one table each with cov_country: the authors pool them (country
##fixed effects, Table 4 and appendix Tables A17-A18) and their processed files carry one shared
##English text for every level. Respondents saw the survey in Spanish (Chile), Chinese (China)
##and English (India, UK); the stored levels are the authors' English (= the UK/India display text).
##Outcomes, each task:
##  choice = destination, "which of the employment destinations do you prefer?" (paper p. 12);
##           forced choice, exactly one chosen in every task.
##  rating = 7-point rating of each destination from the raw exports (Q6 / Q99 / Q106): "On a
##           scale from 1 to 7, where 1 indicates that you strongly disapprove of the employment
##           destination and 7 indicates that you strongly approve of the employment destination,
##           how would you rate Employment Destinations 1 and 2?" Higher = more approval. The digit
##           is taken from the answer text (anchors "Strongly Disapprove 1", "Strongly Approve7",
##           and their Spanish/Chinese versions; some China rows are mis-encoded but keep the
##           digit). The authors do not analyse the ratings.
##Task and profile: the processed files stack the three tasks of a conjoint as blocks (a, b, c)
##and, within a block, candidate 1 rows then candidate 2 rows by respondent; task = block,
##profile = `candidate` (recorded as Destination 1 / 2). Raw rows are matched to the processed
##`id` by replaying the authors' respondent filter (processed id = row number among the kept raw
##rows); the match is checked: the 9 raw choices equal the processed ones for every respondent.
##Randomization: levels randomly assigned to each destination (paper p. 12); attribute order was
##randomized in Qualtrics (the raw F/G/H-t-k fields: once per respondent and conjoint, the same
##order on all 3 tasks of a conjoint) but is not carried into these tables. No task is repeated.
##The country conjoint's unequal attr_country shares are the UK pool's Canada-for-U.K. swap;
##within each pool the three labels are near-equal. No survey weight (student pools).
##Covariates (processed files unless noted): cov_country, cov_age (the processed files' age in
##years, which the authors computed as 2018 - birth year, minus 1 unless born in January or
##February (India: January-May), initial_data_processing.R L31/L450/L877/L1262), cov_birth_year
##(raw export Q28, "What are your year and month of birth? Year"), cov_gender
##("female", "male", "other": the processed gender text Female/Male/Other lowercased; the
##authors translated the Chile/China answers to English, initial_data_processing.R L443, L867),
##cov_ideology (0 left ..
##10 right), cov_interest (interest in employment abroad, 1-7), cov_likely (likelihood of moving
##abroad for a job in 2-3 years, 1-7), cov_rating_australia / _canada_or_uk / _us (1-7 favourability
##ratings of the three countries; in Chile, China and India the source's "can" column holds the
##rating of the U.K., per initial_data_processing.R), cov_ret_correct (number correct in the real-
##effort dice task). The c.same flag (both destinations the same country) is derived and dropped.
##Spot check: per-country logits of choice on the five attributes (the authors' 0_main_models.R
##references) give the Muslim-ban coefficients in replication_log.txt: UK -.771, Chile -.530,
##China -.314, India -.291.
##PII in the raw exports (not read into the tables): China_FINAL.csv has GPS latitude/longitude
##for 13 rows; all four have free-text "other" answers and Qualtrics metadata columns.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ctry <- c(chile = "CL", china = "CN", india = "IN", uk = "GB")
rawf <- c(chile = "Chile_FINAL.csv", china = "China_FINAL.csv", india = "India_FINAL.csv", uk = "UK_FINAL.csv")
consent <- c(chile = "Sí, he leído y comprendido", china = "是，我已阅读上述同意书并充分理解",
             india = "Yes, I have read the above statement and understood it", uk = "Yes, I have read the above statement and understood it")
rq <- list(c("Q5", "Q6"), c("Q100", "Q99"), c("Q107", "Q106"))  # choice, rating stems per conjoint
dig <- function(x) { y <- suppressWarnings(as.integer(gsub("\\D", "", x))); y }
proc <- list(); rat <- list(); byr <- list()
for (k in names(ctry)) {
  ps <- lapply(1:3, function(j) { p <- fread(file.path(raw, sprintf("conjoint%d_%s.csv", j, k)))
    if (j == 3) setnames(p, "country", "country_label")
    n <- uniqueN(p$id); stopifnot(nrow(p) == 6 * n, all(p$id %in% 1:n)); p[, task := rep(1:3, each = 2 * n)]; p[, cj := j]; p })
  n <- uniqueN(ps[[1]]$id)
  ##raw export: rows with all 9 choices answered, in file order (Qualtrics header rows drop out)
  r <- fread(file.path(raw, rawf[[k]]), colClasses = "character", encoding = "UTF-8")
  setnames(r, sub("^X([123]_Q)", "\\1", names(r)))  # India headers carry an X prefix
  cn <- function(t, stem) sprintf("%d_%s", t, stem)
  ch <- matrix(unlist(lapply(1:3, function(j) sapply(1:3, function(t) dig(r[[cn(t, rq[[j]][1])]])))), nrow = nrow(r))
  ##the authors' respondent filter (initial_data_processing.R): consent text, Finished, and for
  ##China ID != "TEST" and birth year > 1928; the kept rows in file order are the processed ids
  keep <- r$Q74 == consent[[k]] & r$Finished == "TRUE"
  if (k == "china") keep <- keep & r$ID != "TEST" & suppressWarnings(as.integer(r$Q28)) > 1928
  keep <- which(keep)
  pr <- matrix(unlist(lapply(1:3, function(j) sapply(1:3, function(t)
    ps[[j]][task == t & destination == 1][order(id), candidate]))), nrow = n)
  stopifnot(length(keep) == n, all(ch[keep, ] == pr))
  rr <- r[keep]
  byr[[k]] <- data.table(country = k, id = seq_len(n), birth_year = suppressWarnings(as.integer(rr$Q28)))
  ##gender must agree too: a second check on the alignment (UK/India text; Chile/China translated)
  if (k %in% c("uk", "india")) stopifnot(all(rr$Q30 == ps[[1]][task == 1 & candidate == 1][order(id), gender]))
  for (j in 1:3) {
    rt <- rbindlist(lapply(1:3, function(t) data.table(id = seq_len(n), task = t,
            r1 = dig(rr[[sprintf("%d_%s_1", t, rq[[j]][2])]]), r2 = dig(rr[[sprintf("%d_%s_2", t, rq[[j]][2])]]))))
    rt <- melt(rt, id.vars = c("id", "task"), variable.name = "candidate", value.name = "rating")[, candidate := as.integer(sub("r", "", candidate))]
    stopifnot(rt[!is.na(rating), all(rating %in% 1:7)])
    rat[[paste(k, j)]] <- rt[, country := k][, cj := j]
  }
  proc[[k]] <- rbindlist(ps, fill = TRUE)[, country := k]
}
P <- rbindlist(proc, fill = TRUE); RT <- rbindlist(rat)
P <- merge(P, RT, by = c("country", "cj", "id", "task", "candidate"), all.x = TRUE)
P <- merge(P, rbindlist(byr), by = c("country", "id"), all.x = TRUE)
stopifnot(P[!is.na(age) | !is.na(birth_year), all(2018L - birth_year - as.integer(age) %in% 0:1)])
P[, gid := as.integer(factor(paste(country, sprintf("%04d", id))))]
stopifnot(P[, sum(destination), .(cj, gid, task)][, all(V1 == 1)], uniqueN(P$gid) == 942)
nm <- c("duch_2022_destination_muslim_ban", "duch_2022_destination_deportation", "duch_2022_destination_country")
for (j in 1:3) {
  x <- P[cj == j]
  d <- x[, .(id = gid, task, profile = as.integer(candidate), choice = as.integer(destination), rating,
             attr_social_benefits = social, attr_economic_performance = econ, attr_service_salaries = service)]
  if (j < 3) d[, attr_immigration_policy := x$immigration] else d[, attr_country := x$country_label]
  d[, `:=`(attr_education = x$education, cov_country = unname(ctry[x$country]), cov_age = as.integer(x$age), cov_birth_year = x$birth_year,
           cov_gender = tolower(x$gender), cov_ideology = as.numeric(x$ideology), cov_interest = as.numeric(x$interest),
           cov_likely = as.numeric(x$likely), cov_rating_australia = as.numeric(x$aus),
           cov_rating_canada_or_uk = as.numeric(x$can), cov_rating_us = as.numeric(x$us), cov_ret_correct = as.integer(x$dice))]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$cov_gender %in% c("female", "male", "other", NA)))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(nm[j], ".csv")))
}
