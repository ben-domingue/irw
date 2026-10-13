##Self-test (diagnostic test) factorial survey among German students from
##Kuecuekbalaban, P., Rostalski, T., Schmidt, S., & Muehlan, H. (2017). Psychological, situational and
##application-related determinants of the intention to self-test: a factorial survey among students.
##BMC Health Services Research, 17 (article number not read).
##https://doi.org/10.1186/s12913-017-2394-x
##Data: figshare collection doi:10.6084/m9.figshare.c.3823129 (the row's DOI ..._d3 is the sub-record
##"Additional file 3: Table S3", article 5193871); licence "CC BY + CC0" (figshare API; the collection's
##articles are CC BY 4.0 / CC0 supplements). Files read: 12913_2017_2394_MOESM4_ESM.sav (Additional file 4,
##SPSS, 208 students x 6 vignettes), MOESM1 (Table S1: constructs and outcome wording), MOESM2 (Table S2:
##level texts and mean intention per level and setting) and MOESM3 (Table S3: group Ns), read as text
##after conversion. The Word files are English; the questionnaire itself was German (variable labels are
##German), so the level text is the authors' English description (label_language en, display de).
##Usage: Rscript kuecuekbalaban_2017.R <dir holding the .sav> <output dir>
##Design: each of 208 students (students of a German university; only the faculty is recorded, and dropped) rated 6 text vignettes
##describing a diagnostic test; one vignette per application purpose. VID<d>_<k> are the level codes of
##vignette k (VIGN_k is their concatenation), vign01..vign19_<k> the 19 outcome items. The deposit has NO
##value labels for the level codes (only VID1_k=1 -> "Risikobeurteilung"), so the codes were mapped to the
##English level texts of Table S2 by MATCHING MEANS: for the intention item (see below) the mean over all
##1,248 vignettes at every code of every dimension reproduces the "Total" mean of exactly one Table S2 row to
##two decimals (e.g. VID1 -> 57.89/64.04/60.91/67.79/63.70/65.60; VID2 -> 61.42/62.63/64.72/64.51;
##VID3 group Ns 337/478/433; VID4 -> 63.98/52.89/54.07/52.11/63.02/73.02/67.51; VID5 -> 59.46/61.13/68.99;
##VID6 -> 61.11/64.09/64.89). The mapping is therefore INFERRED, but every code matches uniquely:
##  VID1 application_purpose: 1 Risk assessment, 2 Early detection of a disease, 3 Clinical diagnostics,
##    4 Therapy diagnostics, 5 Drug effect, 6 Monitoring (VID1 always equals the vignette number k).
##  VID2 seriousness_of_situation: 1 acute and life-threatening, 2 acute, but not life-threatening,
##    3 chronic, slowly advancing and life-threatening, 4 chronic, but not life-threatening.
##  VID3 test_setting (the groups of Tables S2/S3): 1 independently at home without the presence of a health
##    professional (ST), 2 at home, conducted by a health professional (HPH), 3 in the doctor's
##    office/hospital by a health professional (HPD).
##  VID4 analysis_and_feedback: 1 analysed automatically, and the result is displayed immediately;
##    2 transmitted automatically and only a conspicuous result is communicated by a health professional;
##    3 transmitted automatically and the result is communicated by a health professional;
##    4 transmitted automatically and the result is communicated in written form;
##    5 analysed in a laboratory and only a conspicuous result is communicated by a health professional;
##    6 analysed in a laboratory and the result is communicated by a health professional;
##    7 analysed in a laboratory and the result is communicated in written form.
##  VID5 medical_expertise_of_tested_person: 1 no, 2 unprofessional, 3 professional.
##  VID6 emotional_support: 1 not present, 2 potentially available, 3 personally present.
##Restrictions: YES. The analysis/feedback levels are nested in the setting: at home alone (ST) only
##levels 1-4 occur, with a health professional at home or in the practice (HPH, HPD) only levels 1, 5, 6, 7
##(cross-table of the codes, matching the dashes in Table S2). Level shares are unequal (observed): e.g.
##seriousness codes 1-4 occur 310/306/239/393 times.
##Outcome (rating, no choice): intention to use the test, the visual analogue scale 1 = certainly not to
##100 = most certainly: "Would you make use of a test that is conducted as described in the situation above?"
##(Table S1, English). The deposit does not name the item; it is vign18_<k> (identified because its
##per-purpose means equal Table S2). The other 18 items per vignette (susceptibility, severity, outcome
##expectancy, ... ) are not named in the deposit and are dropped. Range 1-100, no missing.
##task = k (vignette number 1..6); whether k is the display order is not stated (task_source unknown),
##profile = 1.
##Respondents: 208 rows in the file = the paper's 208 (183+196+192 group counts in Table S3 are respondents
##counted once per setting). The participant code column has 200 distinct values (colliding self-made codes of
##different persons, e.g. AG04 for a 21- and a 19-year-old); it is dropped and id = the file's row index.
##Covariates: cov_gender (1 maennlich -> male, 2 weiblich -> female, from value labels), cov_age (years),
##cov_education (Bildung value label text, German: 4 Abitur/Fachhochschulreife/EOS, 5 Fachhochschul-/
##Universitaetsabschluss). Dropped: occupation, faculty, TA-EG, general self-efficacy and susceptibility items,
##the last-page timestamp (lastpage), the participant code.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "12913_2017_2394_MOESM4_ESM.sav")))
stopifnot(nrow(s) == 208, uniqueN(s$index) == 208)
purpose <- c("Risk assessment", "Early detection of a disease", "Clinical diagnostics", "Therapy diagnostics", "Drug effect", "Monitoring")
serious <- c("acute and life-threatening", "acute, but not life-threatening", "chronic, slowly advancing and life-threatening", "chronic, but not life-threatening")
setting <- c("independently at home without the presence of a health professional", "at home, conducted by a health professional", "in the doctor's office/hospital by a health professional")
analysis <- c("analysed automatically, and the result is displayed immediately",
  "transmitted automatically and only a conspicuous result is communicated by a health professional",
  "transmitted automatically and the result is communicated by a health professional",
  "transmitted automatically and the result is communicated in written form",
  "analysed in a laboratory and only a conspicuous result is communicated by a health professional",
  "analysed in a laboratory and the result is communicated by a health professional",
  "analysed in a laboratory and the result is communicated in written form")
expert <- c("no", "unprofessional", "professional"); support <- c("not present", "potentially available", "personally present")
L <- list()
for (k in 1:6) {
  g <- function(j) as.integer(s[[sprintf("VID%d_%d", j, k)]])
  stopifnot(all(g(1) == k))
  L[[k]] <- data.table(id = as.integer(s$index), task = k, profile = 1L, rating = as.integer(s[[sprintf("vign18_%d", k)]]),
    attr_application_purpose = purpose[g(1)], attr_seriousness = serious[g(2)], attr_test_setting = setting[g(3)],
    attr_analysis_feedback = analysis[g(4)], attr_expertise_of_tested_person = expert[g(5)], attr_emotional_support = support[g(6)])
}
d <- rbindlist(L)
stopifnot(!anyNA(d), d[, all(rating >= 1 & rating <= 100)], d[, .N, id][, all(N == 6)])
# nesting check: the 4 setting-1 analysis levels vs the others
stopifnot(d[attr_test_setting == setting[1], all(attr_analysis_feedback %in% analysis[1:4])],
          d[attr_test_setting != setting[1], all(attr_analysis_feedback %in% analysis[c(1, 5:7)])])
gl <- attr(s$Geschlecht, "labels"); bl <- attr(s$Bildung, "labels")
cv <- data.table(id = as.integer(s$index), cov_gender = c("male", "female")[as.integer(s$Geschlecht)],
                 cov_age = as.integer(s$Alter), cov_education = names(bl)[match(as.integer(s$Bildung), bl)])
d <- merge(d, cv, by = "id"); setcolorder(d, c("id", "task", "profile", "rating")); setorder(d, id, task, profile)
fwrite(d, file.path(out, "kuecuekbalaban_2017_selftest.csv"))
