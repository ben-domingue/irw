##Residential location conjoint among recent immigrants to Switzerland from
##Bennour, S., Manatschal, A., & Ruedin, D. (2022). How political reception contexts shape location
##decisions of immigrants. Journal of Ethnic and Migration Studies.
##https://doi.org/10.1080/1369183X.2022.2098468
##Replication data: Zenodo record 6965553 (doi:10.5281/zenodo.6965553), "Location Decision",
##CC BY 4.0, open access. Files read: c_LocationDecision.sav (the raw Qualtrics export, 2,309 rows x
##511 columns: NOT the 15-variable long file the DDI codebook describes), a_LocationDecision.pdf
##(DDI codebook: attribute levels, outcome scales) and d_VignetteSample.png (the English screen:
##intro, attribute rows, answer options). b_LocationDecision.xml (same DDI) not needed.
##Usage: Rscript bennour_2022.R <dir holding c_LocationDecision.sav> <output dir>
##
##Immigrants of working age who had arrived in Switzerland in the previous 15 years, recruited
##from the respondents of the Migration-Mobility Survey 2020 (nccr - on the move), Qualtrics,
##2020-10-01 to 2021-02-27 (codebook). "Imagine you have an attractive long-term job offer. You plan
##to accept the job and settle nearby, and can choose to live in one of two municipalities, which
##are at equal distance from your new employment. On the following pages, you'll have to choose
##between two municipalities. In which municipality would you prefer to live?" Five pairs
##(Municipality A / Municipality B) shown as a grid with eight rows in a fixed order.
##Questionnaire languages (UserLanguage): English 1,118, German 449, French 316, Italian 140,
##Spanish 168, Portuguese 118 rows of the export; the export stores each level in every language
##(suffix f/d/i/s/p); this table stores the ENGLISH level text for everyone and the respondent's
##questionnaire language in cov_language.
##Attributes (export <Attr><vignette A-E><municipality 1/2>; levels as in the English grid):
##  attr_transport       Reaching main commodities (shopping centres, schools, doctors, ...)
##  attr_nature          Access to nature (forest, lake, river, ...)
##  attr_cost            Living costs (rent, taxes, health insurance, ...)
##  attr_attitudes       Share of SVP/UDC (anti-immigrant party)
##  attr_naturalization  Swiss citizenship requires
##  attr_coethnic        People from the same country as you
##  attr_voting          Non-citizen voting rights in the municipality for legal permanent residents (C Permit)
##  attr_infrastructure  Local infrastructure for cultural and leisure activities
##All eight are binary and near 50/50 (codebook frequencies); no restrictions documented.
##Vignette letter A-E = task 1-5 and the five choice questions follow in that order
##(Imagineyouhaveanattractivel, MunicipalityAMunicipality, W, Z, AC); the mapping is VERIFIED: a
##cheaper municipality wins 61-63% of choices when the letter and the question match, ~50% otherwise.
##profile 1 = Municipality A (left column), 2 = Municipality B.
##Outcomes:
##  choice  "In which municipality would you prefer to live?" I pick municipality A / B (forced, no
##          opt-out; a blank answer leaves the task without a choice and the task is kept only if
##          a rating exists, choice NA on both rows).
##  rating  "How likely is it that you would choose to live in Municipality A [B]?" 0-10 (codebook:
##          0 = worst evaluation, 10 = best evaluation); export columns Howlikelyisitthatyouwould/S,
##          U/V, X/Y, AA/AB, AD/AE.
##Respondents: only the 1,589 FINISHED records are kept (Finished = True; each answered all five
##choices and all ten ratings); the 437 unfinished records with 1-4 answered tasks are dropped, in
##line with the authors' published long file (codebook: 1,596 respondents x 5 tasks; 7 more than
##the finished records here, not identifiable).
##Covariates: cov_age (Whatisyourageinyears, years; only whole numbers 15-99 kept), cov_gender
##(Male/Female/Other -> male/female/other; the free-text field is dropped), cov_language
##(UserLanguage), cov_duration_sec
##(Durationinseconds, the whole conjoint module).
##Dropped: ExternalDataReference and RecipientFirstName (the respondent's Migration-Mobility Survey
##id, which links to that restricted survey; respondents re-keyed 1..N), placeholder recipient
##name/e-mail fields, dates, Progress, ResponseType, DistributionChannel. No survey weight.
##N: codebook 1,596 respondents (15,960 rows, 5 tasks); export 2,309 records, 1,589 finished.
##This table: 1,589 respondents, 7,945 tasks, 15,890 rows.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "c_LocationDecision.sav")))
stopifnot(nrow(s) == 2309)
s[, rid := .I]
stopifnot(all(s$Finished %in% c("True", "False")))
s <- s[Finished == "True"]
ch <- c("Imagineyouhaveanattractivel", "MunicipalityAMunicipality", "W", "Z", "AC")
ra <- c("Howlikelyisitthatyouwould", "U", "X", "AA", "AD"); rb <- c("S", "V", "Y", "AB", "AE")
at <- c(Transport = "transport", Nature = "nature", Cost = "cost", Attitudes = "attitudes", Naturalization = "naturalization",
        Coethnic = "coethnic", Voting = "voting", Infrastructure = "infrastructure")
L <- list()
for (k in 1:5) for (p in 1:2) {
  pick <- s[[ch[k]]]; stopifnot(all(pick %in% c("", "I pick municipality A", "I pick municipality B")))
  r <- data.table(rid = s$rid, task = k, profile = p,
                  choice = fifelse(pick == "", NA_integer_, as.integer(pick == c("I pick municipality A", "I pick municipality B")[p])),
                  rating = as.integer(s[[c(ra[k], rb[k])[p]]]))
  for (an in names(at)) r[, paste0("attr_", at[[an]]) := s[[paste0(an, LETTERS[k], p)]]]
  L[[length(L) + 1]] <- r
}
d <- rbindlist(L)
stopifnot(all(d$rating %in% c(0:10, NA)))
acols <- paste0("attr_", at)
d[, blank := Reduce(`|`, lapply(.SD, function(x) is.na(x) | x == "")), .SDcols = acols]
d[, task_blank := any(blank), .(rid, task)]
d[, task_out := any(!is.na(choice) | !is.na(rating)), .(rid, task)]
cat("tasks with outcome but blank attributes:", d[task_out & task_blank, uniqueN(paste(rid, task))], "\n")
d <- d[task_out & !task_blank][, c("blank", "task_blank", "task_out") := NULL]
stopifnot(d[, uniqueN(task), rid][, all(V1 == 5)], !anyNA(d$choice), !anyNA(d$rating))
stopifnot(d[, .N, .(rid, task)][, all(N == 2)])
stopifnot(d[!is.na(choice), sum(choice), .(rid, task)][, all(V1 == 1)], d[, uniqueN(is.na(choice)), .(rid, task)][, all(V1 == 1)])
levs <- list(transport = c("Connection every half hour until 24:00", "Connection every hour until 20:00"),
             nature = c("Not in walking distance", "Walking distance"),
             cost = c("15% less expensive than your current municipality", "15% more expensive than your current municipality"),
             attitudes = c("Higher than in surrounding municipalities", "Lower than in surrounding municipalities"),
             naturalization = c("2 years of residence in the municipality", "8 years of residence in the municipality"),
             coethnic = c("No proper network", "Strong social network"),
             voting = c("No noncitizen voting right", "Possible after one year of residence in the canton"),
             infrastructure = c("Limited offer", "Rich offer"))
for (an in names(levs)) stopifnot(all(d[[paste0("attr_", an)]] %in% levs[[an]]))
age <- as.numeric(s$Whatisyourageinyears)
cv <- data.table(rid = s$rid, cov_age = fifelse(!is.na(age) & age == round(age) & age >= 15 & age <= 99, as.integer(age), NA_integer_),
                 cov_gender = c(Male = "male", Female = "female", Other = "other")[s$WhatisyourgenderSelected],
                 cov_language = s$UserLanguage,
                 cov_duration_sec = as.numeric(s$Durationinseconds))
stopifnot(all(s$WhatisyourgenderSelected %in% c("", "Male", "Female", "Other")))
d <- merge(d, cv, by = "rid")
ids <- sort(unique(d$rid)); d[, id := match(rid, ids)][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating", acols))
setorder(d, id, task, profile)
cat(uniqueN(d$id), "respondents,", nrow(d), "rows,", d[, uniqueN(paste(id, task))], "tasks\n")
fwrite(d, file.path(out, "bennour_2022_location_decision.csv"))
