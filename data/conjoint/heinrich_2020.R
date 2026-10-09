##Foreign-aid-package conjoint (US, MTurk, August 2014) from
##Heinrich, T., & Kobayashi, Y. (2020). How do people evaluate foreign aid to "nasty"
##regimes? British Journal of Political Science, 50(1), 103-127.
##https://doi.org/10.1017/S0007123417000503
##Replication data: Harvard Dataverse doi:10.7910/DVN/TKTN5J, CC0 1.0, no restricted files.
##Files read: "Data Export 2014_08_21.csv" (one row per respondent, ';'-separated) and
##conjoint_export_mapping.txt (the authors' codebook: level text of every attribute and the
##covariate codes). Read as text only: "1_Prep the data.R", "x_Auxiliary Functions.R"
##(format_raw_data: A = left/profile 1, B = right/profile 2, rounds 1-4 = tasks),
##"4_Exp Regressions.R", "0_Run It All.R"; Screenshot-1.png (the article's Figure 1: the task
##screen) and "NastyAid Appendix.pdf".
##Usage: Rscript heinrich_2020.R <dir holding the two files> <output dir>
##
##2,219 rows in the export; the 2 rows with ZIP 99999 are the authors' own test responses
##(dropped, as in their prep code), leaving 2,217 respondents x 4 tasks x 2 aid packages.
##The authors further drop respondents with >= 4 screener failures and a conjoint-page time
##outside 40-800 s (prep code; 124 surveys by their comment). Those respondents are KEPT here;
##cov_screener_failures (SCREENER_FAILURES_Q3) and cov_duration_sec (Q5_TIME, seconds on the
##conjoint page) reproduce the filter.
##Outcome (screenshot): "Please express your support for each aid package by checking the
##buttons." 9 radio buttons per package, labelled Oppose (1) / Indifferent (5) / Support (9);
##rating = Q5_<A|B>_<task>, 1-9, higher = more support, as stored. No choice question.
##Attributes (codebook text; screenshot for the fixed parts):
##  attr_benefits: every package showed "Various trade benefits and access to raw materials.";
##    BENEFIT 1-4 adds a second bullet (codebook text), 0 adds none. Stored as the bullets
##    joined with " ".
##  attr_costs: COSTS 25/50/75 displayed "<n> million U.S. dollars per year." (screenshot).
##  attr_issue: POTISSUE 0 "None" (displayed, screenshot) or one of the five codebook texts.
##  attr_remedy_amount, attr_remedy_target: remedial aid. Codebook: amount is 0 when the issue
##    is None or the Olympics placebo, else drawn from 0/1/2/5/10/15/20/25; target drawn from
##    U.S. aid agency / respected non-governmental organization / respected international
##    organization. The DISPLAYED WORDING of the remedy is not deposited: amounts are stored as
##    the codebook number in millions of U.S. dollars per year (unit: the authors' code adds it
##    to the costs, TC = C + RA, "Remedy (in $10m)" in the appendix), e.g. "10 million U.S.
##    dollars per year"; the target as codebook text. When the amount is 0 both are
##    "(not shown)" (INFERRED: the screenshot shows the placebo issue with no remedy line, and
##    the authors' code sets the target to 0 whenever the amount is 0).
##Restrictions: yes (remedy amount is 0 unless the issue is one of the four nasty-regime
##issues; codebook). Levels drawn with rand(): uniform. Attribute order fixed (screenshot).
##Covariates: cov_birth_year (BIRTHYR), cov_gender (GENDER 1 male, 2 female: the authors' CCES
##recode in "1_Prep the data.R" codes Female = 2, else 1), cov_state, cov_education (Q2_2,
##codebook text), cov_faminc (Q2_3, codes as stored; codebook bands, with 9 = $80-89k and
##the overlapping top codes 16/18/31), cov_party_id7 (Q3_1, codebook text), cov_cc415r (Q3_2,
##0-100, -1 = don't know; codebook gives no wording), cov_employ (Q6_1 codes: codebook
##1 full-time, 2 part-time, 3 temporarily laid off, 4 unemployed, 5 retired, 7 homemaker,
##8 student; 6 permanently disabled from the CCES recode; 9 unlabelled, "Other employment" in
##appendix Fig A.1), cov_econ_change (Q6_2 codes, codebook 1 gotten much better ... 5 much
##worse), cov_screener_failures, cov_duration_sec. No survey weight (the authors entropy-
##balance to the CCES; that weight is derived and not in the export).
##Dropped: TIMESTAMP, IP address, INPUTZIP (PII), SCREENER_FAILURES_Q2, Q1-Q4/Q6 page times.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Data Export 2014_08_21.csv"), sep = ";", colClasses = list(character = "INPUTZIP"))
x <- x[INPUTZIP != "99999"]
x[, id := .I]
ben <- c("Minor cooperation from recipient government on counter-terrorism.",
         "Extensive cooperation from recipient on counter-terrorism.",
         "Minor cooperation from recipient government on anti-money laundering.",
         "Extensive cooperation from recipient on anti-money laundering.")
iss <- c("None",
         "At last Summer Olympic Games, athletes from recipient staged upsets against U.S. athletes.",
         "Recipient politicians frequently embezzle money from development aid.",
         "Recipient government systematically manipulates elections in its favor.",
         "Recipient government widely imprisons and tortures members of an ethnic minority.",
         "Recipient government suppresses peaceful protests, independent newspapers, and access to social media.")
tgt <- c("U.S. aid agency", "respected non-governmental organization", "respected international organization")
base <- "Various trade benefits and access to raw materials."
d <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  s <- c("A", "B")[p]; g <- function(v) x[[sprintf("Q5_%s%s_%d", s, v, t)]]
  data.table(id = x$id, task = t, profile = p, rating = as.integer(g("")),
             b = g("_BENEFIT"), c = g("_COSTS"), pi = g("_POTISSUE"), ra = g("_POTISSUEREMEDYAMOUNT"), rt = g("_POTISSUEREMEDYTARGET"))
}))))
stopifnot(all(d$b %in% 0:4), all(d$c %in% c(25, 50, 75)), all(d$pi %in% 0:5), all(d$ra %in% c(0, 1, 2, 5, 10, 15, 20, 25)),
          all(d$rt %in% 0:2), all(d$rating %in% 1:9), all(d[pi <= 1, ra] == 0))
d[, attr_benefits := ifelse(b == 0, base, paste(base, ben[pmax(b, 1)]))]
d[, attr_costs := paste(c, "million U.S. dollars per year.")]
d[, attr_issue := iss[pi + 1]]
d[, attr_remedy_amount := ifelse(ra == 0, "(not shown)", paste(ra, "million U.S. dollars per year"))]
d[, attr_remedy_target := ifelse(ra == 0, "(not shown)", tgt[rt + 1])]
d[, c("b", "c", "pi", "ra", "rt") := NULL]
edu <- c("Less than High School", "High School", "Some College", "2-year College Degree (Associates)",
         "4-year College Degree (BA, BS)", "Post graduate")
pid <- c("Strong Democrat", "Not very strong Democrat", "Lean Democrat", "Independent", "Lean Republican",
         "Not very strong Republican", "Strong Republican")
stopifnot(all(x$GENDER %in% 1:2), all(x$Q2_2 %in% 1:6), all(x$Q3_1 %in% 1:7))
cv <- x[, .(id, cov_birth_year = as.integer(BIRTHYR), cov_gender = c("male", "female")[GENDER], cov_state = STATE,
            cov_education = edu[Q2_2], cov_faminc = as.integer(Q2_3), cov_party_id7 = pid[Q3_1], cov_cc415r = as.integer(Q3_2),
            cov_employ = as.integer(Q6_1), cov_econ_change = as.integer(Q6_2),
            cov_screener_failures = as.integer(SCREENER_FAILURES_Q3), cov_duration_sec = as.numeric(Q5_TIME))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "heinrich_2020_nasty_aid.csv"))
