##Photo-rights contract conjoint (UK and US) from
##Kantorowicz, J., Kantorowicz-Reznichenko, E., & Nahmias, Y. (2025). The price of creativity:
##A conjoint experiment in copyrights. Journal of Public Policy, 45(2), 245-269.
##https://doi.org/10.1017/S0143814X25000042
##Replication data: Harvard Dataverse doi:10.7910/DVN/BIBHUW, CC0 1.0, no restricted files.
##Files read: data_uk_population.RDS, data_uk_professionals.RDS, data_us_professionals.RDS.
##Design from the article (CC BY): pp. 257-259, Table 1 and Figure 1 (a choice screen). The
##supplementary survey instructions were not obtained.
##Usage: Rscript kantorowicz_2025.R <raw dir> <output dir>
##
##Dynata respondents imagined they had taken a landscape photo (and described it; that free
##text is not deposited) and that a guidebook publisher wanted to buy rights in it. Six times
##they chose between Contract A and Contract B (forced choice; the exact question wording is in
##the unobtained supplement, so it is paraphrased). Five attributes, each 2 levels, as in the
##Figure 1 table (row label -> attr_):
##  "Price" -> attr_price "25 GBP"/"50 GBP" (US sample "25 USD"/"50 USD");
##  "You give us the right to use your photo without mentioning your name" -> attr_no_attribution;
##  "You give us the right to issue copies and/or communicate the photo to the public" -> attr_issue_copies;
##  "You give us the right to reproduce your photo in any medium" -> attr_reproduce;
##  "You give us the right to create a different work based on or derived from your photo" -> attr_derivative;
##  rights levels Yes/No. Levels "randomly set" each task (independence/uniformity not stated
##  beyond that; all 32 contracts occur). Attribute row order was randomized per respondent and
##  held constant across that respondent's tasks; the rowpos columns are not deposited.
##THREE TABLES, one per sample, as the authors analyse and report them separately (and the
##price text differs by currency): kantorowicz_2025_copyright_uk_public (UK general
##population, N = 718), kantorowicz_2025_copyright_uk_pros (UK creative-sector
##professionals, N = 268), kantorowicz_2025_copyright_us_pros (US professionals, N = 278).
##Deposited files are the authors' analysis samples (attention check passed, photo described,
##all six choices made); the Ns match the article exactly.
##Task and profile are INFERRED from row order. Each file is a cjoint-style reshape (attribute
##"reshapeLong": timevar "profile", varying <attr>_1/<attr>_2): rows 1..n/2 are profile 1 and
##rows n/2+1..n profile 2 (verified: the same respondent sits in row i and row i+n/2 and exactly
##one of the two is selected, in every row of all three files). Each half is 6 consecutive
##blocks of all respondents in the same respondent order (verified); block k is taken as task k.
##The order in which tasks were shown is therefore an assumption.
##Covariates: cov_gender (1 = male, 2 = female per the authors' code; other codes undocumented),
##cov_age (years). Dropped: education (codes 1-5 with no labels; the authors group 2-4 as higher
##educated), Response.ID (panel response id; respondents re-keyed to integers in file order).
##No survey weight is deposited.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
files <- c(uk_public = "data_uk_population.RDS", uk_pros = "data_uk_professionals.RDS", us_pros = "data_us_professionals.RDS")
nmap <- c(Price = "attr_price",
          You.give.us.the.right.to.use.your.photo.without.mentioning.your.name = "attr_no_attribution",
          `You.give.us.the.right.to.issue.copies.and/or.communicate.the.photo.to.the.public` = "attr_issue_copies",
          You.give.us.the.right.to.reproduce.your.photo.in.any.medium = "attr_reproduce",
          You.give.us.the.right.to.create.a.different.work.based.on.or.derived.from.your.photo = "attr_derivative")
for (s in names(files)) {
  x <- as.data.table(readRDS(file.path(raw, files[[s]])))
  n <- nrow(x); h <- n / 2; r <- uniqueN(x$Response.ID)
  stopifnot(h == 6 * r, x$Response.ID[1:h] == x$Response.ID[(h + 1):n], x$selected[1:h] + x$selected[(h + 1):n] == 1L,
            matrix(x$Response.ID, nrow = r) == x$Response.ID[1:r])
  key <- data.table(Response.ID = x$Response.ID[1:r], id = seq_len(r))
  d <- data.table(Response.ID = x$Response.ID, task = rep(rep(1:6, each = r), 2), profile = rep(1:2, each = h),
                  choice = as.integer(x$selected))
  for (v in names(nmap)) d[, (nmap[[v]]) := as.character(x[[v]])]
  d[, `:=`(cov_gender = as.integer(x$gender), cov_age = as.integer(x$age))]
  d <- merge(key, d, by = "Response.ID")[, Response.ID := NULL]
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
  setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("kantorowicz_2025_copyright_", s, ".csv")))
}
