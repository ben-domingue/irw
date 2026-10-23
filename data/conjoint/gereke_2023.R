##Trust-game vignette experiment (three national samples) from
##Gereke, J., & Ruedin, D. (2023). Shared nationality in social exchange: A trust vignette
##experiment in the United States, South Africa, and Switzerland. Socius, 9, 1-9.
##https://doi.org/10.1177/23780231231189945
##Replication data: OSF https://osf.io/gptx7/, CC BY 4.0. The OSF licence field was empty
##until the depositor set CC BY 4.0 on 2026-10-23 after an IRW licence ask
##(oneoff/licence-asks-2026-10/outbox/gptx7_ruedin.txt). File read:
##Replication_Data_Socius.dta. ReplicationDoFile_GerekeRuedin.do was read as text (not run)
##for the variable meanings, and the article (open access, CC BY, Mannheim madoc 65270) for
##the design.
##Usage: Rscript gereke_2023.R <raw dir> <output dir>
##
##3,173 respondents in online Qualtrics-panel surveys of the United States (1,355 rows;
##November 2017), South Africa (1,382; July 2017) and Switzerland (436; December 2016). The
##article reports 1,332 / 1,378 / 436 analysed; the deposit holds 27 more rows (US +23,
##SA +4), not reconciled.
##
##TWO TABLES, because each respondent saw two vignettes with two DIFFERENT and
##independently randomized interaction partners (article Figure 1, "a between-subject
##design"), so the two decisions are not one task:
##  gereke_2023_trust            vignette 1, the respondent moves first  (3,059 rows)
##  gereke_2023_trustworthiness  vignette 2, the respondent moves second (2,966 rows)
##Each table has one task per respondent (task = 1, profile = 1): a single described alter,
##accepted or refused. id is the same integer in both tables (the row's position among the
##sorted ResponseId values), so the two decisions of one respondent can be joined; the
##Qualtrics ResponseId itself is dropped.
##
##Two attributes, from the authors' own profile_t1 / profile_t2 labels:
##  attr_nationality  citizen / non-citizen  (a conational, or a resident of the same
##                    country holding a foreign nationality)
##  attr_gender       female / male
##The deposit stores only these labels, not the vignette prose respondents read (the full
##instructions are Supplement 6 of the article, which is behind the publisher's paywall),
##so the levels are the deposit's English labels. The vignettes also described the alter's
##city of residence, number of siblings, car colour and hobbies (article, Methods); none of
##that is recorded in the deposit, so those attributes are absent rather than (not shown).
##Gender was manipulated only in the United States and South Africa: every Swiss respondent
##saw a female alter in vignette 1 and a male alter in vignette 2 (article footnote; borne
##out by the data), which is why the pooled gender shares are unequal and why the design
##record carries restrictions = yes.
##ONE TABLE PER VIGNETTE POOLING THE THREE COUNTRIES, with cov_country: the authors analyse
##the three samples together (country x profile interactions in one regression,
##ReplicationDoFile L130-139) and work with the same English labels throughout. The language
##respondents saw is not documented for any of the three fieldings.
##
##Outcomes (binary; the exact question wording is not deposited and the article paraphrases
##it, so design_outcomes carries a paraphrase):
##  gereke_2023_trust            choice = t1, 1 = transferred the 10 hypothetical "Internet
##                               dollars" to the other person, 0 = kept it
##  gereke_2023_trustworthiness  choice = t2, 1 = transferred 22 "Internet dollars" back to
##                               the first player, 0 = kept 40
##Both are a single-profile accept/refuse, so opt_out = yes. Respondents with no decision
##are dropped (114 on vignette 1, 207 on vignette 2).
##
##Covariates. Shared: cov_country; cov_gender (sex); cov_age_group (the four bands as text);
##cov_education_years (RR_edu_1, years of education attained, 0-18); cov_employment
##(RR_work); cov_risk_general and cov_risk_strangers (0-4 sliders, "prepared to take risks"
##in general / in trusting strangers); cov_jobs_immigrants (0-4 slider, "When jobs are
##scarce, employers should give priority to [nationals]", the item naming the respondent's
##own country). Per table: the trust table carries cov_comprehension_1 to _4, the four
##true/false comprehension items asked after vignette 1; the trustworthiness table carries
##cov_check_female, cov_check_national and cov_check_same_person, the three manipulation
##checks, which the do-file scores against profile_t2 (L553-574) and which therefore belong
##to vignette 2. "Don't know" is kept as answer text.
##Dropped: man_check_sex, man_check_age, man_check_citizen and man_check_siblings (asked in
##Switzerland only; their stored values mix answer labels with bare numbers -- citizen holds
##4, 5 and "Don't know", siblings holds "Yes", "No", 0, 4 and "Don't know" -- and no
##codebook maps them, so they are not interpretable), the authors' derived t1/t2 dummies'
##source variables being the same columns, and country_id (a duplicate of country).
##No survey weight: the samples were built with soft quotas (article) and the deposit has no
##weight variable.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Replication_Data_Socius.dta")))
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[y == ""] <- NA; y }
cc <- c(USA = "United States", `South Africa` = "South Africa", Switzerland = "Switzerland")
stopifnot(all(k$country %in% names(cc)), !anyDuplicated(k$ResponseId))

## one row per respondent, columns shared by both tables
base <- data.table(
  id = match(k$ResponseId, sort(unique(k$ResponseId))),
  task = 1L, profile = 1L,
  cov_country = cc[k$country],
  cov_gender = lab(k$sex),
  cov_age_group = sub(" to ", "-", sub(" \\+", "+", lab(k$age_group))),
  cov_education_years = as.numeric(k$RR_edu_1),
  cov_employment = lab(k$RR_work),
  cov_risk_general = as.numeric(k$RR_risk_general_1),
  cov_risk_strangers = as.numeric(k$RR_risk_strangers_1),
  cov_jobs_immigrants = as.numeric(k$RR_jobs_immigrants_1))
stopifnot(all(base$cov_gender %in% c("female", "male", NA)),
          all(base$cov_age_group %in% c("0-24", "25-39", "40-64", "65+", NA)),
          base[, all(cov_education_years %in% c(0:18, NA))],
          base[, all(cov_risk_general >= 0 & cov_risk_general <= 4, na.rm = TRUE)])

## "citizen female" etc -> the two manipulated attributes
split_profile <- function(x) {
  p <- lab(x); stopifnot(all(p %in% c("citizen female", "non-citizen female",
                                      "citizen male", "non-citizen male", NA)))
  list(attr_nationality = sub(" (female|male)$", "", p),
       attr_gender = sub("^(non-)?citizen ", "", p))
}

make <- function(profile_col, outcome_col, extra) {
  d <- copy(base)
  d[, c("attr_nationality", "attr_gender") := split_profile(k[[profile_col]])]
  d[, choice := as.integer(k[[outcome_col]])]
  for (nm in names(extra)) d[, (nm) := lab(k[[extra[[nm]]]])]
  stopifnot(all(d$choice %in% c(0L, 1L, NA)))
  d <- d[!is.na(choice) & !is.na(attr_nationality)]
  stopifnot(nrow(d) > 100, d[, .N, .(id, task)][, all(N == 1)],
            !anyNA(d$attr_nationality), !anyNA(d$attr_gender))
  setcolorder(d, c("id", "task", "profile", "choice", "attr_nationality", "attr_gender"))
  setorder(d, id)
  d
}

t1 <- make("profile_t1", "t1", setNames(paste0("comprehension_", 1:4),
                                        paste0("cov_comprehension_", 1:4)))
t2 <- make("profile_t2", "t2", c(cov_check_female = "man_check_1",
                                 cov_check_national = "man_check_2",
                                 cov_check_same_person = "man_check_3"))
## Switzerland showed one gender per vignette; the US and South Africa crossed both
stopifnot(t1[cov_country == "Switzerland", all(attr_gender == "female")],
          t2[cov_country == "Switzerland", all(attr_gender == "male")],
          t1[cov_country != "Switzerland", uniqueN(attr_gender) == 2L])
fwrite(t1, file.path(out, "gereke_2023_trust.csv"))
fwrite(t2, file.path(out, "gereke_2023_trustworthiness.csv"))
