##Welfare-recipient stereotype rating conjoint (US) from
##Zhirkov, K., Lunz Trujillo, K., & Myers, C. D. (2025). Measuring support for welfare
##policies: Implications for the effects of race and deservingness stereotypes. Journal of
##Experimental Political Science, 12(1), 126-133. https://doi.org/10.1017/XPS.2023.31
##Replication data: Harvard Dataverse doi:10.7910/DVN/6SHF3S, CC0 1.0, no restricted files.
##File read (from replication_materials.zip): data/data_01_repl_raw.dta (the Qualtrics /
##Conjoint Survey Design Tool export: conj<t>_1 ratings, F_<t>_<k> attribute names,
##F_<t>_1_<k> levels). The authors' code/code_01 and code_02 .do files were read as text (not
##run) for the sample rules and the attribute/level list; design facts are from the (CC BY)
##article. The deposit's data/mzlt/ files (the earlier Myers, Zhirkov & Lunz Trujillo study)
##hold only estimated IMCEs, not profile-level data, and are not used.
##Usage: Rscript zhirkov_2025.R <dir holding data_01_repl_raw.dta> <output dir>
##
##1,964 Lucid respondents (August 22-25, 2022). Each saw 30 single profiles of a person
##("Profile <t> of 30"), task 1-30, profile = 1 (one profile per task), described by 7
##attributes: race, gender, marital status, has children, immigration status, employment
##status, criminal record. Outcome: rating = how typical the person described is of welfare
##recipients (article's paraphrase; the export's question text is truncated at "Please review
##the description of a person below, then answer t"), 0-10, higher = more typical; the end
##labels are not in the deposit. "Higher = more favourable" does not apply: this is a
##stereotype-content (typicality) rating. Missing ratings are omitted
##(rows with no outcome): 72 of 58,920 respondent-profiles, 58,848 rows.
##Attribute ORDER was randomized once per respondent (the same order on all 30 profiles,
##checked): attrpos_<name> = the row position (1-7). The article: "the value of each
##attribute in each profile is independently drawn"; no restrictions.
##Sample: the table keeps ALL 1,964 respondents with any rating. The article analyses 1,271
##non-Hispanic white respondents whose ratings vary: cov_ethnicity == 1 & cov_hispanic == 1
##(Lucid standard codes; the authors' code_01 treats these as non-Hispanic white) and a
##non-zero SD of the 30 ratings. That rule reproduces 1,271 exactly from this table, and on
##that sample the 11 AMCEs of the deposit's Figure A2 estimates (lm, SEs clustered by id)
##reproduce exactly (criminal record collapsed to none/drug/violent as the authors do).
##Covariates (source codes, Lucid profile variables stored as text and converted to integer):
##cov_age (years), cov_gender (1 = male, 2 = female per the authors' female = gender - 1),
##cov_hhi (income bracket 1-24), cov_education (1-8, negatives = missing), cov_political_party
##(Lucid code; authors' pid7: 1-5 = Strong Dem..Lean Rep, 9 = Republican, 10 = Strong Rep),
##cov_ethnicity, cov_hispanic (Lucid codes). Survey items keep their 1-7 source codes:
##cov_welfar0-4 (spending on welfare / TANF / Medicaid / SNAP / housing assistance;
##1 = Increased substantially .. 7 = Decreased substantially), cov_fire1-4 and cov_indiv1-4
##(1 = Agree strongly .. 7 = Disagree strongly; item text in the .dta variable labels).
##Dropped: the authors' derived scales and dummies. No platform IDs in the deposit;
##id = row number of the export (as in the authors' respid).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "data_01_repl_raw.dta"))))
k[, id := .I]
nm <- c("Race" = "race", "Gender" = "gender", "Marital status" = "marital", "Has children?" = "children",
        "Immigration status" = "immigration", "Employment status" = "employment", "Criminal record" = "criminal")
## attribute order is per respondent, constant over tasks
for (t in 2:30) for (j in 1:7) stopifnot(all(k[[paste0("F_", t, "_", j)]] == k[[paste0("F_1_", j)]]))
d <- rbindlist(lapply(1:30, function(t) {
  x <- data.table(id = k$id, task = t, profile = 1L, rating = as.integer(k[[paste0("conj", t, "_1")]]))
  for (j in 1:7) {
    an <- nm[k[[paste0("F_", t, "_", j)]]]
    stopifnot(!anyNA(an))
    lev <- k[[paste0("F_", t, "_1_", j)]]
    for (v in nm) {
      w <- an == v
      x[w, paste0("attr_", v) := lev[w]]
      x[w, paste0("attrpos_", v) := j]
    }
  }
  x
}))
d <- d[!is.na(rating)]
stopifnot(d[, all(rating %in% 0:10)], d[, uniqueN(attr_race)] == 3, d[, uniqueN(attr_criminal)] == 7)
cv <- c("age", "gender", "hhi", "education", "political_party", "ethnicity", "hispanic",
        paste0("welfar", 0:4), paste0("fire", 1:4), paste0("indiv", 1:4))
cvd <- k[, c("id", cv), with = FALSE]
for (v in cv) set(cvd, j = v, value = suppressWarnings(as.integer(cvd[[v]])))
cvd[education < 0, education := NA]
setnames(cvd, cv, paste0("cov_", cv))
d <- merge(d, cvd, by = "id")
setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", nm), paste0("attrpos_", nm)))
## article sample check: non-Hispanic white with varying ratings = 1,271
stopifnot(d[cov_ethnicity == 1 & cov_hispanic == 1, sd(rating), id][V1 > 0, .N] == 1271)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhirkov_2025_welfare_stereotypes.csv"))
