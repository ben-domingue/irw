##Two 2x2 vignette experiments on app popularity and other providers' privacy violations from
##Horne, C., & Przepiorka, W. (2021). Technology use and norm change in online privacy: Experimental evidence from vignette
##studies. Information, Communication & Society, 24(9), 1212-1228. https://doi.org/10.1080/1369118X.2019.1684542
##Replication data: Harvard Dataverse doi:10.7910/DVN/SBYXYT, CC0 1.0. Files read: study1_data.tab (Prolific convenience sample),
##study2_data.tab (YouGov representative sample) with their DDI variable labels; analysis_paper.do as text. The paper's text
##(open-access repository copy) supplies the vignette and question wording.
##Usage: Rscript horne_2021.R <dir holding study1_data.tab and study2_data.tab saved as s1.tab / s2.tab> <output dir>
##
##Both studies: a household energy-app vignette (one per respondent; id = case number re-keyed to 1..n; task = profile = 1):
##  "A company is providing a new app that helps people reduce their household energy consumption and thus save money and help the
##   environment. It is possible that the app could be used by the provider to collect personal information about users.
##   [Most/No] other providers of apps for reducing household energy consumption analyze users' personal information.
##   [Most/No] other providers also sell the information they collect. This particular app is very [popular/unpopular].
##   [Many/Few] people are using it."
##  attr_app_popularity   'very popular; many people are using it' / 'very unpopular; few people are using it'
##  attr_other_providers  'most other providers analyze and sell users' personal information' / 'no other providers analyze or sell
##                        users' personal information' (the authors' 'frequent' vs 'rare' privacy violations by other providers)
##Study 1: trt1 (1 unpopular, 2 popular) and trt2 (1 rare = 'No other', 2 frequent = 'Most other') from the DDI labels; ~100 per cell, N = 403.
##Study 2: trt 1-4 with DDI labels '1 Most other providers; Unpopular app; Few', '2 Most other; Popular; Many', '3 No other apps;
##  Unpopular; Few', '4 No other apps; Popular; Many' (consistent with analysis_paper.do), 300 per cell, N = 1,200.
##The two samples are analysed separately in the paper (one table each, separate populations and fieldings; Study 2 is weighted).
##Outcomes (ratings, 1-10, asked after the vignette in this order, wording from the paper's Table 2):
##  rating_others_approve     aprv: 'How much do you think most people would approve of the app provider analyzing and selling users'
##                            personal information to other companies?' 1 strongly disapprove .. 10 strongly approve
##  rating_provider_will_invade invas: 'If you download the app, how likely is it that this app provider will analyze and sell your
##                            personal information?' 1 very unlikely .. 10 very likely
##  rating_provider_trust     twty: 'How trustworthy do you think the app provider is?' 1 not at all .. 10 very much
##  rating_willing_to_use     wling: 'How willing are you to download and use this app?' 1 not at all .. 10 very
##A missing single outcome stays NA (Study 1: one trust answer; Study 2: one approve and one willingness answer); rows are kept.
##Covariates: Study 1: cov_gender (sex: 0 m, 1 f), cov_age (age; the 228 of one respondent is set NA as in the do file), cov_education
##(educ DDI labels: less than high school, finished high school, some college, finished 4-year college, graduate school), cov_race_white
##(race 1 white, 2 other, DDI). Study 2: cov_gender, cov_age, cov_education (DDI labels: No HS, High school graduate, Some college,
##2-year, 4-year, Post-grad), cov_survey_weight (weight, the YouGov case weight). Dropped: political ideology (the DDI label says
##lib. -> con. but the paper says 1 very conservative .. 5 very liberal: direction ambiguous), marital status, employment, race detail,
##news interest, energy-interest and the Study 2 agreement items (closti, biconf, lppriv), and the YouGov case id (re-keyed).
##Count check: N = 403 and 1,200 as in the paper (about 100 and exactly 300 per cell).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
pop <- c("1" = "very unpopular; few people are using it", "2" = "very popular; many people are using it")
oth <- c("1" = "no other providers analyze or sell users' personal information",
         "2" = "most other providers analyze and sell users' personal information")
mk <- function(k, p, o, extra) {
  d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating_others_approve = as.integer(k$aprv),
    rating_provider_will_invade = as.integer(k$invas), rating_provider_trust = as.integer(k$twty), rating_willing_to_use = as.integer(k$wling),
    attr_app_popularity = unname(pop[as.character(p)]), attr_other_providers = unname(oth[as.character(o)]))
  stopifnot(!anyNA(d$attr_app_popularity), !anyNA(d$attr_other_providers))
  d <- cbind(d, extra)
  d[!(is.na(rating_others_approve) & is.na(rating_provider_will_invade) & is.na(rating_provider_trust) & is.na(rating_willing_to_use))]
}
k1 <- fread(file.path(raw, "s1.tab"), showProgress = FALSE)
age1 <- as.integer(k1$age); age1[age1 == 228L] <- NA
e1 <- data.table(cov_gender = c("male", "female")[k1$sex + 1L], cov_age = age1,
  cov_education = c("less than high school", "finished high school", "some college", "finished 4-year college", "graduate school")[k1$educ],
  cov_race_white = ifelse(k1$race == 1, 1L, ifelse(k1$race == 2, 0L, NA)))
d1 <- mk(k1, k1$trt1, k1$trt2, e1)
k2 <- fread(file.path(raw, "s2.tab"), showProgress = FALSE)
stopifnot(all(k2$trt %in% 1:4))
p2 <- ifelse(k2$trt %in% c(2, 4), 2L, 1L); o2 <- ifelse(k2$trt %in% c(1, 2), 2L, 1L)
e2 <- data.table(cov_gender = c("male", "female")[k2$sex + 1L], cov_age = as.integer(k2$age),
  cov_education = c("No HS", "High school graduate", "Some college", "2-year", "4-year", "Post-grad")[k2$educ],
  cov_survey_weight = k2$weight)
d2 <- mk(k2, p2, o2, e2)
for (x in list(list(d1, "horne_2021_privacy_norms_prolific"), list(d2, "horne_2021_privacy_norms_yougov"))) {
  setorder(x[[1]], id, task, profile); fwrite(x[[1]], file.path(out, paste0(x[[2]], ".csv")))
  cat(x[[2]], nrow(x[[1]]), "rows\n")
}
