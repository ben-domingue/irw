##Household energy-use vignette (US) from
##Horne, C., & Kennedy, E. H. (2021). Understanding the rebound: normative evaluations of energy use in the United States.
##Environmental Sociology, 8(1), 64-72. https://doi.org/10.1080/23251042.2021.1958545
##Replication data: Harvard Dataverse doi:10.7910/DVN/LX3SAM, CC0 1.0. Files read: Rebound Stata Dataset.tab
##(Stata original, haven), Rebound Study Materials.docx (the Qualtrics survey export, read as text).
##Usage: Rscript horne_2021_energy_rebound.R <dir holding d.dta> <output dir>   (raw file saved as d.dta)
##
##653 US Prolific respondents (2021) in the data; 640 answered a vignette block. Each respondent read ONE short
##vignette of a two-child family and answered 16 rating questions about it (0-10 slider-style buttons stored 1-11:
##the survey labels the buttons 0 ... 10, the data store 1 ... 11; stored raw, 1 = "0 Not at all"/"0 None").
##Attributes (2 x 2, one vignette per respondent): electricity source (utility company / solar panels) and household
##use (low: small home, no AC, short showers, clothesline, few appliances, much less electricity than neighbours /
##high: large home, lots of AC, long showers, frequent washer and dryer, many appliances, much more electricity).
##Attribute text: the vignette sentences from the survey export. Eight Qualtrics blocks = 4 cells x 2 question orders:
##  "Comp": knowledge items (knowledgeable, common sense, problem solving, good with money) before the moral items
##  (caring, ethical, unselfish); "Moral": moral items first. Stored as trial_question_order.
##Block "Solar HighUse_Moral" (Q11) is labelled high-use in Qualtrics but its vignette text in the export reads
##SOLAR + LOW use, and all 74 of its respondents with the manipulation check answered "much less than others", so
##the displayed text is used (solar, low); the solar x high x moral-order cell therefore does not exist.
##Question-to-column mapping per block follows the export order (Q?.2-4 approval items; comp blocks: 6-9 knowledge,
##11-13 moral, 15-17 environment, 19-21 impact; moral blocks: 6-8 moral, 10-13 knowledge, 15-17, 19-21).
##Outcomes (all ratings, same vignette; "this family"): approve, pleased with them moving next door, interested in
##being friends; knowledgeable, common sense, good at problem solving, good with money; caring, ethical, unselfish;
##concerned about environmental issues, active supporter of environmental protection, environment a high priority;
##actions helping the environment, energy conserving, harm to the environment caused.
##No respondent id and no choice: id = row order of the 640 respondents with an outcome; 13 respondents with no
##block answered are omitted. No opt-out.
##PII FOUND: Prolific IDs (Q3_1, free-typed; dropped), state of residence (dropped), race (dropped).
##Covariates: cov_gender (survey: 0 Male, 1 Female, 2 Other), cov_age (typed years, plausible 18-100 else NA),
##cov_education (survey answer text), cov_income (survey answer text), cov_ideology_code (1 extremely liberal ... 7
##extremely conservative; only the end points are labelled in the survey).
##Dropped: manipulation-check items, vote-intention item, race, state.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "d.dta")))
x <- x[, lapply(.SD, function(c) if (is.labelled(c)) as.numeric(c) else c)]
blocks <- 4:11
comp <- c(4, 6, 8, 10)
src_solar <- c(4, 5, 6, 7) # utility blocks
use_low <- c(4, 5, 8, 9, 11)
cols <- function(b, k) x[[paste0("Q", b, "_", k)]]
blk <- rep(NA_integer_, nrow(x))
for (b in blocks) blk[!is.na(cols(b, 2))] <- b
stopifnot(all(!is.na(blk) | is.na(x$Q4_2)))
keep <- which(!is.na(blk))
stopifnot(length(keep) == 640)
mapk <- function(b) if (b %in% comp)
  c(approve = 2, pleased_neighbor = 3, friends = 4, knowledgeable = 6, common_sense = 7, problem_solving = 8, money = 9,
    caring = 11, ethical = 12, unselfish = 13, env_concern = 15, env_supporter = 16, env_priority = 17,
    helping_env = 19, conserving = 20, harm_env = 21) else
  c(approve = 2, pleased_neighbor = 3, friends = 4, caring = 6, ethical = 7, unselfish = 8, knowledgeable = 10,
    common_sense = 11, problem_solving = 12, money = 13, env_concern = 15, env_supporter = 16, env_priority = 17,
    helping_env = 19, conserving = 20, harm_env = 21)
R <- rbindlist(lapply(keep, function(i) {
  b <- blk[i]; m <- mapk(b)
  as.list(setNames(vapply(m, function(k) as.numeric(cols(b, k)[i]), 0), names(m)))
}), use.names = TRUE)
src <- fifelse(blk[keep] %in% src_solar, "Gets its electricity from its utility company", "Gets most of its electricity from solar panels on its roof")
use <- fifelse(blk[keep] %in% use_low,
  "Lives in a small home, has no air conditioning, takes short showers, dries clothes on a clothesline and has few electric appliances; uses much less electricity than other households in the neighborhood",
  "Lives in a large home, uses air conditioning a lot in the summer, likes long showers, uses the washer and dryer frequently and has lots of electric appliances; uses much more electricity than other people in the neighborhood")
inc <- c(`11` = "Less than $10,000", `12` = "$10,000 - $19,999", `13` = "$20,000 - $29,999", `14` = "$30,000 - $39,999", `15` = "$40,000 - $49,999",
         `16` = "$50,000 - $59,999", `17` = "$60,000 - $69,999", `18` = "$70,000 - $79,999", `19` = "$80,000 - $89,999", `20` = "$90,000 - $99,999",
         `21` = "$100,000 - $149,999", `22` = "More than $150,000")
edu <- c("Less than high school", "High school graduate", "Some college", "2 year degree", "4 year degree", "Professional degree", "Doctorate")
age <- x$Q13_2[keep]; age[!(age >= 18 & age <= 100 & age == round(age))] <- NA
d <- data.table(id = seq_along(keep), task = 1L, profile = 1L, rating = R$approve,
  attr_electricity_source = src, attr_household_use = use)
for (n in setdiff(names(R), "approve")) d[[paste0("rating_", n)]] <- R[[n]]
d[, `:=`(cov_gender = c("male", "female", "other")[x$Q13_1[keep] + 1L], cov_age = as.integer(age),
         cov_education = edu[x$Q13_3[keep]], cov_income = inc[as.character(x$Q13_8[keep])],
         cov_ideology_code = as.integer(x$Q13_6[keep]),
         trial_question_order = fifelse(blk[keep] %in% comp, "knowledge items before moral items", "moral items before knowledge items"))]
stopifnot(d[, .N, .(attr_electricity_source, attr_household_use)][, .N] == 4)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "horne_2021_energy_rebound.csv"))
