##Cross-border climate-transfer conjoints (United States, India) from
##Gaikwad, N., Genovese, F., & Tingley, D. (2025). Climate action from abroad: Assessing mass support
##for cross-border climate transfers. International Organization, 79(1), 146-172.
##https://doi.org/10.1017/S0020818324000365
##Replication data: Harvard Dataverse doi:10.7910/DVN/PQV2BY, CC0 1.0 (zip "...IOReplication.zip").
##Files read (R data frames, loaded into a new environment): IOReplication/Main Results/cj_US.RData and
##cj_India.RData (conjoint 1, policy profiles), IOReplication/App J Country Profiles Cj/cj2_US.RData and
##cj2_India.RData (conjoint 2, country profiles); the authors' scripts (Cj_mainoutput_*.R, Cj2_*.R)
##read as text. There is no codebook or questionnaire in the deposit.
##Usage: Rscript gaikwad_2025.R <dir holding the unzipped IOReplication folder> <output dir>
##
##Four tables, one per (conjoint, country): different attribute sets and samples, so no pooling.
##  gaikwad_2025_climate_policy_us    : US, 2,019 respondents, policy profiles (Target, Cost, Duration, Goal,
##                                      Compensation, Partners, Reciprocity)
##  gaikwad_2025_climate_policy_in    : India, 1,459 respondents, policy profiles (Duration, Goal, Compensation,
##                                      Partners, Reciprocity, Monitoring, Conditionalities)
##  gaikwad_2025_climate_country_us   : same 2,019 US respondents, country profiles (Political regime,
##                                      Climate risk, Policy exposure, Income level, Relationship with US,
##                                      Relative efficiency, Race)
##  gaikwad_2025_climate_country_in   : same 1,459 Indian respondents, country profiles (Political regime,
##                                      Relationship with India, Relative efficiency, Historical emissions,
##                                      Reporting request, Matching request, Climate exposure)
##Each respondent saw 4 paired tasks of each conjoint (conjoint 1: tasks 1-4, conjoint 2: tasks 5-8
##as stored; task numbers kept, so the country-profile tables run 5-8). `id` is the same integer for a
##respondent in the policy and country tables of one country (re-keyed from the Qualtrics ResponseId
##in sorted order, which is dropped). Profile A/B = position. Level text is the authors' text
##("Other.Countries" is called Reciprocity in the authors' scripts: attr_reciprocity; trailing spaces
##in the cost levels trimmed). The cost unit ("$16", "$64", "$256") is not stated in the deposit.
##Outcomes (question wording is not in the deposit; the article says respondents "chose their
##preferred one and then ranked each profile on ten-point scales", so both are paraphrases):
##  choice = `selected` (1 for the profile picked; exactly one per task; no opt-out); equals the
##           `choice` column ("Policy A"/"Country A" ...).
##  rating = `rate`, a 1-10 rating of each profile (anchors not stated; HIGHER assumed = more
##           favourable; the authors' G.1 analysis calls it "Policy Rating"). 19 profiles in the
##           country-profile US table have rating NA (kept; they carry the choice).
##Randomization: the article says the US policy attribute values were "fully randomized" (restrictions
##none for that table); no source documents restrictions for the others. Level shares are near equal.
##No covariates and no survey weight in these files (the deposit's respondent-level covariates are
##not attached to the conjoint frames). Race (white / not white) is a country-profile attribute, not
##a respondent covariate; no gender attribute, so no crosswalk.
##N: article reports 2,006 US and 1,459 Indian respondents; these files hold 2,019 US respondents
##(13 more than the article; the 2,006 may exclude failures of its two comprehension checks) and 1,459.
##Not built: App F vignette files (respondent frames only, no vignette text or assignment) and App E
##Facebook sample (importance ratings).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
D <- file.path(raw, "IOReplication")
ld <- function(f) { e <- new.env(); load(file.path(D, f), e); as.data.table(get(ls(e)[1], e)) }
jobs <- list(
  list("Main Results/cj_US.RData", "gaikwad_2025_climate_policy_us", "US"),
  list("Main Results/cj_India.RData", "gaikwad_2025_climate_policy_in", "IN"),
  list("App J Country Profiles Cj/cj2_US.RData", "gaikwad_2025_climate_country_us", "US"),
  list("App J Country Profiles Cj/cj2_India.RData", "gaikwad_2025_climate_country_in", "IN"))
## consistent integer ids across the two conjoints of one country
ids <- lapply(c(US = "US", IN = "IN"), function(cn) {
  f <- if (cn == "US") "Main Results/cj_US.RData" else "Main Results/cj_India.RData"
  r <- sort(unique(ld(f)$ResponseId)); setNames(seq_along(r), r) })
for (j in jobs) {
  x <- ld(j[[1]]); id <- ids[[j[[3]]]]
  stopifnot(all(x$ResponseId %in% names(id)))
  at <- setdiff(names(x), c("ResponseId", "task", "profile", "choice", "selected", "rate"))
  d <- data.table(id = unname(id[x$ResponseId]), task = as.integer(x$task), profile = match(as.character(x$profile), c("A", "B")),
                  choice = as.integer(x$selected), rating = as.integer(x$rate))
  for (v in at) { nm <- tolower(gsub("\\.", "_", v)); if (nm == "other_countries") nm <- "reciprocity"
    d[, paste0("attr_", nm) := trimws(as.character(x[[v]]))] }
  stopifnot(!anyNA(d$profile), d[, sum(choice), .(id, task)][, all(V1 == 1L)], !anyNA(d[, grep("^attr_", names(d), value = TRUE), with = FALSE]))
  setorder(d, id, task, profile)
  cat(j[[2]], ": respondents", uniqueN(d$id), "rows", nrow(d), "rating NA", sum(is.na(d$rating)), "\n")
  fwrite(d, file.path(out, paste0(j[[2]], ".csv")))
}
