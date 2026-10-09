##Publication-metrics ranking conjoint (researchers rank fictitious publications) from
##Lemke, S., Mazarakis, A., & Peters, I. (2021). Conjoint analysis of researchers' hidden preferences
##for bibliometrics, altmetrics, and usage metrics. Journal of the Association for Information
##Science and Technology, 72(6), 777-792. https://doi.org/10.1002/asi.24445
##Data: Zenodo record 3560886 (doi:10.5281/zenodo.3560886), "Researchers Hidden Preferences for
##Metrics - Datasets" (Lemke, S., 2020), CC BY 4.0. Files read: participant_choice_table.csv,
##participant_choice_matrix.csv (cross-check of the ranks only), demographics.csv (all ';'-separated).
##No codebook or questionnaire is deposited, and the article (Wiley, CC BY) could not be retrieved
##here (403); the six indicators are named by the column abbreviations, the deposit's description
##and the article's abstract: CIT citation count, TWE tweets, MEN Mendeley readers, DOW downloads,
##JIF journal impact factor, HIN h-index (Sachse 2021, BIR workshop, describes the experiment: "participants
##ranked fictitious publications solely based on six indicators (citation counts, journal impact
##factor, h-index, download count, tweets, Mendeley readers) without any other information").
##Levels are the numbers shown (3 per indicator: 0/5/250 citations, 0/10/500 tweets, 0/10/500
##Mendeley readers, 0/100/5000 downloads, 0/5/30 JIF, 0/5/30 h-index), stored as text.
##Usage: Rscript lemke_2021.R <dir holding the three csv files> <output dir>
##
##Online survey of researchers (2018-19; demographics Date_Started), 224 respondents in the choice
##table (247 rows in demographics; the abstract reports 247 participating researchers). FIXED design:
##20 choice sets of 3 of 20 fictitious publications (Pub_ID), the same for everyone and chained (each
##set shares a publication with the next), shown as Task_ID_in_DB 1-20 (task = that number); a "demo"
##practice set is dropped. Each set was ranked in two steps, stored as 6 rows: first RES = 1 on the
##publication picked first among the three, then 3 rows of the remaining two, the first-picked row
##marked "x", RES = 1 on the second pick. So:
##  choice       = picked first among the 3 (no opt-out).
##  rating_rank  = rank 1 (picked first), 2 (picked second), 3 (the remaining one); 1 = most
##                 preferred (rank 3 is implied by the two picks). Cross-checked against
##                 participant_choice_matrix.csv: the files agree on every task the matrix
##                 holds except one (one respondent's set 2, first and third swapped), dropped.
##Screen position is not recorded and the file lists the first-picked publication first, so profile
##numbers follow Pub_ID (ascending), which does not depend on the answers (profile_source unknown).
##One respondent has one task stored three times (identical copies); the first copy is kept. Tasks a
##respondent did not reach are absent.
##Covariates (demographics.csv, joined on Respondent_ID; 1 choice-table respondent has no row):
##cov_discipline, cov_role, cov_workplace (option text; free-typed "Other: ..." answers collapsed to
##"Other"), cov_fav_indicator (FavIndicator option text; garbled non-Latin answers -> NA), cov_gender
##(Male -> male, Female -> female; "I prefer not to answer", blank, garbled text and the one
##"Male?" -> NA), cov_birth_year (Birthyear, 0 -> NA), cov_years_experience (Year_of_AE as recorded,
##years in academia; blank -> NA), cov_country (2-letter code as recorded). Dropped: survey
##timestamps, free-text Features_Before/Features_After, Branch_* sub-discipline (mostly free text),
##the authors' derived Cluster. Respondent_ID re-keyed to integers.
##Restrictions: fixed design (yes); level weights: as in the fixed design (observed unequal).
##Count check: 224 respondents, 12,351 rows, vs 247 participating researchers in the abstract (the
##article's analysed N not checked: article not retrievable here). 96 respondents have all 20 sets and
##110 have 19: set 1 is missing for 36 and set 2 for 83 respondents (122 respondents also have the
##"demo" set, made of publications 323/518/627, which overlap sets 1-2; why sets 1-2 are missing is
##not documented). Spot check: the first-pick share is 0.61 / 0.27 / 0.16 for 250 / 5 / 0
##citations, in line with the abstract's finding that citation counts matter most.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "participant_choice_table.csv"), sep = ";", colClasses = "character")
x <- x[Task_ID_in_DB != "demo"]
x[, k := seq_len(.N), .(Respondent_ID, Task_ID_in_DB)]
# one task is stored 3 times for one respondent (3 first-step blocks, then 3 second-step blocks):
# keep the first first-step block and the first second-step block
x[, xb := cumsum(RES == "x"), .(Respondent_ID, Task_ID_in_DB)]
x[, xs := which(RES == "x")[1], .(Respondent_ID, Task_ID_in_DB)]
x <- x[k <= 3 | (k >= xs & k < xs + 3)]
x[, k := seq_len(.N), .(Respondent_ID, Task_ID_in_DB)][, c("xb", "xs") := NULL]
stopifnot(x[, .N, .(Respondent_ID, Task_ID_in_DB)][, all(N == 6)])
stopifnot(x[, paste(RES, collapse = ""), .(Respondent_ID, Task_ID_in_DB)][, all(V1 == "100x10")])
s1 <- x[k <= 3]; s2 <- x[k >= 5]
s1[, rank := fifelse(RES == "1", 1L, NA_integer_)]
s2 <- s2[, .(Respondent_ID, Task_ID_in_DB, Pub_ID, r2 = fifelse(RES == "1", 2L, 3L))]
d <- merge(s1, s2, by = c("Respondent_ID", "Task_ID_in_DB", "Pub_ID"), all.x = TRUE)
d[is.na(rank), rank := r2]
stopifnot(!anyNA(d$rank), d[, sort(rank), .(Respondent_ID, Task_ID_in_DB)][, all(V1 == 1:3), .(Respondent_ID, Task_ID_in_DB)][, all(V1)])
# cross-check ranks against the deposited respondent x task_publication matrix
m <- fread(file.path(raw, "participant_choice_matrix.csv"), sep = ";", header = TRUE)
setnames(m, 1, "rid")
ml <- melt(m, id.vars = "rid", variable.factor = FALSE, na.rm = TRUE)
ml <- ml[grepl("^T[0-9]+_P[0-9]+$", variable)]
ml[, `:=`(Respondent_ID = sub("^P_", "", rid), Task_ID_in_DB = sub("^T([0-9]+)_.*", "\\1", variable),
          Pub_ID = sub(".*_P", "", variable), mrank = as.integer(value))]
chk <- merge(d, ml[, .(Respondent_ID, Task_ID_in_DB, Pub_ID, mrank)], by = c("Respondent_ID", "Task_ID_in_DB", "Pub_ID"))
bad <- unique(chk[rank != mrank, .(Respondent_ID, Task_ID_in_DB)])
stopifnot(nrow(chk) > 0.9 * nrow(d), nrow(bad) <= 1)
cat("rank cross-check rows:", nrow(chk), "of", nrow(d), "; tasks disagreeing (dropped):", nrow(bad), "\n")
d <- d[!bad, on = c("Respondent_ID", "Task_ID_in_DB")]
d[, task := as.integer(Task_ID_in_DB)]
setorder(d, Respondent_ID, task, Pub_ID)
d[, Pub_ID := as.integer(Pub_ID)]
setorder(d, Respondent_ID, task, Pub_ID)
d[, profile := seq_len(.N), .(Respondent_ID, task)]
dm <- fread(file.path(raw, "demographics.csv"), sep = ";", colClasses = "character", encoding = "UTF-8")
oth <- function(v) { v[is.na(v) | v == ""] <- NA; v[grepl("^Other", v)] <- "Other"; v }
okfav <- c("Citations (e.g., on GS)", "Journal Impact Factor", "Downloads", "h-Index", "Tweets", "Mendeley readers")
dm <- dm[, .(Respondent_ID, cov_discipline = oth(Discipline), cov_role = oth(Role), cov_workplace = oth(Workplace),
             cov_fav_indicator = fifelse(FavIndicator %in% okfav, FavIndicator, NA_character_),
             cov_gender = fifelse(Gender == "Male", "male", fifelse(Gender == "Female", "female", NA_character_)),
             cov_birth_year = {b <- suppressWarnings(as.integer(Birthyear)); fifelse(b >= 1920 & b <= 2005, b, NA_integer_)},
             cov_years_experience = suppressWarnings(as.integer(Year_of_AE)),
             cov_country = fifelse(Country == "", NA_character_, Country))]
stopifnot(!anyDuplicated(dm$Respondent_ID))
r <- d[, .(Respondent_ID, task, profile, choice = as.integer(rank == 1L), rating_rank = rank,
           attr_citations = CIT, attr_tweets = TWE, attr_mendeley_readers = MEN, attr_downloads = DOW,
           attr_journal_impact_factor = JIF, attr_h_index = HIN)]
r <- merge(r, dm, by = "Respondent_ID", all.x = TRUE)
ids <- sort(unique(as.integer(r$Respondent_ID)))
r[, id := match(as.integer(Respondent_ID), ids)][, Respondent_ID := NULL]
setcolorder(r, "id")
setorder(r, id, task, profile)
cat("respondents:", uniqueN(r$id), " rows:", nrow(r), " full 20:", sum(r[, uniqueN(task), id]$V1 == 20), "\n")
fwrite(r, file.path(out, "lemke_2021_research_metrics.csv"))
