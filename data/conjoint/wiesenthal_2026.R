##Energy-sharing (renewable energy community) DCE, Germany 2025, from
##Wiesenthal, J., Sagebiel, J., & Yildiz, O. (2026). Willingness to pay for key attributes of
##energy sharing in Germany: data and materials [Data set]. Zenodo.
##https://doi.org/10.5281/zenodo.22829058 (no article yet; preregistration
##https://doi.org/10.17605/OSF.IO/95BE2, not read).
##Data: Zenodo record 22829058, CC BY 4.0 (record licence; README states no other licence).
##Files read: Results_Survey_Final_Sample.xlsx (raw survey export, one row per respondent),
##Questionnaire_Energy_Sharing_DE_EN.pdf (pdftotext; German original + English translation),
##Exemplary_Choice_Set.png (one choice set as shown), README.md. The authors' public analysis
##code (github.com/sagebiej/energysharing_dce, analysis/1_Data_Procession.R and 3_Soziodem.R)
##read as text for the attribute columns and covariate codes. design_final.RDS and the four
##~790 MB simulation files not used.
##Usage: Rscript wiesenthal_2026.R <raw dir> <output dir>
##
##2,401 German household members (online, 2025; all i_STATUS = 5, complete), screened to those
##who decide or co-decide the electricity contract. 10 choice tasks (C1-C10, Questions 29-38):
##"Bitte wählen Sie, ob Sie das Angebot der Bürgerenergiegemeinschaft (BEG) gegenüber Ihrem
##derzeitigen Stromanbieter bevorzugen würden und sich bei einem entsprechenden Angebot
##tatsächlich einen Wechsel vorstellen könnten." Each task shows ONE offer of a renewable energy
##community ("Angebot der BEG") next to the respondent's current supplier ("derzeitiger
##Stromanbieter": "Sie bleiben bei Ihrem Stromanbieter <name>" and the current monthly cost, no
##other attributes). The current supplier is the status quo / outside option, not a profile:
##one profile per task (profile = 1), choice = 1 if the offer was chosen (ChoiceExp_C<t>A1 = 1),
##0 if the current supplier was kept (= 2; test_defaultA1 counts these); opt_out = yes.
##Attributes (text as stored in choiceA1-choiceA50: task t, attribute k in column 5(t-1)+k, per
##1_Data_Procession.R), German as displayed:
##  attr_organizer     Organisator der Bürgerenergiegemeinschaft: Bürger*innen / Kommune (Dorf-,
##                     Stadt, Gemeinde-, Kreisverwaltung) / Stadtwerke
##  attr_participation Investition und Mitbestimmung: Ausschließlich Kund*in der BEG / Investition in
##                     die Anlagen der BEG / Mitgliedschaft in der BEG
##  attr_statutory_goal Satzungsziel: Kein zusätzliches Satzungsziel / Zusätzliches soziales
##                     Satzungsziel / Zusätzliches ökologisches Satzungsziel / Zusätzliches soziales
##                     und ökologisches Satzungsziel
##  attr_contract      Vertragsausgestaltung: Vollversorgung / Geteilte Versorgung
##  attr_electricity_cost Stromkosten: nicht anders / 3 % höher / 6 % höher / 9 % höher / 12 % höher
##                     / 15 % höher. AS STORED: on screen the cell read e.g. "3 % höher als derzeitige
##                     Kosten (≙ 103,00 Euro pro Monat)", the euro amount computed from the
##                     respondent's own monthly bill (questionnaire note to Q29-38); the export keeps
##                     only the relative part, stored as is.
##Design: 40 choice sets in 4 blocks (README; spdesign efficient design), block kept as
##trial_block; fixed blocked design, levels not drawn independently. Attribute row order: the
##questionnaire reconstruction lists Investition, Organisator, Satzungsziel, Vertrag, Stromkosten,
##the screenshot shows Vertragsausgestaltung first; whether order was randomized is not documented.
##Covariates (codes per the authors' 1_Data_Procession.R / 3_Soziodem.R and the questionnaire):
##cov_gender (S1: 1 male, 2 female, 3 diverse = other), cov_birth_year (S2A1; 9 "keine Angabe" NA),
##cov_education (S5, school-leaving qualification, questionnaire Q4 German answer text: (noch) kein
##Schulabschluss / Volks-/Hauptschulabschluss / Mittlere Reife, Realschulabschluss / Abitur,
##Fachabitur / Sonstiges; 99 keine Angabe -> NA), cov_further_education_code (S6 codes, Q5; the
##authors' code maps 1 keinen, 2 Berufsabschluss, 3 Meister, 4 Hochschul- oder Universitätsabschluss;
##codes 5 and 90 also occur and are not mapped by any source, 99 = presumably keine Angabe),
##cov_income (S8 text, Q6 bands; 99 -> NA), cov_state (S9 Bundesland text, 3_Soziodem.R labels),
##cov_duration_sec (i_TIME, interview duration; assumed seconds, median 812).
##Dropped: i_NUMBER (survey respondent number; re-keyed to row order), free-text "other" answers
##(S5A6, S6A6), F3.2 (name of the respondent's electricity supplier, free text), all other
##attitude and electricity items, test_defaultA1 (derived count).
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "Results_Survey_Final_Sample.xlsx"), sheet = 1, guess_max = 5000))
stopifnot(all(x$i_STATUS == 5), !anyDuplicated(x$i_NUMBER))
x[, id := seq_len(.N)]
an <- c("organizer", "participation", "statutory_goal", "contract", "electricity_cost")
d <- rbindlist(lapply(1:10, function(t) {
  r <- data.table(id = x$id, task = t, profile = 1L, ch = x[[sprintf("ChoiceExp_C%dA1", t)]], trial_block = as.integer(x$block))
  for (k in 1:5) r[, paste0("attr_", an[k]) := x[[paste0("choiceA", 5 * (t - 1) + k)]]]
  r
}))
stopifnot(all(d$ch %in% 1:2), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          all(d$attr_contract %in% c("Vollversorgung", "Geteilte Versorgung")),
          all(d$attr_electricity_cost %in% c("nicht anders", paste(c(3, 6, 9, 12, 15), "% höher"))),
          all(x[, rowSums(.SD == 2), .SDcols = patterns("^ChoiceExp")] == x$test_defaultA1))
d[, choice := as.integer(ch == 1)][, ch := NULL]
lab <- function(v, codes, txt) { y <- x[[v]]; stopifnot(all(y %in% c(codes, 99, NA))); txt[match(y, codes)] }
cv <- data.table(id = x$id,
  cov_gender = lab("S1", 1:3, c("male", "female", "other")),
  cov_birth_year = as.integer(ifelse(x$S2A2 == 99, NA, x$S2A1)),
  cov_education = lab("S5", 1:5, c("(noch) kein Schulabschluss", "Volks-/Hauptschulabschluss", "Mittlere Reife, Realschulabschluss",
                                   "Abitur, Fachabitur", "Sonstiges")),
  cov_further_education_code = as.integer(x$S6),
  cov_income = lab("S8", 1:6, c("unter EUR 1.000", "EUR 1.000 bis unter EUR 2.000", "EUR 2.000 bis unter EUR 3.000",
                                "EUR 3.000 bis unter EUR 4.000", "EUR 4.000 bis unter EUR 5.000", "EUR 5.000 und mehr")),
  cov_state = lab("S9", 1:16, c("Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen",
                                "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland",
                                "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen")),
  cov_duration_sec = as.numeric(x$i_TIME))
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wiesenthal_2026_energy_sharing.csv"))
