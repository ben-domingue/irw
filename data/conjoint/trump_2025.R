##"Tax the rich" factorial vignette experiments (US pilot, US Study 2, Denmark Study 3) from
##Trump, K.-S. (2025). When is it fair to tax the rich? The importance of pro-social behavior.
##Comparative Political Studies, 58(11), 2401-2435 (online 2024). https://doi.org/10.1177/00104140241302716
##Replication data: Harvard Dataverse doi:10.7910/DVN/FHU7ET, CC0 1.0, no restricted files.
##Files read: "Pilot experiment data.tab" (original csv, saved as pilot.csv), "Study 2 data.tab" (original
##csv = raw Qualtrics export with question-text and ImportId rows, saved as s2.csv), "Study 3 data.tab"
##(original Stata file, saved as s3.dta), the three codebooks (.docx: pilot_codebook, s2_codebook,
##s3_codebook) and "Study 3 - Danish translation.docx", ReadMe.rtf. "Tax the rich appendix.Rmd" and
##"Tax the rich manuscript.Rmd" read as text, not run. Study 1 is open-ended (not an experiment): not built.
##Usage: Rscript trump_2025.R <raw dir> <output dir>
##
##THREE TABLES (separate samples, fieldings and attribute sets; the article reports them separately):
##  trump_2025_tax_rich_pilot  Prolific US convenience sample, July 2020 (Appendix A2), 599 respondents.
##  trump_2025_tax_rich_us     Lucid US quota sample (Study 2), 2,040 respondents who passed the two
##                             screeners and rated at least one vignette (the authors keep the 1,825 who
##                             finished AND have a Lucid income profile: cov_authors_sample = 1).
##  trump_2025_tax_rich_dk     YouGov Denmark (Study 3), 1,234 respondents who passed the screeners
##                             (status Complete; one skipped the first vignette). Survey weight kept.
##Design (all three): three vignettes per respondent, one profile each (task = 1-3 in order shown),
##describing a rich person; every slot randomized independently per vignette (codebooks: "The
##randomizations are independent"; gender drawn once per vignette and used for all pronouns).
##US Study 2 template (s2 codebook): "Imagine a person who has a household income of {income}. {He/She}
##comes from {family background} from {his/her} parents. In the workplace, {he/she} is {work ethic}. At
##the same time, {he/she} has a reputation for {treat workers}. When it comes to paying taxes, {loophole
##clause}. Outside of work, {he/she} {charity}. At the same time {he/she} has {consumption}."
##The pilot template differs: income = "{dollar}, which puts them in the top earning {percentile} of
##American households" (dollar and percentile drawn together: $150,000/20%, $250,000/10%, $500,000/1%),
##"Most of {his/her} income comes from {wealth source}" (3 levels) instead of family background, and
##"{He/She} employs an accountant who does {his/her} tax returns. {He/She} tells the accountant {loophole}."
##Attribute text = the slot text as displayed (data fields; pilot dollar amounts trimmed of a trailing
##space). attr_gender = the pronoun ("he"/"she"). US loophole clause = the four displayed loophole fields
##joined with the pronouns, exactly as the template prints them (so its text differs by gender).
##Denmark: the data hold codes; level text = the .dta value labels / codebook's English master text
##(Variation1 = code 1, Variation2 = code 2; loophole codes 1/3 = uses, 2/4 = does not, by gender; the
##authors' Rmd recodes agree). Respondents saw the DANISH text (Danish translation docx); English
##stored because the Danish file leaves a placeholder ("til [himself/herself]") unresolved. The DK
##consumption level is stored as the codebook prints it, "the habit of buying expensive and flashy
##things for himself/herself" with the pronoun matched to the gender.
##Outcome (all): rating = "What, in your opinion, would be fair when it comes to income taxes for people
##like {him/her}? Do you think their income taxes should be:" 1 Reduced a lot, 2 Reduced a little,
##3 Stay the same (DK: Kept the same), 4 Increased a little, 5 Increased a lot. Unanswered vignettes omitted.
##Covariates. Pilot and US, from the codebooks: cov_gender (1 Male, 2 Female, 3 Non-binary/other ->
##male/female/other), cov_birth_year (typed, kept 1900-2005), cov_education (educ text), cov_party_id
##(partisan: Democrat / Republican / Independent), cov_party_strength (dem_lean/rep_lean text: Strong /
##Not very strong ...), cov_party_lean (indep_lean text), cov_hh_income (hh_inc bracket text),
##cov_redistribute / cov_tax_high_incomes / cov_cut_welfare_spending (agree items as answer text; the
##pilot codes them 1 = strongly agree, Study 2 5 = strongly agree: mapped per codebook), cov_getahead
##and cov_luck_hw (answer text). US only: cov_age (Lucid profile age), cov_finished (Qualtrics Finished),
##cov_attention_pass (redistr_agree_3 "Please just choose 'somewhat agree'" answered somewhat agree),
##cov_authors_sample. DK: cov_survey_weight (weight), cov_gender (gender_rc), cov_age_group
##(profile_age2 band text), cov_education (profile_education label text; 9 Do not wish to say -> NA),
##cov_region, cov_hh_income (label text; Prefer not to say -> NA), cov_left_right (political_viewpoint
##label text), cov_born_dk (q11 Yes/No; Prefer not to say -> NA), cov_attention_pass (q5_3 == 2).
##Dropped: open-ended answers (open, q4, att_1, race_6_TEXT), timings, Lucid profile codes other than
##age, race/state/marital codes, racial resentment and migration items. resp_id / caseid are the
##authors' anonymised integers (Lucid/Prolific ids already replaced by the author), re-keyed in order.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rating_ok <- function(x) { x <- suppressWarnings(as.integer(x)); stopifnot(x %in% c(1:5, NA)); x }
map <- function(x, labs) { x <- as.character(x); r <- unname(labs[x]); stopifnot(!anyNA(r[!is.na(x) & x != ""])); r }
yr <- function(x) { x <- suppressWarnings(as.integer(x)); ifelse(!is.na(x) & x >= 1900 & x <= 2005, x, NA_integer_) }
inc <- c("1" = "Less than $10,000", "2" = "$10,000 - $19,999", "3" = "$20,000 - $29,999", "4" = "$30,000 - $39,999",
         "5" = "$40,000 - $49,999", "6" = "$50,000 - $59,999", "7" = "$60,000 - $69,999", "8" = "$70,000 - $79,999",
         "9" = "$80,000 - $89,999", "10" = "$90,000 - $99,000", "11" = "$100,000 - $149,999", "12" = "More than $150,000")
usc <- function(r) data.table(
  cov_gender = map(r$gender, c("1" = "male", "2" = "female", "3" = "other")),
  cov_birth_year = yr(r$year_born),
  cov_education = map(r$educ, c("1" = "Less than high school", "2" = "High school or equivalent", "3" = "Some college",
                                "4" = "College degree", "5" = "Post-graduate degree")),
  cov_party_id = map(r$partisan, c("1" = "Democrat", "2" = "Republican", "3" = "Independent")),
  cov_party_strength = fifelse(r$partisan %in% c(1, "1"), map(r$dem_lean, c("1" = "Strong Democrat", "2" = "Not Very Strong Democrat")),
                       fifelse(r$partisan %in% c(2, "2"), map(r$rep_lean, c("1" = "Strong Republican", "2" = "Not Very Strong Republican")), NA_character_)),
  cov_party_lean = map(r$indep_lean, c("1" = "Closer to Republican Party", "2" = "Closer to Democratic", "3" = "Neither")),
  cov_hh_income = map(r$hh_inc, inc),
  cov_getahead = NA_character_, cov_luck_hw = map(r$luck_hw, c("1" = "Hard work", "2" = "Both equally", "3" = "Luck or help")))
fix_blank <- function(d) { for (v in names(d)) if (is.character(d[[v]])) set(d, which(d[[v]] == ""), v, NA); d }

## ---------- pilot
p <- fread(file.path(raw, "pilot.csv"), encoding = "UTF-8")
stopifnot(nrow(p) == 599L)
p[, id := .I]
L <- lapply(1:3, function(t) {
  g <- function(v) trimws(as.character(p[[paste0("vig", t, "_", v)]]))
  data.table(id = p$id, task = t, profile = 1L, rating = rating_ok(p[[paste0("vig", t, "_tax")]]),
             attr_gender = g("genderv"),
             attr_income = paste0(g("income_dollar"), ", which puts them in the top earning ", g("income_percentile"), " of American households"),
             attr_wealth_source = g("wealth_source"), attr_hard_work = g("hard_work"), attr_treat_workers = g("treat_workers"),
             attr_loopholes = g("loopholes"), attr_charity = g("charity"), attr_consumption = g("consumption"))
})
dp <- rbindlist(L)[!is.na(rating)]
stopifnot(!anyNA(dp), dp[, all(attr_gender %in% c("he", "she"))])
agree_p <- c("1" = "Strongly agree", "2" = "Somewhat agree", "3" = "Neither agree nor disagree", "4" = "Somewhat disagree", "5" = "Strongly disagree")
cp <- cbind(data.table(id = p$id), usc(p))
cp[, `:=`(cov_redistribute = map(p$redistr_agree, agree_p), cov_tax_high_incomes = map(p$tax_highinc_agree, agree_p),
          cov_cut_welfare_spending = map(p$decr_spend_agree, agree_p),
          cov_getahead = map(p$getahead, c("1" = "A great deal", "2" = "A lot", "3" = "A moderate amount", "4" = "A little", "5" = "None at all")))]
dp <- fix_blank(merge(dp, cp, by = "id"))
setorder(dp, id, task, profile)
fwrite(dp, file.path(out, "trump_2025_tax_rich_pilot.csv"))

## ---------- US Study 2
s <- fread(file.path(raw, "s2.csv"), colClasses = "character", encoding = "UTF-8")[-(1:2)]
s <- s[Q_TerminateFlag != "Screened"]
s[, id := .I]
L <- lapply(1:3, function(t) {
  g <- function(v) trimws(s[[paste0(v, "_", t)]])
  reg <- g("gender_reg"); obj <- g("gender_obj")
  loop <- trimws(gsub(" +", " ", paste(g("loopholes0"), reg, g("loopholes1"), obj, g("loopholes2"), reg, g("loopholes3"))))
  data.table(id = s$id, task = t, profile = 1L, rating = rating_ok(s[[paste0("vig", t, "_tax")]]),
             attr_gender = reg, attr_income = g("income"), attr_family_background = g("family_bgr"), attr_hard_work = g("hard_work"),
             attr_treat_workers = g("treat_workers"), attr_loopholes = loop, attr_charity = g("charity"), attr_consumption = g("consumption"))
})
du <- rbindlist(L)[!is.na(rating)]
stopifnot(du[, all(attr_gender %in% c("he", "she"))], !du[, anyNA(.SD) | any(.SD == ""), .SDcols = patterns("^attr_")],
          uniqueN(du$attr_loopholes) == 4L)
agree_u <- c("5" = "Strongly agree", "4" = "Somewhat agree", "3" = "Neither agree nor disagree", "2" = "Somewhat disagree", "1" = "Strongly disagree")
cu <- cbind(data.table(id = s$id), usc(s))
cu[, `:=`(cov_redistribute = map(s$redistr_agree_1, agree_u), cov_tax_high_incomes = map(s$redistr_agree_2, agree_u),
          cov_cut_welfare_spending = map(s$redistr_agree_4, agree_u),
          cov_attention_pass = fifelse(s$redistr_agree_3 == "", NA_integer_, as.integer(s$redistr_agree_3 == "4")),
          cov_getahead = map(s$getahead, c("5" = "A great deal", "4" = "A lot", "3" = "A moderate amount", "2" = "A little", "1" = "None at all")),
          cov_age = suppressWarnings(as.integer(s$age_lucid)), cov_finished = as.integer(s$Finished),
          cov_authors_sample = as.integer(s$Finished == "1" & s$hhi_lucid != ""))]
du <- fix_blank(merge(du, cu, by = "id"))
stopifnot(uniqueN(du$id) == 2040L, du[cov_authors_sample == 1, uniqueN(id)] == 1825L)
du[, id := match(id, sort(unique(id)))]
setorder(du, id, task, profile)
fwrite(du, file.path(out, "trump_2025_tax_rich_us.csv"))

## ---------- Denmark Study 3
k <- read_dta(file.path(raw, "s3.dta"))
k <- k[zap_labels(k$status) == 1, ]
k$id <- seq_len(nrow(k))
z <- function(v) as.integer(zap_labels(k[[v]]))
L <- lapply(1:3, function(t) {
  sfx <- paste0("_scr", t)
  gen <- z(paste0("q_gender", sfx)); stopifnot(gen %in% 1:2)
  lp <- z(paste0("q_useloopholes", sfx)); stopifnot(lp %in% 1:4, (lp %in% 1:2) == (gen == 1))
  lpt <- c("he employs an accountant who helps him make the most use of tax loopholes, so that he pays the smallest amount of taxes legally possible",
           "even though he could employ an accountant to help him make use of tax loopholes and pay less taxes, he chooses not to do this and just pays the tax rates as they are",
           "she employs an accountant who helps her make the most use of tax loopholes, so that she pays the smallest amount of taxes legally possible",
           "even though she could employ an accountant to help her make use of tax loopholes and pay less taxes, she chooses not to do this and just pays the tax rates as they are")
  cons <- z(paste0("q_conspconsump", sfx)); stopifnot(cons %in% 1:2)
  two <- function(v, l1, l2) { x <- z(paste0(v, sfx)); stopifnot(x %in% 1:2); c(l1, l2)[x] }
  data.table(id = k$id, task = t, profile = 1L, rating = rating_ok(z(paste0("q3", letters[t]))),
             attr_gender = c("He", "She")[gen],
             attr_income = two("q_income", "50,000 kroner gross per month, which is more than what 9 out of 10 Danes earn",
                               "130,000 kroner gross per month, which is more than what 99 out of 100 Danes earn"),
             attr_family_background = two("q_famback", "a modest family background and did not inherit money",
                                          "a well-off family, and inherited a large amount of money"),
             attr_hard_work = two("q_workethic", "known as someone who works hard and always puts in the effort",
                                  "not known as someone who works hard, but rather has a tendency to slack off"),
             attr_treat_workers = two("q_treatworkers", "treating workers fairly and paying them a good wage",
                                      "treating workers unfairly and paying them very low wages"),
             attr_loopholes = lpt[lp],
             attr_charity = two("q_charitgiving", "regularly gives money to different charities", "does not give money to charities"),
             attr_consumption = ifelse(cons == 1, "modest habits and does not often buy expensive and flashy things",
                                       paste0("the habit of buying expensive and flashy things for ", c("himself", "herself")[gen])))
})
dk <- rbindlist(L)[!is.na(rating)]
stopifnot(!anyNA(dk))
lab <- function(v, drop = character()) { x <- as.character(as_factor(k[[v]], levels = "labels")); x[x %in% drop] <- NA; x }
ck <- data.table(id = k$id, cov_survey_weight = as.numeric(k$weight),
                 cov_gender = map(z("gender_rc"), c("1" = "female", "2" = "male")),
                 cov_age_group = lab("profile_age2"), cov_education = lab("profile_education", "Do not wish to say"),
                 cov_region = lab("region"), cov_hh_income = lab("household_income", "Prefer not to say"),
                 cov_left_right = lab("political_viewpoint"), cov_born_dk = lab("q11", "Prefer not to say"),
                 cov_attention_pass = as.integer(z("q5_3") == 2))
dk <- merge(dk, ck, by = "id")
stopifnot(uniqueN(dk$id) == 1234L)
dk[, id := match(id, sort(unique(id)))]
setorder(dk, id, task, profile)
fwrite(dk, file.path(out, "trump_2025_tax_rich_dk.csv"))
