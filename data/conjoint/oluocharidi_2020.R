##Delivery-facility discrete choice experiment (Naivasha, Kenya) from
##Oluoch-Aridi, J., Adam, M. B., Wafula, F., & Kokwaro, G. (2020). Understanding what women want:
##Eliciting preference for delivery health facility in a rural subcounty in Kenya, a discrete
##choice experiment. BMJ Open, 10(12), e038865. https://doi.org/10.1136/bmjopen-2020-038865
##Data: Zenodo record 4268587 (doi:10.5281/zenodo.4268587), CC0 1.0 (record licence; the
##article itself is CC BY-NC). File read: BMJOPEN_Datafor_DRYAD.xlsx, sheets "Naivasha database"
##(the long DCE file) and "Readme" (variable names and covariate codings). Level wording and
##the choice question are from the article (Table 1 attributes and levels; Table 2 sample choice
##card), read on Europe PMC (PMC7713193).
##Usage: Rscript oluocharidi_2020.R <raw dir> <output dir>
##
##466 women aged 18-49 who had delivered within the previous 6 weeks, recruited at six health
##facilities in Naivasha Sub-County; enumerator-administered on a mobile phone (ODK). Each choice
##card: "you are pregnant and you are given a choice between the two health facilities to deliver
##your baby. Which one would you prefer? Facility A or facility B? You also have the option of
##choosing none of the two health facilities as option C" (option C: "None of the two health
##facilities - home delivery"). choice = 1 on the chosen facility; option C has no attributes, so
##it is not a profile (opt_out = yes): 7,456 tasks, of which those choosing C have choice 0 on
##both profiles. Facility A = profile 1, B = profile 2 (source `alt` 1/2; alt 3 = opt-out rows,
##dropped after reading the choice). task = the source's choice_set (1-16), assumed to be the
##order shown.
##Attributes (source dummy pairs -> level text of the article's sample card, Table 2):
##  attr_quality ("Quality of clinical care during delivery"): Good quality / Bad quality
##  attr_attitude ("Attitude of healthcare workers"): Kind and supportive attitude / Unkind attitude
##  attr_cost ("Cost of delivery services"): Ksh3000 / Ksh5000 / Ksh8000
##  attr_equipment ("Availability of equipment and supplies"): Equipment and supplies available /
##     Equipment and supplies not available (the card prints "Equipment supplies not available")
##  attr_distance ("Distance to health facility"): Facility is close to home / Facility is far from home
##  attr_referral ("Availability of referral health services"): Referral services available /
##     Referral services unavailable
##Every non-opt-out row has exactly one of each dummy pair set (checked below). The card's row
##order is fixed (article Table 2). The respondents' language is not stated (the article shows
##English); display_language unknown.
##Design: D-efficient fractional design from Ngene, 2 blocks (article). The article says each
##respondent saw one block of 8 choice sets, but the deposit has 16 sets (both blocks, 8 each)
##for every respondent, and the same (block, choice set, alternative) carries 2-3 different
##profiles across respondents (several design versions, source v1); kept as deposited, flagged.
##Covariates (Readme sheet codings): cov_married, cov_head_of_household, cov_influence_hoh,
##cov_main_earner, cov_insurance (1 = Yes, 0 = No);
##cov_birthplace_facility (birthplace_type1, "Where did you deliver this baby?" 1 = Health
##facility, 0 = Home). Codes that do not match the Readme are kept as codes with a _code suffix:
##cov_schooling_code (0-4 in the data; Readme lists Primary 1, Secondary 2, Tertiary 3),
##cov_residence_code (0/1; Readme lists "Within the subCounty", "Outside the subCounty" without
##codes), cov_moved_when_code, cov_pregnancies_code (1-15; Readme lists 1, >2, >3),
##cov_hoh_career_code (1-4; Readme lists Yes 1 / No 0).
##Dropped: ODK uuids (baseline_uuid, dce_uuid, uuid, merge key), consent (all 1), _merge,
##birthplace_facility_level (all 0, not a Readme code), motherhoodpregnantnow ("Are you
##pregnant now?" is 1 = Yes for everyone, implausible for recently delivered women), ncs, asc_optout, the design version v1.
##No survey weight. No repeated task. Respondent IDs re-keyed 1..466 in source order.
##N = 466 as in the article (474 sampled). Spot check: a conditional logit on this table (opt-out
##row added, binary attributes coded 1 = worse level, cost linear, opt-out constant) gives attitude
##-1.18, equipment -1.08, quality -0.80, distance -0.47, referral -0.26, cost 0.00003; the article
##reports 1.184, 1.073, 0.826, 0.457, 0.266, 0.000018 (close, not exact; model details differ).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressMessages(read_excel(file.path(raw, "BMJOPEN_Datafor_DRYAD.xlsx"), sheet = "Naivasha database")))
stopifnot(x[, .N, respondent_id][, all(N == 48)], x[, sum(choice), .(respondent_id, choice_set)][, all(V1 == 1)],
          all(x[alt == 3, asc_optout] == 1), all(x[alt != 3, asc_optout] == 0))
p <- x[alt != 3]
pair <- function(a1, a0, l) { stopifnot(all(p[[a1]] + p[[a0]] == 1)); fifelse(p[[a1]] == 1, l[1], l[2]) }
stopifnot(all(p$cost %in% c(3000, 5000, 8000)))
d <- data.table(id = as.integer(factor(p$respondent_id, levels = unique(x$respondent_id))),
                task = as.integer(p$choice_set), profile = as.integer(p$alt), choice = as.integer(p$choice),
                attr_quality = pair("goodqualityclinicalservices", "badqualityclinicalservices", c("Good quality", "Bad quality")),
                attr_attitude = pair("attitudekindsupportive", "attitudeunkindnotsupportive",
                                     c("Kind and supportive attitude", "Unkind attitude")),
                attr_cost = paste0("Ksh", p$cost),
                attr_equipment = pair("medicalequipmentdrugsavail", "medicalequipmentdrugsnotavail",
                                      c("Equipment and supplies available", "Equipment and supplies not available")),
                attr_distance = pair("distancetofacilityshort", "distancetofacilitylong",
                                     c("Facility is close to home", "Facility is far from home")),
                attr_referral = pair("referralservicesavailable", "referralservicesnotavailable",
                                     c("Referral services available", "Referral services unavailable")))
cm <- c(married = "married", hoh = "head_of_household", hohnoinfluence = "influence_hoh", mainearner = "main_earner",
        motherhoodinsurance = "insurance",
        birthplace_type1 = "birthplace_facility")
for (v in names(cm)) { stopifnot(all(p[[v]] %in% c(0, 1, NA))); d[, paste0("cov_", cm[[v]]) := as.integer(p[[v]])] }
d[, `:=`(cov_schooling_code = as.integer(p$schooling), cov_residence_code = as.integer(p$residence),
         cov_moved_when_code = as.integer(p$movedwhen), cov_pregnancies_code = as.integer(p$motherhoodpregnancyexperiencetim),
         cov_hoh_career_code = as.integer(p$hohcareer))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "oluocharidi_2020_delivery_facility.csv"))
