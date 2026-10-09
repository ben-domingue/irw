##Campus-speaker factorial vignette experiment (German students, Study 1) from
##Diehl, C., Revers, M., Traunmüller, R., Weidmann, N. B., & Wuttke, A. (2025). Students' motives for
##restricting academic freedom: Viewpoint discrimination and prosocial concerns. Proceedings of the
##National Academy of Sciences, 122(47), e2503804122. https://doi.org/10.1073/pnas.2503804122
##(article not read; the batch candidate list gave 10.1073/pnas.2511105122, which Crossref does not know)
##Data: OSF https://osf.io/ezvm4/ ("Adversarial Collaboration: Freedom of Speech on Campus"),
##licence CC BY 4.0 (OSF node licence). Files read: "Replication material/study_1_data.csv" (Qualtrics
##export), READ ME.txt, study_1_create.R and pnas_replication_study_1.R (read as text, not run),
##"Qualtrics files/AdvCollab_Study_1.qsf" (survey flow, question and answer wording).
##Usage: Rscript diehl_2025.R <dir holding study_1_data.csv> <output dir>
##
##995 students (forsa omninet panel; 1,006 exported rows, 11 empty rows without any vignette dropped).
##Each respondent read 5 vignettes, one per topic: gender identity (Herr F.), women in STEM (Herr K.),
##school drop-out of ethnic minorities (Herr G.), Muslim headscarf (Herr T.), racism against whites
##(Herr S.). Each vignette is text built from three independently randomised parts (qsf flow: one
##BlockRandomizer per part and topic, SubSet 1, all levels listed once):
##  attr_speaker   research_k: journalist presenting his view vs professor presenting research results;
##  attr_statement statement_k: 4 variants = conservative or progressive position x with or without a
##                 political demand ("Er leitet daraus ab, dass ...");
##  attr_reaction  reaction_k: "Einige Gruppen an der Universität kritisieren diese Aussage als
##                 diskriminierend und verletzend." or nothing, stored as "(not shown)" (the randomizer's
##                 other branch sets the field to an empty string).
##task = topic number (1 gender, 2 STEM, 3 minority, 4 headscarf, 5 racism). The first four topic blocks
##were shown in random order (BlockRandomizer SubSet 4) that the export does not record, so task is NOT
##display order for tasks 1-4; the racism vignette was always shown last. trial_topic names the topic.
##profile = 1 (one vignette per task).
##Outcomes (Matrix question under each vignette, answers Ja / Nein, stored as Ja = 1, Nein = 0):
##  rating_cancel       "Sollte die Universität den Vortrag absagen?"
##  rating_revoke       "Sollte die Universität Herrn <X>. einen bereits vergebenen Lehrauftrag entziehen?"
##  rating_remove_book  "Sollte das Buch von Herrn <X>. zu diesem Thema aus der Universitätsbibliothek
##                       entfernt werden?"
##  rating_allow_protest "Sollte die Universität störende Proteste gegen den geplanten Vortrag zulassen?"
##These are yes/no judgements of one vignette, not picks among profiles, so they are ratings. "" and -99
##(no answer) are NA; vignettes with no answer at all are omitted.
##Soft-launch correction: for the 19 soft-launch respondents (soft == 1) the order of the four items
##differed; as in study_1_create.R L12-60 their columns _2,_3,_4,_1 are moved to _1,_2,_3,_4 for all five
##topics before mapping.
##Covariates: cov_gender (gender: Weiblich = female, "Männlich " = male, "Ein anderes Geschlecht" and
##"Kein Geschlecht" = other, "Möchte ich nicht sagen" and -99 = NA), cov_birth_year (birthyear, 1940-2010
##else NA), cov_semester, cov_discipline, cov_state (Bundesland of study), cov_leftright (leftright_1 as
##stored, 1-11), cov_vote (answer text; "Möchte ich nicht sagen" = NA), cov_duration_sec (whole survey).
##Survey weight: the authors compute raking weights in study_1_create.R (anesrake, L396-403); no weight is
##stored in the deposit, so none is kept.
##PII in the source file (dropped): IPAddress and LocationLatitude/Longitude (all rows), RecipientEmail
##(1 row), fpid (forsa panel id), ResponseId; respondents re-keyed 1..995 in file order.
##Not built: Studies 2-4 of the same deposit (separate experiments with different topics/outcomes).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "study_1_data.csv"), encoding = "UTF-8", colClasses = "character")
stopifnot(nrow(s) == 1006)
topics <- c("gender", "stem", "minority", "muslim", "racism")
tlab <- c("gender identity", "women in STEM", "minority school drop-out", "Muslim headscarf", "racism against whites")
for (tp in topics) {
  v <- paste0("vig_", tp, "_", 1:4)
  old <- copy(s[, ..v])
  s[soft == "1", (v) := old[s$soft == "1", c(2, 3, 4, 1), with = FALSE]]
}
s <- s[research_1 != ""]
stopifnot(nrow(s) == 995, all(s$research_5 != ""))
s[, id := .I]
yn <- function(x) { r <- rep(NA_integer_, length(x)); r[x == "Ja"] <- 1L; r[x == "Nein"] <- 0L
  stopifnot(all(x %in% c("Ja", "Nein", "", "-99"))); r }
d <- rbindlist(lapply(1:5, function(k) {
  tp <- topics[k]
  data.table(id = s$id, task = k, profile = 1L, trial_topic = tlab[k],
             rating_cancel = yn(s[[paste0("vig_", tp, "_1")]]), rating_revoke = yn(s[[paste0("vig_", tp, "_2")]]),
             rating_remove_book = yn(s[[paste0("vig_", tp, "_3")]]), rating_allow_protest = yn(s[[paste0("vig_", tp, "_4")]]),
             attr_speaker = trimws(s[[paste0("research_", k)]]), attr_statement = trimws(s[[paste0("statement_", k)]]),
             attr_reaction = trimws(s[[paste0("reaction_", k)]]))
}))
d[attr_reaction == "", attr_reaction := "(not shown)"]
d <- d[!(is.na(rating_cancel) & is.na(rating_revoke) & is.na(rating_remove_book) & is.na(rating_allow_protest))]
stopifnot(all(d$attr_speaker != ""), all(d$attr_statement != ""), d[, uniqueN(attr_statement), task][, all(V1 == 4)],
          d[, uniqueN(attr_speaker), task][, all(V1 == 2)], d[, uniqueN(attr_reaction), task][, all(V1 == 2)])
gmap <- c("Weiblich" = "female", "Männlich" = "male", "Ein anderes Geschlecht" = "other", "Kein Geschlecht" = "other")
stopifnot(all(trimws(s$gender) %in% c(names(gmap), "Möchte ich nicht sagen", "-99")))
nz <- function(x) { x <- trimws(x); x[x %in% c("", "-99")] <- NA; x }
by <- suppressWarnings(as.integer(s$birthyear)); by[!(by %in% 1940:2010)] <- NA
cv <- data.table(id = s$id, cov_gender = unname(gmap[trimws(s$gender)]), cov_birth_year = by,
                 cov_semester = nz(s$semester), cov_discipline = nz(s$discipline), cov_state = nz(s$state),
                 cov_leftright = suppressWarnings(as.integer(nz(s$leftright_1))), cov_vote = nz(s$vote),
                 cov_duration_sec = as.integer(s$Duration..in.seconds.))
cv[cov_vote == "Möchte ich nicht sagen", cov_vote := NA]
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "rating_cancel", "rating_revoke", "rating_remove_book", "rating_allow_protest", "trial_topic"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "diehl_2025_campus_speakers.csv"))
