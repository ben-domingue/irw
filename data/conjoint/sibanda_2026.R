##International acceptability of trophy hunting (10 publics, sub-Saharan Africa, UK, US) from
##Sibanda, L., et al. (2026). The international acceptability of trophy hunting in sub-Saharan Africa. (Author list and journal
##are not in the files read; the deposit's R script header names Sibanda et al.; no article DOI.)
##Replication data: figshare doi:10.6084/m9.figshare.34899687, CC BY 4.0 (figshare record licence). Files read: "herbivore
##experiment.csv", "Carnivore experiment.csv" (renamed herb.csv / carn.csv here) and the authors' R script (text).
##Usage: Rscript sibanda_2026.R <dir holding herb.csv and carn.csv> <output dir>
##Different deposit from hare_2024_trophy_hunting (Zenodo 10641548; USA/UK/South Africa urban residents, other design): different
##samples (10 publics incl. rural African communities), different vignettes (herbivore + carnivore sets), not a duplicate.
##
##Two vignette experiments, each respondent reading ONE randomly assigned vignette from each set (the same ~3,650 respondents
##appear in both files: ResponseId overlaps; the id here is the same integer for the same respondent in both tables). Each table is one
##experiment (task = 1, profile = 1; a 2 x 2 x 2 full factorial of vignette factors, 8 scenarios):
##  sibanda_2026_trophy_herbivores (3,699 respondents): species (elephant/zebra), meat use (people/wildlife), revenue use
##    (conservation/development).
##  sibanda_2026_trophy_carnivores (3,694 respondents): hunter (foreigner/local), species (lion/leopard; read from the scenario
##    code in column `species`, which holds the full scenario "hunter.species.revenue"), revenue use (conservation/development).
##LABELS: tags only. The deposit stores the short analysis tags (e.g. "zebra", "people", "development", "foreigner"); the vignette text
##shown is not in the deposit or the script and was not recovered from the article, so attr_ columns carry the tags as stored.
##Outcome rating: acceptability of the hunt described, stored as text and coded 1-7 in scale order: 1 Very unacceptable, 2 Unacceptable,
##3 Somewhat unacceptable, 4 Neither acceptable nor unacceptable, 5 Somewhat acceptable, 6 Acceptable, 7 Very acceptable (higher = more
##acceptable; the numbering follows the scale order, as in the hare_2024 table). Question wording not in the deposit.
##Samples pooled in each table (the authors' models take location as a predictor, with a household random effect): cov_country,
##cov_location (New_location: Hwange, Kariba, Magadi, Mau, Tanzania, Online SSA, UKRural, UKUrban, USRural, USUrban).
##Covariates (answer text as stored): cov_gender (Female/Male), cov_age_group, cov_education, cov_relative_wealth, cov_people_vs_animals,
##cov_individuals_vs_groups, cov_voice_heard. Dropped: ResponseId (Qualtrics id; re-keyed), village, household (field-team codes), Area,
##livelihood, other columns, the empty vignette-wide columns. No weights.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- fread(file.path(raw, "herb.csv"), na.strings = c("", "NA")); cc <- fread(file.path(raw, "carn.csv"), na.strings = c("", "NA"))
stopifnot(nrow(h) == 3699, nrow(cc) == 3694, uniqueN(h$ResponseId) == 3699, uniqueN(cc$ResponseId) == 3694)
ids <- sort(union(h$ResponseId, cc$ResponseId)); idmap <- setNames(seq_along(ids), ids)
sc <- c("Very unacceptable", "Unacceptable", "Somewhat unacceptable", "Neither acceptable nor unacceptable", "Somewhat acceptable", "Acceptable", "Very acceptable")
cov <- function(d) d[, .(cov_country = Country, cov_location = New_location, cov_gender = c(Female = "female", Male = "male")[gender],
                          cov_age_group = age.1, cov_education = formal.education, cov_relative_wealth = relative.wealth,
                          cov_people_vs_animals = people.animals, cov_individuals_vs_groups = individuals.groups, cov_voice_heard = voice.heard)]
stopifnot(all(h$Acceptability %in% sc), all(cc$Acceptability %in% sc))
oh <- cbind(h[, .(id = unname(idmap[ResponseId]), task = 1L, profile = 1L, rating = match(Acceptability, sc),
                  attr_species = species, attr_meat_use = meat.use, attr_revenue_use = revenue)], cov(h))
stopifnot(h[, all(paste(species, meat.use, revenue, sep = ".") == Scenario | paste(species, meat.use, revenue, sep = ".") == sub("develpment", "development", Scenario))])
sp <- tstrsplit(cc$species, ".", fixed = TRUE)
stopifnot(all(sp[[1]] == cc$hunter.from), all(sp[[3]] == cc$revenue), all(sp[[2]] %in% c("lion", "leopard")))
oc <- cbind(cc[, .(id = unname(idmap[ResponseId]), task = 1L, profile = 1L, rating = match(Acceptability, sc))],
            data.table(attr_hunter = cc$hunter.from, attr_species = sp[[2]], attr_revenue_use = cc$revenue), cov(cc))
setorder(oh, id); setorder(oc, id)
fwrite(oh, file.path(out, "sibanda_2026_trophy_herbivores.csv")); fwrite(oc, file.path(out, "sibanda_2026_trophy_carnivores.csv"))
