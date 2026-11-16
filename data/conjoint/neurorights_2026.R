##Neurodata-use choice experiment with a protest option (China), from the replication package "Measuring the Inalienability Boundary of Neurorights:
##A Discrete Choice Experiment with a Protest Option" (authors withheld during peer review; no article located 2026-11-10; year taken from
##the deposit) (Zenodo doi:10.5281/zenodo.23719183, CC BY 4.0; no author is named, so the script and table are topic-named).
##Files read: repkg/data/analysis_ready.csv (one row per respondent x task with the alternative chosen: A, B or protest),
##repkg/data/design_attrs.csv (the attributes of alternatives A and B in each of the 10 questionnaire positions), repkg/data/respondent_level.csv,
##repkg/design/dce_choice_sets.csv and consistency_sets.csv (level text), repkg/code/build_survey_analysis.py (read as text).
##Usage: Rscript neurorights_2026.R <dir holding the unzipped repkg folder> <output dir>
##
##Chinese online sample, 1,019 respondents, 10 tasks each: 8 DCE sets and 2 dominance-based consistency sets (questionnaire positions 2 and 6),
##two alternatives A and B plus a protest option ("reject any compensation"; no attributes: opt-out, not a profile). Alternatives are
##described by 5 attributes: data type (原始神经信号 raw neural signal / 衍生指标 derived indicators), use (学术研究 academic research, 医疗诊疗 medical
##diagnosis and treatment, 商业广告 commercial advertising, 保险核保 insurance underwriting), access control (本人独占 held only by the person /
##机构托管 held in custody by an institution), exit right (可随时撤回 can be withdrawn at any time / 不可撤回 cannot be withdrawn), compensation
##(0元, 1000元, 5000元). Level text is the Chinese text of the design files (label_language zh); the code mapping raw/inst/irr is read from
##build_survey_analysis.py (raw=1 raw signal, inst=1 institutional custody, irr=1 irrevocable). A and B in design_attrs.csv are the positions the
##authors' code reads from the survey export; they are swapped in some sets relative to dce_choice_sets.csv (task 1 A = set 4 B), so design_attrs.csv
##is used (it is the one joined to the respondents' A/B codes in the authors' code and consistent with the consistency sets 9 and 10 at positions 2 and 6).
##Fixed design: all respondents saw the same 10 tasks in the same order (fixed 8 + 2 design; 24 D-optimal candidate profiles in dce_profiles.csv).
##Outcome: choice = which alternative was chosen; protest = both profiles 0 (opt-out). The question wording is not in the deposit.
##trial_task_type marks the two consistency sets ("consistency", positions 2 and 6) versus the 8 "dce" sets.
##Authors' analysis sample: the deposit holds ONLY the retained respondents (the code drops those under age, those who fail both consistency
##sets, straight-liners who chose all A or all B, and those working in the neurotechnology industry; duration and attention rules were not
##executable). The dropped respondents are not in the deposit and cannot be restored; industry is "no" for every row. Flag for Ben.
##Covariates: cov_gender (男 male, 女 female, 其他 other, 不便透露 prefer not to say -> NA; translation of the answer text), cov_education,
##cov_income, cov_health (answer text as stored, Chinese). Dropped: derived scale scores (IUIPC, dignity, privacy, knowledge, familiarity),
##probe class, protest counts, the industry flag. No weights. PII FOUND: none (the respondent id is re-keyed; the package says it is de-identified).
##Respondent count vs paper: no paper located.
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "repkg/data/analysis_ready.csv"))
at <- fread(file.path(raw, "repkg/data/design_attrs.csv"))
stopifnot(d[, uniqueN(id)] == 1019, nrow(d) == 10190, nrow(at) == 20)
at[, `:=`(attr_data_type = fifelse(raw == 1, "原始神经信号", "衍生指标"), attr_use = use,
          attr_access_control = fifelse(inst == 1, "机构托管", "本人独占"),
          attr_exit_right = fifelse(irr == 1, "不可撤回", "可随时撤回"), attr_compensation = paste0(as.integer(comp), "元"))]
# verify the chosen-alternative attributes stored in analysis_ready against design_attrs
chk <- merge(d[alt != "protest"], at, by.x = c("task", "alt"), by.y = c("task", "alt"), suffixes = c("", ".d"))
stopifnot(nrow(chk) == d[alt != "protest", .N], all(chk$raw == chk$raw.d), all(chk$use == chk$use.d), all(chk$inst == chk$inst.d), all(chk$irr == chk$irr.d), all(chk$comp == chk$comp.d))
x <- d[, .(id, task, chosen = alt, gender, edu, income, health)]
prof <- rbind(copy(at)[, profile := 1L][alt == "A"], copy(at)[, profile := 2L][alt == "B"])
x <- merge(x, prof[, .(task, profile, alt, attr_data_type, attr_use, attr_access_control, attr_exit_right, attr_compensation)], by = "task", allow.cartesian = TRUE)
x[, choice := as.integer(chosen == alt)]
stopifnot(x[, sum(choice), .(id, task)][, all(V1 <= 1)], x[, uniqueN(id)] == 1019)
x[, `:=`(cov_gender = fcase(gender == "男", "male", gender == "女", "female", gender == "其他", "other", default = NA_character_),
         cov_education = edu, cov_income = income, cov_health = health,
         trial_task_type = fifelse(task %in% c(2L, 6L), "consistency", "dce"))]
x <- x[, .(id, task, profile, choice, attr_data_type, attr_use, attr_access_control, attr_exit_right, attr_compensation,
           cov_gender, cov_education, cov_income, cov_health, trial_task_type)]
setorder(x, id, task, profile)
fwrite(x, file.path(out, "neurorights_2026_neurodata_dce.csv"))
cat(nrow(x), x[, uniqueN(id)], x[profile == 1, sum(choice)], "\n")
