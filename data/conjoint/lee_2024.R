##Highly-skilled immigration policy conjoint (Hong Kong) from
##Lee, S.-y. (2025). Procedure matters: The distinct attitudinal feedback effects of immigration
##policy. Political Behavior, 47(1), 191-215 (online 17 June 2024).
##https://doi.org/10.1007/s11109-024-09947-5
##Replication data: Harvard Dataverse doi:10.7910/DVN/PPBS5T, CC0 1.0. File read:
##ReplicationData.xlsx, sheets "Values" (codes), "Labels (in Chinese)" (the same cells as Chinese
##text) and "Dictionary" (English variable and value labels). Replication_Code_ImmPolicy.R read as
##text, not run. The article itself could not be read (publisher page behind a JS challenge), so
##fielding dates, exact question wording and the paper's N are NOT checked.
##Usage: Rscript lee_2024.R <dir holding ReplicationData.xlsx> <output dir>
##
##Survey IMMPOLICY21 (Dictionary `Survey`), Hong Kong. Two panels (PanelMemberType, Dictionary):
##1 = "Hong Kong People Representative Panel (Probability panel)", 2 = "Hong Kong People Volunteer
##Panel (Non-probability panel)". The authors analyse them separately (code L165-169: main
##figures on the volunteer panel, the probability panel separately), so two tables:
##  lee_2024_skilled_immig_volunteer    1,432 respondents
##  lee_2024_skilled_immig_probability    204 respondents
##Each respondent saw 5 pairs of immigration-policy schemes (PolicyPairNo 1-5 = task), 7 attributes:
##eligibility, employment (change of employment), nationality, language, welfare, tax, quota.
##Attribute text is the Chinese text from the "Labels (in Chinese)" sheet, i.e. the language of the
##survey (display and label language zh); the Dictionary gives English versions (e.g. nationality
##0 "The scheme is open to mainland Chinese citizens only").
##PROFILE IS INFERRED: the file has no profile column; each respondent x pair has exactly two
##consecutive rows, and in every answered pair exactly one row is chosen, so the first row is
##profile 1 and the second profile 2 (left/right position not documented).
##Outcomes (Dictionary wording; the survey question text is not in the deposit):
##  choice = W2_Q1 "Conjoint experiment outcome- Attitudes toward immigrants [forced choice]",
##    0 Profile not chosen / 1 Profile chosen; -99 Refuse to answer -> NA (178 pairs; the choice
##    is missing on both profiles together). Forced choice, no opt-out offered.
##  rating = W2_Q2 "Conjoint experiment outcome- Attitudes toward immigrants [rating: 1-10]"; the
##    stored values run 0-10 (0 is the most frequent), so the range is 0-10 despite the label;
##    the code calls it "rating of impression toward immigrants" (L1251); anchors not in the
##    deposit. -99 Refuse to answer -> NA.
##  Rows where both outcomes are missing are dropped.
##Restrictions OBSERVED: nationality "mainland Chinese citizens only" never appears with quota
##40,000/year (0 of 16,360 rows); the authors model Nationality*Quota (code L177-181). Other pairs
##all occur. Hence the unequal shares of those two attributes.
##Weights: cov_survey_weight = weight ("data weighted by gender, age, educational attainment, and
##economic activity status", code Figure A18 left); cov_weight2 = weight2 (also Chinese
##identification, Figure A18 right). The main analyses are unweighted.
##Covariates: cov_gender (DM1: 1 Male = male, 2 Female = female, 8881 Other = other, -99 Refuse
##= NA; Dictionary), cov_education (DM3 answer text from the Chinese label sheet; 拒答 = refuse ->
##NA; English in the Dictionary: Primary or below ... PhD), cov_identity (W1_Q16 "You would call
##yourself": Chinese label text, refuse -> NA, 不知道／很難說 kept). Other attitude items dropped.
##SurveyCaseid (the survey's own case id) is re-keyed to integers.
suppressMessages(library(readxl)); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "ReplicationData.xlsx")
v <- as.data.table(read_excel(f, sheet = "Values", col_types = "text"))
l <- as.data.table(read_excel(f, sheet = "Labels (in Chinese)", col_types = "text"))
stopifnot(nrow(v) == 16360, identical(v$SurveyCaseid, l$SurveyCaseid), uniqueN(v$SurveyCaseid) == 1636)
v[, profile := seq_len(.N), .(SurveyCaseid, PolicyPairNo)]
stopifnot(v[, .N, .(SurveyCaseid, PolicyPairNo)][, all(N == 2)],
          v[, .(ok = all(diff(.I) == 1L)), .(SurveyCaseid, PolicyPairNo)][, all(ok)])
v[, id := as.integer(factor(SurveyCaseid))]
an <- c(eligibility = "Policy_Eligibility", employment = "Policy_Employment", nationality = "Policy_Nationality",
        language = "Policy_Language", welfare = "Policy_Welfare", tax = "Policy_Tax", quota = "Policy_Quota")
d <- v[, .(id, task = as.integer(PolicyPairNo), profile = as.integer(profile),
           choice = fifelse(W2_Q1 == "-99", NA_integer_, as.integer(W2_Q1)),
           rating = fifelse(W2_Q2 == "-99", NA_integer_, as.integer(W2_Q2)))]
for (k in names(an)) d[, paste0("attr_", k) := l[[an[[k]]]]]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
# each code maps to one Chinese text
for (k in names(an)) stopifnot(uniqueN(paste(v[[an[[k]]]], l[[an[[k]]]])) == uniqueN(v[[an[[k]]]]),
                               uniqueN(l[[an[[k]]]]) == uniqueN(v[[an[[k]]]]))
d[, `:=`(cov_gender = c("1" = "male", "2" = "female", "8881" = "other", "-99" = NA)[v$DM1],
         cov_education = fifelse(l$DM3 == "拒答", NA_character_, l$DM3),
         cov_identity = fifelse(l$W1_Q16 == "拒答", NA_character_, l$W1_Q16),
         cov_survey_weight = as.numeric(v$weight), cov_weight2 = as.numeric(v$weight2),
         panel = v$PanelMemberType)]
stopifnot(all(v$DM1 %in% c("1", "2", "8881", "-99")), all(v$PanelMemberType %in% c("1", "2")))
stopifnot(d[!is.na(choice), .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)])
stopifnot(d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)], all(d$rating %in% c(0:10, NA)))
stopifnot(nrow(d[attr_nationality == "只接受中國內地居民申請" & attr_quota == "每年40,000人"]) == 0)
d <- d[!(is.na(choice) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d[panel == "2"][, panel := NULL], file.path(out, "lee_2024_skilled_immig_volunteer.csv"))
fwrite(d[panel == "1"][, panel := NULL], file.path(out, "lee_2024_skilled_immig_probability.csv"))
