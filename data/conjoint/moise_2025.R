##Factorial vignettes on EU defence responses to Russian escalation, seven countries (2022), from
##Moise, A. D., Truchlewski, Z., & Oana, I.-E. (2025). Tilly versus Milward: Experimental evidence of public preferences for
##European defense amidst the Russian threat. Political Behavior, 47(3), 1015-1066. https://doi.org/10.1007/s11109-024-09979-x
##Replication data: Harvard Dataverse doi:10.7910/DVN/QUVPD7, CC0 1.0, no restricted files. File read: replication_data_UA.rda
##(object WIDECJ, loaded into its own environment; replication_code_UA.R read as text for the factor level order). Open-access
##article text (PMC12397120, Table 1 and Appendix B) read for the displayed wording.
##Usage: Rscript moise_2025.R <dir holding replication_data_UA.rda> <output dir>
##
##Survey of 12,371 respondents in Germany, France, Italy, Portugal, Poland, Hungary and Finland (July 2022, SOLID-ERC project,
##national quota samples), each shown two policy scenarios (24,742 rows) built from three factors:
##  attr_russian_actions (F1): "The Russian government, on the war front, ..." is continuing its military efforts in Ukraine /
##    is intensifying its military efforts against Ukrainian civilian targets (residential buildings, hospitals, civilians) /
##    is extending its military campaign into Moldova, a non-EU member state / is attacking a military facility in Lithuania, an
##    EU member state (data tags: continuing, intensifying, extending non-EU, extending EU);
##  attr_us_action (F2): "The United States ..." has announced it will continue supplying arms to Ukraine and maintaining troops in
##    EU countries / fearing escalation, has announced a withdrawal of military support for Ukraine, and the removal of a significant
##    number of US troops from EU countries (tags: US supply, US withdraw);
##  attr_policy_response (F3): "In response, ..." EU member states maintain their current level of defense capacity / each EU
##    member state increases their national defense capacity independently / EU member states agree to increase the defense capacity
##    of the EU through greater military cooperation among themselves / ... through the creation of an integrated EU army
##    (tags: maintain, increase independently, increase cooperation, integrated army).
##Attribute level text taken from the article (Table 1); the deposit stores short tags. 4 x 2 x 4 = 32 combinations.
##Outcome: rating = RATING, an evaluation of the scenario on an 11-point scale, 0-10 (article: "evaluate the scenarios ... on an
##11-point scale"; the verbatim question and anchors for this experiment are not in the text read, the companion energy experiment's
##item is 'to what extent do you approve or disapprove of the considered policy? (0-Completely disapprove to 10-Completely
##approve)', so direction is read as higher = more approval, not stated). 4,314 rows have no rating and are dropped.
##Task and profile: each respondent has exactly two rows (checked); they are numbered task 1, 2 in FILE ORDER (inferred; the file
##has no task index, the scenarios are shown one at a time per the article), one profile per task. Order is outcome-independent.
##id: the file's panel ID re-keyed to integers. Covariates: cov_country (Country), cov_eu_identity (EU_identity_rec2, authors'
##recode of the EU identity item, text), cov_ideology (ideology_rec2: left/center/right, authors' recode of the 0-10 item).
##Dropped: the authors' derived threat/attitude recodes and 0-99 items (B13_1, A4_3: codebook not deposited), weapons, escalate.
##Count check: article N = 12,371 = respondents in the file (national Ns 1,024-2,084 match); 10,698 of them have at least one rating
##(1,673 have none: both RATING values NA), so the table holds 10,698 respondents and 20,428 rows.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "replication_data_UA.rda"), envir = e)
d <- as.data.table(e$WIDECJ)
stopifnot(nrow(d) == 24742, d[, .N, ID][, all(N == 2)])
d[, rid := as.integer(factor(as.character(ID), levels = unique(as.character(ID))))]
d[, task := seq_len(.N), by = rid]
f1 <- c(continuing = "is continuing its military efforts in Ukraine",
        intensifying = "is intensifying its military efforts against Ukrainian civilian targets (residential buildings, hospitals, civilians)",
        "extending non-EU" = "is extending its military campaign into Moldova, a non-EU member state",
        "extending EU" = "is attacking a military facility in Lithuania, an EU member state")
f2 <- c("US supply" = "has announced it will continue supplying arms to Ukraine and maintaining troops in EU countries",
        "US withdraw" = "fearing escalation, has announced a withdrawal of military support for Ukraine, and the removal of a significant number of US troops from EU countries")
f3 <- c(maintain = "EU member states maintain their current level of defense capacity",
        "increase independently" = "each EU member state increases their national defense capacity independently",
        "increase cooperation" = "EU member states agree to increase the defense capacity of the EU through greater military cooperation among themselves",
        "integrated army" = "EU member states agree to increase the defense capacity of the EU through the creation of an integrated EU army")
r <- data.table(id = d$rid, task = d$task, profile = 1L, rating = as.integer(d$RATING),
  attr_russian_actions = unname(f1[as.character(d$F1)]), attr_us_action = unname(f2[as.character(d$F2)]),
  attr_policy_response = unname(f3[as.character(d$F3)]), cov_country = d$Country,
  cov_eu_identity = as.character(d$EU_identity_rec2), cov_ideology = as.character(d$ideology_rec2))
stopifnot(!anyNA(r[, .(attr_russian_actions, attr_us_action, attr_policy_response)]))
cat("rows without rating:", r[is.na(rating), .N], "\n")
r <- r[!is.na(rating)]
cat("respondents", uniqueN(r$id), "range rating", range(r$rating), "\n")
print(d[, uniqueN(rid), Country])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "moise_2025_eu_defence.csv")); cat("rows", nrow(r), "\n")
