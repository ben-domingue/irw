##Choice-based conjoint on Facebook use situations from
##Pelzer, E. (2019). The potential of conjoint analysis for communication research.
##Communication Research Reports, 36(2), 136-147. https://doi.org/10.1080/08824096.2018.1559138
##Replication data: OSF component "Data" osf.io/dbg7s (project osf.io/kvuwm), licence
##CC-By Attribution 4.0 International (node licence), public.
##Files read: "Cleaned Data File CBC Long-Form.csv" (';'-separated; the authors' long file for
##the choice-based conjoint) and "Cleaned (Final) Data File.csv" (covariates; same 530
##respondents; the long ID = its row number, checked: its CB<situation> answers equal the long
##file's choices in every situation once the respondent below is dropped). Not used: "Raw Data File.csv" (678 SoSci Survey cases incl.
##incomplete ones; it holds free-text comments).
##Usage: Rscript pelzer_2019.R <raw dir> <output dir>
##
##530 German-speaking students (the comments are in German; the "student sample" per the OSF
##project), SoSci Survey 2016. Choice-based conjoint (CBC): 28 choice situations in 4 fixed
##blocks of 7 (1-7, 8-14, 15-21, 22-28; each respondent answered one block, 125/133/136/135
##respondents), each a pair of Facebook-use situations described by 2 attributes:
##  attr_place   "Uses at home" / "Use from elsewhere"
##  attr_motive  "Information Seeking" / "Companioship" [sic] / "Escapism" / "Entertainment"
##LEVEL TEXT = THE AUTHOR'S ENGLISH DUMMY-COLUMN NAMES of the long file (exactly one place and
##one motive dummy is 1 per row, checked); the German wording respondents saw is not deposited.
##task = order of the situation number within the respondent's block (1-7; the deposit has no
##display order), trial_situation = the authors' situation number; profile = Alternative (1/2).
##Outcome: choice = Choice (1 = chosen; exactly one per situation, checked). Question wording not
##deposited (choose the situation that applies more / is preferred: unknown) -> paraphrase in the
##design record. Time (1 = chosen, 2 = not; the Cox-regression coding) is dropped.
##Not built: the traditional conjoint (TC02_01-08: the same 8 full-factorial profiles ranked by
##everyone; a fixed set of profiles, not a randomized conjoint) and the Likert items.
##Covariates (cleaned file; no value labels deposited): cov_gender_code (Geschlecht 1/2),
##cov_age (Alter, years), cov_education_code (Bildung), cov_facebook_frequency_code (Fb_Häufig).
##Dropped: one respondent whose long-file situations (4-10) straddle two blocks and disagree with
##the wide file's answers (529 respondents kept); CASE (survey id), free-text fields (Bildung_Sonst, SD18_01 comments), timings, constant
##columns (Land, Job, Fb_Anmeldung, Fb_Mobil all one value).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Cleaned Data File CBC Long-Form.csv"), sep = ";", encoding = "UTF-8")
setnames(x, c("ID", "Situation", "Alternative", "home", "elsewhere", "info", "comp", "esc", "ent", "Choice", "Time"))
stopifnot(nrow(x) == 7420, uniqueN(x$ID) == 530, x[, .N, .(ID, Situation)][, all(N == 2)],
          x[, sum(Choice), .(ID, Situation)][, all(V1 == 1)], all(x$home + x$elsewhere == 1),
          all(x$info + x$comp + x$esc + x$ent == 1), x[, uniqueN(Situation), ID][, all(V1 == 7)])
# fixed design: one level combination per situation x alternative
stopifnot(nrow(unique(x[, .(Situation, Alternative, home, info, comp, esc, ent)])) == uniqueN(x$Situation) * 2)
# one respondent's situations (4-10) straddle two blocks, against the blocked design and the wide
# file's answers: dropped
x[, blk := (min(Situation) - 1) %% 7 == 0 & max(Situation) - min(Situation) == 6, ID]
stopifnot(x[blk == FALSE, uniqueN(ID)] == 1)
x <- x[blk == TRUE]
x[, task := frank(Situation, ties.method = "dense"), ID]
cl <- fread(file.path(raw, "Cleaned (Final) Data File.csv"), sep = ";", encoding = "UTF-8", na.strings = "")
cl[, lfd.Nr := .I]   # the long file's ID is the cleaned file's row number (lfd.Nr itself has gaps); checked below
# linkage check: the wide file's CB<situation> answer is the chosen alternative in the long file
cb <- melt(cl[, c("lfd.Nr", sprintf("CB%02d", 1:28)), with = FALSE], id.vars = "lfd.Nr", na.rm = TRUE)
cb[, Situation := as.integer(sub("CB", "", variable))]
chk <- x[Choice == 1][cb[lfd.Nr %in% x$ID], on = .(ID = lfd.Nr, Situation)]
agree <- chk$Alternative == as.integer(chk$value)
stopifnot(nrow(chk) == 3703, all(agree))
cat("linkage check: agree", sum(agree, na.rm = TRUE), "disagree", sum(!agree, na.rm = TRUE), "unmatched", sum(is.na(agree)), "\n")
cv <- cl[, .(ID = lfd.Nr, cov_gender_code = as.integer(Geschlecht), cov_age = as.integer(Alter),
             cov_education_code = as.integer(Bildung), cov_facebook_frequency_code = as.integer(`Fb_Häufig`))]
cv[!(cov_age %between% c(15, 100)), cov_age := NA]
d <- x[, .(ID, task, profile = Alternative, choice = Choice,
           attr_place = fifelse(home == 1, "Uses at home", "Use from elsewhere"),
           attr_motive = fifelse(info == 1, "Information Seeking", fifelse(comp == 1, "Companioship", fifelse(esc == 1, "Escapism", "Entertainment"))),
           trial_situation = Situation)]
d <- cv[d, on = "ID"]
setnames(d, "ID", "id"); setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pelzer_2019_facebook_use.csv"))
cat("rows", nrow(d), "resp", uniqueN(d$id), "blocks", d[task == 1 & profile == 1, paste(sort(unique(trial_situation)), collapse = ",")], "\n")
print(d[, .(share = round(mean(choice), 2)), attr_motive]); print(d[, .(share = round(mean(choice), 2)), attr_place])
