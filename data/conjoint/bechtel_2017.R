##Eurozone bailout conjoint (Germany, January 2012) from
##Bechtel, M. M., Hainmueller, J., & Margalit, Y. (2017). Policy design and domestic support for
##international bailouts. European Journal of Political Research, 56(4), 864-886.
##https://doi.org/10.1111/1475-6765.12210
##Replication data: Harvard Dataverse doi:10.7910/DVN/PMPSWJ, CC0 1.0, no restricted files.
##File read: Repdata_EJPR.dta (Dataverse "original format" download of Repdata_EJPR.tab). Read as
##text only: "01 Repcode_EJPR.do", "02 Repcode_EJPR_figs.R"; the article PDF deposited as
##"Bechtel et al 207 Bailout conjoint.pdf" (Table 1, Figure 1, question wording p. 872).
##Usage: Rscript bechtel_2017.R <dir holding Repdata_EJPR.dta> <output dir>
##
##4,655 German adults eligible to vote (online survey, January 2012; matches the article). Each
##respondent saw up to 4 comparisons (task = conjointno) of two bailout proposals (Scenario 1 =
##profile 1, Scenario 2 = profile 2), on separate screens; 4,541 did all 4, 114 fewer (rows absent in
##the source). 6 attributes, "completely independent randomisation" within and across comparisons
##(article p. 872); attribute row order randomized across respondents, not recorded in the data.
##Outcomes:
##  rating = `rating`: "If you could vote over each proposal in a direct-democratic vote, how likely
##           would you vote against or in favour of each proposal? Please provide your answer on the
##           following scale ranging from 'vote definitely against' to 'vote definitely in favour'."
##           (article p. 872, English rendering). Stored as in the source, 0-6: 0 = vote definitely
##           against .. 6 = vote definitely in favour (the article describes it as 1-7; the authors'
##           do file recodes 0-2 = vote against, 3 = neither, 4-6 = in favour).
##  choice = `chosen` (`binary` = number of the chosen scenario): a forced choice between the two
##           proposals reported in the Online Appendix (Figure A.3, "Forced Choice"); exactly one
##           chosen per comparison. Its wording is in the Online Appendix, not deposited.
##The authors' main analyses keep comparisons whose rating and choice agree (their cleanmarker);
##all comparisons are kept here.
##Attributes (displayed in German; the German screen text is not deposited; English text follows
##the article's Figure 1 example and Table 1; source value labels/values in brackets):
##  attr_contribution "Germany's contribution to the bailout": "123 bn €" / "189 bn €" / "211 bn €" /
##    "418 bn €" (FeatGercontrib; the article text once says €198bn, Table 1 and data say 189)
##  attr_share "Germany's share of the bailout": 19% / 21% / 27% / 53% (FeatGershare)
##  attr_haircut "Haircut for private investors": 10% / 20% / 50% / 75% (FeatHaircut)
##  attr_conditions "Conditions for receiving country": "5% / 15% / 35% cut in public expenditures"
##    (labels "5per spending cut" ...) and "5% / 15% / 35% cuts of public sector jobs" ("5 per public
##    jobs cut" ...) - one attribute with 6 levels (FeatConditions)
##  attr_endorser "Bailout endorsed by": Government / Opposition / German Central Bank (label
##    "Bundesbank") / European Central Bank ("EZB") / Council of Economic Advisors / International
##    Monetary Fund ("IMF") (FeatEndors; Table 1 and Figure 1 wording)
##  attr_country "Receiving country": Greece / Ireland ("Irland") / Italy / Spain (FeatTargetCountry)
##Covariates (value labels in the .dta): cov_age (xxage, years); cov_gender_code (xxfemale, 0/1, codes
##kept: the variable name suggests 1 = female but no label or code documents it); cov_education (xxeduc label text: HS degree low tier / med tier /
##highest tier / technical college/university degree); cov_hh_income_code (xxhhinc 1 = <500 EUR ..
##10 = >4.5k EUR, 99 = don't know); cov_left_right (xxrightideology, 0 left .. 10 right);
##cov_vote_intention (from the xxvotecj_* indicators: CDU/CSU, SPD, Green, FDP, Linke, other,
##RepsNPD, do not vote, don't know); cov_bailout_support_code (xxopposebailouts 1 Strongly in
##favor .. 5 Strongly against, 99 don't know); cov_eu_good (xxEUgood 1 very bad thing .. 5 very good
##thing). No survey weight in the deposit.
##Dropped: ResponseID (Qualtrics; re-keyed in source order), click timers, free-text NGO name
##(xxaltru_whichngo), the other attitude, altruism and knowledge items, contestid.
##Spot check (all comparisons, not only the authors' consistent ones): share of ratings 0-2 ("vote
##against") 0.52 (article baseline 0.53); OLS of vote-against on the attributes: EUR 418bn vs 123bn
##+0.15, 53% vs 19% share +0.10 (article: about +30% and +22% of the 0.53 baseline, i.e. ~0.16, ~0.12).
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Repdata_EJPR.dta"))
stopifnot(identical(names(attr(k$FeatTargetCountry, "labels")), c("Greece", "Irland", "Italy", "Spain")),
          identical(names(attr(k$FeatConditions, "labels")), c("5per spending cut", "15per spending cut", "35per spending cut",
                                                               "5 per public jobs cut", "15 per public jobs cut", "35 per public jobs cut")),
          identical(names(attr(k$FeatEndors, "labels")), c("Government", "Bundesbank", "EZB", "Opposition", "Council of Economic Advisors", "IMF")))
z <- function(x) as.integer(zap_labels(x))
lab <- function(x) { l <- attr(x, "labels"); unname(setNames(names(l), l)[as.character(zap_labels(x))]) }
d <- data.table(rid = k$ResponseID, task = z(k$conjointno), profile = z(k$scenario),
                choice = z(k$chosen), rating = z(k$rating),
                attr_contribution = paste(z(k$FeatGercontrib), "bn €"),
                attr_share = paste0(z(k$FeatGershare), "%"),
                attr_haircut = paste0(z(k$FeatHaircut), "%"),
                attr_conditions = c("5% cut in public expenditures", "15% cut in public expenditures", "35% cut in public expenditures",
                                    "5% cuts of public sector jobs", "15% cuts of public sector jobs", "35% cuts of public sector jobs")[z(k$FeatConditions)],
                attr_endorser = c("Government", "German Central Bank", "European Central Bank", "Opposition",
                                  "Council of Economic Advisors", "International Monetary Fund")[z(k$FeatEndors)],
                attr_country = c("Greece", "Ireland", "Italy", "Spain")[z(k$FeatTargetCountry)])
stopifnot(!anyNA(d), all(d$rating %in% 0:6), d[, sum(choice), .(rid, task)][, all(V1 == 1)],
          all((z(k$binary) == d$profile) == (d$choice == 1)), !anyDuplicated(d[, .(rid, task, profile)]))
vt <- c(CDUCSU = "CDU/CSU", SPD = "SPD", Green = "Green", FDP = "FDP", Linke = "Linke", other = "other",
        RepsNPD = "RepsNPD", donotvote = "do not vote", dontknow = "don't know")
vm <- sapply(names(vt), function(v) z(k[[paste0("xxvotecj_", v)]]))
stopifnot(all(rowSums(vm) <= 1))
d[, `:=`(cov_age = z(k$xxage), cov_gender_code = z(k$xxfemale), cov_education = lab(k$xxeduc),
         cov_hh_income_code = z(k$xxhhinc), cov_left_right = z(k$xxrightideology),
         cov_vote_intention = ifelse(rowSums(vm) == 1, vt[max.col(vm)], NA_character_),
         cov_bailout_support_code = z(k$xxopposebailouts), cov_eu_good = z(k$xxEUgood))]
d[, id := match(rid, unique(rid))][, rid := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bechtel_2017_bailouts.csv"))
