##Tax-for-healthcare policy conjoint (Nigeria, face-to-face, informal workers) from
##Yang, J., Moerenhout, T., & Orgeira Pillai, N. (2025). The post-oil post-Covid social
##contract: Taxing informal workers for healthcare insurance in oil exporting developing
##economies. Journal of Public Policy. https://doi.org/10.1017/S0143814X2500008X
##Replication data: Harvard Dataverse doi:10.7910/DVN/UDFAJF, CC0 1.0, no restricted files.
##File read: Tax_for_Services_Nigeria_final_for_analysis.dta (Dataverse original format; one
##row per respondent, Stata variable and value labels hold the questions and level text).
##Read as text only: README.rtf, MainAnalysis.R. The deposit's long csv
##(Tax_for_Services_Nigeria_final_analysis.csv) was checked but not used: its `select` column
##is misaligned (every respondent has exactly two 1s, always in the first four of six rows,
##so 18,485 tasks have no pick and 6,397 two), while the .dta's comparison<t> has one pick per
##task. The authors' analysis uses only the rating.
##Usage: Rscript yang_2025.R <dir holding the .dta> <output dir>
##
##12,088 respondents in 12 Nigerian states, 3 tasks ("Conjoint 1-3") x 2 policies, 6 attributes.
##task = conjoint number, profile = Policy 1/2.
##  choice = comparison<t>: "Q701. Which of these two policies do you prefer?" Policy 1 /
##           Policy 2; forced, no opt-out (no missing).
##  rating = comparison<t>_policy<p>: "Q702/Q703. How much would you be satisfied or dissatisfied
##           with policy 1/2" 1 Very dissatisfied ... 5 Very satisfied, higher = more satisfied
##           (the authors' MainAnalysis.R regresses it as is, with sampling weights). Don't know
##           (-999) and refused (-888), 106 profile ratings, and 15 missing are NA here.
##Attributes (level text = the Stata value labels / string values, English as stored; the
##interview was in English, Hausa, Yoruba, Pidgin or Igbo, cov_interview_language):
##  attr_whotaxpaid (attribute1), attr_leveltax (2), attr_deduct (3), attr_howtax (4),
##  attr_healthcov (5), attr_perk (6); names follow the authors' csv.
##attribute_order_policy<p>_<t> records the order the six attributes were listed, separately
##for each policy and task (e.g. "3 4 5 6 1 2"): attrpos_<name> = position (1-6) of that
##attribute. Restrictions and level probabilities are not documented (all level shares near
##equal). How the profiles were shown (read aloud, tablet screen) is not documented.
##Covariates: cov_gender (gender: value labels Male 0 / Female 1), cov_age (Q403, years),
##cov_education (schooling, value-label text), cov_state (state value-label text),
##cov_urban_rural (as stored), cov_interview_language (value-label text),
##cov_conjoint_position (conjoint_narrative_order: block placed after section 4/5/6, value-label
##text), cov_survey_weight (sampling_weight, used by the authors). Value labels -999 / -888
##(don't know / refused) -> NA in cov_education.
##Dropped: everything else. PII in the .dta (not read here beyond names): respondent_name,
##full_name, phone_number, resp_latitude/resp_longitude, surveyor and supervisor names and
##enumeration-area names (often personal names).
##N: 12,088 respondents (all consented, all answered the three choices); the article reports
##the sample (12,088 is the deposit's count; the triage note agrees).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("whotaxpaid", "leveltax", "deduct", "howtax", "healthcov", "perk")
cols <- c("id", "gender", "age", "schooling", "state", "urban_rural", "interview_language", "conjoint_narrative_order",
          "sampling_weight", as.vector(outer(c("comparison", "attribute_order_policy1_", "attribute_order_policy2_",
          "comparison"), 1:3, paste0)), sprintf("comparison%d_policy%d", rep(1:3, 2), rep(1:2, each = 3)),
          as.vector(outer(sprintf("attribute%d_policy", 1:6), sprintf("%d_%d", rep(1:2, 3), rep(1:3, each = 2)), paste0)))
x <- read_dta(file.path(raw, "Tax_for_Services_Nigeria_final_for_analysis.dta"), col_select = all_of(unique(cols)))
txt <- function(v) { v <- as.character(as_factor(v, levels = "labels")); v[v %in% c("Don't know (do not read)", "Refuse to answer (do not read)")] <- NA; v }
x <- as.data.table(x)
x[, rid := .I]
d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
  r <- as.numeric(zap_labels(x[[sprintf("comparison%d_policy%d", t, p)]]))
  r[!is.na(r) & r < 0] <- NA
  o <- strsplit(trimws(x[[sprintf("attribute_order_policy%d_%d", p, t)]]), " +")
  stopifnot(all(lengths(o) == 6), all(vapply(o, function(z) setequal(z, as.character(1:6)), TRUE)))
  dd <- data.table(id = x$rid, task = t, profile = p, choice = as.integer(as.numeric(zap_labels(x[[paste0("comparison", t)]])) == p), rating = r)
  for (k in 1:6) {
    dd[, paste0("attr_", attrs[k]) := as.character(as_factor(x[[sprintf("attribute%d_policy%d_%d", k, p, t)]]))]
    dd[, paste0("attrpos_", attrs[k]) := vapply(o, function(z) match(as.character(k), z), 1L)]
  }
  dd
}))))
stopifnot(!anyNA(d$choice), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d[, rating %in% c(1:5, NA)]))
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", attrs), paste0("attrpos_", attrs)))
g <- as.numeric(zap_labels(x$gender))
cv <- x[, .(id = rid, cov_gender = ifelse(g == 1, "female", ifelse(g == 0, "male", NA)), cov_age = as.integer(age),
            cov_education = txt(schooling), cov_state = txt(state), cov_urban_rural = as.character(urban_rural),
            cov_interview_language = txt(interview_language), cov_conjoint_position = txt(conjoint_narrative_order),
            cov_survey_weight = as.numeric(sampling_weight))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "yang_2025_nigeria_tax_health.csv"))
