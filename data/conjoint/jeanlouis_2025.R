##Plankton / marine-biodiversity discrete choice experiment from Deliberative Monetary Valuation
##workshops in five European countries. Data:
##Jean-Louis, G. (2025). Europe-wide public preferences for plankton-based ecosystem services and
##marine biodiversity from a series of Deliberative Monetary Valuation workshops [Data set].
##Zenodo. https://doi.org/10.5281/zenodo.17710200 (CC BY 4.0; Horizon Europe project BIOcean5D).
##No article is linked. Files read (from "Repository Data1.2.zip"): DMV data_EN.csv (';'-separated,
##Latin-1; the English-translated version of DMV data.csv), Codebook.pdf, "Supplementary material/
##WS guideline and questionnaires/Screening questions and workshop questionnaire_EN.docx" (the 16
##choice cards, text parsed from the docx table into `cards` below), the Basque-workshop
##questionnaire (to confirm its language: Spanish), and "Experimental design/Ngene code and designs
##tested.pdf" (final Bayesian D-efficient design, 16 choice situations).
##Usage: Rscript jeanlouis_2025.R <dir holding "DMV data_EN.csv"> <output dir>
##
##15 workshops, Oct 2023 - Feb 2024: Poznan, Sopot (PL), Padova, Chioggia (IT), Vitoria-Gasteiz,
##Bilbao (ES, Basque Country; Spanish questionnaire), Bremerhaven, Hannover (DE), Rennes, Brest (FR);
##176 participants. Every participant answered the same 16 cards (CS1-CS16; fixed design, one
##block), each "[Please select your preferred scenario by placing a cross in the bottom line.]"
##among Scenario 1, Scenario 2 and a "Business as usual scenario". The business-as-usual column
##shows attribute levels (+ 0 %, Yes, Less stable, Minimally protected, 0 EUR), so it is profile 3,
##not an opt-out. Attributes (English questionnaire text):
##  attr_climate_regulation "Climate regulation": + 0 % / + 50 % / + 100 % / + 150 % (carbon storage potential)
##  attr_blooms  "Higher probability of algal blooms and jellyfish blooms": Yes / No
##  attr_plankton "Plankton composition": More stable / Less stable
##  attr_mpa_protection "Protection status of Marine Protected Area": Fully / Highly / Minimally protected
##  attr_cost "Costs (per year and adult citizen)": 0 / 10 / 20 / 40 / 80 / 120 / 180 EUR, written "180 €"
##The design's 3-level plankton attribute is shown as two rows: level 1 = More stable + No blooms,
##2 = Less stable + No, 3 = Less stable + Yes (More stable + Yes never occurs). Checked: carbon, MPA
##and cost on all 32 designed alternatives of the parsed cards equal the Ngene choice situations 1-16
##in order, so CS<k> = card k. The attribute row order differs between cards (the same for everyone):
##attrpos_ = row 1-5 on that card. One table pooling the five countries (the deposit pools them; the
##cards are translations of one design); levels stored in English.
##choice: CS<k> = 1, 2 or 3 = Scenario 1, Scenario 2, business as usual (the codebook does not list
##the CS codes; values 1-3 match the three columns; cost lowers the choice of a scenario, as
##expected). NA answers are omitted. Task = card number (questionnaire order).
##Covariates: cov_country, cov_location (workshop city), cov_workshop (WS_ID), cov_coastal (Coastal 0/1
##as recorded), cov_gender (f/m -> female/male), cov_birth_year (Year of birth), cov_education (ISCED
##code -> codebook label), cov_choice_certainty (Q14, 1 Very uncertain ... 6 Very certain).
##Count: 176 participants in the file, 172 with at least one answered card (8,220 rows, 2,740
##tasks); no article to compare with. Spot check: Scenario 1/2 chosen in 66% of alternatives costing
##10 EUR vs 20% at 180 EUR; business as usual chosen in 14% of tasks.
##PII FOUND and dropped: Postcode (respondents' postcodes). Also dropped: seat number, workshop date,
##income, free-text answers (Q8-Q10, Q18), attitude batteries.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cards <- fread(sep = "|", encoding = "UTF-8", text = "
set|pos|attr|s1|s2|bau
1|1|climate_regulation|+ 150 %|+ 50 %|+ 0 %
1|2|blooms|No|Yes|Yes
1|3|plankton|Less stable|Less stable|Less stable
1|4|mpa_protection|Minimally protected|Highly protected|Minimally protected
1|5|cost|180 €|10 €|0 €
2|1|mpa_protection|Minimally protected|Highly protected|Minimally protected
2|2|climate_regulation|+ 150 %|+ 0 %|+ 0 %
2|3|blooms|Yes|No|Yes
2|4|plankton|Less stable|Less stable|Less stable
2|5|cost|80 €|10 €|0 €
3|1|mpa_protection|Fully protected|Minimally protected|Minimally protected
3|2|plankton|More stable|More stable|Less stable
3|3|blooms|No|No|Yes
3|4|climate_regulation|+ 0 %|+ 150 %|+ 0 %
3|5|cost|20 €|80 €|0 €
4|1|climate_regulation|+ 0 %|+ 50 %|+ 0 %
4|2|mpa_protection|Fully protected|Minimally protected|Minimally protected
4|3|plankton|More stable|Less stable|Less stable
4|4|blooms|No|Yes|Yes
4|5|cost|120 €|20 €|0 €
5|1|blooms|No|No|Yes
5|2|mpa_protection|Minimally protected|Fully protected|Minimally protected
5|3|climate_regulation|+ 0 %|+ 100 %|+ 0 %
5|4|plankton|More stable|Less stable|Less stable
5|5|cost|20 €|80 €|0 €
6|1|mpa_protection|Fully protected|Highly protected|Minimally protected
6|2|climate_regulation|+ 50 %|+ 50 %|+ 0 %
6|3|plankton|Less stable|More stable|Less stable
6|4|blooms|No|No|Yes
6|5|cost|80 €|20 €|0 €
7|1|plankton|Less stable|More stable|Less stable
7|2|blooms|Yes|No|Yes
7|3|climate_regulation|+ 100 %|+ 100 %|+ 0 %
7|4|mpa_protection|Highly protected|Fully protected|Minimally protected
7|5|cost|10 €|120 €|0 €
8|1|mpa_protection|Minimally protected|Fully protected|Minimally protected
8|2|climate_regulation|+ 100 %|+ 100 %|+ 0 %
8|3|plankton|More stable|Less stable|Less stable
8|4|blooms|No|No|Yes
8|5|cost|40 €|40 €|0 €
9|1|mpa_protection|Fully protected|Highly protected|Minimally protected
9|2|plankton|Less stable|More stable|Less stable
9|3|blooms|Yes|No|Yes
9|4|climate_regulation|+ 50 %|+ 0 %|+ 0 %
9|5|cost|20 €|40 €|0 €
10|1|plankton|Less stable|More stable|Less stable
10|2|mpa_protection|Minimally protected|Fully protected|Minimally protected
10|3|climate_regulation|+ 100 %|+ 100 %|+ 0 %
10|4|blooms|No|No|Yes
10|5|cost|10 €|180 €|0 €
11|1|blooms|No|Yes|Yes
11|2|climate_regulation|+ 50 %|+ 150 %|+ 0 %
11|3|mpa_protection|Highly protected|Fully protected|Minimally protected
11|4|plankton|Less stable|Less stable|Less stable
11|5|cost|40 €|40 €|0 €
12|1|mpa_protection|Highly protected|Fully protected|Minimally protected
12|2|climate_regulation|+ 150 %|+ 50 %|+ 0 %
12|3|plankton|Less stable|Less stable|Less stable
12|4|blooms|No|Yes|Yes
12|5|cost|120 €|20 €|0 €
13|1|blooms|Yes|Yes|Yes
13|2|mpa_protection|Highly protected|Minimally protected|Minimally protected
13|3|climate_regulation|+ 50 %|+ 0 %|+ 0 %
13|4|plankton|Less stable|Less stable|Less stable
13|5|cost|180 €|120 €|0 €
14|1|climate_regulation|+ 0 %|+ 150 %|+ 0 %
14|2|blooms|No|No|Yes
14|3|mpa_protection|Fully protected|Highly protected|Minimally protected
14|4|plankton|More stable|More stable|Less stable
14|5|cost|10 €|180 €|0 €
15|1|climate_regulation|+ 150 %|+ 0 %|+ 0 %
15|2|mpa_protection|Highly protected|Minimally protected|Minimally protected
15|3|blooms|Yes|No|Yes
15|4|plankton|Less stable|Less stable|Less stable
15|5|cost|80 €|10 €|0 €
16|1|blooms|No|No|Yes
16|2|plankton|More stable|Less stable|Less stable
16|3|climate_regulation|+ 100 %|+ 150 %|+ 0 %
16|4|mpa_protection|Fully protected|Minimally protected|Minimally protected
16|5|cost|40 €|80 €|0 €")
stopifnot(nrow(cards) == 80, cards[, .N, set][, all(N == 5)], cards[, uniqueN(attr), set][, all(V1 == 5)])
prof <- rbind(cards[, .(set, pos, attr, profile = 1L, lev = s1)], cards[, .(set, pos, attr, profile = 2L, lev = s2)],
              cards[, .(set, pos, attr, profile = 3L, lev = bau)])
pw <- dcast(prof, set + profile ~ attr, value.var = "lev")
pp <- dcast(prof[profile == 1L], set ~ attr, value.var = "pos")
setnames(pw, setdiff(names(pw), c("set", "profile")), paste0("attr_", setdiff(names(pw), c("set", "profile"))))
setnames(pp, setdiff(names(pp), "set"), paste0("attrpos_", setdiff(names(pp), "set")))
pw <- merge(pw, pp, by = "set")
stopifnot(pw[profile == 2 & attr_plankton == "More stable", all(attr_blooms == "No")])
x <- fread(file.path(raw, "DMV data_EN.csv"), sep = ";", encoding = "Latin-1", na.strings = c("NA", ""))
stopifnot(!anyDuplicated(x$ID))
cs <- paste0("CS", 1:16)
long <- melt(x[, c("ID", cs), with = FALSE], id.vars = "ID", variable.name = "q", value.name = "ans", variable.factor = FALSE, na.rm = TRUE)
stopifnot(all(long$ans %in% 1:3))
long[, set := as.integer(sub("CS", "", q))]
d <- merge(long, pw, by = "set", allow.cartesian = TRUE)
d[, choice := as.integer(profile == ans)]
isced <- c("Primary education", "Lower secondary education", "Upper secondary education", "Post-secondary non-tertiary",
           "Short-cycle tertiary education", "Bachelor or equivalent", "Master or equivalent", "Doctoral or equivalent")
cv <- x[, .(ID, cov_country = Country, cov_location = Location, cov_workshop = as.integer(WS_ID), cov_coastal = as.integer(Coastal),
            cov_gender = fifelse(Gender == "f", "female", fifelse(Gender == "m", "male", NA_character_)),
            cov_birth_year = as.integer(`Year of birth`),
            cov_education = isced[suppressWarnings(as.integer(ISCED))], cov_choice_certainty = suppressWarnings(as.integer(Q14)))]
d <- merge(d, cv, by = "ID")
d[, id := match(ID, sort(unique(ID)))]
d <- d[, c("id", "set", "profile", "choice", grep("^attr", names(d), value = TRUE), grep("^cov_", names(d), value = TRUE)), with = FALSE]
setnames(d, "set", "task")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
cat("respondents:", uniqueN(d$id), " rows:", nrow(d), " tasks:", nrow(d) / 3, "\n")
fwrite(d, file.path(out, "jeanlouis_2025_plankton_dmv.csv"))
