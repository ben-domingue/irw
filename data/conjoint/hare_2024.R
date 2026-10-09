##Trophy-hunting acceptability vignette experiment (USA, UK, South Africa) from
##Hare, D., Dickman, A. J., Johnson, P. J., Rono, B. J., Mutinhima, Y., Sutherland, C., Kulunge, S.,
##Sibanda, L., Mandoloma, L., & Kimaili, D. (2024). Public perceptions of trophy hunting are
##pragmatic, not dogmatic. Proceedings of the Royal Society B, 291, 20231638.
##https://doi.org/10.1098/rspb.2023.1638 (open access; read via Europe PMC PMC10865007)
##Replication data: Zenodo record 10641548 (doi 10.5281/zenodo.10641548), CC0 1.0. File read:
##final.data.csv (one row per participant, text values). The record's README.md could not be
##downloaded (Zenodo 504 on three attempts); variables are self-explanatory text.
##Usage: Rscript hare_2024.R <dir holding final.data.csv> <output dir>
##
##1,192 urban residents (Qualtrics panels; 404 USA, 388 UK, 400 South Africa; article: final dataset
##1,192, matches) each read ONE randomly assigned vignette (task = 1, profile = 1) from a full
##2 x 2 x 3 factorial about a tourist from the USA who would like to hunt in sub-Saharan Africa and
##keep the animal's head. The vignette text is in the article's supplement S3 (not read); level text
##is the article's description of the manipulated language (Methods (b)), mapped from the deposit's
##short labels: attr_animal Elephant -> "an elephant", Zebra -> "a zebra"; attr_meat People ->
##"Meat provided to local people", Wildlife -> "Meat left for wildlife"; attr_revenue Conservation ->
##"Revenue supports conservation in the area", Development -> "Revenue supports economic development
##in the area", Hunting -> "Revenue supports hunting enterprises in the area".
##One table: the three countries got the same vignettes and are modelled together (country as a
##predictor); cov_country.
##Outcome: rating = acceptability of the specific hunt described, 7-point bipolar scale stored as
##1 = Very unacceptable, 2 = Unacceptable, 3 = Somewhat unacceptable, 4 = Neither acceptable nor
##unacceptable, 5 = Somewhat acceptable, 6 = Acceptable, 7 = Very acceptable (the deposit stores the
##answer text; the 1-7 numbering follows the scale order of the article, higher = more acceptable).
##The authors removed 25 "I don't know" answers, 8 participants not identifying as female/male, and
##speeders/slow completers before deposit.
##Covariates (answer text as stored): cov_country (SA/UK/USA), cov_gender (Female/Male -> female/male),
##cov_age (years), cov_education, cov_rural_upbringing (rural.past.combined), cov_people_vs_animals,
##cov_individuals_vs_groups, cov_identity_hunter / _conservationist / _animal_protectionist /
##_human_rights (agreement text; "I don't know" kept as text). Dropped: vignette code (redundant).
##No respondent id in the deposit: id = row number. No weights.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "final.data.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 1192L)
sc <- c("Very unacceptable", "Unacceptable", "Somewhat unacceptable", "Neither acceptable nor unacceptable",
        "Somewhat acceptable", "Acceptable", "Very acceptable")
stopifnot(all(s$response.text %in% sc), s[, all(paste0(tolower(substr(animal, 1, 1)), ".", tolower(substr(meat, 1, 1)), ".",
                                                       tolower(substr(revenue, 1, 1))) == vignette)])
d <- s[, .(id = .I, task = 1L, profile = 1L, rating = match(response.text, sc),
           attr_animal = c(Elephant = "an elephant", Zebra = "a zebra")[animal],
           attr_meat = c(People = "Meat provided to local people", Wildlife = "Meat left for wildlife")[meat],
           attr_revenue = c(Conservation = "Revenue supports conservation in the area",
                            Development = "Revenue supports economic development in the area",
                            Hunting = "Revenue supports hunting enterprises in the area")[revenue],
           cov_country = country.1, cov_gender = c(Female = "female", Male = "male")[gender], cov_age = as.integer(age),
           cov_education = trimws(education), cov_rural_upbringing = rural.past.combined,
           cov_people_vs_animals = people.animals, cov_individuals_vs_groups = individuals.groups,
           cov_identity_hunter = hunter, cov_identity_conservationist = conservationist,
           cov_identity_animal_protectionist = animal.protectionist, cov_identity_human_rights = human.rights)]
for (v in grep("^attr_|^cov_gender", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hare_2024_trophy_hunting.csv"))
