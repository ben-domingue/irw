##E-mental-health intervention discrete choice experiment (German general population) from
##Phillips, E. A., Himmler, S. F., & Schreyögg, J. (2021). Preferences for e-mental health interventions
##in Germany: A discrete choice experiment. Value in Health, 24(3), 421-430.
##https://doi.org/10.1016/j.jval.2020.09.018
##Data: OSF project af2rw (https://osf.io/af2rw/), node licence CC BY 4.0, no other terms. Files read
##(from "Analysis repository DCE eMHI ZIP.zip"): data_12_11_reduziert.xlsx (sheet "Export 1.1", one row
##per respondent, Unipark export), "Choice Profiles main study.xlsx" (sheet Tabelle1: choice set,
##alternative, short German level codes). Read as text only: Readme.txt, 01_merge_and_clean_data.do,
##02_main_analysis.do, Codebuch_01_11_2019.pdf (Unipark codebook with the full text of every choice set).
##Usage: Rscript phillips_2021.R <dir holding the two xlsx files> <output dir>
##
##German online panel (Norstat), November 2019, survey in German. 16 choice tasks (one block, Bayesian
##D-efficient fractional design, the same 16 pairs for everyone, shown in this order), two unlabelled
##options (OPTION A / OPTION B), 6 attributes, NO opt-out (article: "We did not include an opt-out option").
##choice: "Bitte wählen Sie eine der beiden Varianten eines Online-Therapieprogramms, die Sie bevorzugen
##würden:" (codebook pages 22-37; answers v_31, v_33-v_47: 1 = OPTION A, 2 = OPTION B, 0 = no answer).
##Task = choice set number (= order shown), profile = 1 (A) / 2 (B): RECORDED.
##Attribute text = the displayed text from the codebook choice-set pages, mapped one-to-one from the
##design file's short codes (verified on all 32 profiles):
##  training (Einführungstraining): Online -> "Online-Lernprogramm (eigenständig)", Telefon ->
##    "Individuell telefonisch", Persönlich -> "Mit einem Trainer in einer Gruppe vor Ort"
##  contact (Menschlicher Kontakt): kein -> "Kein Kontakt", email -> "Per E-Mail", telefon -> "Per Telefon",
##    videotelefonie -> "Per Videotelefonie", persönlich -> "Persönlich (begleitende Therapiesitzungen)"
##  effectiveness (Wirksamkeit bestätigt): wirksam -> "Ja", nicht wirksam -> "Noch nicht"
##  peer_support (Gruppenunterstützung): keine -> "Keine", Forum -> "Online-Forum", Forum plus Treffen ->
##    "Online-Forum plus Gruppentreffen vor Ort"
##  content (Vermittlung von Inhalten): text/audio/video/spiel -> "Überwiegend textbasiert" /
##    "Überwiegend audiobasiert" / "Überwiegend videobasiert" / "Überwiegend spielbasiert (virtuelle Realität)"
##  price (Preis; per month per the article): 0 / 69,9 / 99,9 / 179,9 -> "0 EUR" / "69,90 EUR" / "99,90 EUR" /
##    "179,90 EUR"
##  (The codebook shows "Überwiegend Überwiegend audiobasiert" in one option of choice set 16; the
##  regular text is stored.) Attribute order fixed (codebook order: training, contact, effectiveness,
##  peer support, content, price).
##Two context scenarios (prevention vs mental-health condition) were randomized in equal numbers (article).
##The export has an undocumented system variable c_0001 (codes 1/2, 1,017 / 987 respondents), stored as
##trial_c_0001: it is probably the scenario, but which code is which is not documented.
##20 respondents did not answer choice set 13 (code 0); that task is dropped for them (the authors drop
##these respondents entirely: article N = 1,984). Table: 2,004 respondents.
##Covariates (codebook answer text, German; 0 = no answer -> NA): cov_gender (v_48: weiblich -> female,
##männlich -> male), cov_age (v_49, free-typed "Wie alt sind Sie?": only whole numbers 16-100 kept, other
##entries such as "31 Jahre", "siebzig" or "149" set NA), cov_education (v_50), cov_occupation_field (v_55),
##cov_psychotherapy_experience (v_3, ja/nein), cov_psychotherapy_effectiveness (v_2), cov_online_program_used
##(v_11), cov_social_media_use (v_20), cov_k6_1 ... cov_k6_6 (Kessler-6 items v_12-v_17, raw codes
##1 = immer ... 5 = nie), cov_financial_satisfaction (v_57), cov_online_therapy_acceptable (v_58),
##cov_survey_difficulty (v_52). Dropped: lfdn (participant number, re-keyed), free-text fields (v_5,
##v_8, v_18, v_22, v_53, v_54, v_59), v_10/v_7 (experience ratings, asked only of users), v_23 (consent).
##Check: mean cov_age over respondents 51.2 (article Table 2: 51.2, SD 13.3).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_excel(file.path(raw, "data_12_11_reduziert.xlsx"), sheet = "Export 1.1"))
g <- as.data.table(read_excel(file.path(raw, "Choice Profiles main study.xlsx"), sheet = "Tabelle1"))
stopifnot(nrow(s) == 2004, !anyNA(s$lfdn), uniqueN(s$lfdn) == 2004, nrow(g) == 32)
setorder(s, lfdn); s[, id := seq_len(.N)]
setnames(g, c("task", "profile", "training", "contact", "peer_support", "effectiveness", "price", "content"))
map <- list(
  training = c(Online = "Online-Lernprogramm (eigenständig)", Telefon = "Individuell telefonisch",
               "Persönlich" = "Mit einem Trainer in einer Gruppe vor Ort"),
  contact = c(kein = "Kein Kontakt", email = "Per E-Mail", telefon = "Per Telefon", videotelefonie = "Per Videotelefonie",
              "persönlich" = "Persönlich (begleitende Therapiesitzungen)"),
  effectiveness = c(wirksam = "Ja", "nicht wirksam" = "Noch nicht"),
  peer_support = c(keine = "Keine", Forum = "Online-Forum", "Forum plus Treffen" = "Online-Forum plus Gruppentreffen vor Ort"),
  content = c(text = "Überwiegend textbasiert", audio = "Überwiegend audiobasiert", video = "Überwiegend videobasiert",
              spiel = "Überwiegend spielbasiert (virtuelle Realität)"),
  price = c("0" = "0 EUR", "69,9" = "69,90 EUR", "99,9" = "99,90 EUR", "179,9" = "179,90 EUR"))
for (nm in names(map)) {
  stopifnot(all(as.character(g[[nm]]) %in% names(map[[nm]])))
  g[, paste0("attr_", nm) := unname(map[[nm]][as.character(get(nm))])]
}
g <- g[, c("task", "profile", paste0("attr_", names(map))), with = FALSE]
qc <- c("v_31", paste0("v_", 33:47))
ch <- rbindlist(lapply(1:16, function(t) data.table(id = s$id, task = t, ans = as.integer(s[[qc[t]]]))))
stopifnot(all(ch$ans %in% 0:2), ch[ans == 0, .N] == 20, ch[ans == 0, all(task == 13)])
ch <- ch[ans > 0]
d <- merge(ch[, .(id, task, ans, k = 1)], data.table(profile = 1:2, k = 1), by = "k", allow.cartesian = TRUE)[, k := NULL]
d[, choice := as.integer(profile == ans)][, ans := NULL]
d <- merge(d, g, by = c("task", "profile"))
lab <- function(x, l) { x <- as.integer(x); x[x == 0] <- NA; l[x] }
age <- suppressWarnings(as.integer(ifelse(grepl("^[0-9]+$", s$v_49), s$v_49, NA)))
age[!is.na(age) & (age < 16 | age > 100)] <- NA
freq5 <- c("sehr häufig", "häufig", "gelegentlich", "selten", "nie")
stopifnot(all(s$v_48 %in% 0:2))
cv <- data.table(id = s$id, trial_c_0001 = as.integer(s$c_0001),
  cov_gender = lab(s$v_48, c("female", "male")), cov_age = age,
  cov_education = lab(s$v_50, c("Hauptschule", "Mittlere Reife", "Allgemeine Hochschulreife", "Bachelor", "Master/ Diplom", "PhD")),
  cov_occupation_field = lab(s$v_55, c("IT/ Technologie/ Technik/ Ingenieurwesen", "Bildung/Forschung", "Erziehung",
    "Management/Verkauf/ Bankwesen", "Gesundheit/ Pflege", "Produktion/ Fertigung", "Kunst/ Design", "Medien/ Journalismus",
    "Landwirtschaft", "Transport", "Bauwesen", "Administration", "Handwerk", "Services (Sicherheitsservice, Reinigung, etc.)")),
  cov_psychotherapy_experience = lab(s$v_3, c("ja", "nein")),
  cov_psychotherapy_effectiveness = lab(s$v_2, c("sehr wirksam", "wirksam", "kann mir darunter nichts vorstellen", "weniger wirksam", "nicht wirksam")),
  cov_online_program_used = lab(s$v_11, c("ja", "nein")), cov_social_media_use = lab(s$v_20, freq5),
  cov_k6_1 = as.integer(s[["12"]]), cov_k6_2 = as.integer(s$v_13), cov_k6_3 = as.integer(s$v_14),
  cov_k6_4 = as.integer(s$v_15), cov_k6_5 = as.integer(s$v_16), cov_k6_6 = as.integer(s$v_17),
  cov_financial_satisfaction = lab(s$v_57, c("sehr zufrieden", "zufrieden", "weder zufrieden noch unzufrieden", "unzufrieden", "sehr unzufrieden")),
  cov_online_therapy_acceptable = lab(s$v_58, c("ja", "nein")),
  cov_survey_difficulty = lab(s$v_52, c("sehr einfach", "einfach", "genau richtig", "schwer", "sehr schwer")))
stopifnot(all(unlist(cv[, .(cov_k6_1, cov_k6_2, cov_k6_3, cov_k6_4, cov_k6_5, cov_k6_6)]) %in% 1:5))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          uniqueN(d$id) == 2004, nrow(d) == 2004 * 32 - 40)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "phillips_2021_emental_health.csv"))
