##Refugee-policy package conjoint (Germany) from
##Hillenbrand, T. (2025). Reforms welcome? Evidence on the nature of asylum backlash and orderly
##admissions as a remedy (UNU-MERIT Working Paper 2025-026). https://doi.org/10.53330/PZPD3802
##(Chapter 4 of Hillenbrand's doctoral thesis, Maastricht University, 2026.)
##Replication data: DataverseNL doi:10.34894/YDL4EZ ("Replication Data for Chapter 4"), CC0 1.0, no
##restricted files. File read: "Doctoral Thesis Ch 4_Conjoint Experiment Data Set_Hillenbrand, T.dta".
##Read as text, not run: the chapter's .R and .do replication code and the deposit's explanations
##.txt. Level text, question wording and design from the working paper (Table 3, Figure 1 notes,
##questionnaire Appendix E, English translation; read as PDF from unu-merit.nl).
##Usage: Rscript hillenbrand_2025.R <raw dir> <output dir>
##
##2,211 German adults (TGM online panel, 4-17 Dec 2024, quotas on gender, age, state), as in the paper.
##Each made 7 comparisons of two refugee-policy packages (task_profile "1A".."7B": task and profile
##RECORDED; A = profile 1), 4 attributes: admission policies (4 levels), selection criteria,
##partner-country cooperation, welfare access (3 each), "randomly combined", all combinations allowed
##("no restrictions had to be imposed", WP p. 11). Attribute order randomized per respondent and kept
##constant across that respondent's tasks (WP fn 26); recorded as AttributeOrder, the display sequence
##of attribute numbers 1 admission, 2 selection, 3 cooperation, 4 welfare (author's code L397-405,
##position = which(element == k)) -> attrpos_*.
##Outcomes (questionnaire, English translation of the German survey):
##  choice: "If you had to choose a policy mix for Germany, which of the two options would you
##          prefer?" Forced (exactly one chosen per task, checked), no opt-out.
##  rating: "And how would you rate the two options?" 1 (very negative) - 7 (very positive), raw.
##Attribute text: the deposit holds the author's short codes; each is replaced by the English level
##text of WP Table 3 (a translation; respondents saw German): AccessProtection Restrictive / Regularized
##(the paper's "Orderly") / StatusQuo / Liberal, SelectionCrit Econ&Sec&Hum / Sec&Hum / HumOnly,
##Cooperation None / HumRights / HumRights&Legal, Welfare LimAll / Conditional / FullAll. The match is
##fixed by the author's own recode in the .R file (codes -> Table 3 short labels).
##Priming experiment before the conjoint: each respondent was assigned one of three primes for the
##reform description (Orderliness / National interest / Humanitarian): trial_prime (constant within
##respondent). cov_attention_pass = Attention (1 = understood the proposal's core idea; the paper's
##main results use only those, ~66%). All respondents are kept.
##Covariates as deposited (the deposit holds only the author's recodes): cov_gender_code (the
##author's Female dummy: 1 female, 0 not female; whether 0 also holds non-binary answers is not
##documented, so it is not mapped to cov_gender), cov_age (years),
##cov_state (Bundesland, value-label text), cov_east, cov_university_educ, cov_unemployed,
##cov_migration_background (0/1 as stored), cov_income (subjective income, value-label text),
##cov_party_preference (value-label text, German, includes "Ich würde nicht wählen."; not reserved
##cov_party_id because it reads as vote intention). Dropped: AfD dummy (derived from Party), the
##three prime dummies (folded into trial_prime). No survey weight in the deposit.
##Spot check (choice ~ 4 attributes, attention passers, printed below; baseline status quo): Orderly
##+0.128, Restrictive +0.086, Liberal +0.042: the paper's ordering (STC options above status quo and
##liberal, Orderly most popular; WP p. 18). The figure's numbers were not read off.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(haven::read_dta(file.path(raw, "Doctoral Thesis Ch 4_Conjoint Experiment Data Set_Hillenbrand, T.dta")))
stopifnot(nrow(x) == 30954, uniqueN(x$ID) == 2211, all(grepl("^[1-7][AB]$", x$task_profile)))
lv <- function(v, map) { r <- unname(map[v]); stopifnot(!anyNA(r)); r }
d <- x[, .(id = as.integer(ID), task = as.integer(substr(task_profile, 1, 1)),
           profile = match(substr(task_profile, 2, 2), c("A", "B")),
           choice = as.integer(Choice), rating = as.integer(Eval),
           attr_admission = lv(AccessProtection, c(
             Restrictive = "Direct transfer of asylum seekers who entered irregularly to a third country. No expansion of resettlement.",
             Regularized = "Direct transfer of asylum seekers who entered irregularly to a third country. Resettlement is expanded.",
             StatusQuo = "Asylum seekers who entered irregularly can apply for asylum in Germany. No expansion of resettlement.",
             Liberal = "Asylum seekers who entered irregularly can apply for asylum in Germany. Resettlement is expanded.")),
           attr_selection = lv(SelectionCrit, c(
             `Econ&Sec&Hum` = "Humanitarian aspects, security aspects, and economic capacity are considered.",
             `Sec&Hum` = "Humanitarian aspects and security risks are considered.",
             HumOnly = "Only humanitarian aspects are considered.")),
           attr_cooperation = lv(Cooperation, c(
             None = "No requirements for non-EU countries.",
             HumRights = "Transfer only to non-EU countries that respect human rights.",
             `HumRights&Legal` = "Transfer only to non-EU countries that respect human rights. Strengthening of legal immigration pathways from the non-EU country (e.g., work visas).")),
           attr_welfare = lv(Welfare, c(
             LimAll = "Limited access to social benefits for all persons seeking protection.",
             Conditional = "Limited access for persons seeking protection who entered irregularly. Those who entered legally have full access.",
             FullAll = "Full access to social benefits for all persons seeking protection.")))]
ord <- strsplit(x$AttributeOrder, ",")
stopifnot(all(vapply(ord, function(o) identical(sort(o), as.character(1:4)), TRUE)))
pos <- function(k) vapply(ord, function(o) which(o == k), 1L)
d[, attrpos_admission := pos("1")][, attrpos_selection := pos("2")][, attrpos_cooperation := pos("3")][, attrpos_welfare := pos("4")]
stopifnot(all(x$Orderliness + x$Humanitarian + x$National == 1))
d[, trial_prime := fifelse(x$Orderliness == 1, "Orderliness", fifelse(x$National == 1, "National interest", "Humanitarian"))]
d[, `:=`(cov_attention_pass = as.integer(x$Attention), cov_gender_code = as.integer(x$Female), cov_age = as.integer(x$Age),
         cov_state = as.character(haven::as_factor(x$State)), cov_east = as.integer(x$East),
         cov_university_educ = as.integer(x$UniversityEduc), cov_unemployed = as.integer(x$Unemployed),
         cov_migration_background = as.integer(x$MigBackground), cov_income = as.character(haven::as_factor(x$Income)),
         cov_party_preference = as.character(haven::as_factor(x$Party)))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d$rating), d[, uniqueN(trial_prime), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hillenbrand_2025_asylum_reform.csv"))
m <- lm(choice ~ attr_admission + attr_selection + attr_cooperation + attr_welfare, data = d[cov_attention_pass == 1])
print(coef(m)[2:4])
