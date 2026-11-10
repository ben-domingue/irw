##Participatory-process conjoint (Germany) from
##Dean, R., Kindermann, P. A., & Ruler, M. (2026). INSPIRE-PoPPiE Conjoint Survey on Inclusive Participatory Processes,
##Germany 2026 (Version 1.0) [Data set]. Zenodo. (No article.)
##Deposit: Zenodo doi:10.5281/zenodo.23595458 (version DOI; concept twin 23595456 not used), CC BY 4.0 (record licence and the
##README sheet agree). File read: INSPIRE-PoPPiE_master_clean_2026-09-29.xlsx, sheets conjoint_data_long (one row per
##respondent x task x profile), data_full (only resp_id and the row labels __js_F-<task>-<row> and the task-order
##fields), README, routing, conjoint_attributes_codebook (all read as data/text). The authors' GitHub scripts are not read.
##Usage: Rscript dean_2026.R <dir holding the .xlsx> <output dir>
##
##3,002 adults living in Germany (Dynata online panel, non-probability quota sample; Qualtrics, in German; 6 Aug - 29 Sep
##2026), after the authors' own quality screening (completion time under 300 s, straightlining etc.; the retained
##respondents are the file). 4 tasks x 2 profiles ("Verfahren A" = profile 1 and "Verfahren B" = profile 2, side by side),
##6 attributes of a participation process: selection of participants (6 levels), policy area (4), communication (3), mode
##of participation (2), duration (2), obligation of policymakers (3). Attribute levels are the GERMAN text shown to
##respondents (label_language de; the codebook sheet gives English translations that were not fielded).
##Outcomes on the same tasks (both in this table):
##  choice: "Welches Verfahren ist Ihrer Meinung nach die bessere Form der Bürgerbeteiligung?" VERFAHREN A / VERFAHREN B
##    ("In your opinion, which process is the better form of citizen participation?"); forced, no opt-out.
##  rating: "Und inwieweit befürworten oder lehnen Sie Verfahren A und B als Formen der Bürgerbeteiligung ab?" 0 (Lehne stark
##    ab = strongly oppose), 3 (Weder noch), 6 (Befürworte sehr = strongly support), one rating per process; higher = more
##    support, stored raw.
##task = the position at which the task was shown (task_position; the four tasks were shown in random order, the field
##FL_15_DO_Conjoint_task_t holds the position of task t); the source `task` number (the draw index) is not kept.
##Randomization (README / codebook sheets): levels drawn independently per profile; selection of participants has unequal
##probabilities (0.25 for each of the two non-targeted levels, 0.125 for each of the four levels targeting an
##under-represented group); all other attributes equal; no restrictions on combinations (two identical profiles in a task
##were not prevented). Rows 1-2 are fixed to selection and policy area; the other four attributes were randomized once per
##respondent and kept in all four tasks: attr_order = respondent, recorded as attrpos_ (row position 1-6, from __js_F-1-<row>).
##Missing (-99, displayed but not answered): 21 tasks (7 respondents) have no choice: the 6 tasks with no outcome at all (both
##choice and both ratings -99) are dropped, tasks with a rating but no choice keep choice NA on both profiles, a missing single
##rating is NA. Weights: the deposit provides none (quota variables only).
##Covariates: cov_gender (Weiblich female, Männlich male, Divers other), cov_birth_year (dem_birthyear), cov_age_group
##(age_band), cov_education (dem_education, German answer text), cov_party_id (pol_partyclose, the party the respondent feels
##close to, German text; "-99" NA, "Nein, fühle mich keiner Partei verbunden" stays text), cov_left_right (pol_leftright,
##0-10), cov_region (federal state), cov_place (dem_place), cov_duration_sec (meta_duration_sec).
##Dropped: all free-text (_text) columns, occupation items, party vote probabilities, attitude batteries, timers,
##recaptcha score, framing_condition (assigned after the conjoint, for Part 2), the survey's other pages. resp_id (a study id,
##P00214 style) is re-keyed to an integer. No IP, location or panel id is in the file. Respondent count vs paper: no paper.
library(data.table); library(readxl)
a <- commandArgs(TRUE); f <- file.path(a[1], "INSPIRE-PoPPiE_master_clean_2026-09-29.xlsx"); out <- a[2]
l <- as.data.table(read_excel(f, "conjoint_data_long", col_types = "text"))
x <- as.data.table(read_excel(f, "data_full", col_types = "text"))
stopifnot(l[, uniqueN(resp_id)] == 3002, l[, .N, .(resp_id, task)][, all(N == 2)], x[, uniqueN(resp_id)] == 3002)
amap <- c("Die Auswahl der Teilnehmenden erfolgt:" = "selection", "Inhaltlich geht es bei dem Verfahren um:" = "policy_area",
          "Die <u>Teilnehmenden kommunizieren</u> vorrangig:" = "communication", "Im Verfahren werden die Teilnehmenden:" = "mode",
          "Die <u>Dauer</u> des Verfahrens ist:" = "duration", "Die <u>Politik muss</u>:" = "obligation")
pos <- x[, c("resp_id", paste0("__js_F-1-", 1:6)), with = FALSE]
for (k in 1:6) pos[[paste0("p", k)]] <- amap[pos[[paste0("__js_F-1-", k)]]]
stopifnot(!anyNA(pos[, paste0("p", 1:6), with = FALSE]))
pl <- melt(pos[, c("resp_id", paste0("p", 1:6)), with = FALSE], id.vars = "resp_id", variable.name = "row", value.name = "attr")
pl[, row := as.integer(sub("p", "", row))]
pw <- dcast(pl, resp_id ~ attr, value.var = "row"); setnames(pw, names(pw)[-1], paste0("attrpos_", names(pw)[-1]))
## consistency: row labels identical across the four tasks
for (t in 2:4) stopifnot(all(x[[paste0("__js_F-", t, "-3")]] == x[["__js_F-1-3"]]))
l[, fc := conjoint_fchoice]
l[, rt := fifelse(conjoint_rating == "-99", NA_integer_, as.integer(conjoint_rating))]
l[, ch := fifelse(fc == "-99", NA_integer_, as.integer((fc == "VERFAHREN A") == (as.integer(profile) == 1L)))]
l[, none := all(is.na(ch)) & all(is.na(rt)), .(resp_id, task)]
cat("tasks with no outcome dropped:", l[none == TRUE, uniqueN(paste(resp_id, task))], "\n")
l <- l[none == FALSE]
d <- l[, .(rid = resp_id, task = as.integer(task_position), profile = as.integer(profile), choice = ch, rating = rt,
           attr_selection = selection_of_participants, attr_policy_area = policy_area, attr_communication = communication,
           attr_mode_of_participation = mode_of_participation, attr_duration = duration,
           attr_obligation_of_policymakers = obligation_of_policymakers,
           cov_gender = c(Weiblich = "female", `Männlich` = "male", Divers = "other")[dem_gender],
           cov_birth_year = as.integer(dem_birthyear), cov_age_group = age_band, cov_education = dem_education,
           cov_party_id = fifelse(pol_partyclose %in% c("-99", ""), NA_character_, pol_partyclose),
           cov_left_right = fifelse(pol_leftright %in% c("-99", ""), NA_integer_, as.integer(pol_leftright)),
           cov_region = region, cov_place = dem_place)]
setnames(pw, "resp_id", "rid")
d <- merge(d, pw, by = "rid")
du <- x[, .(rid = resp_id, cov_duration_sec = as.integer(round(as.numeric(meta_duration_sec))))]
d <- merge(d, du, by = "rid")
setnames(d, c("attrpos_selection", "attrpos_mode", "attrpos_obligation"), c("attrpos_selection", "attrpos_mode_of_participation", "attrpos_obligation_of_policymakers"))
setnames(d, "attr_selection", "attr_selection_of_participants"); setnames(d, "attrpos_selection", "attrpos_selection_of_participants")
d[, id := as.integer(factor(rid))]; d[, rid := NULL]
stopifnot(!anyNA(d[, .(attr_selection_of_participants, attr_policy_area, attr_communication, attr_mode_of_participation, attr_duration, attr_obligation_of_policymakers)]),
          d[, .N, .(id, task)][, all(N == 2)], d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)],
          d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(task_check <- task)] == 4)
ac <- sort(grep("^attr_", names(d), value = TRUE)); pc <- sort(grep("^attrpos_", names(d), value = TRUE))
cc <- grep("^cov_", names(d), value = TRUE)
setcolorder(d, c("id", "task", "profile", "choice", "rating", ac, pc, cc)); setorder(d, id, task, profile)
fwrite(d, file.path(out, "dean_2026_participatory_processes.csv"))
