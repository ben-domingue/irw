##Public bus service improvements in Hanoi, face-to-face discrete choice experiment, from the Mendeley Data
##deposit "Bus_DCE_DIB_Data" by Anh Bui Duc (published 2026; no article found, no article DOI).
##Deposit: doi:10.17632/wrxc9jxc2g (version 1), CC BY 4.0. Files read: Bus_DCE_DIB_Encoded_Data.xlsx (sheet
##"Data (Sample)"), Bus_DCE_DIB_Codebook.pdf and Bus_DCE_DIB_Survey.pdf (the 20 choice-card images, read
##visually for the displayed level wording).
##Usage: Rscript buiduc_2026.R <dir holding the xlsx> <output dir>
##
##Sample: 366 bus users/residents of Hanoi, Vietnam, interviewed face to face; each completes one of two blocks
##of 10 cards (blockid 1: cards 3, 7, 8, 9, 10, 12, 14, 17, 18, 20; block 2: cards 1, 2, 4, 5, 6, 11, 13, 15, 16,
##19), 2 alternatives per card ("Bus service A", "Bus service B"), forced choice, no opt-out (codebook; exactly
##one chosen per card). 6 attributes: travel time to the bus stop, bus schedule punctuality, operation
##experience, bus service application, reduction in air pollutant emissions (vs diesel buses), ticket price.
##Level text is the wording printed on the choice cards (survey PDF; card n of the data = "Form n"):
##time Under 3' / 3' - 10' / Over 10'; punctuality Under 75% accuracy / 75% - 90% accuracy / Over 90% accuracy;
##operation Runs safely and smoothly / Runs quite smoothly, occasional shaking / Reckless driving, shaking,
##sudden braking; app Easy to use / Difficult to use; emissions Undecrease / 30% reduction / 100% reduction;
##ticket price Unchange / 10% increase / 20% increase / 40% increase / 100% increase (the cards' own spelling
##"Undecrease" and "Unchange" is kept). The data hold one-hot dummies (time_long etc.); the mapping to these
##texts is the codebook's level meanings, and cards 1, 2 and 4 were checked against the data level for level.
##Respondent id: the file's censusno. Two rows carry a wrong censusno (row 4460 labelled 224 but belongs to
##respondent 223, row 6441 labelled 322 but belongs to 323): the file is exactly 20 rows per respondent in
##order, and the stray rows carry the covariates of the neighbouring respondent, so id = (row - 1) div 20 + 1
##(verified: covariates and block constant within each id). Task = card order within respondent as stored
##(ascending card id; the presentation order is not documented: task_source inferred); profile = alternative
##(1 = A, 2 = B, recorded). trial_card_id = the card number.
##Covariates (codebook coding, text from the codebook): gender (1 = male, 0 = female), age, education (6
##levels), monthly income band in VND (5 bands), marital status, bus use frequency, interest in environmental
##protection, interest in reducing emissions, agreement that buses protect the environment (statement A9),
##willingness to pay a higher fee (tax_agree, A10, 0/1). No survey weight. No identifying columns (the survey
##PDF contains the researchers' contact details, not copied).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_excel(file.path(raw, "Bus_DCE_DIB_Encoded_Data.xlsx"), sheet = "Data (Sample)"))
stopifnot(nrow(d) == 366 * 20)
d[, id := (.I - 1L) %/% 20L + 1L]
stopifnot(d[, uniqueN(blockid), id][, all(V1 == 1)], d[, uniqueN(paste(gender, age, edu, income, marriage, frequency)), id][, all(V1 == 1)],
          d[id != censusno, .N] == 2, d[id != censusno, id] %in% c(223, 323))
d[, task := as.integer(factor(cardid, levels = sort(unique(cardid)))), by = id]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(task), id][, all(V1 == 10)])
oh <- function(cols, labs) { m <- as.matrix(d[, ..cols]); stopifnot(all(rowSums(m) == 1)); labs[max.col(m, ties.method = "first")] }
pl <- c("0" = "Unchange", "10" = "10% increase", "20" = "20% increase", "40" = "40% increase", "100" = "100% increase")
o <- d[, .(id, task, profile = as.integer(alternative), choice = as.integer(choice), trial_card_id = as.integer(cardid), trial_block = as.integer(blockid))]
o[, attr_travel_time_to_stop := oh(c("time_short", "time_ave", "time_long"), c("Under 3'", "3' - 10'", "Over 10'"))]
o[, attr_schedule_punctuality := oh(c("unaccurate", "accurate_ave", "accurate"), c("Under 75% accuracy", "75% - 90% accuracy", "Over 90% accuracy"))]
o[, attr_operation_experience := oh(c("unsafe", "safe_ave", "safe"), c("Reckless driving, shaking, sudden braking", "Runs quite smoothly, occasional shaking", "Runs safely and smoothly"))]
o[, attr_service_app := oh(c("difficult", "easy"), c("Difficult to use", "Easy to use"))]
o[, attr_emission_reduction := oh(c("undecrease", "decrease_30", "decrease_100"), c("Undecrease", "30% reduction", "100% reduction"))]
stopifnot(all(as.character(d$price) %in% names(pl)))
o[, attr_ticket_price := unname(pl[as.character(d$price)])]
tx <- function(x, labs) unname(labs[as.character(x)])
o[, cov_gender := ifelse(d$gender == 1, "male", "female")]
o[, cov_age := as.integer(d$age)]
o[, cov_education := tx(d$edu, c("1" = "Lower secondary", "2" = "Upper secondary", "3" = "Vocational/Intermediate", "4" = "College", "5" = "University", "6" = "Postgraduate"))]
o[, cov_income_band_vnd_month := tx(d$income, c("1" = "<5M", "2" = "5-<8M", "3" = "8-<15M", "4" = "15-<30M", "5" = ">30M"))]
o[, cov_marital_status := tx(d$marriage, c("0" = "Single", "1" = "Married but no children", "2" = "Married with small children", "3" = "Other"))]
o[, cov_bus_use_frequency := tx(d$frequency, c("1" = "When there is no other option", "2" = "Occasionally (under 4 times/month)", "3" = "Frequently (2 to 3 times/week)", "4" = "Very frequently (over 3 times/week)"))]
lik <- c("1" = "Not interested at all", "2" = "Not interested", "3" = "Interested", "4" = "Very interested")
o[, cov_interest_environment := tx(d$envi_con, lik)]
o[, cov_interest_reduce_emissions := tx(d$emmis_con, lik)]
o[, cov_agree_bus_protects_environment := tx(d$agree, c("1" = "Strongly disagree", "2" = "Disagree", "3" = "Agree", "4" = "Strongly agree"))]
o[, cov_willing_pay_higher_fee := as.integer(d$tax_agree)]
stopifnot(!anyNA(o$attr_ticket_price), !anyNA(o$cov_education), !anyNA(o$cov_income_band_vnd_month))
## card 1 = Form 01: A under 3', under 75%, quite smoothly, difficult, 30% reduction, unchanged; B 3'-10', over 90%, safely, easy, 100%, 40% increase
c1 <- o[trial_card_id == 1 & id == 1]
stopifnot(c1[profile == 1, paste(attr_travel_time_to_stop, attr_schedule_punctuality, attr_operation_experience, attr_service_app, attr_emission_reduction, attr_ticket_price)] ==
            "Under 3' Under 75% accuracy Runs quite smoothly, occasional shaking Difficult to use 30% reduction Unchange",
          c1[profile == 2, paste(attr_travel_time_to_stop, attr_schedule_punctuality, attr_operation_experience, attr_service_app, attr_emission_reduction, attr_ticket_price)] ==
            "3' - 10' Over 90% accuracy Runs safely and smoothly Easy to use 100% reduction 40% increase")
setorder(o, id, task, profile)
fwrite(o, file.path(out, "buiduc_2026_hanoi_bus.csv"))
