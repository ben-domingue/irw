##Political-ad perception conjoint (US, NORC AmeriSpeak) from
##Edelson, L., Lockett, D., Guillard, C., Lauinger, T., Li, Z., Montgomery, J. M., & McCoy, D.
##(2025). What drives perceptions of the political in online advertising? The source, content,
##and political orientation. Journal of Experimental Political Science, 13(1), 36-50.
##https://doi.org/10.1017/xps.2025.4
##Replication data: Harvard Dataverse doi:10.7910/DVN/DW6ZGZ, CC0 1.0, no restricted files.
##File read: CJ.csv (the NORC2 conjoint, long format). Read as text, not run: readme.md,
##replication_032325.Rmd; pilot2_RmAt.csv header read for message wording only. The real-ads
##experiment files (data/datb/datc/original/correction/pooled*.csv, ra.csv) are a separate
##experiment that manipulates only the sponsor of real ads, so not a conjoint; not built.
##Usage: Rscript edelson_2025.R <dir holding CJ.csv> <output dir>
##
##1,013 US adults (NORC AmeriSpeak / TASS, March 31 - April 19, 2021, "NORC2"; the NORC1
##conjoint of July 2020 was unusable after a programming error, readme), 8 pairs of mock-up
##online ads, 3 attributes: sponsor (source: Biden, Trump, Sierra Club, Patagonia,
##ExxonMobil, Power the Future), message (6) and image (5). presentation = image: the ads
##were pictures (image_set P_IMAGE<t>A/B); attr_ holds the AUTHORS' LABELS of what each ad
##showed (source name, message short label such as "Cut methane", image label such as
##"Oil rig"), not the displayed text, which survives only as pictures not in the deposit.
##The AMT pilot (pilot2_RmAt.csv) gives six message statements that appear to be these
##messages (e.g. "...will #CutMethane pollution...", "Let's work together to preserve
##America's natural beauty..."), but no source maps statements to labels, so they are not
##substituted. The authors' derived codings messageStrength / messageOrient / sourceType /
##sourceOrient (functions of message and source) and `profile` (their ad id) are dropped.
##task = pair number t of image_set P_IMAGE<t><A|B>, profile = 1 for A, 2 for B. Whether t
##is the display order is not documented.
##Outcome: choice = ad judged more political. Wording (pilot questionnaire, same design):
##"Which of these two ads is more political?"; dv = 1 (A) / 2 (B); forced choice. 96 tasks
##of 61 respondents have no answer and are omitted: 8,008 tasks / 16,016 rows remain, all
##1,013 respondents. The paper's N (1,013) is the fielded sample.
##Covariates: cov_survey_weight (WEIGHT), cov_age (AGE, years), cov_gender (GENDER 1 Male,
##2 Female per replication_032325.Rmd L64-65, lowercased), cov_party_id7 (PID, the deposit's
##own text for PartyID7 1-7; PartyID7 = -1, 2 respondents, has no PID text -> NA),
##cov_education_code (EDUC5 1-5; no labels in the deposit). Dropped: P_ZIPCODE, P_CBSA, STATE
##(geography), STARTDT/ENDDT, duration (unit not documented), real-ads and attitude items,
##derived pid/priors. CaseId re-keyed in sorted order. No task is repeated.
##Spot check: weighted lm(choice ~ authors' codings), SEs clustered by id: strong vs weak message
##+.38, candidate vs company sponsor +.09 (paper not read, so not compared to a published figure).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "CJ.csv"))
stopifnot(uniqueN(s$CaseId) == 1013, s[, .N, CaseId][, all(N == 16)], all(grepl("^P_IMAGE[1-8][AB]$", s$image_set)))
s[, `:=`(task = as.integer(substr(image_set, 8, 8)), profile = fifelse(substr(image_set, 9, 9) == "A", 1L, 2L))]
stopifnot(s[, uniqueN(paste(dv)), .(CaseId, task)][, all(V1 == 1)], s[, .N, .(CaseId, task)][, all(N == 2)])
s <- s[!is.na(dv)]
stopifnot(all(s$dv %in% 1:2), s[, uniqueN(.SD), .SDcols = c("CaseId", "AGE", "GENDER", "WEIGHT", "PID", "EDUC5")] == 1013)
ids <- sort(unique(s$CaseId))
d <- s[, .(id = match(CaseId, ids), task, profile, choice = as.integer(dv == profile),
           attr_source = as.character(source), attr_message = as.character(message), attr_image = as.character(image),
           cov_survey_weight = as.numeric(WEIGHT), cov_age = as.integer(AGE),
           cov_gender = unname(c("1" = "male", "2" = "female")[as.character(GENDER)]),
           cov_party_id7 = fifelse(PID == "", NA_character_, as.character(PID)),
           cov_education_code = as.integer(EDUC5))]
stopifnot(!anyNA(d$cov_gender), d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 16016,
          d[, uniqueN(attr_source)] == 6, d[, uniqueN(attr_message)] == 6, d[, uniqueN(attr_image)] == 5)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "edelson_2025_political_ads.csv"))
