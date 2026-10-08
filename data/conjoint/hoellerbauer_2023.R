##Civil-society-organization conjoint (Malawi market vendors) from
##Hoellerbauer, S. (2023). Why join? How civil society organizations' attributes signal
##congruence and impact community engagement. Journal of Experimental Political Science, 10(1),
##88-99. https://doi.org/10.1017/XPS.2021.27 (online 2021-10-19)
##Replication data: Harvard Dataverse doi:10.7910/DVN/O6NMGE, CC0 1.0, no restricted files.
##Files read: vendor_long.RData (respondent level), Codebook.pdf (level labels).
##create_org_level_data.R and paper_appendix_analysis.R read as text. The article and its
##appendix are paywalled and were not read.
##Usage: Rscript hoellerbauer_2023.R <raw dir> <output dir>
##
##2,531 market vendors in Malawi (8 districts, 128 markets, 47 enumerators; face-to-face survey,
##district/market/enumerator ids anonymized by the author). Each saw 2 pairs (task 1-2) of
##hypothetical organizations, "Organization A" (profile 1) and "Organization B" (profile 2),
##described by 4 attributes; fields pair<t><a|b>_att<k>_value, so task and profile are recorded.
##Two questions about the same pairs (ONE table, two outcome columns):
##  choice_meeting: pair<t>_meeting, Organization A or B. The meeting question asks about
##    willingness to attend the organization's meetings (abstract); verbatim wording unknown.
##  choice_scandal: pair<t>_scandal, Organization A or B; wording unknown. The author reverses it
##    (scandal_ny = 1 - chosen) to match the meeting outcome "in substantive terms", so choosing an
##    organization here is UNFAVOURABLE (presumably: more likely to be involved in a scandal). Stored
##    as chosen (1 = this organization picked), not reversed.
##  Both forced A/B (factor levels Organization A/B only); a task missing one answer keeps the other.
##Attribute text: Codebook.pdf labels (English; display language not documented):
##  founded ("Organization founded"): Western Donor Capital / Capital of South Africa / Lilongwe
##    (capital of Malawi) / District Capital.
##  leader_former_profession ("Leader used to be"): Vendor / Carpenter / Laborer / Business owner /
##    Government Bureaucrat / politician. Code 6 is not in the codebook; "politician" is the
##    author's label for it in create_org_level_data.R (level shares are even, ~1/6 each).
##  funding ("Funding from"): Western government / Chinese government / South African government /
##    Malawian government / Contributions from Malawian citizens.
##  party ("Party affiliation"): Connected to political party / Independent of political party.
##Randomization restrictions and attribute order are not documented here.
##13 profiles have a missing attribute value (not saved); those tasks are dropped. Tasks with
##neither answer are omitted.
##Covariates: cov_female, cov_age, cov_literate, cov_education (0 none, 1 grade school, 2 high
##school, 3 college or above), cov_hh_income (as entered), cov_years_in_market (author's version
##with data-entry errors set to missing), cov_service (1 sells a service, 0 a good), cov_sells_daily,
##cov_intend_vote, cov_registered, cov_ngo_apathy (agreement with "When nongovernmental
##organizations work on our behalf, we need to do less work ourselves to get the government to
##listen to us", 1 = strongly disagree .. 4 = strongly agree), cov_community_org_member (0/1),
##cov_district, cov_market, cov_enumerator (the author's anonymized codes).
##Dropped: resp_id (survey ID; re-keyed), the trimmed income, the author's logical duplicates.
##N: 2,531 respondents in the deposit; the article's count was not checked (paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "vendor_long.RData"), envir = e)
v <- as.data.table(e$vendor_long)
stopifnot(nrow(v) == 2531, uniqueN(v$resp_id) == 2531)
v[, id := seq_len(.N)]
lv <- list(founded = c("Western Donor Capital", "Capital of South Africa", "Lilongwe (capital of Malawi)", "District Capital"),
           leader_former_profession = c("Vendor", "Carpenter", "Laborer", "Business owner", "Government Bureaucrat", "politician"),
           funding = c("Western government", "Chinese government", "South African government", "Malawian government",
                       "Contributions from Malawian citizens"),
           party = c("Connected to political party", "Independent of political party"))
rows <- list()
for (t in 1:2) for (p in 1:2) {
  ab <- c("a", "b")[p]
  r <- data.table(id = v$id, task = t, profile = p)
  for (q in c("meeting", "scandal")) {
    x <- as.character(v[[paste0("pair", t, "_", q)]])
    stopifnot(all(x %in% c(NA, "Organization A", "Organization B")))
    r[, paste0("choice_", q) := fifelse(is.na(x), NA_integer_, as.integer(x == paste("Organization", toupper(ab))))]
  }
  for (k in 1:4) {
    code <- v[[paste0("pair", t, ab, "_att", k, "_value")]]
    stopifnot(all(code %in% c(NA, seq_along(lv[[k]]))))
    r[, paste0("attr_", names(lv)[k]) := lv[[k]][code]]
  }
  rows[[length(rows) + 1]] <- r
}
d <- rbindlist(rows)
ac <- grep("^attr_", names(d), value = TRUE)
d[, bad := any(is.na(unlist(.SD))), by = .(id, task), .SDcols = ac]
stopifnot(d[profile == 1, sum(rowSums(is.na(.SD)) > 0), .SDcols = ac] + d[profile == 2, sum(rowSums(is.na(.SD)) > 0), .SDcols = ac] == 13)
d <- d[bad == FALSE & !(is.na(choice_meeting) & is.na(choice_scandal))][, bad := NULL]
for (q in c("choice_meeting", "choice_scandal")) stopifnot(d[!is.na(get(q)), .(s = sum(get(q)), n = .N), .(id, task)][, all(s == 1 & n == 2)])
cv <- v[, .(id, cov_female = as.integer(female), cov_age = as.integer(age), cov_literate = as.integer(literacy_any),
            cov_education = as.integer(educ_cat), cov_hh_income = hh_income, cov_years_in_market = yrs_in_mkt_fix,
            cov_service = as.integer(service), cov_sells_daily = as.integer(sell_daily), cov_intend_vote = as.integer(intend_vote),
            cov_registered = as.integer(registered_vt),
            cov_ngo_apathy = match(as.character(apathy_NGO), c("Strongly Disagree", "Somewhat Disagree", "Somewhat Agree", "Strongly Agree")),
            cov_community_org_member = as.integer(as.character(member_co) == "Yes"),
            cov_district = as.integer(as.character(district)), cov_market = as.integer(as.character(market)),
            cov_enumerator = as.integer(as.character(enum)))]
stopifnot(all(is.na(v$apathy_NGO) == is.na(cv$cov_ngo_apathy)))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hoellerbauer_2023_civil_society_orgs.csv"))
