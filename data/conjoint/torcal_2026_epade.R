##Democratic / authoritarian candidate conjoint in the EPADE panel (wave 3) from
##Torcal, M. (PI) (2026). Elections, Affective Polarization and Democratic Erosion in 10
##Democracies (EPADE) [Data set]. OSF. https://osf.io/u43pb/ (DOI 10.17605/OSF.IO/U43PB),
##CC BY 4.0 (node licence; the Germany component osf.io/mhaut is also CC BY 4.0). No article yet;
##pre-analysis plan "PAP Conjoint Experiment.docx" at osf.io/fwn9a (read).
##Files read: Data/Germany_2025_Harmonized.dta, Portugal_2025_Harmonized.dta,
##Netherlands_2026_Harmonized_UP.dta, Chile_2026_Harmonized.dta (Stata value labels). Also read
##as text: the four "Survey Data Protocol" PDFs (section "Conjoint Experiment", Table 31) and the
##English wave-3 questionnaires for Germany and Chile.
##Usage: Rscript torcal_2026_epade.R <dir holding the four .dta files> <output dir>
##
##TWO TABLES.
##  torcal_2026_epade_candidates: Germany, Portugal, Netherlands pooled (cov_country). The PAP
##    plans pooled and by-country estimates across EU countries; same 9 attributes, same master
##    wording, same 1-7 rating.
##  torcal_2026_epade_candidates_chile: Chile, kept apart: not in the (EU) PAP, a different tax
##    level wording ("Decrease taxes for all although it meant to reduce social spending.") and the
##    favourability rating is stored 1-10 (value labels 1 Very unfavorable ... 10 Very favorable,
##    although the English questionnaire prints a 1-7 scale).
##Online panel, wave 3 (after national elections); respondents who took wave 3 did the conjoint
##(DE 995, PT 956, NL 811, CL 798; every wave-3 respondent has all 7 tasks). Each saw 7 pairs of
##hypothetical candidates for head of government (task = N in CJ_*_N; profile 1 = Candidate A,
##2 = Candidate B), 9 two-level attributes. Levels and attribute order were "fully randomized"
##(protocol); the attribute order shown was not saved, so there are no attrpos_ columns. The grid
##shows the level texts only (no attribute names) in two columns.
##Attribute text: the master English wording (protocol and English questionnaire), mapped from the
##value codes (1 = first level listed, checked against the value labels). Respondents saw German,
##Portuguese, Dutch or Spanish. The dta value labels are short forms (DE, PT) or back-translations
##(NL: "Lower House", "social security"); the master wording is stored for all three EU countries.
##Chile: the Chile .dta value labels, which are the English Chile questionnaire wording.
##Outcomes:
##  choice: "Which candidate do you prefer as [Chancellor / Prime Minister / President of the
##    Republic]?" Candidate A / Candidate B, forced choice; exactly one chosen per task (checked).
##  rating: "Please rate each of the two candidates for [office]: Candidate A/B" 1 Very
##    unfavorable ... 7 Very favorable (EU; Chile 1-10 as stored). Higher = more favourable.
##The open-ended justification (CJ_3_N) is free text and is dropped.
##Covariates: cov_country (Germany/Portugal/Netherlands; Chile table: Chile), cov_gender (L_Gender:
##Male/Female/Something else -> male/female/other), cov_age (L_Age, years), cov_education
##(L_Education value-label text; 998 No response -> NA, 999 Don't know kept). No survey weight in
##the files.
##Dropped (PII FOUND): record and uuid identifiers, panel respondent IDs (General_ID, ID), session
##identifiers and browser user-agent strings, survey timestamps; all other panel items.
##Respondent id = row order within country, Germany first (EU table).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
L <- list(age = c("40 years old", "60 years old"),
          education = c("University Education", "Non-University Education"),
          law_order = c("Strengthen penalties in existing laws and give more power to the police to maintain order",
                        "Increase guarantees for fair legal process and protect citizens from potential police abuse"),
          culture = c("Defend national values and traditional culture, favoring native nationals",
                      "Protect minority rights of all citizens and foster a multicultural society"),
          decision_style = c("Makes quick decisions without relying on political agreements",
                             "Consults and negotiates with different political and social actors before making decisions"),
          tax = c("Decrease taxes for all to reduce public deficit", "Increase taxes on the wealthy to fund social programs"),
          institutions = c("Completes his/her political program without respecting the control of the parliament and the courts",
                           "Respects the control of the parliament and courts even if it slows his/her governing agenda"),
          civil_society_media = c("Believes organizations in the society and independent media interfere with the will of the majority",
                                  "Supports strong organizations in the society and independent media to ensure the democratic control of the government"),
          crisis = c("Takes unilateral decisions in times of crisis to ensure fast and effective action",
                     "Follows institutional procedures and consults experts and the opposition before making decisions in times of crisis"))
pre <- setNames(paste0("CJ", letters[1:9]), names(L))
one <- function(f, country, rA, rB, chile = FALSE) {
  x <- read_dta(file.path(raw, f)); x <- x[!is.na(x$CJ_1_1), ]
  edu <- as.character(as_factor(x$L_Education, levels = "labels")); edu[zap_labels(x$L_Education) == 998] <- NA
  g <- as.integer(zap_labels(x$L_Gender)); stopifnot(all(g %in% c(1:3, NA)))
  rows <- list()
  for (t in 1:7) for (p in c("A", "B")) {
    ch <- as.integer(zap_labels(x[[paste0("CJ_1_", t)]])); stopifnot(all(ch %in% 1:2))
    r <- as.integer(zap_labels(x[[sprintf(if (p == "A") rA else rB, t)]]))
    d <- data.table(rid = seq_len(nrow(x)), task = t, profile = if (p == "A") 1L else 2L,
                    choice = as.integer(ch == (if (p == "A") 1L else 2L)), rating = r)
    for (k in names(L)) {
      v <- x[[paste0(pre[k], "_", t, "_", p)]]; cd <- as.integer(zap_labels(v)); stopifnot(all(cd %in% 1:2))
      d[, paste0("attr_", k) := if (chile) trimws(names(attr(v, "labels"))[match(cd, attr(v, "labels"))]) else L[[k]][cd]]
    }
    rows[[length(rows) + 1]] <- d
  }
  d <- rbindlist(rows)
  d[, `:=`(cov_country = country, cov_gender = c("male", "female", "other")[g][rid], cov_age = as.integer(zap_labels(x$L_Age))[rid],
           cov_education = edu[rid])]
  d[]
}
eu <- rbind(one("Germany_2025_Harmonized.dta", "Germany", "CJ_2_%drA", "CJ_2_%drB"),
            one("Portugal_2025_Harmonized.dta", "Portugal", "CJ_2_%dr1", "CJ_2_%dr2"),
            one("Netherlands_2026_Harmonized_UP.dta", "Netherlands", "CJ_2_%drA", "CJ_2_%drB"))
k <- paste(eu$cov_country, eu$rid); eu[, id := match(k, unique(k))][, rid := NULL]
cl <- one("Chile_2026_Harmonized.dta", "Chile", "CJ_2_%dA", "CJ_2_%dB", chile = TRUE)
setnames(cl, "rid", "id")
stopifnot(all(eu$rating %in% c(1:7, NA)), all(cl$rating %in% c(1:10, NA)), uniqueN(eu$id) == 995 + 956 + 811, uniqueN(cl$id) == 798)
for (d in list(eu, cl)) stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
for (k in names(L)) stopifnot(uniqueN(cl[[paste0("attr_", k)]]) == 2)
setcolorder(eu, "id"); setcolorder(cl, "id")
setorder(eu, id, task, profile); setorder(cl, id, task, profile)
fwrite(eu, file.path(out, "torcal_2026_epade_candidates.csv"))
fwrite(cl, file.path(out, "torcal_2026_epade_candidates_chile.csv"))
