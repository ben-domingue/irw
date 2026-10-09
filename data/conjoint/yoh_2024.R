##Journal-choice discrete choice experiment (conservation authors) from
##Yoh, N., Holle, M. J. M., Willis, J., Rudd, L. F., Fraser, I. M., & Veríssimo, D. (2024).
##Understanding author choices in the current conservation publishing landscape. Conservation
##Biology, 39(2), e14369. https://doi.org/10.1111/cobi.14369 (preprint bioRxiv
##10.1101/2023.08.24.554591, used for design facts; the Zenodo record cites it under its earlier
##title "How do conservationists choose where to publish?").
##Data: Zenodo record 8276263 (doi:10.5281/zenodo.8276263), CC BY 4.0, one file.
##File read: ChoiceExperiment_Finaldata_Zenodo.xlsx, sheet ChoiceExperiment_PPconservation
##(the ReadMe sheet documents the columns). Usage: Rscript yoh_2024.R <raw dir> <output dir>
##
##1,038 authors who had published in a conservation-related journal (online survey; contacted via
##18 target journals and conservation organisations' channels; worldwide). DCE: 12 choice sets of
##three hypothetical journals (a, b, c) plus the opt-out "Would not choose any of these journals"
##(preprint L104). The design is FIXED: a Bayesian D-efficient design from Ngene (preprint L107-117),
##no blocks; every respondent saw the same 12 cards (verified: each card id has one set of levels).
##task = the card number (1-12) of that fixed design, NOT the presentation order: the deposit's row
##order is not grouped by respondent and the order shown is not recorded. profile = alternative
##a/b/c -> 1/2/3 (recorded). The opt-out alternative has no attributes and is not a profile.
##Outcome: choice = FinalChoice ("Card preference per choice"), opt_out yes: when the opt-out was
##chosen (3,510 of 12,365 sets) all three profiles have choice 0. The question wording is not in the
##deposit or preprint (Appendix 1 questionnaire not seen); recorded as a paraphrase.
##91 respondent x card sets have no choice at all (skipped) and are dropped; 12,365 sets remain,
##matching the preprint's "12,365 choice cards from 1038 respondents" (L178).
##Attributes (7; level text as stored in the deposit, which writes them as short CamelCase words;
##the displayed card is an image, Figure 1, not recoverable): scope Global/Regional/National;
##access OpenAccess/Paywall; impact_factor 1/6/12/20/40 and "Non" -> "No impact factor" (preprint
##Table 1 note b); editorial_support FreeSupport/PaidSupport/NoSupport (English-language support
##for non-native speakers, ReadMe); review SingleBlind/DoubleBlind; society Society/NonSociety;
##cost (US$) 100/1500/3000/7000/10000 and 0 -> "Free" (preprint Table 1 note f). Display language
##English (assumed from the English-only instrument; no translation is mentioned).
##Covariates (ReadMe sheet): cov_n_papers (papers published in the last year, as typed; one
##respondent has 45079, kept as recorded); cov_age_group (AgeInter; "Prefer not to say" -> NA);
##cov_country_residence, cov_region_residence, cov_income_group (World Bank 2022 group of the
##country of residence); cov_nationality_region_1..5 (nationalities summarised to region);
##cov_racial_identity_1..4 (multi-choice text as stored, "No response" kept as stored).
##No survey weight. No PII in the deposit (respondent numbers are survey sequence numbers, kept).
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "ChoiceExperiment_Finaldata_Zenodo.xlsx"), sheet = "ChoiceExperiment_PPconservation",
                              col_types = "text"))
x[, card := as.integer(sub("([a-c]|WouldNot)$", "", Card))]
stopifnot(all(x$card == as.integer(x$ChoiceRaw)), all(x$FinalChoice %in% c("0", "1")))
x[, s := sum(as.integer(FinalChoice)), .(Respondent, card)]
stopifnot(all(x$s %in% 0:1))
x <- x[s == 1 & !grepl("WouldNot", Card)]
d <- data.table(id = as.integer(x$Respondent), task = x$card, profile = match(sub("^[0-9]+", "", x$Card), c("a", "b", "c")),
                choice = as.integer(x$FinalChoice))
stopifnot(!anyNA(d$profile), d[, .N, .(id, task)][, all(N == 3)])
d[, `:=`(attr_scope = x$Scope, attr_access = x$Access, attr_impact_factor = fifelse(x$Ifactor == "Non", "No impact factor", x$Ifactor),
         attr_editorial_support = x$EditSup, attr_review = x$Review, attr_society = x$SocietyAff,
         attr_cost_usd = fifelse(x$Cost == "0", "Free", x$Cost))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), !any(unlist(d[, .SD, .SDcols = patterns("^attr_")]) == "-999"))
# one set of levels per card (fixed design)
stopifnot(unique(d[, !c("id", "choice")])[, .N, .(task, profile)][, all(N == 1)])
na <- function(v) { v[v %in% c("NA", "")] <- NA; v }
d[, cov_n_papers := as.integer(na(x$NPapers))]
d[, cov_age_group := fifelse(x$AgeInter == "Prefer not to say", NA_character_, x$AgeInter)]
d[, `:=`(cov_country_residence = na(x$CountryOfResidence), cov_region_residence = na(x$RegionOfResidence),
         cov_income_group = na(x$`Income group`))]
for (k in 1:5) d[, paste0("cov_nationality_region_", k) := na(x[[paste0("Nationality_", k, "Sum")]])]
for (k in 1:4) d[, paste0("cov_racial_identity_", k) := na(x[[paste0("RacialIdentity_", k)]])]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "yoh_2024_journal_choice.csv"))
