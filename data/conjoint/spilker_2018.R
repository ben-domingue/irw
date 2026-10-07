##Trade-agreement (PTA) conjoints in Costa Rica, Nicaragua and Vietnam from
##Spilker, G., Bernauer, T., & Umana, V. (2018). What kinds of trade liberalization agreements
##do people in developing countries want? International Interactions, 44(3), 510-536.
##https://doi.org/10.1080/03050629.2018.1436316
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z4GACS, CC0 1.0, no restricted files.
##Files read: CR_agree_final.dta, NI_agree_final.dta, VI_agree_final.dta. The deposit has no
##questionnaire; outcome wording and the displayed level text are from the article (Table 1,
##Table 2 = example Vietnam choice task in English, and the "Empirical study design" section).
##Usage: Rscript spilker_2018.R <raw dir> <output dir>
##
##Face-to-face national samples aged 18-64, Dec 2013 - Feb 2014: Costa Rica 821 (paper 820),
##Nicaragua 800, Vietnam 700 (Hanoi and Ho Chi Minh City areas). Each respondent saw 5 tasks
##of 2 hypothetical trade agreements ("PTA 1", "PTA 2" side by side) with 11 attributes.
##THREE TABLES, one per country: the article analyses each country separately (Figures
##2.1-2.3), the samples were fielded separately in Spanish / Vietnamese, and the membership
##attribute has different levels per country (Russia only in Vietnam; Venezuela plus the
##neighbour, Nicaragua or Costa Rica, only in the two Central American surveys).
##Outcomes (same in all three):
##  choice = agree, "Which agreement would you prefer?" Forced choice, no opt-out.
##  rating = like, "how much they like each of the two agreements", 7-point, 1 = would
##           "never support" such an agreement .. 7 = "always support" (higher = more
##           favourable). The source's 0-1 rescaled like2 is dropped.
##Task and profile come from ROW ORDER: each file is stacked in 10 blocks of one row per
##respondent (block k = the k-th profile shown); blocks 2t-1 and 2t are task t, profile 1 and 2.
##Verified: in every such pair of an intact task exactly one profile is chosen.
##DEPOSIT DEFECTS, the affected task dropped (both profiles):
##  Costa Rica and Nicaragua, task 4: block 7's agree, like and like2 are an exact copy of
##    block 1's for every respondent (its attributes differ), so the task-4 outcomes are not
##    the answers given; 4 tasks remain per respondent. The authors' models include these rows.
##  Vietnam, task 5: in block 10 every row has one attribute missing and the attribute dummies
##    disagree with the categorical codes (some groups sum to 2), so the profile shown is not
##    recoverable; 4 tasks remain per respondent.
##In the intact rows the categorical attribute codes agree 100% with the authors' dummies.
##Level text (English rendering from the article's Table 2; respondents saw Spanish or
##Vietnamese): countries 2/5/10/50/150 ("Numbers of countries involved"); membership ("The
##agreement also includes") European Union/Brazil/China/India/Russia/United States/Venezuela/
##Nicaragua/Costa Rica; prices ("Prices of the goods you buy will"), employment in agriculture /
##manufacturing / services ("Employment in the ... sector will"), environmental and labour
##protection standards ("... standards will"): increase / stay the same / decrease; high /
##medium / low skilled foreign citizens allowed to work in the country: yes / no. Source codes:
##env/work/job_* 1 = reduce/less, 2 = maintain/no effect, 3 = increase/more; price 1 =
##increase, 2 = no effect, 3 = reduce (from the dummies priceinc/pricenoeff/pricered);
##*_skills 1 = no, 2 = yes. Attribute row order was fixed (not randomized) as far as the
##article says; no randomization restrictions are reported.
##Covariates: cov_female (Costa Rica, Nicaragua: sexo 2 = female); cov_education (codes as
##labelled in the .dta. Costa Rica/Nicaragua 0 none, 1 primary, 2 secondary, 3 vocational,
##4 college, 5 university, 6 postgraduate, one Costa Rican coded 7 (unlabelled) set missing; Vietnam 1 none, 2 primary, 3 secondary, 4 high
##school, 5 vocational, 6 college or university, 7 postgraduate); cov_age (Vietnam only, years).
##Dropped: sector of employment, p7_1, p7_7 and Vietnam's gender and person (no labels deposited),
##the source respondent id (re-keyed from the running number), all attribute dummies, like2.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- function(x, l) { stopifnot(all(x %in% seq_along(l))); l[x] }
build <- function(file, origins, drop_task, tab) {
  s <- as.data.table(zap_labels(read_dta(file.path(raw, file))))
  n <- uniqueN(s$respondent)
  stopifnot(nrow(s) == 10 * n, all(s$respondent == rep(seq_len(n), 10)))
  s[, blk := rep(1:10, each = n)][, task := (blk + 1L) %/% 2L][, profile := 2L - blk %% 2L]
  stopifnot(s[task != drop_task, sum(agree), .(respondent, task)][, all(V1 == 1)])
  s <- s[task != drop_task]
  s[task > drop_task, task := task - 1L]
  d <- s[, .(id = as.integer(respondent), task = as.integer(task), profile = as.integer(profile),
             choice = as.integer(agree), rating = as.integer(like),
             attr_countries = lv(count, c("2", "5", "10", "50", "150")),
             attr_membership = lv(origin, origins),
             attr_prices = lv(price, c("increase", "stay the same", "decrease")),
             attr_employment_agriculture = lv(job_ag, c("decrease", "stay the same", "increase")),
             attr_employment_manufacturing = lv(job_man, c("decrease", "stay the same", "increase")),
             attr_employment_services = lv(job_ser, c("decrease", "stay the same", "increase")),
             attr_environmental_standards = lv(env, c("decrease", "stay the same", "increase")),
             attr_labor_standards = lv(work, c("decrease", "stay the same", "increase")),
             attr_work_permits_high_skill = lv(job_high_skills, c("no", "yes")),
             attr_work_permits_medium_skill = lv(job_med_skills, c("no", "yes")),
             attr_work_permits_low_skill = lv(job_low_skills, c("no", "yes")))]
  # the categorical codes agree with the authors' dummies
  stopifnot(s[, all((env == 1) == (env_prot_red == 1) & (env == 3) == (env_prot_inc == 1) & (work == 1) == (work_prot_red == 1) &
                    (work == 3) == (work_prot_inc == 1) & (price == 1) == (priceinc == 1) & (price == 3) == (pricered == 1) &
                    (job_ag == 3) == (job_ag_more == 1) & (job_man == 1) == (job_man_less == 1) & (job_ser == 2) == (job_ser_same == 1) &
                    (job_high_skills == 2) == (high_skills_yes == 1) & (job_low_skills == 2) == (low_skill_yes == 1) &
                    (count == 5) == (count_150 == 1) & (origin == 6) == (US == 1))])
  if ("sexo" %in% names(s)) d[, cov_female := as.integer(s$sexo == 2)]
  d[, cov_education := as.integer(s$education)]
  if ("sexo" %in% names(s)) d[!cov_education %in% 0:6, cov_education := NA_integer_]  # one Costa Rican coded 7, unlabelled
  if ("age" %in% names(s)) d[, cov_age := as.integer(s$age)]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
build("CR_agree_final.dta", c("European Union", "India", "Nicaragua", "Brazil", "China", "United States", "Venezuela"), 4L,
      "spilker_2018_trade_costa_rica")
build("NI_agree_final.dta", c("European Union", "India", "Costa Rica", "Brazil", "China", "United States", "Venezuela"), 4L,
      "spilker_2018_trade_nicaragua")
build("VI_agree_final.dta", c("European Union", "China", "Brazil", "India", "Russia", "United States"), 5L,
      "spilker_2018_trade_vietnam")
