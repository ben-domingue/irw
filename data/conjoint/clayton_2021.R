##Immigrant-admission conjoint (France, 2017-18) from
##Clayton, K., Ferwerda, J., & Horiuchi, Y. (2021). Exposure to immigration and admission
##preferences: Evidence from France. Political Behavior, 43(1), 175-200.
##https://doi.org/10.1007/s11109-019-09550-z
##Replication data: Harvard Dataverse doi:10.7910/DVN/2OOLD7, CC0 1.0. File read (from
##ReplicationPackage.tar.gz): clayton-ferwerda-horiuchi/data/Qualtrics/Thesis_Experiment_3.csv
##(raw Qualtrics export, two header rows). Wording: documents/Codebook.docx (Qualtrics codebook,
##English translation) and the CSV's second header row (French); design, level probabilities
##and restrictions: documents/cfh.php (the profile generator, read as text, not run).
##Usage: Rscript clayton_2021.R <dir holding Thesis_Experiment_3.csv> <output dir>
##
##French adults on a Qualtrics online panel, 28 Dec 2017 - 10 Jan 2018. Sample kept as the
##authors' 02_read_qualtrics.R does: Finished (V10 = 1), consented (QID31 = 1), Qualtrics
##"good complete" flag gc = 1, and conjoint tables displayed (F-1-1 not blank; 4 dropped):
##1,500 respondents, matching the article. 10 tasks of 2 profiles ("Immigrant 1/2"), 9 attributes.
##Outcome (choice): "S'il vous fallait choisir entre les deux, lequel ou laquelle de ces deux
##immigrant(e)s devrait être admis(e) ..." (codebook translation: "If you had to choose between
##the two, which of these two immigrants should be admitted to live in France?"), Immigrant 1 /
##Immigrant 2. Forced choice, no opt-out, no rating. Respondents were told to act as an
##immigration officer.
##Attributes (French, as displayed; the authors' English labels in brackets): Pays d'origine
##[Origin], Raison de la demande [Application reason], Visites précédentes en France [Prior
##trips], Profession, Expérience professionnelle [Job experience], Projet d'emploi [Job plans],
##Sexe [Gender], Langue [Language], Niveau scolaire [Education]. Attribute order was randomized
##(once per respondent; constant across that respondent's tasks) with Profession, Expérience
##professionnelle and Projet d'emploi kept together in that order; attrpos_* gives the row
##position (1-9) from the F-t-k columns.
##Randomization: origin weighted (Portugal, Italie, Espagne, Royaume-Uni 0.175 each; Algérie,
##Maroc, Tunisie, Turquie, Chine, Roumanie 0.05 each); others uniform. Restrictions: Professeur,
##Analyste financier(ère), Chercheur(euse), Médecin and Programmeur(euse) only with the two
##highest education levels (université/grande école or deuxième cycle); Infirmier(ère) not with
##the four lowest; Western-European origins (Portugal, Italie,
##Espagne, Royaume-Uni) never with "persecution" as reason or with tourist-visa/unauthorised
##prior visits.
##Survey versions. Three fieldings used slightly different level text:
##  cov_fielding 1 = soft launch 28 Dec 2017 (155 respondents): "Non scolarisé" instead of
##    "Non scolarisé(e)", which did not match the restriction table, so the education
##    restrictions did NOT apply (e.g. "Non scolarisé" doctors occur). The authors drop every
##    task in which either profile pairs no formal education with a doctor, programmer,
##    financial analyst, nurse, professor or research scientist; those tasks are KEPT here.
##  cov_fielding 1 and 2 (2 = 2-4 Jan 2018, 319 respondents): "Ce(tte) demandeur(e) n'a pas un contrat ..." for
##    "n'a pas de contrat ...", and "Cet(te) demandeur(e) a passé six mois ..." for "Ce(tte) ...".
##  cov_fielding 3 = from 5 Jan 2018 (1,026): final wording.
##  These three spelling variants are harmonized here to the final (cfh.php) wording; nothing
##  else differs. cov_fielding is derived from the start date, which is not kept.
##Covariates (source codes and codebook wording unless stated): cov_age_group QID33 as the
##  codebook's band text (18 to 19 years, 20 to 29 years, ..., 60 years and over); cov_gender
##  QID34 (codebook 1 Male, 2 Female -> male/female); cov_education QID15 as the codebook's
##  answer text (No school instruction, Primary school only, High School only, Diploma from a
##  university or a polytechnic school, Postgraduate degree, Other graduate studies);
##  cov_party_id QID18 ("Is there a political party you identify with more than the other
##  parties?") as the codebook's answer text (Standing France, ..., The Republic on the move!,
##  "Others (DVG, DVD, REG, NI, ECO, EXD)", "There is no party I feel closer to than others.").
##  The codebook (documents/Codebook.docx) is the authors' English translation of the French
##  questionnaire; the French option text is not in the deposit, so these texts are English.
##  cov_nationality QID35 (1 born French, 2 became French, 3 foreign; all 1,500 kept
##  respondents are 1); cov_region QID36 (13 metropolitan regions, codebook order); cov_income
##  QID16 (1 EUR 0-19,999 ... 6 EUR 100,000+); cov_left_right QID17 recoded from code 1-11 to
##  the displayed 0-10 (0 far left); cov_voted_2017 QID19 (1 yes 2 no); cov_vote_2017 QID20
##  (1 Macron 2 Le Pen); cov_public_transport QID21 (1 never ... 5 every day); cov_school_
##  satisfaction QID22 (1 very satisfied ... 5 very dissatisfied); cov_contact_everyday QID23
##  (daily exchanges with people born abroad, 1 never ... 5 every day); cov_meal_foreign_born
##  QID24 (shared a meal at home with someone born abroad in past 6 months, 1 yes 2 no);
##  cov_trusted_foreign_born QID25 (trusted people born abroad, 1 = 0, 2 = 1, 3 = 2-5, 4 = 6-10,
##  5 = more than 10); cov_immigration_level QID26 (number of immigrants should be 1 increased a
##  lot ... 5 decreased a lot).
##Dropped: Qualtrics IDs, IP address, latitude/longitude, start/end times, postal code and
##département (the authors' exposure measures are built from postal code + INSEE data, not
##included), free-text comments (QID27) and party "other" text (QID18_TEXT), the panel's
##tic/term/i flags, groupsize (authors: "error in this variable"), Q_TotalDuration (panel-set total duration). No
##survey weight ships; no attention check in the codebook.
##The authors' odd-combination filter removes 332 tasks, all from cov_fielding 1.
##Spot check (2026-10-07): after that filter, language differences in choice probability vs fluent
##French (interpreter -0.1785, tried but unable -0.1523, broken French -0.0924) match the
##authors' AMCEs in figures/_csv/AMCEs.csv (-0.1788, -0.1525, -0.0915) within 0.001.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Thesis_Experiment_3.csv")
h <- strsplit(sub("^\xef\xbb\xbf", "", readLines(f, n = 1, encoding = "UTF-8"), useBytes = TRUE), ",")[[1]]
x <- fread(f, skip = 2, header = FALSE, encoding = "UTF-8", colClasses = "character")
stopifnot(length(h) <= ncol(x)); setnames(x, c(h, paste0("blank", seq_len(ncol(x) - length(h)))))
x <- x[V10 == "1" & QID31 == "1" & gc == "1" & `F-1-1` != ""]
stopifnot(nrow(x) == 1500, uniqueN(x$V1) == 1500)
x[, id := .I]
fix <- function(v) {
  v[v == "Non scolarisé"] <- "Non scolarisé(e)"
  v <- sub("n'a pas un contrat", "n'a pas de contrat", v, fixed = TRUE)
  sub("^Cet\\(te\\) demandeur\\(e\\) a passé six mois", "Ce(tte) demandeur(e) a passé six mois", v)
}
anames <- c("Pays d'origine" = "origin", "Raison de la demande" = "application_reason", "Visites précédentes en France" = "prior_trips",
            "Profession" = "profession", "Expérience professionnelle" = "job_experience", "Projet d'emploi" = "job_plans",
            "Sexe" = "gender", "Langue" = "language", "Niveau scolaire" = "education")
rows <- list()
for (t in 1:10) for (p in 1:2) {
  r <- data.table(id = x$id, task = t, profile = p, choice = as.integer(x[[sprintf("QID%d", 66 + 3 * (t - 1))]] == as.character(p)))
  for (k in 1:9) {
    an <- x[[sprintf("F-%d-%d", t, k)]]; lv <- fix(x[[sprintf("F-%d-%d-%d", t, p, k)]])
    stopifnot(all(an %in% names(anames)))
    for (nm in names(anames)) { i <- an == nm; if (any(i)) { set(r, which(i), paste0("attr_", anames[[nm]]), lv[i]); set(r, which(i), paste0("attrpos_", anames[[nm]]), k) } }
  }
  rows[[length(rows) + 1]] <- r
}
d <- rbindlist(rows, use.names = TRUE)
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", anames), paste0("attrpos_", anames)))
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)])
stopifnot(d[, uniqueN(attrpos_origin), id][, all(V1 == 1)])  # order fixed per respondent
dt <- as.Date(substr(x$V8, 1, 10))
x[, cov_fielding := fifelse(dt <= as.Date("2017-12-28"), 1L, fifelse(dt <= as.Date("2018-01-04"), 2L, 3L))]
cv <- c(QID33 = "age_group", QID34 = "gender", QID35 = "nationality", QID36 = "region", QID15 = "education", QID16 = "income",
        QID17 = "left_right", QID18 = "party_id", QID19 = "voted_2017", QID20 = "vote_2017", QID21 = "public_transport",
        QID22 = "school_satisfaction", QID23 = "contact_everyday", QID24 = "meal_foreign_born", QID25 = "trusted_foreign_born",
        QID26 = "immigration_level")
cx <- x[, .(id, cov_fielding)]
for (v in names(cv)) cx[, paste0("cov_", cv[[v]]) := suppressWarnings(as.integer(x[[v]]))]
cx[, cov_left_right := cov_left_right - 1L]
txt <- list(  # documents/Codebook.docx answer options, by code
  cov_age_group = c("Under 18", "18 to 19 years", "20 to 29 years", "30 to 39 years", "40 to 49 years", "50 to 59 years", "60 years and over"),
  cov_gender = c("male", "female"),
  cov_education = c("No school instruction", "Primary school only", "High School only", "Diploma from a university or a polytechnic school",
                    "Postgraduate degree", "Other graduate studies"),
  cov_party_id = c("Standing France", "Republican People's Union", "National Front", "French Communist Party",
                   "Union of Democrats and Independents", "Left Radical Party", "France insubordinate", "Socialist Party",
                   "Democratic Movement", "The Republicans", "The Republic on the move!", "Others (DVG, DVD, REG, NI, ECO, EXD)",
                   "There is no party I feel closer to than others."))
for (v in names(txt)) { stopifnot(all(cx[[v]] %in% c(seq_along(txt[[v]]), NA))); cx[, (v) := txt[[v]][get(v)]] }
d <- merge(d, cx, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "clayton_2021_france_immigrants.csv"))
