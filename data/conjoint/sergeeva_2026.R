##XR (extended reality) system vignettes for machinery operators from
##Sergeeva, A. (2026). THEIA-XR: Machinery operators' perceptions of different XR implementations
##[Data set]. Zenodo. https://doi.org/10.5281/zenodo.18467408  (no article DOI in the record)
##Licence: CC BY 4.0 (Zenodo record). File read: 20250203_THEIA_XR_Dataset.xlsx, sheets "Dataset" and
##"Scales Description" (the codebook).
##Usage: Rscript sergeeva_2026.R <dir holding the xlsx> <output dir>
##
##Prolific panel, December 2025 (Theia-XR EU Horizon project), persons with machinery-operating
##experience. 264 respondents x 3 vignettes (UCCondition 1-3) = 792 rows. Four binary vignette
##conditions: storage (CheckPUC), switch (CheckAUC), reminders (CheckOUC), communication (CheckCUC).
##The rows of a vignette whose content attention check was failed have all four conditions and all
##outcomes erased by the depositors (53 rows): dropped. Two respondents whose Sex field reads CONSENT_REVOKED
##(6 rows) are dropped too. Result: 733 rows, 262 respondents (2 or 3 vignettes each).
##Attribute text: the deposit stores 1/2 codes; the vignette wording itself (Figure 2 of the article) is
##not in the deposit. The levels are PARAPHRASED from the "Scales Description" explanations:
##  storage: 1 = collection but not storage, 2 = collection and storage of data
##  switch: 1 = the operator can switch the XR system on and off at any moment, 2 = always active
##  reminders: 1 = the system reminds the operator to verify the operating conditions themselves, 2 = no reminder
##  communication: 1 = the system does not affect working communication, 2 = reduces communication
##(LABELS: paraphrased from the codebook, not the displayed vignette text.)
##Outcome kept: rating = AcceptabilityUC, one item "how acceptable is the technology", 1 (not at all
##acceptable) to 20 (totally acceptable) (codebook). Dropped as derived scale sums: the per-vignette
##scale totals (autonomy, boredom, communication, distraction, detachment, devaluation, collection concerns,
##overreliance, ease of use/TAM); item-level data are not in the deposit. No opt-out. Task = UCCondition
##(vignette number 1-3; the codebook says each participant evaluated 3 vignettes; presentation order not documented); profile = 1.
##Randomization: eight combinations hold 98% of the rows and form a half-fraction of the 2^4 (never all 16:
##storage/switch/reminders/communication = 1111,1122,1212,1221,2112,2121,2211,2222 in code order). Three further
##combinations occur 1-3 times each (1 2 1 1, 1 2 2 2, 2 1 2 2: 1+2+1 rows), kept as recorded;
##restrictions OBSERVED, level shares near-equal. Age: values that are not numbers become NA.
##Covariates: cov_gender (Female/Male text -> female/male; blank -> NA), cov_age (years),
##cov_country_of_residence, cov_language (native language, text), cov_operator_years (years as operator),
##cov_current_operator (CurWork). Dropped: ResponseID (LimeSurvey id, re-keyed), the free-text feedback
##(FFEDB) and OtherExperience, nationality, ME-Work and privacy-concern item batteries and totals (respondent
##scales), machine-experience flags. No survey weight. No Prolific IDs in the file.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_excel(file.path(raw, "20250203_THEIA_XR_Dataset.xlsx"), sheet = "Dataset"))
stopifnot(nrow(s) == 792, uniqueN(s$ResponseID) == 264)
revoked <- unique(s[Sex == "CONSENT_REVOKED", ResponseID])
s <- s[!(ResponseID %in% revoked)]
s <- s[!is.na(CheckPUC) & !is.na(AcceptabilityUC)]
M <- function(x, lab) unname(lab[as.character(x)])
d <- s[, .(id = as.integer(factor(ResponseID, levels = unique(ResponseID))), task = as.integer(UCCondition), profile = 1L,
           rating = as.integer(AcceptabilityUC),
           attr_storage = M(CheckPUC, c("1" = "Data collection but no storage", "2" = "Data collection and storage")),
           attr_switch = M(CheckAUC, c("1" = "Operator can switch the XR system on and off at any moment", "2" = "XR system always active")),
           attr_reminders = M(CheckOUC, c("1" = "XR system reminds the operator to verify the operating conditions themselves", "2" = "XR system gives no such reminder")),
           attr_communication = M(CheckCUC, c("1" = "XR system does not affect working communication", "2" = "XR system reduces working communication")),
           cov_gender = M(Sex, c(Female = "female", Male = "male")), cov_age = as.integer(Age),
           cov_country_of_residence = Countryofresidence, cov_language = Language,
           cov_operator_years = as.numeric(Operator), cov_current_operator = CurWork)]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]), d[, all(rating %between% c(0, 20))])
setorder(d, id, task, profile)
cat(nrow(d), uniqueN(d$id), "\n")
fwrite(d, file.path(out, "sergeeva_2026_xr_operators.csv"))
