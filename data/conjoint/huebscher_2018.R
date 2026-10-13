##Party-platform fiscal-austerity conjoint (five countries) from
##Huebscher, E., Sattler, T., & Wagner, M. (2018). Voter responses to fiscal austerity. SSRN working paper.
##https://doi.org/10.2139/ssrn.3289341
##Replication data: Harvard Dataverse doi:10.7910/DVN/VHS0J3, CC0 1.0. Files read (Stata, format=original):
##Germany_Conjoint.tab, Italy_Conjoint.tab, Portugal_Conjoint.tab, Spain_Conjoint.tab, UK_Conjoint.tab (renamed
##Germany.tab etc. on download); codebook 00_Codebook_VoterResponseDataset.pdf and 02_ReplicationFile_Conjoint.do
##(text). The Vignette files (single treatment E2Vignettes: tax increases / spending cuts / status quo) are one
##manipulated factor and are not built.
##Usage: Rscript huebscher_2018.R <dir holding the *.tab files> <output dir>
##Writes five tables (the authors estimate the conjoint country by country; same design and attribute text):
##  huebscher_2018_austerity_de / _it / _pt / _es / _uk
##Design: online surveys fielded 13-30 March 2018 (RecordedDate; sampling firm not stated in the files); each respondent saw FIVE screens
##(E5task 1-5), each with TWO policy packages, one proposed by a conservative and one by a leftist party
##(platform; the conservative package is first on screen in ~51% of tasks, so the file's row order within a
##task is taken as screen position: profile = row within task; inferred). Each package: spending cuts (small or
##large) to public health care, pensions, education, unemployment benefits and public infrastructure, and a tax
##increase (none / across the board / for the wealthy only). The authors' do file notes the last attribute is
##a "linear function of the policy packages" and excludes it from the figure; it is not in the file.
##Levels are the codebook's value labels (Small/Large, None/Across the board/For the wealthy only,
##Conservative/Leftist); the exact on-screen phrasing is in the paper's online appendix (A5.2), not in the
##deposit. Randomization restrictions: the party attribute always differs within a task (one conservative, one
##leftist, checked); others not documented. Level shares near-equal.
##Outcome (wording not in the deposit; paraphrase): choice = vote for this package's party, CJvote 0/1 per
##package. In every task at most ONE package has CJvote = 1 (checked); tasks where neither does are respondents
##who vote for neither: OPT-OUT (CJvote = 0 on both). This is a vote-intention measure, one-of-two-or-none.
##Dropped: rows with no package or outcome values (1,324 / 1,370 / 1,754 / 1,324 / 1,830 rows for DE/IT/PT/ES/UK,
##screens the respondent did not reach or complete; 130 Germany respondents have none, so Germany keeps 2,243 of
##the 2,373 in the file). Complete respondents have 10 rows; a few have 2-8.
##Covariates (codebook): cov_gender (1 = male, 0 = female), cov_age (years), cov_education (eisced answer text:
##1 less than lower secondary, 2 lower secondary, 3 lower tier upper secondary, 4 upper tier upper secondary,
##5 advanced vocational/sub-degree, 6 lower tertiary education (BA level), 7 higher tertiary (MA, PhD), 55 other),
##cov_left_right (Q16_1, 0 extreme left .. 10 extreme right), cov_income_decile (Q1010, 1 lowest .. 10 highest;
##ESS-style bands), cov_identifies_center_left (leftid: identifies with the dominant centre-left party: SPD /
##PSOE / PS / Labour / PD; 0/1), cov_survey_weight (weighttoess, population weight; MISSING for ~19% of rows,
##left NA; the authors' pweight regressions therefore drop those rows). Respondent ids re-keyed (the source `id`
##is the authors' cluster id; ResponseId dropped).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
edu <- c("less than lower secondary", "lower secondary", "lower tier upper secondary", "upper tier upper secondary",
         "advanced vocational, sub-degree", "lower tertiary education, BA level", "higher tertiary (MA, PhD)")
for (cc in list(c("Germany", "de"), c("Italy", "it"), c("Portugal", "pt"), c("Spain", "es"), c("UK", "uk"))) {
  s <- as.data.table(haven::read_dta(file.path(raw, paste0(cc[1], ".tab"))))
  s[, k := seq_len(.N), .(id, E5task)]
  nb <- nrow(s); s <- s[!is.na(platform)]
  stopifnot(!anyNA(s[, .(tax_rec, pension_rec, health_rec, infra_rec, unemp_rec, educ_rec, CJvote)]),
            s[, .N, .(id, E5task)][, all(N == 2)], s[, sum(CJvote), .(id, E5task)][, all(V1 <= 1)],
            s[, uniqueN(platform), .(id, E5task)][, all(V1 == 2)])
  sm <- c("Small", "Large")
  d <- s[, .(id = as.integer(factor(id)), task = as.integer(E5task), profile = as.integer(k), choice = as.integer(CJvote),
    attr_party = c("Conservative", "Leftist")[platform], attr_health_cuts = sm[health_rec], attr_pension_cuts = sm[pension_rec],
    attr_education_cuts = sm[educ_rec], attr_unemployment_cuts = sm[unemp_rec], attr_infrastructure_cuts = sm[infra_rec],
    attr_tax_increase = c("None", "Across the board", "For the wealthy only")[tax_rec],
    cov_gender = c("female", "male")[gender + 1L], cov_age = as.integer(age),
    cov_education = ifelse(eisced == 55, "other", edu[pmin(eisced, 8L)]),
    cov_left_right = as.integer(Q16_1), cov_income_decile = as.integer(Q1010),
    cov_identifies_center_left = as.integer(leftid), cov_survey_weight = weighttoess)]
  stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
  setorder(d, id, task, profile)
  nm <- paste0("huebscher_2018_austerity_", cc[2])
  fwrite(d, file.path(out, paste0(nm, ".csv")))
  cat(nm, uniqueN(d$id), nrow(d), "dropped rows", nb - nrow(s), "chose neither", d[, sum(choice), .(id, task)][, mean(V1 == 0)], "\n")
}
