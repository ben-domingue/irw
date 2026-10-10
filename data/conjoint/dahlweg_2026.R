##Public servants' single-profile citizen-candidate conjoint (Germany and Taiwan) from
##Dahlweg, A., Guo, Y., Liu, H. K., & Vogel, R. (2026). Public servants' implicit citizenship
##theories and willingness to collaborate with citizens: A cross-country study. Public
##Performance & Management Review (article DOI not given in the record).
##Replication data: Zenodo record 23160049, doi:10.5281/zenodo.23160049, CC BY 4.0 (record
##licence field), open access.
##File read: ICT_replication_data.xlsx (sheets "data" and "codebook").
##Usage: Rscript dahlweg_2026.R <raw dir> <output dir>
##
##Public servants in Germany (n = 379) and Taiwan (n = 365) read a scenario about a citizen
##initiative and evaluated 4 citizen candidate profiles each (single-profile conjoint; 2,976
##profile evaluations, as the codebook states). ONE TABLE with cov_country: the authors pool the
##two samples (ICT indices standardized over the pooled sample, country as a moderator), and the
##stored attribute text is the codebook's English description, the same for both samples.
##Attributes randomized within respondent (codebook "randomized attribute"):
##  attr_character  v_character_prototype 1 = "prototypical (friendly, nice, grateful)",
##                  0 = "antiprototypical (impatient, unfriendly, causing effort)"
##  attr_gender     v_gender_female 1 = female, 0 = male
##  attr_position   v_position_leader 1 = leader, 0 = ordinary member
##LEVEL TEXT IS THE CODEBOOK'S ENGLISH DESCRIPTION, not the displayed German / Chinese vignette
##text (not deposited). Scenario factors randomized BETWEEN respondents are kept as trial_:
##trial_policy_field (v_policy_field_energy: "energy transition" / "AI implementation") and
##trial_interaction (v_interaction_coproduction: "coproduction" / "consultation").
##Outcome: rating = wtc_collaboration, willingness to collaborate with the candidate, 1 = very
##unlikely ... 7 = very likely (codebook; question wording not deposited, paraphrase).
##task = row order within respondent (1-4); the deposit records no task/display index, so this
##is not known to be the display order. profile = 1 (single profile).
##Covariates: cov_country (germany 1 -> DE, 0 -> TW), cov_age (years), cov_gender_code (female: 1 female,
##0 male or diverse: not mappable to cov_gender), cov_university_degree, cov_studying (1 yes),
##cov_political_orientation (1 left ... 7 right), cov_central_level (1 central, 0 local
##government), cov_workfield_ps (codes 1-11, OECD areas, see codebook), cov_typical_<trait>
##(15 raw typicality ratings of citizens, 1 very untypical ... 7 very typical).
##Dropped: responseid (Qualtrics ResponseId; re-keyed), v_character_antitype (complement of
##prototype), the derived ICT indices, and the 15 desirability items (stored recoded: Taiwan
##reversed, antitype items reversed again).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "ICT_replication_data.xlsx"), sheet = "data"))
stopifnot(nrow(x) == 2976, all(x$v_character_prototype + x$v_character_antitype == 1),
          all(x$wtc_collaboration %in% 1:7))
x[, rid := match(responseid, unique(responseid))]
stopifnot(uniqueN(x$rid) == 744, x[, .N, rid][, all(N == 4)])
stopifnot(x[, lapply(.SD, uniqueN), rid, .SDcols = c("v_policy_field_energy", "v_interaction_coproduction", "germany", "age")][, all(unlist(.SD[, -1]) == 1)])
x[, task := seq_len(.N), rid]
typ <- grep("^citizen_typical_", names(x), value = TRUE)
d <- x[, .(id = rid, task, profile = 1L, rating = as.integer(wtc_collaboration),
           attr_character = fifelse(v_character_prototype == 1, "prototypical (friendly, nice, grateful)",
                                    "antiprototypical (impatient, unfriendly, causing effort)"),
           attr_gender = fifelse(v_gender_female == 1, "female", "male"),
           attr_position = fifelse(v_position_leader == 1, "leader", "ordinary member"),
           trial_policy_field = fifelse(v_policy_field_energy == 1, "energy transition", "AI implementation"),
           trial_interaction = fifelse(v_interaction_coproduction == 1, "coproduction", "consultation"),
           cov_country = fifelse(germany == 1, "DE", "TW"), cov_age = as.integer(age),
           cov_gender_code = as.integer(female), cov_university_degree = as.integer(university_degree),
           cov_studying = as.integer(studying), cov_political_orientation = as.integer(political_orientation),
           cov_central_level = as.integer(central_level), cov_workfield_ps = as.integer(workfield_ps))]
for (v in typ) d[, (sub("^citizen_typical_", "cov_typical_", v)) := as.integer(x[[v]])]
d[!(cov_age %between% c(15, 100)), cov_age := NA]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dahlweg_2026_citizen_collaboration.csv"))
cat("rows", nrow(d), "resp", uniqueN(d$id), "by country", d[task == 1, .N, cov_country][, paste(cov_country, N)], "\n")
print(d[, .(m = round(mean(rating), 2)), .(attr_character)])
