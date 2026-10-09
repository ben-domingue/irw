##Collective housing-investment DCE, Czech online sample, from the ENBLOC survey:
##Frankowski, J., Stara, S., Belch, W., Sokolowski, J., Mazurkiewicz, J., Nesladek, M., Prusak, A.,
##& Vacha, T. (2026). Housing conditions, residents' attitudes and preferences towards
##investments in multi-apartment buildings in Poland and Czechia: ENBLOC survey and discrete
##choice experiment data [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22097143
##(related working paper: Frankowski et al. 2026, Collective decision-making in private
##multi-apartment buildings: Evidence from a discrete choice experiment, IBS WP 02/2026).
##Licence: CC BY 4.0 (Zenodo record; the readme states no other terms). Files read:
##ENBLOC_survey_ and_DCE_dataset.xlsx, sheets dce_dataset, dce_variables_codebook,
##survey_dataset. Design facts: ENBLOC_survey_and_DCE_dataset_readme.pdf and the
##questionnaire ENBLOC_survey_and_DCE_vignette_EN.pdf (question G1).
##Usage: Rscript frankowski_2026.R <raw dir> <output dir>
##
##THIS TABLE HOLDS ONLY THE CZECH CAWI SAMPLE (CZ_cawi, 1,531 respondents, Czech national online
##panel, Sept-Oct 2024). The deposit has four fieldings run by four companies (readme); the
##other three are not built:
##  PL_cawi (4,488): the stored choice is not consistent across the five attribute rows of an
##    option in 88% of tasks (in the other samples it is consistent in 100%); the per-attribute
##    choices are nearly uncorrelated (r ~ .05), so which option was chosen cannot be recovered.
##  PL_capi (1,201) and CZ_capi (302): the property-value attribute has 7 codes where the
##    codebook lists 9 levels, so the level text cannot be assigned.
##Respondents read G1 ("Please imagine that [housing cooperative/association] considers various
##investments from the renovation fund ...") and made 5 choices (task = screen) between OPTION A
##(profile 1, variant 1) and OPTION B (profile 2), "Please check the option that suits you best";
##no opt-out (readme). Five attributes, level text = the Czech labels of the codebook (cz_name;
##respondents saw Czech): attr_beneficiary (Pro koho budou prinosne: Spolecne prostory v ramci
##vchodu / Cely blok / Mistni komunita; English: my staircase / entire block / local community),
##attr_engagement (Vase zapojeni: internet vote / raising hand at the meeting / discussing the
##scope), attr_decision (Konecne rozhodnuti: board alone / unanimous / majority), attr_housing_cost
##(monthly housing costs after the investment, -30% .. +30% in steps of 10) and
##attr_property_value (value per m2 in 5 years, -20% .. +20% in steps of 5). The last two were
##SHOWN AS AMOUNTS computed from the respondent's own answers (E1 housing fees, D3 value per m2,
##times the percentage; questionnaire G1); the table stores the percentage (the codebook level),
##not the amount on screen. Both options of a task can share a level (allowed).
##The deposit's `order` column ("Order in which particular pair was displayed") repeats values
##within a screen for 15% of screens, so it is not stored as attrpos_.
##rating_confidence = G2 "To what extent are you confident with your choice?" 0-100 in steps of
##10 (task level; stored on both rows of the task).
##Covariates (survey_dataset, codebook): cov_gender (I1 1 man, 2 woman, 3 other), cov_education
##(I2 1 primary, 2 secondary, 3 tertiary, as codebook text), cov_birth_year (I3), cov_institution
##(A2: housing association / housing cooperative; the sample was drawn in both, 777 / 754),
##cov_owner (A4 code, codebook: 1 owner, 2 cooperative ownership right, 4 rents from the
##cooperative, 5 rents, 6 lives with the owner, 7 lent for free), cov_income (J3 Czech bands,
##codebook text; 6 "do not want to answer" -> NA), cov_polit_belief (0 left .. 10 right),
##cov_duration_sec (time_full_survey, assumed seconds). Respondent ids re-keyed 1..1,531 (the source
##number after CZ_cawi_ may be a panel id). The weights column is 1 for this sample
##(the readme's weight applies to PL_cawi only). Other survey items not kept.
##N = 1,531 as in the readme.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "ENBLOC_survey_ and_DCE_dataset.xlsx")
x <- as.data.table(read_excel(f, sheet = "dce_dataset"))
x <- x[grepl("^CZ_cawi_[0-9]+$", id)]
cb <- as.data.table(read_excel(f, sheet = "dce_variables_codebook"))
i0 <- which(cb$variable == "value if kid=1")
cz <- cb$cz_name[i0:(i0 + 24)]; cdv <- cb$code[i0:(i0 + 24)]
kidn <- rep(1:5, c(3, 3, 3, 7, 9))
stopifnot(identical(as.numeric(cdv), as.numeric(c(1:3, 1:3, 1:3, 1:7, 1:9))))
x[, lev := cz[match(paste(kid, value), paste(kidn, cdv))]]
stopifnot(!is.na(x$lev), x[, .N, .(id, screen)][, all(N == 10)], all(x$pid == (x$kid - 1) * 2 + x$variant))
# choice consistent across the five rows of an option, exactly one option per task
ch <- x[, .(choice = unique(choice)), .(id, screen, variant)]
stopifnot(ch[, .N, .(id, screen, variant)][, all(N == 1)], ch[, sum(choice), .(id, screen)][, all(V1 == 1)])
w <- dcast(x, id + screen + variant ~ kid, value.var = "lev")
setnames(w, as.character(1:5), c("attr_beneficiary", "attr_engagement", "attr_decision", "attr_housing_cost", "attr_property_value"))
w <- merge(w, ch, by = c("id", "screen", "variant"))
conf <- unique(x[, .(id, screen, rating_confidence = as.integer(choice_confidence))])
stopifnot(conf[, .N, .(id, screen)][, all(N == 1)], all(conf$rating_confidence %in% seq(0, 100, 10)))
w <- merge(w, conf, by = c("id", "screen"))
dur <- unique(x[, .(id, cov_duration_sec = time_full_survey)]); stopifnot(!anyDuplicated(dur$id))
s <- as.data.table(read_excel(f, sheet = "survey_dataset", guess_max = 8000))[grepl("^CZ_cawi_[0-9]+$", id)]
stopifnot(all(s$gender %in% 1:3), all(s$education %in% 1:3), all(s$institution %in% 1:2), all(s$income %in% 1:6), all(s$weights == 1))
cv <- s[, .(id, cov_gender = c("male", "female", "other")[gender], cov_education = c("primary", "secondary", "tertiary")[education],
            cov_birth_year = as.integer(year),
            cov_institution = c("housing association", "housing cooperative")[institution], cov_owner = as.integer(owner),
            cov_income = c("do 25 001", "25 001 - 40 000", "40 001 - 55 000", "55 001 - 70 000", "70 001 a v\u00edce", NA)[income],
            cov_polit_belief = as.integer(polit_belief))]
d <- merge(merge(w, cv, by = "id"), dur, by = "id")
stopifnot(uniqueN(d$id) == 1531)
d[, idn := match(id, sort(unique(id)))]  # the numeric part may be a panel id: re-keyed
d <- d[, c(list(id = idn, task = as.integer(screen), profile = as.integer(variant)), .SD),
       .SDcols = !c("id", "idn", "screen", "variant")]
setcolorder(d, c("id", "task", "profile", "choice", "rating_confidence"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "frankowski_2026_housing_invest_cz.csv"))
