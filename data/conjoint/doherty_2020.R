##Congressional-newsletter vignette experiment on blaming others for legislative inaction (core vignette) from
##Doherty, D., & Harbridge-Yong, L. (2020). The effects of blaming others for legislative inaction on individual and collective
##evaluations. Legislative Studies Quarterly, 45(1). https://doi.org/10.1111/lsq.12252
##Replication data: Harvard Dataverse doi:10.7910/DVN/XHGDPA, CC0 1.0. Files read: core_vignette.dta (Stata original, saved locally as core.dta) and
##core_vignette.do (core.do; text, not run), README.txt. The auxiliary experiments, the newsletter-excerpts experiment, the net-effects
##experiment and the observational newsletter data in the deposit are NOT built here (different designs/files).
##Usage: Rscript doherty_2020.R <dir holding core.dta> <output dir>
##
##1,901 US respondents (online panel; the do-file names the sample "ssi"), one vignette each: a newsletter written by a member of Congress
##describing a bill in one of three policy areas. Attributes (level text = the text stored in the deposit; the party name in the party-blame
##arm is not stored and is written as a placeholder):
##  attr_issue (issuetext, the opening clause): "working families are the backbone of our country" (child care; coded issue_3 in the
##    do-file) / "a healthy public is critical to the future of our country" (opioids) / "our infrastructure is the backbone of our economy".
##  attr_author_chamber: House of Representatives / Senate;   attr_author_party: Democrat / Republican.
##  attr_bill_status (blametreatment): "Fortunately, Congress recently took action to pass this bill." / "Unfortunately this bill looks
##    unlikely to pass."
##  attr_blame (blametreatment2/3 and blametreatmenttarget2): "(not shown)" (no blame sentence: all passed-bill vignettes and the
##    unpassed no-blame ones) / opposing CHAMBER blamed: "[the House | the Senate] simply refuses to move on this important legislation. They are
##    allowing this common sense legislation to languish and die. Put simply, [the House | the Senate] is dooming this important legislation
##    by refusing to act." (the blamed chamber is the one the author is not in, per the target column) / opposing PARTY blamed: the same text
##    with plural verbs ("simply refuse ... are dooming"); the party named is not stored (the target column is empty), so it is written
##    "[the opposing party]" (inferred as the party the author is not in, from the do-file's "Blame Opposing Party").
##Restrictions: a blame sentence only appears when the bill is unlikely to pass (the do-file creates trt_passed, trt_nopass, trt_blame_party,
##trt_blame_chamber as four conditions); the author's chamber and party x issue are otherwise crossed. One vignette with an anomalous
##passed + blame text (1 row) is dropped. Cell sizes are unequal (passed 501, unpassed with no blame 495, chamber blame 443, party blame 460).
##Outcomes (0-100 ratings unless noted; the full wording is truncated in the deposit's variable labels, which start "On this page we would
##like to get your feelings about some political groups ..."):
##  rating_author (legislator who wrote the newsletter), rating_congress, rating_senate, rating_house, rating_democrats, rating_republicans
##  rating_policy_support: "Based on what you read about the bill the legislator described in the newsletter ..." 1-4; the do-file recodes
##  1=4, 2=3, 3=2, 4=1 to make a 0-1 "Policy Support", so 1 = most supportive in the stored coding (higher raw = less support).
##The 0-100 $ allocations to the author / parties (constant-sum "imagine you were given $100") are not in the standard and are dropped.
##Covariates: cov_gender (the do-file's female: 1 = female), cov_age, cov_education_code (1 = no high school ... 6 = post-graduate per the
##do-file), cov_income_code (1 = <$10k ... 14 = $150k+; 15 = refused per the do-file; kept as coded), cov_party_id7 (the authors' scale from
##the four party-ID branch items: row mean, -.5/.5 recoded to 0; -3 strong Democrat ... 3 strong Republican), as text.
##Dropped: race dummies (kept only as authors' recodes), political interest, issue importance items, recall check, the $ allocations.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "core.dta")))
stopifnot(nrow(d) == 1901)
d[, blame := fcase(blametreatment2 == "", "none",
                   blametreatmenttarget2 != "", "chamber", default = "party")]
passed <- grepl("^Fortunately", d$blametreatment)
stopifnot(sum(passed & d$blame != "none") == 1)
d <- d[!(passed & blame != "none")]
d[, attr_blame := fcase(blame == "none", "(not shown)",
  blame == "chamber", paste0(blametreatmenttarget2, " simply refuses to move on this important legislation. They are allowing this common sense legislation to languish and die. Put simply, ", blametreatmenttarget2, " is dooming this important legislation by refusing to act."),
  default = "[the opposing party] simply refuse to move on this important legislation. They are allowing this common sense legislation to languish and die. Put simply, [the opposing party] are dooming this important legislation by refusing to act.")]
d[, pid := rowMeans(cbind(wouldyoucallyourselfastrongdemoc, wouldyoucallyourselfastrongrepub, doyouthinkofyourselfasclosertoth, ifyouhadtochoosewhichpartywouldy), na.rm = TRUE)]
d[pid > -.5 & pid < .5, pid := 0]; d[is.nan(pid), pid := NA]
stopifnot(all(d$pid[!is.na(d$pid)] %in% -3:3))
pidtxt <- c("Strong Democrat", "Not very strong Democrat", "Closer to the Democratic party", "Independent", "Closer to the Republican party", "Not very strong Republican", "Strong Republican")
r <- d[, .(id = .I, task = 1L, profile = 1L,
  rating_author = as.integer(Thelegislatorwhowrotethenewslett), rating_congress = as.integer(CongressOnthispagewewouldliketog),
  rating_senate = as.integer(TheUSSenateOnthispagewewouldlike), rating_house = as.integer(TheHouseofRepresentativesOnthisp),
  rating_democrats = as.integer(DemocratsinCongressOnthispagewew), rating_republicans = as.integer(RepublicansinCongressOnthispagew),
  rating_policy_support = as.integer(basedonwhatyoureadaboutthebillth),
  attr_issue = issuetext, attr_author_chamber = authorchamber, attr_author_party = authorparty,
  attr_bill_status = blametreatment, attr_blame,
  cov_gender = c("male", "female")[as.integer(whatisyourgender) + 1L], cov_age = as.integer(age),
  cov_education_code = as.integer(whatisthehighestlevelofeducation), cov_income_code = as.integer(whatwasyourtotalfamilyincomein20),
  cov_party_id7 = pidtxt[pid + 4L])]
oc <- grep("^rating_", names(r), value = TRUE)
r <- r[rowSums(!is.na(r[, ..oc])) > 0]
stopifnot(all(unlist(r[, .(rating_author, rating_congress, rating_senate, rating_house, rating_democrats, rating_republicans)]) %in% c(0:100, NA)),
          all(r$rating_policy_support %in% c(1:4, NA)), !anyNA(r[, .(attr_issue, attr_author_chamber, attr_author_party, attr_bill_status)]))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "doherty_2020_blame_inaction.csv"))
