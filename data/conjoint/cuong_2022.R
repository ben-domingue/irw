##Rice certification-label choice experiment (Vietnam) from
##Cuong, O. Q., Connor, M., Demont, M., Sander, B. O., & Nelson, K. (2022). How do rice consumers
##trade off sustainability and health labels? Evidence from Vietnam. Frontiers in Sustainable Food
##Systems, 6, 1010161.
##https://doi.org/10.3389/fsufs.2022.1010161 (CC BY; read: design section, Tables 1-4)
##Replication data: Harvard Dataverse doi:10.7910/DVN/ORLQQ7, CC0 1.0, no restricted files.
##File read: Data-DIB.tab (original csv): one row per respondent x choice set x alternative; ID,
##Block (0-3), Group (running choice-set counter over the file), Alti (1 = alternative A, 2 = B,
##3 = status quo), Choice, the four labels effects-coded (+1 certification, -1 none), Price (VND/kg),
##Gender, Education, Age, Household_income.
##Usage: Rscript cuong_2022.R <raw dir> <output dir>
##
##410 supermarket shoppers (main food purchasers who eat rice) in Can Tho city, September 2020,
##interviewed by enumerators at supermarket entrances. Fixed blocked design: a 16-profile orthogonal
##fractional factorial (alternative A) plus a shifted alternative B, split into 4 blocks of 4 choice
##cards (checked: each block x card x alternative has one fixed profile). Each card showed
##Alternative A, Alternative B and the status quo, and ended "I prefer:" (article Table 2). The
##status quo (a premium long-grain fragrant rice without certification, shown as "No certification
##VND 20,000/kg") has displayed attributes, so it is profile 3, not an opt-out; 6.2% of choices.
##Attribute text as in the article's Table 2 example card (English; the survey language is not
##stated): label attributes "Certification" / "None" for A and B, "No certification" for the
##status quo; price "VND 22,000/kg" .. "VND 32,000/kg" (A, B), "VND 20,000/kg" (status quo).
##Certified alternatives were also shown with a label logo (article Fig. 1, 2).
##Task = position of the card within the respondent's block, from the order of the Group counter
##(INFERRED: the display order of the four cards is not documented). Profile = Alti (recorded).
##Covariates: cov_gender_code (Gender 0/1), cov_education_code (1-6), cov_age (years),
##cov_household_income_mvnd (monthly household income, million VND, as recorded). No codebook maps
##the codes; the article's Table 4 counts match Gender 0 = female (354), 1 = male (56) and Education
##1-6 = no school, primary, secondary, high school, bachelor's, post-graduate (3/12/61/142/180/12),
##but codes are kept as codes. trial_block = Block (0-3).
##N = 410 respondents, 1,640 choice sets, as in the article. Spot check: share choosing the status
##quo 6.2% (article: 5-8% across blocks).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Data-DIB.csv"))
stopifnot(uniqueN(s$ID) == 410, s[, .N, ID][, all(N == 12)], s[, sum(Choice), Group][, all(V1 == 1)],
          s[, uniqueN(ID), Group][, all(V1 == 1)], s[Alti == 3, all(Low_emission == -1 & Eco_friendly == -1 &
            Ethically_produced == -1 & Low_glycemic == -1 & Price == 20000)])
setorder(s, ID, Group, Alti)
s[, task := match(Group, unique(Group)), ID]
stopifnot(s[, max(task), ID][, all(V1 == 4)],
          s[, uniqueN(paste(Low_emission, Eco_friendly, Ethically_produced, Low_glycemic, Price)), .(Block, task, Alti)][, all(V1 == 1)])
lab <- function(x, alt) fifelse(alt == 3L, "No certification", fifelse(x == 1L, "Certification", "None"))
stopifnot(all(unlist(s[, .(Low_emission, Eco_friendly, Ethically_produced, Low_glycemic)]) %in% c(-1, 1)))
d <- s[, .(id = ID, task, profile = Alti, choice = Choice,
           attr_low_emission = lab(Low_emission, Alti), attr_eco_friendly = lab(Eco_friendly, Alti),
           attr_ethically_produced = lab(Ethically_produced, Alti), attr_low_glycemic_index = lab(Low_glycemic, Alti),
           attr_price = paste0("VND ", formatC(Price, format = "d", big.mark = ","), "/kg"),
           trial_block = Block, cov_gender_code = Gender, cov_education_code = Education, cov_age = Age,
           cov_household_income_mvnd = Household_income)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "cuong_2022_rice_labels.csv"))
