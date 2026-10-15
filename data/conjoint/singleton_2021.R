##Bicyclists' preferences for roundabout designs, stated-choice experiment from
##Singleton, P. A., & Poudel, N. (2021). singletonpa/bicycle-safety-roundabouts: Initial release of survey data and stated preference analysis
##(MPC-603 "Investigating bicyclist safety perceptions and behaviors at roundabouts", Mountain-Plains Consortium) [Software/data]. Zenodo. No article DOI.
##Deposit: Zenodo doi:10.5281/zenodo.5107738 (version record; concept DOI 10.5281/zenodo.5107737). Zenodo record licence is "other-open"; the
##repository LICENSE file (inside the zip) is CC0 1.0 Universal, recorded as "CC0 1.0 (repository LICENSE file)".
##Files read, all inside singletonpa-bicycle-safety-roundabouts-v0.1.zip, after extraction to one flat folder: Stated.csv and WeightsAll.csv
##(Analysis/Stated preference/Data cleaning and weighting/), create_stated.R (read as text; the design and the exclusions), Survey-Qs.pdf (Data/Survey/,
##questionnaire print: level text and question).
##Usage: Rscript singleton_2021.R <dir holding Stated.csv and WeightsAll.csv> <output dir>
##
##613 respondents (online survey of US bicyclists and others; "No way, no how" non-cyclists and 25 respondents with fewer than 6 answers were removed
##by the authors' create_stated.R) answered 6 of the 18 design questions, each "Which roundabout would you prefer for bicycling?" between two
##roundabouts A and B (no neither option: Choice is 1 or 2 in every row, exactly one chosen per task). Each roundabout is shown with a picture and text.
##Attribute text follows the questionnaire cards: island "Small (80ft) central island" / "Large (120ft) central island"; lanes "One travel lane" / "Two travel lanes";
##facility "No bicycle facilities" / "Bicycle ramps to the sidewalk" / "Shared lane bicycle markings & signs" / "Separated bicycle lanes"; volume "Low/Medium/High traffic
##volumes (rarely / sometimes / usually have to yield to and interact with other vehicles)"; speed "25mph / 35mph speed limit on adjacent roads (25mph or
##less in the roundabout)". The deposit stores dummies, decoded with create_stated.R.
##Fixed blocked design: 18 rows from the authors' design (create_stated.R), 3 blocks of 6 (one block per person); the deposit gives no level probabilities.
##Tasks: rows are in the order of the questionnaire question number (E01...E22) within respondent, not display order: the display order is not
##stored in Stated.csv, so task is inferred (the authors' sort order). Profile 1 = roundabout A, 2 = B (Choice 1 = A).
##cov_survey_weight = the authors' raking weight (WeightsAll.csv, matched by ID; age, gender, race/ethnicity, income to census targets), constant within respondent.
##Dropped: Qualtrics ResponseId, availability flag, the authors' dummies. Hetero.csv (covariates) is not used. PII FOUND: Data/Survey/dat3.csv (survey data) holds
##IPAddress, RecipientLastName/FirstName/Email and LocationLatitude/Longitude; that file is not used here.
##N not checked against a paper (none cited).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "Stated.csv"))
w <- fread(file.path(raw, "WeightsAll.csv"))
stopifnot(uniqueN(d$ID) == 613, d[, .N, ID][, all(N == 6)], d[, all(Choice %in% 1:2)], nrow(w) == 613)
d[, task := seq_len(.N), ID]
pick <- function(s, labs) { m <- as.matrix(d[, paste0(names(labs), "_", s), with = FALSE]); stopifnot(all(rowSums(m) == 1)); unname(labs)[max.col(m)] }
lv <- list(
  island = c(Island_small = "Small (80ft) central island", Island_large = "Large (120ft) central island"),
  lanes = c(Lane_1 = "One travel lane", Lane_2 = "Two travel lanes"),
  facility = c(Facility_No = "No bicycle facilities", Facility_Ramps = "Bicycle ramps to the sidewalk", Facility_Shared = "Shared lane bicycle markings & signs", Facility_Seperated = "Separated bicycle lanes"),
  volume = c(Volume_Low = "Low traffic volumes (rarely have to yield to and interact with other vehicles)", Volume_Medium = "Medium traffic volumes (sometimes have to yield to and interact with other vehicles)", Volume_High = "High traffic volumes (usually have to yield to and interact with other vehicles)"),
  speed = c(Speed_25 = "25mph speed limit on adjacent roads (25mph or less in the roundabout)", Speed_35 = "35mph speed limit on adjacent roads (25mph or less in the roundabout)"))
rows <- lapply(c("A", "B"), function(s) {
  r <- data.table(id = d$ID, task = d$task, profile = if (s == "A") 1L else 2L, choice = as.integer(d$Choice == if (s == "A") 1 else 2))
  for (a in names(lv)) r[[paste0("attr_", a)]] <- pick(s, lv[[a]])
  r })
r <- rbindlist(rows)
r <- merge(r, w[, .(id = ID, cov_survey_weight = weight)], by = "id")
stopifnot(r[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(r))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "singleton_2021_roundabout_bicycle.csv"))
