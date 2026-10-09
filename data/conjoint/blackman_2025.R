##Local development project conjoint among Tunisian municipal candidates (2018) from
##Blackman, A. D., Sasmaz, A., Singh, R., & Williamson, S. (2025). Anti-Americanism and foreign
##aid preferences among political elites: Evidence from Tunisia. Working paper / journal
##article (Oxford ORA uuid:d775208a-6186-4214-a862-c6e36220290e; journal and DOI not stated).
##Replication data: Harvard Dataverse doi:10.7910/DVN/POIP41, CC0 1.0, no restricted files.
##File read: lecs_conjoint_dev.rds from lecs_usaid_rep_files.zip (codebook LECS_Codebook.pdf,
##README.pdf). Level text and question wording from the paper (ORA PDF, section 4.1, Table 1).
##The zip also re-hosts Arab Barometer waves V and VII (.sav); they are not used.
##Usage: Rscript blackman_2025.R <raw dir> <output dir>   (raw dir = unzipped lecs_usaid_rep_files)
##
##939 candidates in the April-May 2018 municipal elections (Local Election Candidate Survey,
##100 municipalities; tablet, self-administered with enumerators present), the half randomized
##to this experiment (paper: n = 940). Four forced choices (task = dev_contest, recorded) between
##two development projects. Question (paper): "After you are a member of the municipal council,
##you will have the opportunity to vote for or against different project proposals for your
##municipality. Imagine that you are presented with two different development projects for your
##municipality and can only support one of them. Below you are presented with the details of the
##two projects. Which project do you prefer for your municipality?" choice = dev_choice / 100.
##Forced choice, no opt-out; 36 tasks with no answer are omitted.
##Attributes, data label -> paper Table 1 text (stored): co-financing organization (CSO "Local
##civil society organization", World Bank "The World Bank", CPSCL "Caisse des Prets et de
##Soutien des Collectivites Locales (CPSCL)" [accents as in Table 1], GIZ "Germany's development
##agency (GIZ)", USAID "United States Agency for International Development (USAID)"); project
##(7 levels, e.g. "roads in poor neighborhood" -> "Improve local roads in the poorest area of
##town", "jobs for non-graduates" -> "Provide jobs to people who did not attend university");
##support, "This project was proposed by..." (leaders of party/list -> "Members of your party or
##movement", union leaders, business association, youth and activists, community petition ->
##"Over 500 members of the community who signed a petition"); cost, "the municipality will have
##to pay..." ("5,000" -> "5.000 TND" ...). The mapping pairs each data label with the Table 1
##row of the same meaning. Table 1 is the paper's English; the survey language is not stated.
##Randomization: "fully randomized, and all combinations were permitted"; attribute order
##randomized across respondents, not recorded.
##PROFILE IS INFERRED FROM ROW ORDER: the file stacks 8 blocks of 939 rows (contest 1 x2,
##contest 2 x2, ...), each block in the same respondent order, i.e. a reshape of profile-1 and
##profile-2 columns; the first block of a contest is taken as profile 1 (verified: every
##answered task has exactly one chosen profile; which block was shown first is assumed).
##Covariates (codebook): cov_list_class (Independent/Third Party/Ennahdha/Nidaa Tounes as in the
##data), cov_coalition_member, cov_gender (cand_fem 1 = female, 0 = male), cov_age_group,
##cov_employed (0/1), cov_income (codebook text, monthly household income in dinars),
##cov_edu_higher (1 = BA, MA or higher), cov_prev_councilor (mun_coun), cov_prev_admin,
##cov_policy_governor (1 = governors should be able to dissolve councils, 2 = only voters),
##cov_mun_unemployment_rate, cov_mun_urbanization (municipality). Dropped: resp_id (Qualtrics
##response ID, re-keyed), u_id (municipality ID, to limit re-identification of candidates),
##the authors' derived splits (exp_pol, pro_electoral, list_class_2, above_mean_*, *_status) and
##pop_com_per (= urbanization). No survey weight.
##N = 938 with at least one answered task (939 in the file; 940 in the paper). Spot check: OLS AMCE
##of USAID vs local CSO = -0.092 (SE 0.019, clustered by id) and USAID marginal mean 0.43; the paper
##reports "nearly 10 percentage points" and "approximately forty-five percent".
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "lecs_conjoint_dev.rds")))
n <- uniqueN(s$resp_id); stopifnot(n == 939L, nrow(s) == 8L * n)
s[, blk := (.I - 1L) %/% n + 1L]
stopifnot(s[, uniqueN(dev_contest), blk][, all(V1 == 1)], s[, all(dev_contest == (blk + 1L) %/% 2L)],
          s[, identical(resp_id, s[blk == 1]$resp_id), blk][, all(V1)])
s[, profile := 2L - blk %% 2L]
s[, id := match(resp_id, unique(resp_id))]
mp <- function(x, m) { stopifnot(all(x %in% names(m))); unname(m[x]) }
fin <- c(CSO = "Local civil society organization", "World Bank" = "The World Bank",
         CPSCL = "Caisse des Prêts et de Soutien des Collectivités Locales (CPSCL)", GIZ = "Germany’s development agency (GIZ)",
         USAID = "United States Agency for International Development (USAID)")
prj <- c("roads in poor neighborhood" = "Improve local roads in the poorest area of town",
         "roads in city center" = "Improve local roads in the center of town",
         "lighting in city center" = "Improve street lighting in the center of town",
         "lighting in poor neighborhood" = "Improve street lighting in the poorest area of town",
         "jobs for non-graduates" = "Provide jobs to people who did not attend university",
         "jobs for graduates" = "Provide jobs to people who completed university",
         "cultural center" = "Open a new cultural center")
sup <- c("leaders of party/list" = "Members of your party or movement", "union leaders" = "Local union leaders",
         "business association" = "Local business association", "youth and activists" = "Youth and local activists",
         "community petition" = "Over 500 members of the community who signed a petition")
cst <- c("5,000" = "5.000 TND", "10,000" = "10.000 TND", "15,000" = "15.000 TND", "20,000" = "20.000 TND", "25,000" = "25.000 TND")
inc <- c("1" = "Under 500 dinars", "2" = "Between 500 and 1,000 dinars", "3" = "Between 1,000 and 1,500 dinars",
         "4" = "Between 1,500 and 2,000 dinars", "5" = "Between 2,000 and 2,500 dinars", "6" = "More than 2,500 dinars")
stopifnot(all(s$dev_choice %in% c(0, 100, NA)), all(s$cand_fem %in% 0:1), all(s$income %in% c(names(inc), NA)))
d <- s[, .(id, task = as.integer(dev_contest), profile, choice = as.integer(dev_choice / 100),
           attr_cofinancing = mp(dev_finance, fin), attr_project = mp(dev_project, prj), attr_support = mp(dev_endorse, sup),
           attr_cost = mp(dev_cost, cst),
           cov_list_class = list_class, cov_coalition_member = as.character(coalition_mem),
           cov_gender = fifelse(cand_fem == 1, "female", "male"), cov_age_group = as.character(age_group),
           cov_employed = as.integer(employed), cov_income = unname(inc[income]), cov_edu_higher = as.integer(edu_hig),
           cov_prev_councilor = as.integer(mun_coun), cov_prev_admin = as.integer(prev_admin),
           cov_policy_governor = as.integer(policy_governor), cov_mun_unemployment_rate = emp_unemploy_rate,
           cov_mun_urbanization = urbanization)]
d[, answered := !anyNA(choice), .(id, task)]
d <- d[answered == TRUE][, answered := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "blackman_2025_aid_tunisia.csv"))
