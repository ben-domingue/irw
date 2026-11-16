##Support for a trade agreement with a hypothetical country described by binary cues (democracy, alliance, culture,
##wages/income, economy size, military size; Study 2: democracy, honouring trade commitments, fair legal treatment),
##one vignette per respondent, four samples, from
##Chen, F. R., Pevehouse, J. C. W., & Powers, R. M. (2023). Great expectations: The democratic advantage in trade
##attitudes. World Politics, 75(2). https://doi.org/10.1353/wp.2023.0010
##Data: Chen, F. R., Pevehouse, J. C. W., & Powers, R. M. (2023). Replication Data for: Great Expectations: The Democratic
##Advantage in Trade Attitudes. Harvard Dataverse. https://doi.org/10.7910/DVN/L7PPCQ (CC0 1.0; no terms, no restricted files).
##Files read (Stata originals): study1_elites.dta, study1_lucid.dta, study1_mturk.dta, study2_lucid.dta.
##Manuscript.r and med.do read as text only (never run). lucid_med_df/mturk_med_df/mediation_results/pew_formatted not used
##(analysis copies and aggregate data).
##Usage: Rscript chen_2023.R <dir holding the four .dta files> <output dir>
##
##Tables (one per sample: the authors estimate and plot each sample separately, and the elite and Study 2 attribute
##sets differ):
##  chen_2023_trade_democracy_elites  Study 1, US trade/development policy elites (212): democracy, ally, high_income,
##                                    small_econ, small_mil.
##  chen_2023_trade_democracy_lucid   Study 1, US public on Lucid (3,037): democracy, ally, sim_culture, high_income, small_econ.
##  chen_2023_trade_democracy_mturk   Study 1, US public on MTurk (764): same five attributes.
##  chen_2023_trade_democracy_study2  Study 2, US public on Lucid (1,659): democracy, honor_int, treat_fair.
##One profile per respondent: id = row number (the deposit has no respondent id), task = 1, profile = 1.
##
##CODED ATTRIBUTES (#3474). No questionnaire is deposited and the article is closed access, so no source gives the
##vignette wording. Every attribute is a 0/1 variable that the authors analyse as one binary treatment
##(Manuscript.r: lm(bin_support ~ democracy+sim_culture+high_income+small_econ+ally); names "Democracy", "Similar
##culture", "High wages", "Small economy", "Ally"; elites "High wages", "Small military"; Study 2 treat_fair*honor_int,
##"Fair Legal Treatment", "Honor Trade Commit."), so the codes stand one-to-one for two displayed levels. Kept as
##deposited in attr_<variable>_code; 1 = the named property (by the Stata variable labels and the authors' names); the
##text of either level is unknown. Elites: large_econ is exactly 1 - small_econ (checked), so it is the same
##attribute and is dropped.
##Outcome: rating = support_trade_cont (Stata label "Support trade (cont.)"), 1-6, stored raw. Direction from the
##deposit: the authors' binary "Support trade (binary)" (bin_support / bin_support_trade) is 100 (Study 2: 1) exactly
##when support_trade_cont is 4-6 and 0 when 1-3 (checked), so higher = more support. Question wording and anchors are
##not deposited (unknown). Respondents with no support_trade_cont are dropped.
##Dropped: bin_* and avg_* (derived), the 1-5 mechanism items (improve_us_economy, honor_commitments, ...: wording and
##direction not deposited), manipulation (derived), complete_case(s), hhi_collapsed (derived).
##Covariates as deposited (value labels as text, the source of each mapping): cov_age; cov_gender_code (0/1 = Female, Stata label
##"Female"; kept as is because no source says what 0 covers); cov_education (value labels); cov_region (labels);
##cov_income (Lucid hhi labels, text) / cov_income_code (MTurk income, unlabelled); cov_party_id7 (Lucid partyID labels,
##"Party ID (7pt D-R)") / cov_partyid_recode_code (MTurk, unlabelled 1-7); cov_ethnicity (labels; "Prefer not to
##answer" -> NA); cov_<x>_correct (manipulation-check items as deposited, 0/1, the authors' names); cov_thought_of_china;
##elites: cov_sample (development/trade), cov_rank (labels), cov_trade_practitioner. No exclusions applied
##(Manuscript.r fits complete cases via na.omit over covariates; reproduce with complete cases on the covariates).
##Counts vs the paper: not checked (closed access). Deposit rows: 212 / 3,037 / 764 / 1,659.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) as.data.table(read_dta(file.path(raw, f)))
lab <- function(x) gsub("\\textdollar", "$", as.character(as_factor(x, levels = "labels")), fixed = TRUE)  # Stata labels write $ as \textdollar
b01 <- function(x) { stopifnot(all(x %in% c(0, 1))); as.integer(x) }
mk <- function(d, at, binv, binhi, covs, tab) {
  stopifnot(all(d[!is.na(support_trade_cont) & !is.na(get(binv)), (support_trade_cont >= 4) == (get(binv) == binhi)]))
  d[, id := .I]; d <- d[!is.na(support_trade_cont)]
  o <- d[, .(id, task = 1L, profile = 1L, rating = as.integer(support_trade_cont))]
  for (k in at) set(o, j = paste0("attr_", k, "_code"), value = b01(d[[k]]))
  for (k in names(covs)) set(o, j = k, value = covs[[k]](d))
  setorder(o, id, task, profile); fwrite(o, file.path(out, paste0(tab, ".csv")))
  cat(tab, nrow(o), "of", nrow(d) , "\n")
}
pub <- list(cov_age = function(d) as.integer(d$age), cov_gender_code = function(d) as.integer(d$Female),
            cov_education = function(d) lab(d$education), cov_region = function(d) lab(d$region),
            cov_income = function(d) lab(d$hhi), cov_party_id7 = function(d) lab(d$partyID),
            cov_ethnicity = function(d) { v <- lab(d$recode_ethnicity); v })
chk <- function(nm) setNames(lapply(nm, function(k) function(d) as.integer(d[[k]])), paste0("cov_", nm))
e <- rd("study1_elites.dta"); stopifnot(nrow(e) == 212L, all(e$large_econ == 1 - e$small_econ))
mk(e, c("democracy", "ally", "high_income", "small_econ", "small_mil"), "bin_support_trade", 100,
   list(cov_sample = function(d) as.character(d$sample), cov_age = function(d) as.integer(d$age), cov_gender_code = function(d) as.integer(d$female),
        cov_education = function(d) lab(d$education), cov_rank = function(d) lab(d$rank),
        cov_trade_practitioner = function(d) as.integer(d$trade_practitioner)), "chen_2023_trade_democracy_elites")
l <- rd("study1_lucid.dta"); stopifnot(nrow(l) == 3037L)
mk(l, c("democracy", "ally", "sim_culture", "high_income", "small_econ"), "bin_support", 100,
   c(pub, chk(c("demo_correct", "ally_correct", "econ_correct", "cult_correct", "inco_correct", "thought_of_china"))),
   "chen_2023_trade_democracy_lucid")
m <- rd("study1_mturk.dta"); stopifnot(nrow(m) == 764L)
mk(m, c("democracy", "ally", "sim_culture", "high_income", "small_econ"), "bin_support", 100,
   c(list(cov_age = function(d) as.integer(d$age), cov_gender_code = function(d) as.integer(d$Female),
          cov_education = function(d) lab(d$edu), cov_region = function(d) lab(d$region),
          cov_income_code = function(d) as.integer(d$income), cov_partyid_recode_code = function(d) as.integer(d$partyID_recode),
          cov_ethnicity = function(d) { v <- lab(d$ethnicity); v[v %in% "Prefer not to answer"] <- NA; v }),
     chk(c("demo_correct", "ally_correct", "econ_correct", "cult_correct", "inco_correct"))),
   "chen_2023_trade_democracy_mturk")
s <- rd("study2_lucid.dta"); stopifnot(nrow(s) == 1659L)
mk(s, c("democracy", "honor_int", "treat_fair"), "bin_support", 1,
   c(pub, chk(c("demo_correct", "honor_correct", "legal_correct"))), "chen_2023_trade_democracy_study2")
