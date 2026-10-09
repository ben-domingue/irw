##Climate-policy-package conjoint with the proposing body as an attribute (Germany, USA) from
##Fesenfeld, L. P., Freudlsperger, C., Kuntze, L., & Ingold, K. "Legitimizing climate action in
##democracies" (article not located; no article DOI in the deposit).
##Replication data: Harvard Dataverse doi:10.7910/DVN/WQW6EK (published 2023-11-24), CC0 1.0, no
##restricted files, no terms. Files read: df_joint.RData (object df_joint) and
##Descriptives_Germany_final.xlsx (sheet "Question Codes Socio-demo.", for the German covariate
##codes). Read as text, not run: Script_Fesenfeld_etal.R. Design facts from the deposited
##Appendix_Fesenfeld_Freudlsperger_Kuntze_Ingold-2.pdf (App. A sample tables, App. B example task).
##Usage: Rscript fesenfeld_2023.R <raw dir> <output dir>
##
##Germany fielded August 2020 (624 conjoint respondents, App. Table 1), USA December 2020
##(N = 1,360, App. Table 2): matched here exactly. Each respondent compared two policy packages
##("Policy Package A/B" = profile 1/2) in four rounds (task = round), 6 attributes, all shown.
##TWO TABLES, one per country (fesenfeld_2023_climate_legit_de / _us): every model in the authors'
##script is estimated on subset(df_joint, country == ...), nothing is pooled, and the two
##samples were fielded separately. Respondent ids restart at 1 in each country.
##Outcomes:
##  choice = choice_cor (1 = the package chosen; source `choice` names "Package A/B" (DE) or
##           1/2 (US), checked equal). App. B (US instrument): "Which policy package do you
##           prefer?", Package A / Package B, with "If you don't really support either of the
##           two policy packages, please choose the one that you oppose less" -> no opt-out.
##           Exactly one chosen per kept task (checked). German wording not deposited.
##  rating = rate, 1-7, one per package. Its wording and anchors are not in the deposit (the
##           appendix shows only the choice question); stored raw.
##Attributes (row labels of App. B, level text exactly as in df_joint, which matches the text
##in the App. B screenshot): support ("Governmental support"), investments ("Public
##investments"), standards ("Standards for producers"), tax ("CO2 tax"), restrictions
##("Restrictions"), proposer ("Package proposed by": Federal government / Expert commission /
##Climate citizens assembly). The stored text is English for both countries; German screens
##are not deposited.
##Restrictions attribute: "No restrictions" has share ~1/3 and each of the four car/meat
##restrictions ~1/6, so levels were evidently not equally likely (level_weights = observed; no
##source gives the design). No randomization rule is documented. App. B shows one attribute
##order; whether it was randomized is not stated.
##Dropped: 93 US tasks that have only one package row in the source (no partner profile; 30
##of them with no choice), as incomplete tasks; this removes 10 US respondents entirely (US table:
##1,350 of 1,360); the authors' derived columns (...1 row number,
##choice_f, package_f, Left_Right_Median_split, Left_Right_Center, Education_Median_Split).
##Covariates:
##  DE: cov_gender (Gender: 1 maennlich = male, 2 weiblich = female), cov_age_group (Age, band
##      text "18 bis 29 Jahre" .. "70 Jahre oder aelter"), cov_education (Education: Kein
##      Abschluss / Haupt-/ Volksschulabschluss .. (Fach-) Hochschulabschluss). Mapping from the
##      deposit's Descriptives_Germany_final.xlsx codebook (screeners S1, S2, S4). That workbook
##      belongs to the separate descriptive survey (n = 628), but the conjoint codes reproduce
##      App. Table 1's conjoint column (50/50 gender; age bands 21/15/18/21/18/7 %), checked below.
##  US: no codebook. cov_gender_code (0, 1, 98, 99 as in source; App. Table 2: 50 % male, 49.5 %
##      female, 0.5 % other), cov_age (years, as in source), cov_education_code (1-5).
##  Both: cov_left_right (Left_Right 1-10; DE codebook Q9: 1 = Links/left, 10 = Rechts/right;
##      the US scale is undocumented).
##No survey weight in the deposit.
##Spot check: US difference in marginal means, Expert commission - Federal government, for
##"Moderate Support" (App. Table 3: 0.07) and DE (App. Table 4: 0.10), computed below.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "df_joint.RData"), envir = e)
s <- as.data.table(e$df_joint)
stopifnot(nrow(s) == 15469, s[country == "USA", uniqueN(id)] == 1360, s[country == "Germany", uniqueN(id)] == 624)
s[, task := as.integer(sub("round", "", round))]
s[, profile := match(package, c("A", "B"))]
s[, picked := fifelse(choice %in% c("1", "Package A"), 1L, 2L)]
stopifnot(all(s$choice %in% c("1", "2", "Package A", "Package B")), all((s$picked == s$profile) == (s$choice_cor == 1)),
          s[, .N, .(country, id, task, profile)][, all(N == 1)], !anyNA(s$rate))
s[, nt := .N, .(country, id, task)]
stopifnot(s[nt == 1, .N] == 93, s[nt == 1, all(country == "USA")])
s <- s[nt == 2]
stopifnot(s[, sum(choice_cor), .(country, id, task)][, all(V1 == 1)])
# German covariate codebook
cb <- as.data.frame(read_excel(file.path(raw, "Descriptives_Germany_final.xlsx"), sheet = "Question Codes Socio-demo.",
                               col_names = FALSE, .name_repair = "minimal"))
lab <- function(rows) setNames(as.character(cb[rows, 3]), as.character(cb[rows, 2]))
age_lab <- lab(8:14); edu_lab <- lab(37:40); sex_lab <- lab(3:4)
stopifnot(unname(sex_lab) == c("männlich", "weiblich"), age_lab[["2"]] == "18 bis 29 Jahre", length(edu_lab) == 4)
mk <- function(x) {
  d <- x[, .(id = as.integer(id), task, profile, choice = as.integer(choice_cor), rating = as.integer(rate),
             attr_support = as.character(Support), attr_investments = as.character(Investments),
             attr_standards = as.character(Standards), attr_tax = as.character(Tax),
             attr_restrictions = as.character(Restrictions), attr_proposer = as.character(Governance))]
  d
}
de <- mk(s[country == "Germany"]); sd <- s[country == "Germany"]
stopifnot(all(sd$Gender %in% 1:2), all(sd$Age %in% 2:7), all(sd$Education %in% 1:4))
de[, cov_gender := c("male", "female")[sd$Gender]]
de[, cov_age_group := unname(age_lab[as.character(sd$Age)])]
de[, cov_education := unname(edu_lab[as.character(sd$Education)])]
de[, cov_left_right := as.integer(sd$Left_Right)]
us <- mk(s[country == "USA"]); su <- s[country == "USA"]
us[, cov_gender_code := as.integer(su$Gender)]
us[, cov_age := as.integer(su$Age)]
us[, cov_education_code := as.integer(su$Education)]
us[, cov_left_right := as.integer(su$Left_Right)]
# checks vs the appendix
p <- unique(de[, .(id, cov_age_group, cov_gender)])
stopifnot(nrow(p) == 624,
          max(abs(as.numeric(prop.table(table(factor(p$cov_age_group, levels = age_lab[2:7])))) -
                  c(.21, .15, .18, .21, .18, .07))) < .006,
          abs(mean(p$cov_gender == "male") - .5) < .01)
mmd <- function(d) d[attr_proposer == "Expert commission", mean(choice[attr_support %like% "^Support"])] -
  d[attr_proposer == "Federal government", mean(choice[attr_support %like% "^Support"])]
cat("US respondents kept:", uniqueN(us$id), "\n")
cat(sprintf("diff MM Moderate Support (Expert - Federal): US %.3f (paper 0.07), DE %.3f (paper 0.10)\n", mmd(us), mmd(de)))
setorder(de, id, task, profile); setorder(us, id, task, profile)
fwrite(de, file.path(out, "fesenfeld_2023_climate_legit_de.csv"))
fwrite(us, file.path(out, "fesenfeld_2023_climate_legit_us.csv"))
