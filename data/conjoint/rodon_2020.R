##Fairness of redistributive policies conjoint (US, Prolific) from
##Rodon, T., & Sanjaume-Calvet, M. (2020). How fair is it? An experimental study of perceived
##fairness of distributive policies. The Journal of Politics, 82(1), 384-391. https://doi.org/10.1086/706053
##Replication data: Harvard Dataverse doi:10.7910/DVN/3EONKV, CC0 1.0. Files read: conjoint.xlsx (raw
##Qualtrics export, sheet "Redistribution") and ses_data.xlsx (Dataverse "original format" of
##ses_data.tab; Prolific demographics, sheet "data"). Wording from the article and its online appendix
##(A.1-A.5, UPF repository copy); level text from the export's Q*_k_TEXT fields as displayed.
##Usage: Rscript rodon_2020.R <dir holding conjoint.xlsx and ses_data.xlsx> <output dir>
##
##Prolific survey of US adults, 12-17 May 2017 (appendix). Each respondent saw 5 tables (tasks), each
##comparing two hypothetical countries (profiles A/B) on 5 policy consequences: the country's wealth,
##origin of people's wealth, the wealthiest, the poorest, social mobility. Below each table:
##  rating = "On a scale from 0 to 10, how FAIR do you think the impact of these policies would be
##           in:" [each country]. Stored as in the export, codes 1-11 = 0 (very unfair) ... 10 (very
##           fair); 11 options; the authors analyse the same 1-11 codes (their reported mean 5.75 is on
##           this coding). Non-response was not allowed.
##Attribute order: the export's Q*_11_TEXT lists the row labels in display order for each table; it
##differs between a respondent's tables (only ~1% of table pairs share an order), so the order was
##randomized per task (the article says "across respondents") -> attrpos_ = row 1-5.
##Table 4 (Q29) used a second set of row labels and mobility wording: "The wealthiest 20%", "The
##poorest 20%", "Most of people's wealth comes from:", "Social mobility" with levels "Upward mobility
##would be likely", "Downward mobility would be likely", "Upward and Downward mobility would be
##likely", "None"; tables 1-3 and 5 read "The wealthiest", "The poorest", "People's wealth would still
##come from", "There would be" + "Upward social mobility", ..., "No social mobility". Levels are kept
##as displayed (the authors merge the two mobility wordings); trial_label_set = "standard" or
##"20% labels" (table 4) records the row-label set. The article says the design was fully randomized;
##the appendix mentions unrealistic combinations (e.g. wealthiest and poorest wealthier while the
##country's wealth decreases) that were allowed. Level weights not stated.
##Covariates: cov_attention_pass (IMC "Please click 'somewhat approve' below": 1 if imc = 4, else 0;
##code 4 = "somewhat approve" is inferred: 1,551 of 1,579 chose it and the appendix says 1.8% failed,
##28/1,579 = 1.8%); cov_imc_code (raw); cov_self_ideol (self_ideol_1, 1 Very liberal ... 7 Very
##conservative, appendix A.6); cov_duration_sec (survey end minus start, V9 - V8). From ses_data.xlsx
##(Prolific profile, matched on prolific_id): cov_age (plausible whole ages 18-99, else NA),
##cov_gender (sex Female/Male -> female/male), cov_ethnicity, cov_education, cov_employment,
##cov_party_id (political_affiliation text; MISSING and N/A -> NA, "None" and "Other" kept),
##cov_income (option text, "Â£" mojibake repaired to "£"; MISSING, N/A, "Rather not say" -> NA).
##PII dropped: IP address (V6), Prolific ID, Qualtrics ResponseID (V1), free-text "why" answer
##(whyct3), Prolific timestamps. 2 Prolific IDs appear twice in the export: the later-started copy
##is dropped. The authors also drop respondents faster than 5 minutes (appendix A.2); kept here with
##cov_duration_sec (129 under 300 s). 12 kept respondents have no Prolific profile row (covariates NA).
##Count check: 1,577 respondents x 5 tables x 2 = 15,770 rows; the article reports 1,567 respondents
##and 15,670 observations, which is the subset that matches the Prolific file (the authors' merge).
##Spot check (lm, SE clustered by id, mobility wordings pooled): wealth from family connections
##-1.20 (SE 0.06) vs people's talent, matching the article's "one point less fair"; mean rating 5.80.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "conjoint.xlsx"), sheet = "Redistribution"))
x[, start := as.POSIXct(V8, tz = "UTC")][, end := as.POSIXct(V9, tz = "UTC")]
setorder(x, start)
x <- x[!duplicated(prolific_id)]
x[, rid := .I]
qs <- c("Q20", "Q19", "Q24", "Q29", "Q33")
lab <- c("The country's wealth" = "wealth", "People's wealth would still come from" = "origin",
         "Most of people's wealth comes from:" = "origin", "The wealthiest" = "wealthiest",
         "The wealthiest 20%" = "wealthiest", "The poorest" = "poorest", "The poorest 20%" = "poorest",
         "There would be" = "mobility", "Social mobility" = "mobility")
an <- c("wealth", "origin", "wealthiest", "poorest", "mobility")
rows <- list()
for (t in 1:5) {
  q <- qs[t]
  ord <- strsplit(x[[paste0(q, "_11_TEXT")]], ",", fixed = TRUE)
  stopifnot(all(lengths(ord) == 5), all(unlist(ord) %in% names(lab)))
  pos <- t(sapply(ord, function(o) match(an, lab[o])))
  stopifnot(!anyNA(pos))
  for (p in 1:2) {
    d <- data.table(rid = x$rid, task = t, profile = p, rating = as.integer(x[[sprintf("cf%d_%d", t, p)]]))
    for (j in 1:5) {
      d[, paste0("attr_", an[j]) := x[[sprintf("%s_%d_TEXT", q, j + 5 * (p - 1))]]]
      d[, paste0("attrpos_", an[j]) := pos[, j]]
    }
    d[, trial_label_set := if (t == 4) "20% labels" else "standard"]
    rows[[length(rows) + 1]] <- d
  }
}
d <- rbindlist(rows)
stopifnot(all(d$rating %in% 1:11), !anyNA(d[, paste0("attr_", an), with = FALSE]))
s <- as.data.table(read_excel(file.path(raw, "ses_data.xlsx"), sheet = "data"))
stopifnot(!anyDuplicated(s$prolific_id))
na_txt <- function(v, drop) { v[v %in% drop] <- NA; v }
s[, age_n := suppressWarnings(as.numeric(age))]
s <- s[, .(prolific_id,
           cov_age = fifelse(!is.na(age_n) & age_n >= 18 & age_n <= 99 & age_n == round(age_n), as.integer(age_n), NA_integer_),
           cov_gender = fifelse(sex == "Female", "female", fifelse(sex == "Male", "male", NA_character_)),
           cov_ethnicity = ethnicity,
           cov_education = na_txt(education, c("MISSING", "N/A")),
           cov_employment = employment_status,
           cov_party_id = na_txt(political_affiliation, c("MISSING", "N/A")),
           cov_income = na_txt(gsub("Â£", "£", income, fixed = TRUE), c("MISSING", "N/A", "Rather not say")))]
cv <- x[, .(rid, prolific_id, cov_attention_pass = as.integer(imc == 4), cov_imc_code = as.integer(imc),
            cov_self_ideol = as.integer(self_ideol_1),
            cov_duration_sec = as.integer(round(as.numeric(difftime(end, start, units = "secs")))))]
cat("respondents without Prolific profile row:", sum(!cv$prolific_id %in% s$prolific_id), "\n")
cv <- merge(cv, s, by = "prolific_id", all.x = TRUE)[, prolific_id := NULL]
d <- merge(d, cv, by = "rid")
setnames(d, "rid", "id")
setorder(d, id, task, profile)
cat("respondents:", uniqueN(d$id), " rows:", nrow(d), " mean rating:", round(mean(d$rating), 2), "\n")
fwrite(d, file.path(out, "rodon_2020_fair_redistribution.csv"))
