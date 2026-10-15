##Delivery-facility discrete choice experiment (peri-urban Nairobi, Kenya) from
##Oluoch-Aridi, J., Adam, M. B., Wafula, F., & Kokwaro, G. (2020). Eliciting women's preferences for place of
##child birth at a peri-urban setting in Nairobi, Kenya: A discrete choice experiment. PLOS ONE, 15(12), e0242149.
##https://doi.org/10.1371/journal.pone.0242149
##Data: figshare doi:10.6084/m9.figshare.11933568 (v1), CC BY 4.0 (figshare API). File read:
##"Appendix 10 Nairobi combined DCE and Baseline Joluoch Aridi PLOS ONE _2020.xlsx" (one sheet, long DCE rows
##joined to household-survey columns; only the DCE columns, age and schooling were used).
##Usage: Rscript oluocharidi_2020_nairobi.R <dir holding the xlsx, any name ending .xlsx> <output dir>
##
##421 women aged 18-49 who had delivered in the previous five years, recruited from a household survey in a
##peri-urban area of Nairobi (Dandora; ODK, enumerator-administered; 2018 fielding dates in the file, dropped).
##Each choice set: health facility A, health facility B and an opt-out "none of the two facilities", explained as
##home delivery (paper, Methods). Option 3 has no attributes (all dummies 0, cost 0): opt_out = yes; its rows are
##dropped and choice is 0 on both profiles when it was chosen (3.7% of tasks). Outcome: choice among A/B/none
##(wording of the question is the paper's scenario: women imagine they are expecting a baby and choose between
##facilities A and B for delivery, or none; exact on-screen wording not in the paper or deposit).
##D-efficient design (JMP), 16 choice sets in two blocks of 8 ("blocking using ODK"); the paper says each woman
##answered eight questions in one block, but the deposit holds all 16 sets (block 1 = sets 1-8, block 2 = sets 9-16)
##for every one of the 421 women: kept as stored (trial_block). task = the source's choice_set 1-16 (assumed to be
##the order shown); profile = alt 1/2. Restrictions: none documented; level weights: D-efficient design, not stated.
##Attributes (source dummy pairs -> level text of the paper's Table 1; the survey's on-screen wording is not
##available, so the text is the paper's table wording):
##  attr_quality: Good / Bad quality of clinical services
##  attr_cleanliness: Clean / Dirty health facility
##  attr_attitude: Kind and supportive / Unkind and unsupportive healthcare worker
##  attr_equipment: Medical equipment and supplies available / not available
##  attr_distance: Health facility is close to residence / far from residence
##  attr_cost: Ksh3000 / Ksh5000 / Ksh8000 (paper: costs in Ksh, 1 USD = 100 Ksh)
##Attribute order fixed (not stated otherwise; no position column).
##Covariates kept: cov_age (years, as recorded), cov_schooling_code (codes 1-4 have no codebook in the deposit).
##Respondent key respondent_id re-keyed to integers 1..421.
##Dropped: PII/device columns (deviceid IMEI-like device id, subscriberid, simid, devicephonenum, submission and
##start/end times, today), all other household-survey and pregnancy columns, the source dummy columns.
##N vs paper: 421 here vs 411 women and "20,080 choice tasks" in the paper (here 6,736 tasks, 20,208 option rows).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fn <- list.files(raw, pattern = "[.]xlsx$", full.names = TRUE)[1]
x <- as.data.table(read_excel(fn, sheet = 1, guess_max = 1e5))
need <- c("respondent_id","choice_set","alt","block","choice","Qualityofservicesatfacilitybad","Qualityofservicesatfacilitygood",
  "cleanlinessclean","cleanlinessdirty","attitudekindsupportive","attitudeunkindnotsupportive","medicalequipmentdrugsavailable",
  "medicalequipmentdrugsnotequiped","DistanceShort","DistanceLong","cost","age","schooling")
x <- x[, ..need]
stopifnot(nrow(x) == 20208, uniqueN(x$respondent_id) == 421, x[, .N, respondent_id][, all(N == 48)])
stopifnot(x[, sum(choice), .(respondent_id, choice_set)][, all(V1 == 1)])
stopifnot(x[alt == 3, all(cost == 0)], x[alt < 3, all(cost > 0)])
x[, id := match(respondent_id, sort(unique(respondent_id)))]
pick <- function(a, b, la, lb) ifelse(a == 1 & b == 0, la, ifelse(b == 1 & a == 0, lb, NA_character_))
p <- x[alt < 3]
d <- p[, .(id, task = as.integer(choice_set), profile = as.integer(alt), choice = as.integer(choice),
  attr_quality = pick(Qualityofservicesatfacilitygood, Qualityofservicesatfacilitybad, "Good quality of clinical services", "Bad quality of clinical services"),
  attr_cleanliness = pick(cleanlinessclean, cleanlinessdirty, "Clean health facility", "Dirty health facility"),
  attr_attitude = pick(attitudekindsupportive, attitudeunkindnotsupportive, "Kind and supportive healthcare worker", "Unkind and unsupportive healthcare worker"),
  attr_equipment = pick(medicalequipmentdrugsavailable, medicalequipmentdrugsnotequiped, "Medical equipment and supplies available", "Medical equipment and supplies not available"),
  attr_distance = pick(DistanceShort, DistanceLong, "Health facility is close to residence", "Health facility is far from residence"),
  attr_cost = paste0("Ksh", as.integer(cost)),
  cov_age = ifelse(age >= 15 & age <= 60, as.integer(age), NA_integer_), cov_schooling_code = as.integer(schooling),
  trial_block = as.integer(block))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), d[, .N, .(id, task)][, all(N == 2)],
  d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, uniqueN(cov_age), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "oluocharidi_2020_nairobi.csv"))
