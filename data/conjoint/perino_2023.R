##Meat-tax referendum vignette experiment (Germany, 2021) from
##Perino, G., & Schwickert, H. (2023). Animal welfare is a stronger determinant of public support for
##meat taxation than climate change mitigation in Germany. Nature Food, 4(2), 160-169.
##https://doi.org/10.1038/s43016-023-00696-y
##Replication data: Harvard Dataverse doi:10.7910/DVN/YNMG1R, CC0 1.0, no restricted files.
##Files read: PerinoSchwickert2023_data.xlsx (one row per respondent x proposal);
##PerinoSchwickert2023_codebook.xlsx; PerinoSchwickert2023_questionnaire_ger.pdf (German
##questionnaire; vote pages 27-50 are screenshots of all 4 schemes x 6 proposals, read for the
##displayed text); PerinoSchwickert2023_stata_code.do read as text (not run).
##Usage: Rscript perino_2023.R <raw dir> <output dir>
##
##3,169 German adults (online panel, quotas on sex, age, region, education, income). Each respondent
##was randomized to one of 8 groups (between subjects): justification (animal welfare / climate) x
##differentiation (uniform / differentiated) x timing of a belief-elicitation task (before or after
##voting; trial_belief_timing). They then voted on 6 proposals for a levy on meat, shown one per page
##in a FIXED order of rising levy ("1. Vorschlag" ... "6. Vorschlag"; questionnaire p.27-50; the
##data's proposal 1-6 always carries tax 0.19 ... 1.56): task = proposal, one profile per task.
##The vote page shows a grid "VORSCHLAG ZUR ABSTIMMUNG"; stored rows (German, as displayed):
##  attr_justification "Begründung für die Abgabe": Tierwohl in der Fleischproduktion /
##     Treibhausgasemissionen der Fleischproduktion
##  attr_revenue_use "Verwendung der Einnahmen aus der Abgabe": Investitionen in die Verbesserung des
##     Tierwohls in der Nutztierhaltung / Investitionen in den Klimaschutz (always paired with the
##     justification: one randomized factor shown in two rows)
##  attr_levy_basis "Höhe der Abgabe": "Für alle Fleischsorten gleich" / "Für alle
##     Haltungsformstufen gleich" (uniform) or "Abhängig von der Fleischsorte" / "Abhängig von der
##     Haltungsformstufe" (differentiated), each followed by ", für pflanzliche Alternativen keine
##     Abgabe". Climate schemes list meat types, animal-welfare schemes list housing stages.
##  attr_levy_row1..4: the four rows of the levy table, "<row label>: +<x> EUR/kg", e.g.
##     "Rind: +0,54 EUR/kg" or "Stufe 1 (Stallhaltung): +0,54 EUR/kg". Uniform: one amount for all
##     rows (0,19 / 0,39 / 0,58 / 0,78 / 1,17 / 1,56 for proposals 1-6). Differentiated: the same four
##     amounts for both justifications (row 1-4 at proposal 1: 0,54 / 0,44 / 0,14 / 0,08; ... at
##     proposal 6: 4,30 / 3,52 / 1,08 / 0,62), read off the screenshots and hard-coded below. The fifth
##     row "Pflanzliche Alternative +0,00 EUR/kg" is constant and not stored, as is the constant row
##     "Zusätzliche Abgabe auf Fleischprodukte: Ja – Pro Kilogramm Fleisch".
##Outcome (questionnaire p.27): "Stimmen Sie diesem Vorschlag zu?" Ja. Ich stimme für die Einführung
##dieser Abgabe. / Nein. Ich stimme gegen die Einführung dieser Abgabe. / Ich möchte nicht abstimmen.
##  choice = 1 for Ja; choice_against = 1 for Nein; an abstention is 0 on both (opt-out).
##  CODING CONFLICT: the codebook says vote 0 = Yes, 1 = No; the authors' do-file (L44) labels 0 = no,
##  1 = yes. The data side with the do-file (share of 1 falls from 0.58 at proposal 1 to 0.23 at
##  proposal 6 and is higher under animal welfare, as the article reports), so 1 = Ja is used.
##Restrictions: yes - the levy rows (meat types vs housing stages) depend on the justification, and
##the amounts are fixed by proposal number and differentiation. Group shares are near-equal
##(389-401 per group) but no source states the assignment probabilities.
##Covariates: cov_age (years), cov_gender (sex: 1 female, 2 male, codebook), cov_education,
##cov_income, cov_region (codebook English labels of the German answer options), cov_duration_sec
##(svytime, survey time in seconds). The article's analyses keep respondents with svytime between
##the 5th and 95th percentiles (do-file L311-323; "more than 2,800"); all 3,169 are kept here.
##Dropped: free-text answers (job/media/pop "other", remark, com), the authors' belief-elicitation
##and attitude batteries, derived variables. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(suppressWarnings(readxl::read_excel(file.path(raw, "PerinoSchwickert2023_data.xlsx"), guess_max = 30000)))
s <- s[, .(id, proposal, vote, scheme, tax, purpose, type, timing, age, sex, edu, inc, region, svytime)]
stopifnot(nrow(s) == 19014, uniqueN(s$id) == 3169, s[, .N, id][, all(N == 6)], s[, uniqueN(scheme), id][, all(V1 == 1)],
          all(s$vote %in% 0:2), all(s$sex %in% 1:2))
upr <- c(0.19, 0.39, 0.58, 0.78, 1.17, 1.56)
stopifnot(all(abs(s$tax - upr[s$proposal]) < 1e-9))
eur <- function(x) paste0("+", formatC(x, format = "f", digits = 2, decimal.mark = ","), " EUR/kg")
dif <- rbind(c(0.54, 0.44, 0.14, 0.08), c(1.08, 0.88, 0.27, 0.16), c(1.61, 1.32, 0.41, 0.23),
             c(2.15, 1.76, 0.54, 0.31), c(3.23, 2.64, 0.81, 0.47), c(4.30, 3.52, 1.08, 0.62))
rowlab <- list(climate = c("Rind", "Lamm", "Schwein", "Geflügel"),
               aw = c("Stufe 1 (Stallhaltung)", "Stufe 2 (Stallhaltung Plus)", "Stufe 3 (Außenklima)", "Stufe 4 (Premium)"))
s[, cl := purpose == 1][, dff := type == 1]
for (k in 1:4) s[, paste0("attr_levy_row", k) := paste0(fifelse(cl, rowlab$climate[k], rowlab$aw[k]), ": ",
                                                       eur(fifelse(dff, dif[cbind(proposal, k)], upr[proposal])))]
sfx <- ", für pflanzliche Alternativen keine Abgabe"
s[, attr_levy_basis := paste0(fifelse(dff, fifelse(cl, "Abhängig von der Fleischsorte", "Abhängig von der Haltungsformstufe"),
                                           fifelse(cl, "Für alle Fleischsorten gleich", "Für alle Haltungsformstufen gleich")), sfx)]
s[, attr_justification := fifelse(cl, "Treibhausgasemissionen der Fleischproduktion", "Tierwohl in der Fleischproduktion")]
s[, attr_revenue_use := fifelse(cl, "Investitionen in den Klimaschutz", "Investitionen in die Verbesserung des Tierwohls in der Nutztierhaltung")]
stopifnot(s[, all(scheme == fifelse(cl, 3L, 1L) + dff)])
edul <- c("Still in school", "Certificate of general secondary education", "Certificate of intermediate secondary education",
         "University-entrance diploma", "University degree/PhD")
incl <- c("Below 1000 EUR", "1000 - below 2000 EUR", "2000 - below 4000 EUR", "4000 - 6000 EUR", "Above 6000 EUR")
regl <- c("Baden-Wuerttemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern",
         "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thueringen")
stopifnot(all(s$edu %in% 1:5), all(s$inc %in% 1:5), all(s$region %in% 1:16))
d <- s[, .(id = as.integer(id), task = as.integer(proposal), profile = 1L,
           choice = as.integer(vote == 1), choice_against = as.integer(vote == 0),
           attr_justification, attr_revenue_use, attr_levy_basis, attr_levy_row1, attr_levy_row2, attr_levy_row3, attr_levy_row4,
           trial_belief_timing = fifelse(timing == 1, "beliefs elicited before voting", "beliefs elicited after voting"),
           cov_age = as.integer(age), cov_gender = c("female", "male")[sex], cov_education = edul[edu], cov_income = incl[inc],
           cov_region = regl[region], cov_duration_sec = as.integer(svytime))]
stopifnot(d[, all(choice + choice_against <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "perino_2023_meat_tax.csv"))
