##Indonesian coffee consumers, online discrete choice experiment, from the Mendeley Data deposit "Data Online
##Questionnaire - Indonesian Coffee Consumers" by Andika Wicaksono Putro (published 2025-03; part of a Copenhagen
##PhD work package; no article found, no article DOI).
##Deposit: doi:10.17632/zpmsftxspb (version 1), CC BY 4.0. File read: "Data Online Questionnaire.xlsx", sheets
##"Filtered" (DCE responses with level text), "demog filtered" (demographics), "Combination from JMP" (design,
##used as a check), "Dummy Data Coding" and "Data change logger" (read for context).
##Usage: Rscript putro_2025.R <dir holding the xlsx> <output dir>
##
##Sample: ONLY 174 of the 1,161 respondents of the online questionnaire have DCE rows in the deposit. The 1,161
##"Final" sheet holds the attitude and lifestyle items and the k-means segment (Cluster) but no DCE responses,
##and the "Filtered" sheet is exactly the 174 respondents flagged in the extreme_filtered column of "Final"
##(the cluster "extremists": 47 Average and price insensitive, 51 Health and sustainability, 76 Less health and
##sustainability). So this table is a selected subset (selected on the attitude clustering, not on choices).
##Indonesian consumers who buy coffee, online panel (questionnaire in Indonesian per the deposit description; year not stated).
##Design: 36 choice sets of 3 coffee alternatives in 4 fixed blocks of 9 sets (survey_group 1-4 = sets 1-9,
##10-18, 19-27, 28-36; each respondent saw one block: trial_block); forced choice (exactly one chosen per set,
##no opt-out). The rows of "Filtered" reproduce the "Combination from JMP" design sheet row for row (all 1,566
##respondent-sets checked), the alternatives within a set being the design's three rows in order; the screen
##position of each alternative is not documented, so profile = row order in a set (profile_source inferred).
##Task = rank of the choice_set within the respondent's block (the order in which the sets were shown is not
##documented: task_source inferred).
##Attributes: price (20000, 25000, 30000, shown here as "Rp 20000" etc.: the deposit gives numbers only, the
##currency is inferred from the Rupiah income bands, so the displayed currency format is an inference),
##sustainability label (None / Fair Trade / Organic), roasting profile (the `quality` column: "Dark roasted
##Robusta coffee with familiar bitter taste" / "Light roasted Arabica coffee with fruity taste"), milk type (None /
##Cow milk / Plant-based milk), sugar choice (None / Palm sugar). Level text is the deposit's own text.
##Outcome: choice = `response` (1 = chosen alternative). The wording of the choice question is not in the deposit.
##Covariates from "demog filtered" (joined on the panelist code MIN####, which is dropped): age (years), gender
##(F/M), province of residence (text), level of urbanisation, education (text), household income band
##(text; the DCE sheet spells some bands "Less thanRp 2.500.000", these are normalised to the demographics
##sheet's "Less than Rp 2.500.000" form), coffee purchase frequency (text). The authors' cluster/segment, anthropometrics
##(height, weight, BMI) and panelist codes are dropped. No survey weight.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Data Online Questionnaire.xlsx")
d <- as.data.table(read_excel(f, sheet = "Filtered"))
dm <- as.data.table(read_excel(f, sheet = "demog filtered"))
j <- as.data.table(read_excel(f, sheet = "Combination from JMP")); setnames(j, make.names(names(j)))
stopifnot(nrow(d) == 174 * 27, d[, uniqueN(respondent)] == 174, d[, .N, .(respondent, choice_set)][, all(N == 3)],
          d[, sum(response), .(respondent, choice_set)][, all(V1 == 1)], d[, uniqueN(survey_group), respondent][, all(V1 == 1)])
## design check: row-for-row identical to the JMP design
d[, rr := seq_len(.N), .(respondent, choice_set)]; j[, rr := seq_len(.N), Choice]
ck <- merge(d, j, by.x = c("choice_set", "rr"), by.y = c("Choice", "rr"))
stopifnot(nrow(ck) == nrow(d), all(ck$price == ck$Price), all(ck$sustainability_label == ck$Sustainability.label),
          all(ck$quality == ck$Roasting.profile), all(ck$milk == ck$Milk.type), all(ck$sugar == ck$Sugar.choice))
d[, id := as.integer(factor(code, levels = sort(unique(code))))]
d[, task := as.integer(factor(choice_set)), by = id]
stopifnot(d[, uniqueN(task), id][, all(V1 == 9)])
inc <- function(x) gsub("Less thanRp", "Less than Rp", gsub("More thanRp", "More than Rp", x, fixed = TRUE), fixed = TRUE)
m <- dm[match(d$code, dm$MIN)]
stopifnot(!anyNA(m$age), identical(m$MIN, d$code))
o <- d[, .(id, task, profile = rr, choice = as.integer(response),
           attr_price = paste("Rp", as.integer(price)), attr_sustainability_label = sustainability_label,
           attr_roasting_profile = quality, attr_milk_type = milk, attr_sugar_choice = sugar, trial_block = as.integer(survey_group))]
o[, `:=`(cov_age = as.integer(m$age), cov_gender = ifelse(m$gender == "F", "female", ifelse(m$gender == "M", "male", NA)),
         cov_province = m$location, cov_urbanisation = m$urbanization, cov_education = m$edu,
         cov_income_band = inc(m$income), cov_coffee_frequency = m$freq)]
stopifnot(!anyNA(o$attr_milk_type), !anyNA(o$cov_gender))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "putro_2025_indonesian_coffee.csv"))
