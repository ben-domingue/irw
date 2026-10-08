##Pandemic and democracy conjoint (Myanmar) from
##Mon, S. O., & Yamada, K. (2024). Do pandemics reduce support for democracy? A survey
##experiment in Myanmar. Japanese Journal of Political Science, 25(3), 140-161.
##https://doi.org/10.1017/S1468109924000069
##Replication data: Harvard Dataverse doi:10.7910/DVN/YUZSDO, CC0 1.0, no restricted files.
##File read: Conjoint.dta (Dataverse "original format"; Stata variable labels used).
##Codebook: Variables.xlsx (sheet "Conjoint"); Conjoint.do read as text, not run.
##Usage: Rscript mon_2024.R <dir holding Conjoint.dta> <output dir>
##
##756 respondents in Myanmar (June 2022, per the abstract), 5 pairs of hypothetical 2023
##scenarios; task = QES, profile = ALT (both recorded). 4 attributes, stored in the source only
##as 0/1 dummies (A<attribute>L<level>), rebuilt here as level text:
##  attr_covid_situation: Good / Not so good / Bad (A1L1-A1L3; codebook "good / not so good /
##    bad COVID-19 situation");
##  attr_vaccine: "Pfizer/Moderna" (base, the label of A2L2/A2L3 "base: Pfize/Moderna"; exact
##    displayed text not deposited) / "Chinese vaccines are available, but not Pfizer or
##    Moderna" (A2L2) / "Difficult to get vaccines" (A2L3);
##  attr_government: "Election restored" (A3L1) / "Election is not restored yet" (A3L2);
##  attr_medical_services: "You can easily visit a clinic" (base) / "You can visit a clinic only
##    in emergency" (A4L2).
##LABEL CONFLICT, resolved: Variables.xlsx calls A3 medical services and A4 government, but the
##Stata variable labels say A3L1 = "Election restored", A3L2 = "Election not restored", A4L2 =
##"Medical service only in emergency"; the authors' .do interacts A3L1 with the COVID levels
##and plots it by COVID condition (the paper's question), and the abstract reports democracy
##preferred "by a wide margin" (A3L1 profiles are chosen 81% vs 19%). The Stata labels are used.
##Level text for the codebook's levels is the codebook's English wording; respondents likely saw
##Burmese (not documented).
##Outcome: choice = Y, "1 if the profile is selected as the preferred alternative" (codebook);
##question wording not deposited. Forced choice: exactly one chosen in every pair.
##Randomization: not documented. The table shows a fixed design rather than independent
##draws: the vaccine base level appears in 2,727 of 7,560 profiles (36%) against about 2,415
##for each other level, and attributes are associated (election restored co-occurs with "easily
##visit a clinic" in 2,113 profiles vs 1,668 with "only in emergency"; with Pfizer/Moderna in
##1,670 vs about 1,055 for each other vaccine level), as in a pre-generated (e.g. efficient)
##choice design. Every pair of levels does occur, so no combination is ruled out (restrictions
##= unknown; the association is in the restrictions note); the unequal vaccine shares make
##level_weights = observed. Estimate effects with all attributes in the model.
##Attribute order and the display format are not documented. No task is repeated (checked).
##No covariates in this file and no survey weight in the deposit (Vignette.dta, a separate
##experiment, has female / age group / education; not linked here). The source ID (9-digit, possibly a panel ID) is re-keyed to 1..756.
##Spot check: lm(choice ~ attributes) as in the .do's Table 5 column 1 gives an election-restored
##effect of +.59; the paper's table was not reachable (abstract: democracy preferred "by a wide
##margin").
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "Conjoint.dta"))))
stopifnot(uniqueN(s$ID) == 756, s[, .N, ID][, all(N == 10)], s[, all(A1L1 + A1L2 + A1L3 == 1)], s[, all(A3L1 + A3L2 == 1)],
          s[, all(A2L2 + A2L3 <= 1)], s[, sum(Y), .(ID, QES)][, all(V1 == 1)])
d <- s[, .(id = match(ID, sort(unique(ID))), task = as.integer(QES), profile = as.integer(ALT), choice = as.integer(Y),
           attr_covid_situation = fifelse(A1L1 == 1, "Good", fifelse(A1L2 == 1, "Not so good", "Bad")),
           attr_vaccine = fifelse(A2L2 == 1, "Chinese vaccines are available, but not Pfizer or Moderna",
                                  fifelse(A2L3 == 1, "Difficult to get vaccines", "Pfizer/Moderna")),
           attr_government = fifelse(A3L1 == 1, "Election restored", "Election is not restored yet"),
           attr_medical_services = fifelse(A4L2 == 1, "You can visit a clinic only in emergency", "You can easily visit a clinic"))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mon_2024_covid_democracy.csv"))
