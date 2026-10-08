##Foreign-acquisition vignette conjoints (US and China) from
##Chilton, A. S., Milner, H. V., & Tingley, D. (2020). Reciprocity and public opposition to
##foreign direct investment. British Journal of Political Science, 50(1), 129-153.
##https://doi.org/10.1017/S0007123417000552 (online December 2017)
##Replication data: Harvard Dataverse doi:10.7910/DVN/NN9KZT, CC0 1.0, no restricted files,
##no terms. Files read: USConjoint.RData, ChinaConjoint.RData (one data frame `use` each, loaded
##into their own environments). The authors' conjoint.R and .Rhistory were read as text only.
##Instrument wording: Supplementary Materials (S0007123417000552sup001.docx, Cambridge), Parts
##1 and 3. Not built: the secondary experiment (one manipulated factor) and the mTurk
##follow-up (reciprocityfollowup.dta; separate design), DescriptivesMergedConjointDataUSAChina
##.dta (demographics with no respondent id, cannot be linked).
##Usage: Rscript chilton_2020.R <raw dir> <output dir>
##
##Primary experiment, SSI online panels, February 2015 (supplement Part 1): 2,010 US adults and
##1,659 Chinese adults recruited; each evaluated five vignettes (supplement Part 7), one company
##per screen (single-profile tasks, profile = 1). US vignette (supplement 3.1.3):
##  "Company A is a [Ownership] company based in [Country]. Company A is currently attempting to
##  acquire an American company in an industry that is considered to pose a [National Security]
##  risk to national security. The American company is a [Firm Size]. The American company is in
##  an industry that is experiencing [Economic Distress] than the American economy overall. The
##  country that Company A is based in currently has [Reciprocity] in the same industry. In your
##  opinion, should the United States government prevent the proposed transaction?" Yes / No.
##China vignette (3.2.3, English version given in the supplement; fielded in China, display
##  language presumably Chinese, not in the deposit): "Company A is a [Ownership] company based in
##  a foreign country. The Chinese company is a [Firm Size]. The Chinese company is in an industry
##  that is experiencing [Economic Distress] than the Chinese economy overall. The country that
##  Company A is based in currently has [Reciprocity] in the same industry. In your opinion,
##  should the Chinese government prevent the proposed transaction?" Yes / No. (No country or
##  national-security attribute.)
##Two tables (different attribute sets and countries; the article reports them separately):
##  chilton_2020_fdi_reciprocity_us, chilton_2020_fdi_reciprocity_cn.
##attr_ text: the deposited factor levels, which for the US are the supplement's fill-in text
##  (Distress stored with a trailing "than", which the template also carries; the "than" is
##  stripped). China levels are the authors' shorter English labels as deposited ("no
##  restrictions", "large national company" where the supplement lists "national Fortune 500
##  company"; the Chinese text is not in the deposit).
##choice: 1 = "Yes" (the government should prevent the transaction), 0 = "No" (cj_response /
##  cj_response.n; the authors' plots label it Pr(... should block acquisition)). A single-profile
##  yes/no question: opt_out = yes by the README convention.
##task is INFERRED from row order within respondent (the source has no task column; rows of a
##  respondent are contiguous except one US id). Ids with 10 rows (1 US, 3 China) are dropped as
##  ambiguous (two respondents or a double entry); respondents with fewer than 5 rows are kept
##  (US: six with 4, one with 1; China: one with 2, two with 3, twelve with 4).
##Randomization: no restriction or probabilities stated in the supplement; the authors call
##  amce(..., design = "uniform"). No covariates or weights can be linked (ids are Qualtrics-style
##  response tokens; re-keyed to integers in order of first appearance).
##N: US 2,004 ids in the deposit (2,010 recruited), 2,003 after the drop; China 1,616 ids (1,659
##  recruited), 1,613 after the drop.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(f) { e <- new.env(); load(file.path(raw, f), envir = e); as.data.table(e$use) }
prep <- function(s, y) {
  s[, src := id][, n := .N, src]
  s <- s[n <= 5]
  s[, id := match(src, unique(src))][, task := seq_len(.N), id][, profile := 1L]
  s[, choice := as.integer(get(y))]
  stopifnot(!anyNA(s$choice), all(s$choice %in% 0:1))
  s
}
us <- prep(ld("USConjoint.RData"), "cj_response")
stopifnot(uniqueN(us$id) == 2003)
du <- us[, .(id, task, profile, choice,
             attr_ownership = as.character(Owner), attr_country = as.character(Country),
             attr_national_security = as.character(Natsec), attr_firm_size = as.character(Firmsize),
             attr_economic_distress = sub(" than$", "", as.character(Distress)),
             attr_reciprocity = as.character(Reciprocity))]
stopifnot(!anyNA(du))
setorder(du, id, task, profile)
fwrite(du, file.path(out, "chilton_2020_fdi_reciprocity_us.csv"))
cn <- prep(ld("ChinaConjoint.RData"), "cj_response.n")
stopifnot(uniqueN(cn$id) == 1613)
dc <- cn[, .(id, task, profile, choice,
             attr_ownership = as.character(Ownership), attr_firm_size = as.character(Firmsize),
             attr_economic_distress = as.character(Distress), attr_reciprocity = as.character(Reciprocity))]
stopifnot(!anyNA(dc))
setorder(dc, id, task, profile)
fwrite(dc, file.path(out, "chilton_2020_fdi_reciprocity_cn.csv"))
