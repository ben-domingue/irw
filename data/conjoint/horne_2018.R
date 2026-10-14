##Bridewealth norm-conditionality vignettes (Ghana) from
##Horne, C., Dodoo, N. D., & Dodoo, F. N.-A. (2018). The conditionality of norms: The case of bridewealth. Social Psychology Quarterly,
##81(4), 319-339. https://doi.org/10.1177/0190272518804532
##Replication data: Harvard Dataverse doi:10.7910/DVN/GELPR5, CC0 1.0. Files read: SPQ Dataset HavardDataverse.tab (saved as data.tab) and
##SPQ Codebook HarvardDataVerse.docx (read as text). The article is not open access and the vignette wording is not deposited.
##Usage: Rscript horne_2018.R <dir holding data.tab> <output dir>
##
##2,400 respondents (versnumber 1-24, about 100 each). Every respondent answered BOTH a "chop money" vignette and an "HIV" vignette about a
##married couple (question blocks 2.x and 3.x of the codebook), with the same bridewealth condition in both. The two vignettes have different
##manipulated facts and different attribute sets, so they are two tables (horne_2018_bridewealth_chop, horne_2018_bridewealth_hiv); id is the
##same respondent number (row number of the file; the file's qid is dropped) in both.
##Conditions come from the AUTHORS' RECODE of versnumber in the codebook, not from the o2-o5 columns: bride = 0 (versions 1-8), 1 (9-16), 2 (17-24)
##= bridewealth none / some / all (matches o5 1/2/3 in 97-98% of rows); manbad = 1 for even versions (the codebook's "chop money" recode
##label: man did not pay chop money; o2 = 1 paid, 0 not paid; versions odd = paid); hiv = 1 for versions 1,2,5,6,9,10,13,14,17,18,21,22
##(man HIV positive; o3 = 1 positive). o2/o3/o5 disagree with the version-based codes in 142/49/27 rows; in the disagreeing rows the ratings
##resemble the version-based group (chop money), so the version codes are used. o4 (man had sex with other women since the marriage, 4% yes) is
##not a balanced condition and is dropped. The versions also split on a further undocumented 2-level bit (versions 1-4, 9-12, 17-20 vs
##5-8, 13-16, 21-24; maybe presentation order); the raw versnumber is kept as trial_version.
##LABELS: paraphrased from the codebook's condition descriptions ("Whether or not the man paid chop money", "Whether the man was HIV positive or
##negative", "Bridewealth status (1=none; 2=some; 3=all)"); the displayed vignette sentences are not available.
##Outcomes (ratings 1-10, wording from the codebook; asked about the woman/man of the vignette, same eight items in each vignette):
##  rating_norm_*      "How right or wrong [the man's family / men in the community / the woman's family / women in the community] will say the woman is"
##                     (1 very wrong .. 10 very right)   v22-v25 (chop), v32-v35 (HIV)
##  rating_metanorm_*  "How much [the man's family / other men in the community / the woman's family / other women in the community] will encourage or
##                     discourage the man from leaving the woman" (1 strongly discourage .. 10 strongly encourage)   v29-v212, v39-v312
##A missing single outcome stays NA; rows with all eight missing are omitted. No opt-out. No covariates (the deposit omits sociodemographics).
##PII FOUND: none (qid, an identifier with site codes, is dropped and re-keyed).
##Count check: 2,400 respondents (about 400 per cell, 6 cells per table).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.tab"), showProgress = FALSE)
stopifnot(nrow(x) == 2400, all(x$versnumber %in% 1:24))
v <- as.integer(x$versnumber)
bride <- c("No bridewealth paid", "Some of the bridewealth paid", "All of the bridewealth paid")[1 + (v > 8) + (v > 16)]
chop <- ifelse(v %% 2 == 1, "Man paid chop money", "Man did not pay chop money")
hiv <- ifelse(v %in% c(1,2,5,6,9,10,13,14,17,18,21,22), "Man is HIV positive", "Man is HIV negative")
items <- c(norm_man_family = 2, norm_men_community = 3, norm_woman_family = 4, norm_women_community = 5,
           metanorm_man_family = 9, metanorm_men_community = 10, metanorm_woman_family = 11, metanorm_women_community = 12)
mk <- function(p, attrname, attr) {
  d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L)
  for (n in names(items)) d[[paste0("rating_", n)]] <- as.integer(x[[sprintf("v%d%d", p, items[[n]])]])
  d[["attr_bridewealth"]] <- bride; d[[attrname]] <- attr; d[["trial_version"]] <- v
  d[rowSums(!is.na(d[, .SD, .SDcols = patterns("^rating")])) > 0]
}
d1 <- mk(2, "attr_chop_money", chop); d2 <- mk(3, "attr_hiv_status", hiv)
for (z in list(list(d1, "horne_2018_bridewealth_chop"), list(d2, "horne_2018_bridewealth_hiv"))) {
  setorder(z[[1]], id, task, profile); fwrite(z[[1]], file.path(out, paste0(z[[2]], ".csv"))); cat(z[[2]], nrow(z[[1]]), "rows\n")
}
