##Housework-sharing factorial survey from
##Schulz, F. (2020). Attitudes towards sharing housework in context: An empirical, factorial survey
##approach. Journal of Family Research (Early View). https://doi.org/10.20377/jfr-419
##Replication data: OSF osf.io/msx35 (node licence CC BY 4.0; no other terms; files: replication package zip and
##the open-access article PDF). Files read: schulz_2020_replication_package/data/data.dta (value labels), the
##article (design, wording, Appendix A: dimensions and levels). The do-files were read as text only.
##Usage: Rscript schulz_2020.R <raw dir> <output dir>   (raw dir holds data/data.dta of the package)
##
##1,120 German women and men (a 2016 online panel survey; 644 women, 476 men). Each respondent was assigned one
##of 30 decks (block 1-30; trial_deck) of 4 vignettes (run 1-4 = order within the block, recorded) about a
##couple, with six randomized factors; one profile per task. The respondent went through the SAME four
##vignettes three times, each pass with a different question (total housework, routine housework,
##non-routine housework): these three answers are columns of one table (rating_total, rating_routine,
##rating_nonroutine), so there are 4 tasks per respondent. Whether the order of the four vignettes was
##re-randomized between passes is not stated; the order stored is that of the data.
##Vignette example (translated): "An unmarried couple is living together. They don't have children. The man
##is working full-time, the woman is not employed. The woman has 1,800 Euros per month at her disposal. With
##this money, the woman contributes less to the household income than her partner."
##Attributes (level text = the Stata value labels, which follow Appendix A's dimension list):
##  attr_marital_status   x1  Not married / Married
##  attr_parenthood       x2  No children / Child newborn / Child kindergarten / Child school
##                          (article: no children, one child aged 6 months, 3-6 years, 6 years or older)
##  attr_employment_man   x3  Not employed / Part-time / Full-time
##  attr_employment_woman x4  Not employed / Part-time / Full-time
##  attr_income_woman     x5  woman's monthly income in euros: 0 / 800 / 1,800 / 3,500
##  attr_relative_income  x6  woman's contribution to household income: Less than man / Same as man / More than man
##                          (the labels in the data; the vignette says "less than her partner" etc.)
##Randomization restrictions: full factorial 2x4x3x3x4x3 = 864; implausible combinations of employment and
##income (above all employed with zero income) were removed, leaving 648; 120 vignettes were drawn by
##d-efficient sampling (resolution IV, d-efficiency 92.3), so levels are balanced within each dimension of the
##design but the shares in Table 1 are unequal for income (0: .13, others .28-.29) and relative income (.35/.35/.30).
##Outcomes, 7-point (stored 1-7, not reversed): "Who do you think should be doing the housework [cooking,
##cleaning and laundry / repairs, paperwork, and caring for the car] in this couple?" 1 = woman alone, 2 = woman
##most, 3 = woman more, 4 = both equally, 5 = man more, 6 = man most, 7 = man alone. Higher = more to the man.
##No opt-out. Rows with all three outcomes missing are omitted.
##Covariates: cov_gender (sex_r), cov_age (age_r, as in the deposit), cov_birth_year (byear_r), cov_education
##(school_r, highest school qualification, own categories; "Don't know" kept), cov_partnered (couple Yes/No).
##Dropped: plz (postal code; dropped, never kept), the derived er1 (relative employment) and issp/tradroles
##scales, parents' and partner variables, difficulties item. id = re-key of the panel id.
##Count check: article N = 1,120 respondents, 4,480 vignettes; matches (before dropping rows without outcomes).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "data", "data.dta")))
stopifnot(nrow(d) == 4480, uniqueN(d$id) == 1120, !anyDuplicated(d[, .(id, run)]))
lab <- function(x) { l <- attr(x, "labels"); l <- l[!duplicated(l)]; as.character(names(l)[match(as.numeric(x), l)]) }
chk <- function(x) { stopifnot(!anyNA(x)); x }
x <- data.table(id = match(d$id, sort(unique(d$id))), task = as.integer(d$run), profile = 1L,
  rating_total = as.integer(d$h), rating_routine = as.integer(d$f), rating_nonroutine = as.integer(d$m),
  attr_marital_status = chk(lab(d$x1)), attr_parenthood = chk(lab(d$x2)), attr_employment_man = chk(lab(d$x3)),
  attr_employment_woman = chk(lab(d$x4)), attr_income_woman = chk(lab(d$x5)), attr_relative_income = chk(lab(d$x6)),
  trial_deck = as.integer(d$block),
  cov_gender = ifelse(d$sex_r == 1, "female", ifelse(d$sex_r == 0, "male", NA)),
  cov_age = as.integer(d$age_r), cov_birth_year = as.integer(d$byear_r), cov_education = lab(d$school_r),
  cov_partnered = lab(d$couple))
x[, id := id]
x <- x[!(is.na(rating_total) & is.na(rating_routine) & is.na(rating_nonroutine))]
setorder(x, id, task, profile); fwrite(x, file.path(out, "schulz_2020_housework_sharing.csv"))
cat(nrow(x), uniqueN(x$id), "\n")
