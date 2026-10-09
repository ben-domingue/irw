##Open-government-data portal discrete choice experiment (Adama City, Ethiopia, Aug-Dec 2025) from
##Debele, G. (2026). Dataset for: User-centered design for open government data platforms in
##developing smart cities: A discrete choice experiment in Adama City, Ethiopia [Data set].
##Zenodo. https://doi.org/10.5281/zenodo.18877925 (the manuscript named in the record was not
##found published on 2026-10-09).
##Replication data: Zenodo record 18877925, CC BY 4.0. File read: ogd_survey_long_format_R.csv
##(one row per respondent x task x alternative). The record description is the codebook.
##Usage: Rscript debele_2026.R <dir holding the csv> <output dir>
##
##150 respondents (50 researchers, 50 technology-startup members, 50 final-year computing
##students; cov_role) x 5 choice tasks x 3 hypothetical OGD platforms (Alternatives A, B, C =
##profile 1-3) plus a "Status Quo" alternative D. The status quo carries no attribute levels
##(every attribute reads "Status Quo") so it is not a profile (an outside option).
##Outcome: "Participants were asked to rank these four alternatives from most preferred (Rank
##1) to least preferred (Rank 4)" (record description). rating = Ranking of the alternative,
##1-4, LOWER = MORE PREFERRED, stored as in the source. The status quo's own rank is not stored
##as a row; it is the rank (3 or 4) missing from a task's three profiles (status quo ranked
##4th in 702 of 750 tasks, 3rd in 48). No choice column: the only question is the ranking.
##Design: FIXED -- the data hold 15 distinct profiles in 5 choice sets, and every respondent
##saw the same 5 sets with the same platforms under the same letters (task k, alternative A-C
##identical for all; checked). Not randomized per respondent; level frequencies are unequal (e.g. Keyword search
##in 7 of 15 profiles). Task order and how the sets were constructed are not documented.
##Attributes (level text as stored): attr_search_functionality, attr_download_format,
##attr_api_availability, attr_data_quality, attr_visualization.
##Covariates: cov_role (PrimaryRole), cov_age_group (AgeGroup, as stored, e.g. "Under25"),
##cov_gender (Gender Male/Female), cov_experience (Experience years band), cov_used_ogd
##(UsedOGDBefore 1/0). ParticipantID (P001...) re-keyed to integers in file order.
##CAVEAT: the triage flagged the very regular structure (exactly 50 per stratum, fixed design);
##nothing in the deposit shows the data are simulated, and the record calls them "raw,
##anonymized responses".
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "ogd_survey_long_format_R.csv"))
x[, id := match(ParticipantID, unique(ParticipantID))]
x[, task := as.integer(sub("^Task", "", Task))]
attrs <- c("Search_Functionality", "Download_Format", "API_Availability", "Data_Quality", "Visualization")
sq <- x[Is_Status_Quo == 1]
stopifnot(all(sq$Alternative == "D"), all(unlist(sq[, ..attrs]) == "Status Quo"), x[, .N, .(id, task)][, all(N == 4)],
          x[, setequal(Ranking, 1:4), .(id, task)][, all(V1)], all(x[Is_Status_Quo == 0, Alternative] %in% c("A", "B", "C")))
p <- x[Is_Status_Quo == 0]
d <- p[, .(id, task, profile = match(Alternative, c("A", "B", "C")), rating = as.integer(Ranking))]
for (v in attrs) d[, paste0("attr_", tolower(v)) := p[[v]]]
d[, `:=`(cov_role = p$PrimaryRole, cov_age_group = p$AgeGroup, cov_gender = tolower(p$Gender),
         cov_experience = p$Experience, cov_used_ogd = as.integer(p$UsedOGDBefore))]
stopifnot(all(d$cov_gender %in% c("female", "male")), !anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "debele_2026_opendata_portal.csv"))
