##State-legislature choice conjoint (US) from
##Dobson, M. R., Lollis, J. M., Harden, J. J., & Kirkland, J. H. (2026). Legislative
##professionalism and perceptions of white-collar government. Journal of Political
##Institutions and Political Economy. https://doi.org/10.1108/JPIPE-10-2025-0027
##(article paywalled, not read).
##Replication data: Harvard Dataverse doi:10.7910/DVN/LUICHB, CC0 1.0, no restricted files.
##File read (from replication.zip): replication/conjoint/CleanedUpQualtrics.dta (the Qualtrics
##export). The authors' conjoint.R, helper.functions.R and .Rhistory were read as text (not
##run). The zip's ces/ folder (2016 CES module and Bowen & Greene professionalism scores, for
##the paper's observational Table 2) is not used.
##Usage: Rscript dobson_2026.R <dir holding CleanedUpQualtrics.dta> <output dir>
##
##Qualtrics export of 2,028 responses (March 27, 2024; the authors call the data frame
##`prolific`, and the consent field holds 24-hex Prolific IDs, so Prolific respondents). Each
##saw 5 pairs of hypothetical newly elected state legislatures (task 1-5, profile 1 = A,
##2 = B; source f<task><profile><position>), with 7 attributes: occupational class of members,
##session length, staff, salary, party in control, bill introduction limits, calendar posting.
##The export holds only the level texts, not the attribute names: the attribute of each row
##position is identified per respondent from its levels, as the authors' code does, and is the
##same in every task (checked); attrpos_<name> = row position 1-7. Session length and bill
##limits share the level text "Unlimited"; when a respondent's session row or bill-limit row
##shows "Unlimited" on all 10 profiles, it is identified by elimination (the other row's
##levels identify it); if both show only "Unlimited", their values are the same text either
##way and their attrpos_ are left blank. Attribute names are this script's (the export has
##none); the authors' figure labels are Class, Session, Salary, Staff, Party, Bill Limit,
##Calendar. Level text is as displayed (trailing spaces trimmed; "legisaltors" sic).
##Outcomes, three forced choices (1 = A, 2 = B; no opt-out option in the data) per task,
##source q<3t-2>, q<3t-1>, q<3t> (authors' q1t, q2t, q3t):
##  choice = "Which legislature is best positioned to benefit society?"
##  choice_people_like_you = "Which legislature is best positioned to benefit people like you?"
##    (both wordings from the authors' Figure 4 titles; may be shortened)
##  choice_q3 = the third question, the paper's Figure 1 outcome; its wording is NOT in the
##    deposit (the abstract suggests it is about which legislature is professional / white-
##    collar, but this is not stated anywhere readable).
##TASK 2 IS DROPPED: the export's column F-2-1-2 (task 2, profile A, attribute row 2) is
##empty for all 2,028 respondents, so one attribute of every task-2 profile A is lost (the
##authors' code drops those profile-A rows and keeps task-2 profile B unpaired). task keeps
##the shown order (1, 3, 4, 5).
##Tasks with no answer to any of the three questions are omitted; a task missing only some
##questions keeps NA on those. Randomization restrictions are not documented; the authors'
##cregg calls assume design = "uniform". In the table, salary $0k is on 3,155 profiles vs
##about 4,250 for each other salary, and session "Unlimited" on 3,099 vs about 4,270 for each
##month level; other attributes are balanced. Weights were probably not uniform
##(restrictions = observed). Table: 1,996 respondents with any answered task, 15,898 rows.
##The article's N is not known (paywalled). Spot check: marginal mean of the white-collar
##level is 0.42 on choice (benefit society) and 0.60 on choice_q3, in line with the abstract
##(white-collar legislatures seen as professional but not governing for the public).
##Covariates (source codes; the export carries no value labels): cov_gender (authors: 2 =
##female), cov_party (authors: 1 = Democrat, 2 = Republican, 3 = Independent), cov_working_class
##(authors: 1 = working class, else white collar), cov_race_<group> (1 = selected, 0 = not),
##cov_hisp, cov_check (attention check; authors treat 5 as passing), cov_finished (Qualtrics
##finished flag). Other profile items (birth year, education, marital status, employment,
##state, income, economic situation, q39) have unlabelled codes and are dropped.
##PII in the source, dropped: IP address, latitude/longitude, Qualtrics ResponseId, the
##consent field (Prolific IDs), free-text occupation, start/end dates. id = row order of
##the export (1-2,028), re-keyed.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "CleanedUpQualtrics.dta"))))
k[, id := .I]
lev <- list(class = "^The newly elected legislature", session = "^[136] months?$", staff = "legislature staff members$",
            salary = "^\\$[0-9]+k$", party_control = "^(Republicans|Democrats)$", intro_limits = "^5 bill limit$",
            posting = "^Session calendars")
fv <- function(t, p, j) trimws(as.character(k[[sprintf("f%d%d%d", t, p, j)]]))
## attribute of each position, per respondent
pos <- matrix(NA_character_, nrow(k), 7)
for (j in 1:7) {
  vals <- do.call(cbind, lapply(1:5, function(t) cbind(fv(t, 1, j), fv(t, 2, j))))
  for (nm in names(lev)) {
    hit <- rowSums(matrix(grepl(lev[[nm]], vals), nrow(k))) > 0
    stopifnot(all(is.na(pos[hit, j])))
    pos[hit, j] <- nm
  }
  ## a row with values that matches no pattern must be all "Unlimited"
  un <- is.na(pos[, j]) & !is.na(vals[, 1])
  stopifnot(all(rowSums(vals[un, , drop = FALSE] != "Unlimited", na.rm = TRUE) == 0))
}
## elimination for an all-"Unlimited" row
for (i in seq_len(nrow(k))) {
  if (is.na(k$f111[i])) next
  miss <- setdiff(names(lev), pos[i, ])
  open <- which(is.na(pos[i, ]))
  stopifnot(length(miss) == length(open), all(miss %in% c("session", "intro_limits")))
  if (length(open) == 1) pos[i, open] <- miss
  if (length(open) == 2) pos[i, open] <- "both_unlimited"
}
## every value of a position is a level of its attribute in every task (position fixed over tasks)
lvl <- list(session = c("1 month", "3 months", "6 months", "Unlimited"), intro_limits = c("5 bill limit", "Unlimited"))
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = k$id, task = t, profile = p)
  for (nm in names(lev)) { x[, paste0("attr_", nm) := NA_character_]; x[, paste0("attrpos_", nm) := NA_integer_] }
  for (j in 1:7) {
    v <- fv(t, p, j)
    for (nm in names(lev)) {
      w <- which(pos[, j] == nm)
      ok <- if (nm %in% names(lvl)) v[w] %in% lvl[[nm]] else grepl(lev[[nm]], v[w])
      stopifnot(all(ok | is.na(v[w])))
      set(x, w, paste0("attr_", nm), v[w]); set(x, w, paste0("attrpos_", nm), j)
    }
    w <- which(pos[, j] == "both_unlimited")
    stopifnot(all(v[w] == "Unlimited" | is.na(v[w])))
    set(x, w, "attr_session", v[w]); set(x, w, "attr_intro_limits", v[w])
  }
  q <- function(n) { r <- as.integer(k[[paste0("q", 3L * t - 3L + n)]]); as.integer(r == p) }
  x[, `:=`(choice = q(1), choice_people_like_you = q(2), choice_q3 = q(3))]
  x
}))))
d <- d[!(is.na(choice) & is.na(choice_people_like_you) & is.na(choice_q3))]
## F-2-1-2 (task 2, profile A, row 2) is empty for every respondent in the deposit
stopifnot(all(is.na(k$f212)), d[task != 2 | profile != 1, !anyNA(.SD), .SDcols = patterns("^attr_")])
d <- d[task != 2]
stopifnot(!anyNA(d[, paste0("attr_", names(lev)), with = FALSE]))
for (o in c("choice", "choice_people_like_you", "choice_q3"))
  stopifnot(d[!is.na(get(o)), sum(get(o)), .(id, task)][, all(V1 == 1)])
cv <- k[, .(id, cov_gender = as.integer(gender), cov_party = as.integer(party), cov_working_class = as.integer(working_class))]
for (r in c("white", "black", "hisp", "native", "asian", "nhpi", "mena", "mixed", "other"))
  cv[, paste0("cov_race_", r) := as.integer(!is.na(k[[paste0("race_", r)]]))]
cv[, `:=`(cov_hisp = as.integer(k$hisp), cov_check = as.integer(k$check), cov_finished = as.integer(k$finished))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "choice_people_like_you", "choice_q3",
                 paste0("attr_", names(lev)), paste0("attrpos_", names(lev))))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dobson_2026_legislative_professionalism.csv"))
