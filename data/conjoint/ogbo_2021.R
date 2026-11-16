##Nigerian mobile users' choice between two mobile bundled plans (Internet, voice calls, text, price) or no mobile
##service, from the data set
##Ogbo, E., Brown, T., Gant, J., Davis, A., & Sicker, D. (2019). Data for: The Impact of Access to Over-the-top Services
##on Preferences for Mobile Services: A Conjoint Analysis of Mobile Users in Nigeria [Data set]. Mendeley Data, V1.
##https://doi.org/10.17632/z83t75xm22.1 (CC BY 4.0, Mendeley record licence). Article: Ogbo-Gebhardt, E. et al. (2021).
##The Impact of Over-the-Top Services on Preferences for Mobile Services: A Conjoint Analysis of Users in Nigeria.
##Journal of Information Policy, 11, 403-. https://doi.org/10.5325/jinfopoli.11.2021.0403 (publisher and SSRN copy
##both return 403 here; not read).
##Files read: "tabular data.xlsx" (Sheet1, 16,194 rows = 388 respondents x 7-14 choice sets x 3 alternatives).
##Usage: Rscript ogbo_2021.R <dir holding the xlsx> <output dir>
##
##Design (Mendeley description): CBC, "choose between two different mobile bundled plans or going without mobile
##service under the assumption that their current mobile plan ends the next day"; recruited June-August 2016 in Lagos
##and Delta States, site-based sampling, N = 390 (the file holds 388 respondent ids). Alternatives 1 and 2 are the plans
##(profiles 1 and 2, recorded); alternative 3 has every level 0 and is the no-service option: opt-out, no profile row
##(chosen in some sets; exactly one of the three alternatives chosen in every set, checked). CS is a running set index
##over the file; task = rank of CS within respondent (the deposit does not say CS is display order). version = design
##block 1-10 for 12 sets; the last two sets of every respondent carry version 0 and identical plans for everyone
##(fixed holdout sets; one such set only for 4 respondents): kept, trial_version records the block (0 = fixed set).
##21 respondents have fewer than 14 sets (7-13), as deposited.
##CODED ATTRIBUTES (#3474). No codebook, questionnaire or readable article gives the displayed wording. All four
##attributes keep the deposit's values, named after the deposit's variables:
##  attr_internet_code: the authors' concatenated labels SlowLowAll, SlowModAll, SlowHighAll, ModModOTT, ModHighAll,
##    FastLowOTT, None (by the words, speed Slow/Mod/Fast x data allowance Low/Mod/High x access to All services or OTT
##    only, None = no Internet; seven levels, one label each; displayed wording unknown).
##  attr_calls_code: 0 / 300 / 500 / unlimited (voice calls; unit, presumably minutes, not stated; how 0 was shown unknown).
##  attr_sms_code: 0 / 300 / 500 / unlimited (text messages; how 0 was shown unknown).
##  attr_price_code: 6.3 / 12.7 / 25.3 (price; currency not stated -- the values look like a dollar conversion of
##    naira amounts, which would make them the authors' recode of a one-to-one level; displayed amount unknown).
##Outcome: choice among plan 1, plan 2 and no service; question wording = the Mendeley paraphrase; opt_out = yes.
##Covariates as deposited (constant within respondent, checked): cov_location (Urban/...), cov_age_group (band text),
##cov_gender (male/female as deposited), cov_income (band text), cov_edu (Grad / Non-grad, the authors' coarsening, so
##not the reserved cov_education), cov_ban_ott_policy, cov_internet_use (years of Internet use, band text),
##cov_willing_to_download_ott, cov_view_ott_info (TRUE/FALSE; meaning undocumented -- possibly an information arm),
##cov_arpu (numeric, undocumented), cov_attn_checks (1 or NA, undocumented; not mapped to cov_attention_pass because
##the meaning of NA is not stated). Dropped: the row key column. No exclusions applied.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.xlsx$", full.names = TRUE); stopifnot(length(f) == 1L)
k <- as.data.table(suppressMessages(read_excel(f, sheet = "Sheet1")))
stopifnot(nrow(k) == 16194L, uniqueN(k$individual) == 388L, all(k$alternative %in% c("1", "2", "3")))
stopifnot(all(k$choice %in% c("TRUE", "FALSE")))
k[, ch := as.integer(choice == "TRUE")]
stopifnot(k[, .(n = .N, s = sum(ch)), .(individual, CS)][, all(n == 3L & s == 1L)])
z <- k[alternative == "3"]
stopifnot(all(z$Internet == "0"), all(z$calls == "0"), all(z$sms == "0"), all(z$price == 0))
cv <- c("location", "age", "gender", "income", "edu", "ban_OTT_policy", "internet", "willing_to_download_ott",
        "view_ott_info", "arpu", "attn_checks")
stopifnot(k[, lapply(.SD, uniqueN), individual, .SDcols = cv][, all(as.matrix(.SD) == 1L), .SDcols = cv])
p <- k[alternative %in% c("1", "2")]
p[, task := frank(CS, ties.method = "dense"), individual]
d <- p[, .(id = as.integer(individual), task, profile = as.integer(alternative), choice = ch,
  attr_internet_code = Internet, attr_calls_code = calls, attr_sms_code = sms, attr_price_code = price,
  trial_version = as.integer(version), cov_location = location, cov_age_group = age, cov_gender = gender,
  cov_income = income, cov_edu = edu, cov_ban_ott_policy = ban_OTT_policy, cov_internet_use = internet,
  cov_willing_to_download_ott = willing_to_download_ott, cov_view_ott_info = view_ott_info, cov_arpu = arpu,
  cov_attn_checks = attn_checks)]
stopifnot(all(d$attr_internet_code %in% c("SlowLowAll", "SlowModAll", "SlowHighAll", "ModModOTT", "ModHighAll",
  "FastLowOTT", "None")), all(d$attr_price_code %in% c(6.3, 12.7, 25.3)),
  all(d$attr_calls_code %in% c("0", "300", "500", "unlimited")), all(d$attr_sms_code %in% c("0", "300", "500", "unlimited")),
  all(d$cov_gender %in% c("female", "male", NA)))
# the last two sets of each respondent are the fixed version-0 sets
stopifnot(d[trial_version == 0L, .N, id][, all(N %in% c(2L, 4L))], uniqueN(d[trial_version == 0L]$id) == 388L,
          d[, .(v = trial_version[task == max(task)][1]), id][, all(v == 0L)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ogbo_2021_mobile_plans_ng.csv"))
cat(nrow(d), uniqueN(d$id), d[, sum(choice), .(id, task)][, mean(V1 == 0)], "\n")
