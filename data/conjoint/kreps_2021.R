##COVID-19 vaccine single-profile conjoint with financial incentives (US) from
##Kreps, S., Dasgupta, N., Brownstein, J. S., Hswen, Y., & Kriner, D. L. (2021). Public
##attitudes toward COVID-19 vaccination: The role of vaccine attributes, incentives, and
##misinformation. npj Vaccines, 6, 73. https://doi.org/10.1038/s41541-021-00335-2
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZYU6CO, CC0 1.0. File read:
##vax_misinfo_replication_data_raw.dta (raw Qualtrics export, original Stata format).
##vax_misinfo_final_replication_do.do read as text. A different study and sample from
##kreps_2020_covid_vaccine (paired design, JAMA Netw Open 2020).
##Usage: Rscript kreps_2021.R <dir holding the .dta> <output dir>
##
##1,096 US adults (Lucid), seven tasks, each ONE hypothetical vaccine profile with five
##attributes (Qualtrics conjoint export: F_<task>_<pos> = attribute name at row <pos>,
##F_<task>_1_<pos> = its level). task = 1-7 (recorded), profile = 1. Attribute row order
##was randomized once per respondent (identical in all 7 tasks for every respondent,
##checked): attrpos_* = row position 1-5. Levels are the displayed strings as exported;
##the emergency-use-authorization text is cut at 244 characters in the deposit ("... but
##that early results suggest are safe and may be eff"), stored as exported; "Your receive
##$10 incentive" is the displayed spelling.
##Outcomes:
##  choice: "If you had to choose, would you choose to get this vaccine, or would you choose
##    not to be vaccinated?" (label cut at 80 characters after "or would you choose"; ending
##    from the answer options) (vax_bin_<t>; value labels "I would choose to get this vaccine"
##    = 1, "I would choose not to be vaccinated" = 0). Single-profile accept/reject, so
##    opt_out = yes (rejecting is the outside option). The authors' do-file codes missing as
##    0; here missing stays NA (none in the data).
##  rating: "How likely or unlikely would you be to get the vaccine described above?"
##    (vaxa_ord_1-3, vax_ord_4-7), 7-point, STORED RAW: 1 = Extremely likely ... 7 =
##    Extremely unlikely (lower = more likely; the authors reverse it).
##Restrictions: none documented; all level combinations occur.
##Covariates: cov_age (age code + 17, as the do-file and the value labels "18" = 1 give),
##cov_gender (1 Male, 2 Female; 3 Prefer not to say -> NA), cov_education (value-label
##text), cov_party_id (party3 value-label text: Republican / Democrat / Independent /
##Other/don't know), cov_ideology (value-label text, 7 points), cov_state (value-label
##text), cov_duration_sec (Qualtrics Duration (in seconds), whole survey).
##Dropped: ResponseId, Lucid rid (platform IDs; ids re-keyed from row order), ZIP CODE
##(5-digit zip for 1,095 respondents: PII, dropped), IP/location/recipient fields (blanked
##in the deposit), UserAgent and browser meta, timers, the free-text closing comment, the
##panel's own demographic fields (age_0 ... region), and all other survey items. No weights.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "vax_misinfo_replication_data_raw.dta")))
stopifnot(nrow(s) == 1096)
s[, rid_row := .I]
anm <- c("Cost or Financial Incentive" = "cost", "Development and testing procedure" = "approval",
         "Efficacy – protection against severe symptoms such as respiratory failure, admission to a hospital ICU, or death" = "efficacy",
         "Manufacturer" = "manufacturer", "Risk of mild side effects \r\n(flu-like symptoms)" = "mild_side_effects")
ordv <- c("vaxa_ord_1", "vaxa_ord_2", "vaxa_ord_3", "vax_ord_4", "vax_ord_5", "vax_ord_6", "vax_ord_7")
L <- rbindlist(lapply(1:7, function(t) rbindlist(lapply(1:5, function(p) {
  data.table(rid_row = s$rid_row, task = t, pos = p, attr = anm[as.character(s[[sprintf("F_%d_%d", t, p)]])],
             level = as.character(s[[sprintf("F_%d_1_%d", t, p)]]))
}))))
stopifnot(!anyNA(L$attr), L[, uniqueN(attr), .(rid_row, task)][, all(V1 == 5)], all(nzchar(L$level)))
stopifnot(L[, uniqueN(pos), .(rid_row, attr)][, all(V1 == 1)])   # order fixed within respondent
W <- dcast(L, rid_row + task ~ attr, value.var = c("level", "pos"))
setnames(W, sub("^level_", "attr_", names(W))); setnames(W, sub("^pos_", "attrpos_", names(W)))
Y <- rbindlist(lapply(1:7, function(t) data.table(rid_row = s$rid_row, task = t,
  choice = c(1L, 0L)[as.integer(zap_labels(s[[paste0("vax_bin_", t)]]))], rating = as.integer(zap_labels(s[[ordv[t]]])))))
stopifnot(all(Y$rating %in% c(1:7, NA)))
lt <- function(x) as.character(as_factor(x, levels = "labels"))
cv <- s[, .(rid_row, cov_age = as.integer(zap_labels(age)) + 17L,
            cov_gender = c("male", "female")[match(as.integer(zap_labels(gender)), 1:2)],
            cov_education = lt(education), cov_party_id = lt(party3), cov_ideology = lt(ideology), cov_state = lt(state),
            cov_duration_sec = as.integer(Duration__in_seconds_))]
d <- merge(merge(Y, W, by = c("rid_row", "task")), cv, by = "rid_row")
d <- d[!(is.na(choice) & is.na(rating))]
d[, id := rid_row][, rid_row := NULL][, profile := 1L]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kreps_2021_vaccine_incentives.csv"))
