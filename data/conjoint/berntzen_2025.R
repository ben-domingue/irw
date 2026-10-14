##2 x 3 factorial vignette (one per respondent) on a political-rally beating from
##Berntzen, L. E., Cappelen, C., Mason, L. H., & Midtbø, T. (2025). Mind the gap: Partisan bias in justifying political
##violence in the United States. Public Opinion Quarterly (conditionally accepted; no article DOI yet).
##Replication data: Harvard Dataverse doi:10.7910/DVN/C2I1FK, CC0 1.0 (no restricted files). Files read: the SPSS file
##"NO26467145_Power_of_Party_data_Final (1).sav" (original-format download of the .tab; variable names are intact only there),
##the codebook PDF ("Codebook. POQ Mind the gap. 2025.pdf") and mind_the_gap_replication.R (as text).
##Usage: Rscript berntzen_2025.R <dir holding the .sav> <output dir>
##
##YouGov matched web panel, US, 25-31 January 2024; 2,030 raw respondents, each assigned to ONE of six vignettes (columns B1-B6; exactly one
##is non-missing per respondent: Split_Sample 1-6). The authors analyse only attentive partisans (QAttention == 4; strong or not-very-strong
##Democrats/Republicans and leaners): 1,521 respondents, and this table keeps exactly that sample (898 Democrats, 623 Republicans), because
##the inparty/outparty tokens of the vignette are filled from the respondent's party and are undefined for non-partisans.
##Attributes (codebook B1-B6):
##  party condition: B1, B2 = no party labels (control: "(not shown)"); B3, B4 = the respondent's own-party people beat disruptors of the
##    opposing party; B5, B6 = opposing-party people beat disruptors of the respondent's own party ("Inparty"/"Outparty" in the authors' code is the
##    party of the victims: B3/B4 = Outparty, B5/B6 = Inparty).
##  disruption severity: B1, B3, B5 = mild (the disruptors shout and scream); B2, B4, B6 = severe (the disruptors physically block the
##    entrance to the venue). Attribute text is paraphrased from the codebook's descriptions, not the verbatim vignette (not deposited).
##Outcome: rating = the B-item, "justifiability of a beating administered by rally attendees to disruptors", 1 = completely unjustified ...
##7 = completely justified (codebook). No choice, no opt-out. One vignette per respondent; no usable respondent id (caseid dropped; id = row).
##Covariates: cov_age; cov_party_id (the authors' party family from pid3 and the leaner item A3: Democrat or Republican, leaners included);
##cov_partisan_strength (Strong / Moderate, authors' recode from A2 and A3); cov_gender_code, cov_race_code, cov_region_code, cov_income_code (the codes
##have no value labels in the deposit: gender order Male, Female, Other is the codebook's list but not a stated mapping); cov_survey_weight (the file's
##weight, which the authors do NOT use: "Analyses are unweighted"); cov_attention_pass (QAttention == 4 for all kept rows, so omitted). Dropped: timings,
##the dark-personality item (C1), parent items, marital status.
##Count check: 1,521 = codebook analysis sample; cell sizes No Party 498, Inparty 501, Outparty 522; Mild 744, Severe 777 (checked by stopifnot).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_sav(list.files(raw, pattern = "\\.sav$", full.names = TRUE)[1]))
Bc <- c("B1", "B2", "B3", "B4", "B5", "B6")
stopifnot(nrow(d) == 2030, all(rowSums(!is.na(d[, ..Bc])) == 1))
d[, arm := max.col(!is.na(as.matrix(d[, ..Bc])), ties.method = "first")]
d[, response := as.numeric(fcoalesce(B1, B2, B3, B4, B5, B6))]
d[, party := fcase(pid3 %in% 1:2, c("Democrat", "Republican")[pid3], pid3 == 3 & A3 == 1, "Democrat", pid3 == 3 & A3 == 2, "Republican")]
d[, strength := fcase(pid3 %in% 1:2 & A2 == 1, "Strong", pid3 %in% 1:2 & A2 == 2, "Moderate", pid3 == 3 & A3 %in% 1:2, "Moderate")]
k <- d[!is.na(strength) & QAttention == 4 & !is.na(response)]
stopifnot(nrow(k) == 1521, k[, sum(party == "Democrat")] == 898, all(k$response %in% 1:7))
cond <- c("(not shown)", "(not shown)", "own party attendees beat disruptors of the opposing party", "own party attendees beat disruptors of the opposing party",
          "opposing party attendees beat disruptors of the respondent's own party", "opposing party attendees beat disruptors of the respondent's own party")[k$arm]
sev <- rep(c("mild: the disruptors shout and scream", "severe: the disruptors physically block the entrance to the venue"), 3)[k$arm]
stopifnot(table(c("No Party", "No Party", "Outparty", "Outparty", "Inparty", "Inparty")[k$arm]) [c("No Party", "Inparty", "Outparty")] == c(498, 501, 522),
          table(rep(c("Mild", "Severe"), 3)[k$arm]) == c(744, 777))
r <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating = as.integer(k$response), attr_party_condition = cond, attr_disruption_severity = sev,
  cov_age = as.integer(k$age), cov_party_id = k$party, cov_partisan_strength = k$strength, cov_gender_code = as.integer(k$Q_Gender),
  cov_race_code = as.integer(k$race), cov_region_code = as.integer(k$region), cov_income_code = as.integer(k$profile_gross_household),
  cov_survey_weight = as.numeric(k$weight))
print(r[, .(n = .N, mean = mean(rating)), .(attr_party_condition, attr_disruption_severity)])
fwrite(r, file.path(out, "berntzen_2025_political_violence.csv")); cat("rows", nrow(r), "\n")
