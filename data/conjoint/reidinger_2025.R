##Group-composition factorial survey (fairness and output expectations) from
##Reidinger, V. (2025). How men react to shifts in gender representation: Ignored interests? Good for
##society? Political Research Quarterly, 78(4), 1394-1407. https://doi.org/10.1177/10659129251364219
##Replication data: Harvard Dataverse doi:10.7910/DVN/IOXIKG, CC0 1.0, no restricted files, no terms.
##(Not the deposit behind reidinger_2026.R, which is 10.7910/DVN/BCYWJK.)
##Files read: fair_dat.RData (object f), out_dat.RData (object o), resp_dat_all.RData (object all; only
##ResponseId and GENDER used). README.html, Rep_Analysis.R, Rep_Diagnostics.R read as text.
##Usage: Rscript reidinger_2025.R <raw dir> <output dir>   (files must be named as in the deposit)
##
##7,047 UK respondents (online panel). Each rated 7 profiles (shown as an attribute table, per the README) of a decision-making body whose
##composition was randomized on five attributes (share of women, age group, class, ethnicity, ideological
##majority; attribute position in the vignette table randomized once per respondent (constant across a respondent's tasks; checked) and recorded as *_loc ->
##attrpos_*). Two separate rating sets exist per respondent, 7 vignettes each, with DIFFERENT randomized
##attribute combinations (checked: attribute levels and positions of f and o disagree for the same
##ResponseId x task number):
##  fair_dat (trial_block = "fairness"): two fairness items, COND_RAT and RECOG_RAT
##  out_dat  (trial_block = "output"):   two output-expectation items, REP_RAT and STAT_RAT
##Table: task 1-7 = fairness vignettes (task number as in fair_dat), task 8-14 = output vignettes
##(out_dat task + 7). The order in which the two blocks were shown to a respondent, and whether the task
##number is the order shown, is not documented in the deposit (task_source = unknown); the rating_* columns of
##the other block are NA. One profile per task; no opt-out.
##Attribute level text. gender and ideology: the authors' own readable recode in Rep_Analysis.R
##("20% Women 80% Men" etc.; newline replaced by a space-comma). age, class, ethnicity: the deposit stores
##only short tags (age_boomerlow, class_bluehigh, ethnicity_minequal ...); the displayed text could not be
##recovered (the PRQ article page is blocked to this agent and the ZORA copy sits behind a bot check), so
##THE TAGS ARE KEPT for those three. LABELS: tags only (age, class, ethnicity).
##  attr_gender    gender    "20% Women, 80% Men" / "50% Women, 50% Men" / "65% Women, 35% Men"
##  attr_ideology  ideology  "40% Left-wing, 60% Right-wing" / "50% Left-wing, 50% Right-wing" / "60% Left-wing, 40% Right-wing"
##  attr_age, attr_class, attr_ethnicity: tags as stored
##Outcomes, 0-10 numeric as stored. The README describes them only in words: COND_RAT "fairness for
##decisions", RECOG_RAT "unfairness to some groups" (fairness perceptions); REP_RAT "decisions in their
##interest", STAT_RAT "future well-being" (output expectations). Question wording and the scale anchors are not
##in the deposit (paraphrase). Direction of RECOG_RAT (is high fair or unfair?) is not documented; stored raw.
##Dropped: ResponseId (platform id; id = integer re-key), open-ended answers and attitude scales in
##resp_dat_male (not read), LR_split (derived). Rows with missing attributes (7 per file) and
##rows with both outcomes of their block missing are omitted.
##Covariates: cov_gender (GENDER: Female -> female, Male -> male, Non-binary -> other, Prefer not to say/NA -> NA).
##Count check: 7,047 respondents x 7 = 49,329 rows per file; after the drops 98,558 rows, 7,043 respondents; the paper's N not checked (article not accessible).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(fn, nm) { e <- new.env(); load(file.path(raw, fn), e); as.data.table(e[[nm]]) }
f <- ld("fair_dat.RData", "f"); o <- ld("out_dat.RData", "o"); al <- ld("resp_dat_all.RData", "all")
o[, task := as.integer(task)]; f[, task := as.integer(task)]
ids <- sort(unique(f$ResponseId)); stopifnot(all(unique(o$ResponseId) %in% ids))
idmap <- setNames(seq_along(ids), ids)
gl <- c(gender_womenlow = "20% Women, 80% Men", gender_womenequal = "50% Women, 50% Men", gender_womenhigh = "65% Women, 35% Men")
il <- c(ideology_righthigh = "40% Left-wing, 60% Right-wing", ideology_equal = "50% Left-wing, 50% Right-wing", ideology_lefthigh = "60% Left-wing, 40% Right-wing")
prep <- function(d, off, blk, o1, o2, n1, n2) {
  d <- d[!is.na(gender) & !is.na(age) & !is.na(class) & !is.na(ethnicity) & !is.na(ideology) & !(is.na(get(o1)) & is.na(get(o2)))]
  data.table(id = unname(idmap[d$ResponseId]), task = d$task + off, profile = 1L,
    rating_cond = NA_real_, rating_recog = NA_real_, rating_rep = NA_real_, rating_stat = NA_real_,
    attr_gender = unname(gl[as.character(d$gender)]), attr_age = as.character(d$age), attr_class = as.character(d$class),
    attr_ethnicity = as.character(d$ethnicity), attr_ideology = unname(il[as.character(d$ideology)]),
    attrpos_gender = d$gender_loc, attrpos_age = d$age_loc, attrpos_class = d$class_loc,
    attrpos_ethnicity = d$ethn_loc, attrpos_ideology = d$ideo_loc, trial_block = blk)[
    , (n1) := d[[o1]]][, (n2) := d[[o2]]][]
}
x <- rbind(prep(f, 0L, "fairness", "COND_RAT", "RECOG_RAT", "rating_cond", "rating_recog"),
           prep(o, 7L, "output", "REP_RAT", "STAT_RAT", "rating_rep", "rating_stat"))
stopifnot(!anyNA(x$attr_gender), !anyNA(x$attr_ideology))
gm <- c(Female = "female", Male = "male", `Non-binary` = "other")
al[, cov_gender := unname(gm[GENDER])]
x <- merge(x, data.table(id = unname(idmap[al$ResponseId]), cov_gender = al$cov_gender), by = "id", all.x = TRUE)
setorder(x, id, task, profile); setcolorder(x, c("id", "task", "profile"))
fwrite(x, file.path(out, "reidinger_2025_gender_representation.csv"))
cat(nrow(x), uniqueN(x$id), "\n")
