##Factorial vignette survey of veterinarians' antimicrobial prescribing (UK) from
##Doidge, C., Hudson, C., Lovatt, F., & Kaler, J. (2019). To prescribe or not to prescribe? A factorial
##survey to explore veterinarians' decision making when prescribing antimicrobials to sheep and beef
##farmers in the UK. PLOS ONE, 14(4), e0213855. https://doi.org/10.1371/journal.pone.0213855
##Replication data: Harvard Dataverse doi:10.7910/DVN/TRR6JJ, CC0 1.0. File read: data_plosone.tab
##(Dataverse "original format": an .xlsx, sheet 1). Vignette wording from the article's S1 File
##(example paper survey, journal.pone.0213855.s001.docx); design facts from the article text.
##Usage: Rscript doidge_2019.R <dir holding data_plosone.tab> <output dir>
##
##306 farm veterinarians from 199 UK practices (English-language postal survey, March 2018; = the
##article), 8 text vignettes each (VigNum = task; one vignette per task, profile = 1). A farmer asks
##for a bottle of antibiotic; 7 factors vary, in a fixed order within a fixed template (S1 File):
##  "A farmer comes into the vet practice asking for a bottle of particular antibiotic as [knowledge].
##   [habit] [farmer], [vet], but [ease]. [time], and [confidence]."
##attr_* hold the varying clauses exactly as printed in the S1 File (the deposit stores the authors'
##short codes, mapped 1:1 here; e.g. knowledgecode "preventwaterymouth" = "he wants to prevent watery
##mouth in a group of home-born lambs on the farm").
##Outcomes (both asked of every vignette):
##  rating = outcomeA: "Based only on the information provided above, how likely or unlikely is the vet
##           to prescribe the farmer with the antibiotic without visiting the farm first?" circled on
##           -5 (Definitely would not prescribe) .. 0 (Not sure) .. +5 (Definitely would prescribe);
##           stored by the authors as 1-11 (1 = -5, 11 = +5; article), kept as stored.
##  rating_others = outcomeB: "What proportion of vets do you think would prescribe this farmer
##           antibiotics without visiting the farm first?" marked on a 0-100% line; the authors grouped
##           it to the nearest 10% and coded 1-10 (article); stored 1-10, higher = more vets.
##39 rows lack outcomeA and 22 lack outcomeB; the 10 rows missing both are omitted (2,438 rows kept).
##Design (article): 384 possible combinations; vignettes drawn from them with a resolution-V
##D-efficient design and allocated at random to respondents; factor order fixed.
##Covariates (the authors' groupings, stored text): cov_age_group (agebin "<=30" / ">31"; the
##questionnaire asked 20-30, 31-40, ...), cov_practice_sa (practiceSA yesSA/noSA; presumably whether
##the practice also treats small animals), cov_region (grouped regions), cov_agreeableness (1-3; a
##grouping of the TIPI agreeableness items, cut points not documented), cov_practice_id (PracticeID,
##the practice; 199 practices). UniqueVigID (= id x 10 + task) dropped. No survey weight.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_excel(file.path(raw, "data_plosone.tab"), sheet = 1))
stopifnot(nrow(s) == 2448, uniqueN(s$UniqueID) == 306, s[, .N, UniqueID][, all(N == 8)], s[, uniqueN(VigNum), UniqueID][, all(V1 == 8)])
map <- list(
  knowledge = c(preventwaterymouth = "he wants to prevent watery mouth in a group of home-born lambs on the farm",
                suspectswaterymouth = "he suspects multiple cases of watery mouth on the farm",
                preventpneumonia = "he wants to prevent calf pneumonia in a group of home-born calves on the farm",
                suspectspneumonia = "he suspects multiple cases of calf pneumonia on the farm"),
  habit = c(sametimeeveryyear = "The farmer says that they use this antibiotic the same time every year.",
            neverused = "The farmer says that they have never used this antibiotic for this reason before, but have used it on the farm for a different reason."),
  farmer = c(`10yrsrare` = "The farmer has been a client at the vet practice for 10 years and the vet rarely visits the farm.",
             `10yrsreg` = "The farmer has been a client at the vet practice for 10 years and the vet regularly visits his dairy herd but not as involved with the sheep or beef cattle.",
             newclient = "The farmer has been a client at the vet practice for less than a year and the vet has visited the farm once."),
  vet = c(othervets = "Other vets in the practice have prescribed the farmer this antibiotic without a farm visit before",
          noothervet = "No other vet in the practice has prescribed the farmer this antibiotic without a farm visit before"),
  ease = c(happytopay = "the farmer is happy to pay for a vet visit if needed",
           notwanttopay = "the farmer does not want to pay for a vet visit"),
  time = c(notrunninglate = "The vet is not running late for their afternoon consults",
           runninglate = "The vet is running late for their afternoon consults"),
  confidence = c(confident = "is confident in the farmers’ judgement of disease",
                 notconfident = "is not confident in the farmers’ judgement of disease"))
d <- s[, .(id = as.integer(UniqueID), task = as.integer(VigNum), profile = 1L, rating = as.integer(outcomeA),
           rating_others = as.integer(outcomeB))]
for (k in names(map)) {
  v <- s[[paste0(k, "code")]]; stopifnot(all(v %in% names(map[[k]])))
  d[, paste0("attr_", k) := unname(map[[k]][v])]
}
d[, `:=`(cov_age_group = s$agebin, cov_practice_sa = s$practiceSA, cov_region = s$region,
         cov_agreeableness = as.integer(s$agreeableness), cov_practice_id = as.integer(s$PracticeID))]
stopifnot(d[, all(rating %in% 1:11 | is.na(rating))], d[, all(rating_others %in% 1:10 | is.na(rating_others))],
          d[, sum(is.na(rating))] == 39, d[, sum(is.na(rating_others))] == 22, d[, uniqueN(cov_practice_id)] == 199)
d <- d[!(is.na(rating) & is.na(rating_others))]
stopifnot(nrow(d) == 2438L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "doidge_2019_vet_antimicrobials.csv"))
