##Democracy trade-off conjoint (US) from
##Mortenson, C., & Nisbet, E. (2025). Benefit seekers or principle holders? Experimental evidence
##on Americans' democratic trade-offs. Perspectives on Politics. https://doi.org/10.1017/S1537592725104052
##Replication data: Harvard Dataverse doi:10.7910/DVN/YPNPMA, CC0 1.0, no restricted files. File
##read: "Understanding Democracy Final Version_August 16, 2024_13.32.tab" in its original format
##(Qualtrics CSV export with numeric answer codes; row 2 holds the question texts, row 3 import ids).
##README Final.Rmd and Analysis_Code_PP2025.Rmd read as text (not run). Design facts from the
##article (open access, CC BY-SA 4.0).
##Usage: Rscript mortenson_2025.R <dir holding the csv saved as data.csv> <output dir>
##
##Opt-in online panel (quota sample; the export carries PureSpectrum fields), US adults, 9-10
##August 2024. 638 rows: 15 were screened out at the first attention check before the conjoint
##(term = attention_1, no conjoint answers) and are dropped; 623 respondents remain (= article N).
##5 tasks x 2 country profiles (Qualtrics conjoint, "Country 1" / "Country 2"), 4 attributes
##with 3 levels each ("completely randomized", article): Economic Wellbeing, Freedom of the Press
##and Speech, Role of the President and Elections, Rule of Law. Level text stored as displayed
##(capitals as shown). Attribute order was randomized per respondent: featureK.DISPLAY_NAME names
##the attribute in row K+1, the same for all 5 tasks; attrpos_ = row (as in the authors' code).
##  choice: "Democracy comes in many different flavors. Below are two countries with different
##  features to their democracy. Please select which country you would MOST prefer to live in from
##  the selections below. Read each item CAREFULLY, as the options will vary in each round."
##  C1-C5 = 1/2; the authors' code sets selected = (C_t == profile). Forced choice.
##Covariates: cov_age (years, "How old are you?"); cov_gender_code, cov_education_code,
##cov_race_code, cov_party_id_code (Qualtrics codes; the export has no answer labels and the
##authors' code labels only race 1 = White, so they keep codes); cov_ideology_political /
##_social / _economic (idpol, idsoc, eideo codes, wording in the export, no labels);
##cov_interest_politics (attent_1), cov_interest_government (attent_2) codes;
##cov_attention_pass_2: 0 for the 6 respondents the survey terminated at the post-conjoint
##attention check ("please select Y"; term = attention_2), 1 otherwise (everyone kept passed the
##first one); cov_duration_sec (Qualtrics Duration, whole survey).
##Dropped (PII FOUND): IPAddress, LocationLatitude/Longitude, ResponseId (re-keyed), panel and
##fraud fields (rid, transaction_id, PS, pureSpectrum*, Q_RelevantID*, RISN, CMRID, Q_URL),
##free-text fields (race_6_TEXT, party_8_TEXT, denom_4_TEXT); other survey items not kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.csv"), colClasses = "character")[-(1:2)]
stopifnot(nrow(x) == 638)
x <- x[C1 != ""]
stopifnot(nrow(x) == 623, all(x$term %in% c("", "attention_2")))
x[, id := .I]
attrs <- c("Economic Wellbeing" = "economic_wellbeing", "Freedom of the Press and Speech" = "press_speech",
           "Role of the President and Elections" = "president_elections", "Rule of Law" = "rule_of_law")
rows <- list()
for (t in 1:5) for (p in 1:2) {
  d <- data.table(id = x$id, task = t, profile = p, choice = as.integer(x[[paste0("C", t)]] == as.character(p)))
  for (k in 0:3) {
    nm <- attrs[x[[sprintf("feature%d.DISPLAY_NAME", k)]]]
    stopifnot(!anyNA(nm))
    val <- trimws(x[[sprintf("feature%d.%d.%d_CBCONJOINT", k, t, p)]])
    for (n in attrs) {
      if (k == 0) { d[, paste0("attr_", n) := NA_character_]; d[, paste0("attrpos_", n) := NA_integer_] }
      w <- which(nm == n)
      set(d, w, paste0("attr_", n), val[w]); set(d, w, paste0("attrpos_", n), k + 1L)
    }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
stopifnot(!anyNA(d), all(d[, .SD, .SDcols = patterns("^attr_")] != ""))
stopifnot(all(sapply(d[, .SD, .SDcols = patterns("^attr_")], uniqueN) == 3))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
num <- function(v) suppressWarnings(as.integer(v))
cv <- x[, .(id, cov_age = num(age), cov_gender_code = num(gender), cov_education_code = num(educ), cov_race_code = num(race),
            cov_party_id_code = num(party), cov_ideology_political = num(idpol), cov_ideology_social = num(idsoc),
            cov_ideology_economic = num(eideo), cov_interest_politics = num(attent_1), cov_interest_government = num(attent_2),
            cov_attention_pass_2 = as.integer(term != "attention_2"), cov_duration_sec = num(`Duration (in seconds)`))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mortenson_2025_democracy_tradeoffs.csv"))
