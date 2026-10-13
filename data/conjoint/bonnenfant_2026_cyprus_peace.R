##Cyprus peace-settlement packages, local Greek Cypriot (GC) and Turkish Cypriot (TC) respondents, from
##Kuscu Bonnenfant, I., Morgan-Jones, E., Psaltis, C., Popp, R., Sudulich, L., & Loizides, N. (2026). Long-distance nationalism
##and peace settlement preferences. International Studies Quarterly, 70(1), sqag008. https://doi.org/10.1093/isq/sqag008
##(authors/journal/year from the journal landing page; the deposit's README names only the title and ISQ)
##Replication data: Harvard Dataverse doi:10.7910/DVN/OVWLIV, CC0 1.0. Files read: local_replication.tab (datafile 13638233, the
##original .csv ingested as tab; 16,210 rows = 1,621 respondents x 10 profiles), plus "ISQ replication.R" and Readme.txt as text.
##Usage: Rscript bonnenfant_2026_cyprus_peace.R <dir> <output dir> [file name; default local_replication.tab]
##  (the dir holds that file; the Dataverse original-format download is named by its datafile id)
##
##Design: Hainmueller-style paired conjoint of hypothetical Cyprus peace settlements. Each local respondent compared five pairs of
##settlement packages (5 tasks x 2 profiles) described by five attributes (the authors' feature labels in the R code):
##  fed   (federal executive), terr (territory returned/adjusted), proper (property compensation), impl (implementation/guarantor
##  arrangement), sup (supreme court composition). Level text is as shipped (full displayed phrases).
##Outcome: `selected`, 0/1 package chosen within the pair (forced choice; exactly one of the two = 1 for every pair).
##  The deposit does not contain the question wording or the instrument: wording recorded as unknown.
##Task / profile are NOT recorded: the file has 10 rows per respondent in the order profile-1 of tasks 1..5, then profile-2 of
##tasks 1..5. Verified: pairing row k with row k+5 gives exactly one selected = 1 in all 8,105 pairs (1,621 x 5), whereas pairing
##adjacent rows does not (2,127 pairs with 0 and 2,127 with 2). So task = k (k<=5) or k-5, profile = 1 or 2 by row block;
##task_source and profile_source are inferred; the within-task order is the row order of the deposit (outcome-independent key;
##the chosen profile is first in 4,363 and second in 3,742 pairs: not first by construction, but 54% first, which may be a
##position effect or partly sorted source order: unknown).
##Samples: GC (817 respondents) and TC (804) pooled in one table (same attribute text, the authors fit both with one model and split by
##`community`); cov_community = GC/TC.
##NOT built (held): diaspora_replication_weighted.tab (756 respondents x 10 rows, 4 attributes without the court attribute and
##different property wording): `selected` is NA for 209 respondents and for 2 or more profile rows for many others, and no row
##pairing gives one selected per pair (476 + 475 answered pairs have 0 or 2 selected for the k/k+5 pairing), so the task structure
##cannot be verified: held.
##Covariates: cov_community (GC/TC), cov_gender (Female/Male, source labels), cov_age_group (18-34, 35-54, 55+), cov_education (source
##categories: Elementary, Secondary, High School, Bachelors or equivalent, Postgraduate), cov_survey_weight (weights; constant within
##respondent). Income dropped (labels truncated in the source: "High Inc", "Low Inco", "Middle I"; 13% missing).
##Dropped: nothing identifying present (IDM is an integer respondent index; no IDs, IPs or geography in the local file).
##Restrictions: not documented in the deposit. level_weights not documented (level shares near 20% / 25% ~ uniform; not asserted).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- if (length(a) >= 3) a[3] else "local_replication.tab"
d <- fread(file.path(raw, f), encoding = "UTF-8")
stopifnot(nrow(d) == 16210, uniqueN(d$IDM) == 1621, all(d[, .N, IDM]$N == 10))
d[, k := seq_len(.N), IDM]
d[, `:=`(task = ifelse(k <= 5, k, k - 5), profile = ifelse(k <= 5, 1L, 2L))]
stopifnot(all(d[, .(s = sum(selected)), .(IDM, task)]$s == 1))
t <- d[, .(id = IDM, task = as.integer(task), profile, choice = as.integer(selected),
           attr_federal_executive = fed, attr_territory = terr, attr_property = proper,
           attr_implementation = impl, attr_supreme_court = sup,
           cov_community = community, cov_gender = tolower(gender), cov_age_group = agegroup,
           cov_education = education, cov_survey_weight = weights)]
ac <- grep("^attr_", names(t), value = TRUE); stopifnot(!anyNA(t[, ..ac]), !anyNA(t$choice))
setorder(t, id, task, profile)
fwrite(t, file.path(out, "bonnenfant_2026_cyprus_peace.csv"))
