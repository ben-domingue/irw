##Oregon Coast Coho salmon recovery choice experiment (US Pacific Northwest) from
##Lewis, D. J., Dundas, S. J., Kling, D. M., Lew, D. K., & Hacker, S. D. (2019). The non-market benefits of early and
##partial gains in managing threatened salmon. PLOS ONE, 14(8), e0220260. https://doi.org/10.1371/journal.pone.0220260
##Data: figshare doi:10.6084/m9.figshare.7869299 (OC_Coho_Data.zip), CC BY 4.0 (figshare API). Files read:
##Estimation.xlsx and, as text, Codebook.docx. Level text from the paper's Fig 2 (attribute-level table, an image read
##visually; the codebook calls it Table 1) : Usage: Rscript lewis_2019.R <dir holding Estimation.xlsx> <output dir>
##
##926 households (mail survey 2017 of residents of OR, WA, ID, CA; Oregon oversampled, cov_survey_weight = the
##codebook's Weight for stratified sampling). Each answered up to 3 choice questions (#12-14): status quo (always the
##same, $0) vs program A vs program B. The data store only A and B; the status quo has no stored levels (150,000 fish,
##no change, $0 per the paper, its ESA and fishing levels are not stored): it is an opt-out (opt_out = yes; Response 1
##= status quo, choice 0 on both profiles, 425 of 2,734 tasks). Profile = A (1) / B (2); task = question order 1-3.
##Attributes (codes -> Fig 2 text): ESA status 1 Threatened / 2 Endangered; returning fish in 50 years 2-5 -> 250,000 /
##325,000 / 375,000 / 525,000; rate of change 2 Slow / 3 Quick (shown with a graph; text only here); fishing regulations
##1 Open occasionally with 5 fish/year bag limit / 2 Open annually with 5 fish/year bag limit / 3 Open annually with 10
##fish/year bag limit; annual cost 2-9 -> $10 $20 $50 $75 $100 $150 $250 $350. Restrictions: the paper says a D0-optimal
##design with permissible combinations only (S1 Text Table A, not read): restrictions yes, see restrictions_note.
##Covariates: cov_gender (Male 1/0 -> male/female, codebook), cov_age (years; one deposit-wide column, 98 max kept),
##cov_state (StateAbbr), cov_household_income_usd, cov_survey_weight, cov_ever_fished (EverFished 0/1).
##Dropped: confidence/importance dummies, pdiff, college, race, ID (survey id), derived columns.
##Respondent key = RespondentID. N 926 respondents / 2,734 choices matches the paper's N = 2,734 (Table 1).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(list.files(raw, pattern = "Estimation[.]xlsx$", full.names = TRUE)[1]))
stopifnot(nrow(x) == 2734, uniqueN(x$RespondentID) == 926, x[, all(Response %in% 1:3)], x[, .N, .(RespondentID, Question)][, all(N == 1)])
setorder(x, RespondentID, Question); x[, task := seq_len(.N), RespondentID]
mk <- function(s) {
  esa <- c("Threatened", "Endangered"); pop <- c(NA, "250,000", "325,000", "375,000", "525,000")
  dyn <- c(NA, "Slow", "Quick"); fis <- c("Open occasionally with 5 fish/year bag limit", "Open annually with 5 fish/year bag limit", "Open annually with 10 fish/year bag limit")
  cost <- c(NA, "$10", "$20", "$50", "$75", "$100", "$150", "$250", "$350")
  p <- ifelse(s == "A", 1L, 2L)
  x[, .(id = RespondentID, task, profile = p, choice = as.integer(Response == p + 1L),
    attr_esa_status = esa[get(paste0("ESA_", s))], attr_returning_fish_50yr = pop[get(paste0("Pop_", s))],
    attr_rate_of_increase = dyn[get(paste0("Dynamics_", s))], attr_fishing_regulations = fis[get(paste0("Fishing_", s))],
    attr_annual_cost = cost[get(paste0("Cost_", s))],
    cov_gender = ifelse(Male == 1, "male", "female"), cov_age = ifelse(Age <= 100, as.integer(Age), NA_integer_), cov_state = State_ABBR,
    cov_household_income_usd = as.integer(Income), cov_survey_weight = Weight, cov_ever_fished = as.integer(EverFished))]
}
d <- rbind(mk("A"), mk("B"))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lewis_2019_coho_salmon.csv"))
