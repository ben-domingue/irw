##QAnon candidate conjoint from
##Noble, B. S., & Carlson, T. N. (2024). CueAnon: What QAnon signals about congressional
##candidates and what it costs them. Political Behavior. https://doi.org/10.1007/s11109-024-09957-3
##Replication data: Harvard Dataverse doi:10.7910/DVN/UVVSIR, CC0 1.0. Files read: conjoint_df.csv
##and conjoint_demo.csv (Dataverse "original format" downloads of the .tab files); labels from
##cueanon-codebook.pdf (deposit) and Online Appendix C (article ESM). The deposit's vignette
##experiment (tass_small, one candidate news story, 3 conditions) is not a conjoint and is not built.
##Usage: Rscript noble_2024.R <dir holding the two csv files> <output dir>
##
##690 US respondents (Republicans and Democrats incl. leaners, plus 4 independents), 10 tasks of 2
##hypothetical congressional candidates (profile 1 = Candidate A, 2 = Candidate B; the
##source's `pref` names the chosen one), 8 attributes stored as text in the data: party, prior
##office, QAnon support, gender, first-impeachment position, infrastructure bill, taxes vs
##services, border wall. The sample source and fielding date are not stated in the deposit; the
##accessible article text does not identify them (unknown).
##Outcomes:
##  choice          = Y, the candidate the respondent preferred in the pair (codebook: "1 if
##                    candidate is chosen by respondent"). No opt-out. 4 tasks (1 respondent) have no
##                    choice recorded: choice is NA there, the ratings are kept.
##  rating_favor    = likert_favor, 7-point favorability of each candidate (codebook). Higher = more
##                    favorable (Appendix Fig. C4: "QAnon support causes a decline in favorability"
##                    on this scale); anchor wording not in any source.
##  rating_ideology = likert_ideology, perceived ideology of each candidate, 1 = extremely liberal,
##                    7 = extremely conservative (codebook).
##  Each respondent answered one of the two ratings for all tasks (346 favorability, 344 ideology;
##  the data show the split, no source documents how it was assigned).
##Restrictions: none documented; party is drawn per profile (the source's `primary` flag, same-party
##pair, is derived and dropped). Attribute order: no source.
##Covariates: conjoint_df respondent columns cov_resp_pid7 (codebook: 1 = strong Democrat ... 7 =
##strong Republican, intermediate labels not given: codes), cov_ideo (1 extremely liberal ... 7
##extremely conservative), cov_trust (trust in mainstream media, 1 none at all ... 4 a great
##deal), cov_antiestablishment_1-14 (codebook lists 1-12; the data hold 14), cov_believe_q (1
##strongly disagree ... 5 strongly agree), cov_alt_right_news (0/1), cov_fox4 (1 never ... 4 every
##day). conjoint_demo.csv has no id: its 690 rows are linked to respondents r_1 ... r_690 in order,
##verified by its resp_gop/resp_dem/resp_ind columns matching conjoint_df's for all 690 rows;
##from it cov_age (years; free-typed: values outside 18-100, e.g. 823, set to NA), cov_gender (female 1 = female, 0 = male; codebook), cov_employed (0/1).
##Dropped: party dummies (resp_gop/dem/ind), fox_user (derived from fox4), antiestablish_scale,
##choice_uid, other_party, primary. Respondent ids r_<n> re-keyed to n.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint_df.csv"))
m <- fread(file.path(raw, "conjoint_demo.csv"))
s[, rid := as.integer(sub("^r_", "", id))]
d <- data.table(id = s$rid, task = as.integer(sub("choice", "", s$choice_num)),
                profile = as.integer(sub("profile", "", s$profile_num)),
                choice = s$Y, rating_favor = s$likert_favor, rating_ideology = s$likert_ideology,
                attr_party = s$party, attr_prior_office = s$prior, attr_qanon = s$qanon, attr_gender = s$gender,
                attr_impeachment = s$impeach, attr_infrastructure = s$infra, attr_taxes = s$econ, attr_border_wall = s$imm)
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
# pref names the chosen candidate; check it agrees with Y and profile order
stopifnot(s[!is.na(Y), all((pref == "Candidate A") == (profile_num == "profile1") | Y == 0)])
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
cv <- c("resp_pid7", "ideo", "trust", paste0("antiestablishment_", 1:14), "believe_q", "alt_right_news", "fox4")
for (v in cv) d[, paste0("cov_", v) := s[[v]]]
r <- unique(s[, .(rid, resp_gop, resp_dem, resp_ind)]); setorder(r, rid)
stopifnot(nrow(r) == nrow(m), identical(r$rid, seq_len(nrow(m))),
          all(r$resp_gop == m$resp_gop & r$resp_dem == m$resp_dem & r$resp_ind == m$resp_ind))
ag <- suppressWarnings(as.integer(m$age)); ag[!(ag >= 18 & ag <= 100)] <- NA
dm <- data.table(id = r$rid, cov_age = ag, cov_gender = c("male", "female")[m$female + 1L], cov_employed = m$employed)
d <- merge(d, dm, by = "id")
d <- d[!(is.na(choice) & is.na(rating_favor) & is.na(rating_ideology))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "noble_2024_qanon_candidates.csv"))
